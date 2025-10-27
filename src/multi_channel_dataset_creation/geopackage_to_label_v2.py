import argparse
import os
import glob
import logging
from pathlib import Path

import geopandas as gpd
import rasterio
from rasterio.features import rasterize
import numpy as np
import pandas as pd
from scipy.ndimage import distance_transform_edt
from shapely.geometry import box

# --- Configuration and Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_label_generation():
    parser = argparse.ArgumentParser(
        description="Converts polygons from a GeoPackage into GeoTIFF label images for semantic segmentation. \n if no --atribute VALUE is given , the areas covered by all polygons will get the same value",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--geopackage", type=str, required=True, help="Path to the input GeoPackage file.")
    parser.add_argument("--input_folder", type=str, required=True, help="Path to the folder containing input GeoTIFF images (RGB).")
    parser.add_argument("--output_folder", type=str, required=True, help="Path to the folder where output label GeoTIFFs will be saved.")
    parser.add_argument("--unknown_boarder_size", type=float, default=0.1, help="Width of the 'unknown' border (value 0) between different class areas, in map units (e.g., meters). Default is 0.1.")
    parser.add_argument("--atribute", type=str, help="The polygon attribute field (column name) used for the class value (e.g., ML_CATEGORY). Must contain integers 0-255. If not provided, all valid polygons will be assigned a class value.")
    parser.add_argument("--background_value", type=int, default=1, help="sets the initial raster background value before filling polygons and borders. If you want areas not covered by a polyogn to be considered unkown, then use ignore_id e.g. 0 ")
    parser.add_argument("--border_value", type=int, default=0, help="Value used for the border/unknown region between polygons. Default is 0.")
    parser.add_argument("--value_used_for_all_polygons", type=int, default=2, help="Value assigned to all polygons if no attribute is provided. Default is 2.")

    args = parser.parse_args()

    # --- Validation ---
    if args.background_value is not None:
        assert args.background_value != args.value_used_for_all_polygons, (
            f"Invalid configuration: background_value ({args.background_value}) cannot be equal to value_used_for_all_polygons ({args.value_used_for_all_polygons})."
        )

    use_constant_class = args.atribute is None
    class_attribute_name = args.atribute

    output_path = Path(args.output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    logging.info(f"Starting label generation. Output folder: {output_path}")

    logging.info(f"Loading GeoPackage: {args.geopackage}")
    gdf = gpd.read_file(args.geopackage)

    if use_constant_class:
        logging.info(f"No attribute provided. All polygons will be treated as class {args.value_used_for_all_polygons}.")
        attr_column = 'label_class_constant'
        gdf[attr_column] = np.uint8(args.value_used_for_all_polygons)
    else:
        attr_column = class_attribute_name
        if attr_column not in gdf.columns:
            print("avilable columns: "+str(gdf.columns))
            raise ValueError(f"Attribute column '{attr_column}' not found in the GeoPackage.")

        original_count = len(gdf)
        missing_mask = pd.isna(gdf[attr_column])
        gdf = gdf[~missing_mask]
        dropped_count = original_count - len(gdf)
        if dropped_count > 0:
            logging.info(f"Removed {dropped_count} polygons because the attribute '{attr_column}' was missing (NaN).")

        try:
            gdf[attr_column] = gdf[attr_column].astype(np.uint8)
        except ValueError as e:
            logging.error(f"Error converting attribute column '{attr_column}' to uint8. Check if values are non-numeric or outside the 0-255 range.")
            raise e

    gdf['area'] = gdf.geometry.area

    raster_files = glob.glob(os.path.join(args.input_folder, '**', '*.tif'), recursive=True)
    raster_files.extend(glob.glob(os.path.join(args.input_folder, '**', '*.tiff'), recursive=True))

    if not raster_files:
        logging.info(f"No GeoTIFF files found in the input folder: {args.input_folder}")
        return

    for input_raster_path in raster_files:
        input_raster_path = Path(input_raster_path)
        output_label_path = output_path / input_raster_path.name
        logging.info(f"Processing image: {input_raster_path.name}")

        with rasterio.open(input_raster_path) as src:
            out_shape = (src.height, src.width)
            out_transform = src.transform
            out_crs = src.crs

            x_res = abs(src.transform.a)
            y_res = abs(src.transform.e)
            mean_res = (x_res + y_res) / 2
            pixel_border_width = args.unknown_boarder_size / mean_res

            bbox = box(*src.bounds)
            gdf_subset = gdf[gdf.geometry.intersects(bbox)].copy()

            fill_value = args.background_value if args.background_value is not None else 0

            if gdf_subset.empty:
                logging.info(f"No valid polygons intersect {input_raster_path.name}. Creating an all-background label file.")
                label_array = np.full(out_shape, fill_value, dtype=np.uint8)
            else:
                gdf_subset = gdf_subset.sort_values(by='area', ascending=False)
                shapes = [(geom, value) for geom, value in zip(gdf_subset.geometry, gdf_subset[attr_column])]

                label_array = rasterize(
                    shapes=shapes,
                    out_shape=out_shape,
                    transform=out_transform,
                    fill=fill_value,
                    dtype=np.uint8,
                    all_touched=False
                )

                padded_labels = np.pad(label_array, 1, mode='edge')
                diff_n = padded_labels[1:-1, 1:-1] != padded_labels[:-2, 1:-1]
                diff_s = padded_labels[1:-1, 1:-1] != padded_labels[2:, 1:-1]
                diff_w = padded_labels[1:-1, 1:-1] != padded_labels[1:-1, :-2]
                diff_e = padded_labels[1:-1, 1:-1] != padded_labels[1:-1, 2:]

                boundary_mask = diff_n | diff_s | diff_w | diff_e
                dt_map = distance_transform_edt(np.invert(boundary_mask))
                border_mask = dt_map < pixel_border_width
                label_array[border_mask] = args.border_value

            profile = src.profile
            profile.update(dtype=rasterio.uint8, count=1, nodata=args.border_value)

            unique, counts = np.unique(label_array, return_counts=True)
            result = dict(zip(unique, counts))
            print("ids presetn in the label image together with their counts")
            print(result)

            with rasterio.open(output_label_path, 'w', **profile) as dst:
                dst.write(label_array, 1)

            logging.info(f"Successfully created label file: {output_label_path.name}")

if __name__ == "__main__":
    process_label_generation()
