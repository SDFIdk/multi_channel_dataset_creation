import os
import pathlib
import rasterio
from rasterio.windows import Window
from osgeo import ogr



def main(inputfolder, outputfolder, replacestring, newstring, only_consider_files_with_matching_names, shapefile_path):
    files = os.listdir(inputfolder)
    for (index, file) in enumerate(files):
        print("working on file :" + str(index) + " out of :" + str(len(files)))
        input_path = pathlib.Path(inputfolder) / pathlib.Path(file)
        output_path = pathlib.Path(outputfolder) / pathlib.Path(file.replace(replacestring, newstring))
        if only_consider_files_with_matching_names and replacestring not in file:
            pass
        else:
            main_crop_geotiff(geotiff_path=input_path, shapefile_path=shapefile_path, output_path=output_path)


import rasterio
from rasterio.windows import from_bounds

def crop_geotiff(input_path, output_path, bounding_box):
    print("HELLO")
    with rasterio.open(input_path) as src:
        # Create a window based on the bounding box
        window = from_bounds(bounding_box[0], bounding_box[2], bounding_box[1], bounding_box[3], src.transform)

        # Read the data within the window
        data = src.read(window=window)

        # Update the transform for the new window
        window_transform = src.window_transform(window)

        # Update the metadata
        meta = src.meta
        meta.update({
            'driver': 'GTiff',
            'height': window.height,
            'width': window.width,
            'transform': window_transform
        })

        # Write the cropped GeoTIFF
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(data)

# Rest of your code remains unchanged
"""

def crop_geotiff(input_path, output_path, bounding_box):
    with rasterio.open(input_path) as src:
        # Get the window based on the bounding box
        window = src.window(bounding_box[0], bounding_box[2], bounding_box[1], bounding_box[3])

        # Read the data within the window
        data = src.read(window=window)

        # Update the transform for the new window
        window_transform = src.window_transform(window)

        # Update the metadata
        meta = src.meta
        meta.update({
            'driver': 'GTiff',
            'height': window.height,
            'width': window.width,
            'transform': window_transform
        })

        # Write the cropped GeoTIFF
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(data)
"""
def main_crop_geotiff(geotiff_path, shapefile_path, output_path):
    # Open the shapefile to get the bounding box
    shape_ds = ogr.Open(shapefile_path)
    layer = shape_ds.GetLayer()
    extent = layer.GetExtent()

    original_bounds = rasterio.open(geotiff_path).bounds

    # Adjust the bounding box to be within the original image boundaries
    xmin, xmax, ymin, ymax = extent
    xmin = max(xmin, original_bounds.left)
    ymin = max(ymin, original_bounds.bottom)
    xmax = min(xmax, original_bounds.right)
    ymax = min(ymax, original_bounds.top)

    print("shapefile:" + str(extent))
    print("original image :" + str(original_bounds))
    print("rasterio version: " + str([xmin, xmax, ymin, ymax]))

    # Calculate the pixel coordinates of the bounding box
    src = rasterio.open(geotiff_path)
    xmin_pixel, ymin_pixel = map(int, ~src.transform * (xmin, ymin))
    xmax_pixel, ymax_pixel = map(int, ~src.transform * (xmax, ymax))

    # Add a 10-pixel border to the bounding box
    #xmin_pixel -= 10
    #ymin_pixel -= 10
    #xmax_pixel += 10
    #ymax_pixel += 10

    # Ensure the adjusted bounding box is within the image boundaries
    xmin_pixel = max(0, xmin_pixel)
    ymin_pixel = max(0, ymin_pixel)
    xmax_pixel = min(src.width, xmax_pixel)
    ymax_pixel = min(src.height, ymax_pixel)

    # Get the geographic coordinates of the adjusted bounding box
    xmin_adj, ymin_adj = src.transform * (xmin_pixel, ymin_pixel)
    xmax_adj, ymax_adj = src.transform * (xmax_pixel, ymax_pixel)

    print("Adjusted bounding box in pixels: ", [xmin_pixel, xmax_pixel, ymin_pixel, ymax_pixel])
    print("Adjusted bounding box in geographic coordinates: ", [xmin_adj, xmax_adj, ymin_adj, ymax_adj])

    # Crop the GeoTIFF using the adjusted bounding box
    crop_geotiff(geotiff_path, output_path, [xmin_adj, xmax_adj, ymin_adj, ymax_adj])

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Crop GeoTIFF using a shapefile with a 10-pixel border.")
    parser.add_argument("--geotif", required=True, help="Path to the GeoTIFF file.")
    parser.add_argument("--shapefile", required=True, help="Path to the shapefile.")
    args = parser.parse_args()

    output_path = "output_cropped7.tif"  # You can customize the output path if needed
    main_crop_geotiff(args.geotif, args.shapefile, output_path)

