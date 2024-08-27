import pathlib
import os
from osgeo import gdal, ogr
import subprocess

def main(inputfolder,outputfolder,replacestring,newstring,only_consider_files_with_matching_names,shapefile_path):
    """
    croping all images in a folder to the shape of the n.shp file . saving all the croped images in outputfolder after renaming acording to replacestring,newstring
    """
    files = os.listdir(inputfolder)
    croped_to=[]
    tosmall_to=[]
    for (index,file) in enumerate(files):
        print("working on file :"+str(index) + " out of :"+str(len(files)))
        input_path = pathlib.Path(inputfolder)/pathlib.Path(file)
        output_path = pathlib.Path(outputfolder)/pathlib.Path(file.replace(replacestring,newstring))
        if only_consider_files_with_matching_names and replacestring not in file:
            tosmall_to.append(input_path)
        else:
            size= crop_geotiff(geotiff_path=input_path, shapefile_path=shapefile_path, output_path=output_path)
            croped_to.append(size)
    print("to small:"+str(tosmall_to))
    print("croped to :"+str(croped_to))


def crop_geotiff(geotiff_path, shapefile_path, output_path):
    # Open the shapefile to get the bounding box
    shape_ds = ogr.Open(shapefile_path)
    layer = shape_ds.GetLayer()
    extent = layer.GetExtent()

    # Add a 10-pixel border to the bounding box
    xmin, xmax, ymin, ymax = extent
    xmin -= 10
    ymin -= 10
    xmax += 10
    ymax += 10


    min_width = min([xmax- xmin,ymax- ymin])
    if min_width < 1010:
        print("skipping image as it becomes to small after cropping")
    else:
        print("croping the image to size :"+str([xmax- xmin,ymax- ymin]))
        # Build the gdalwarp command
        gdalwarp_cmd = [
            'gdalwarp',
            '-cutline', shapefile_path,
            '-crop_to_cutline',
            '-te', str(xmin), str(ymin), str(xmax), str(ymax),
            '-dstalpha',  # Preserve alpha channel if present
            '-overwrite',  # Overwrite output file if it exists
            geotiff_path,
            output_path
        ]

        # Execute the gdalwarp command
        subprocess.run(gdalwarp_cmd)
        return [xmax- xmin,ymax- ymin]

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Crop GeoTIFF using a shapefile with a 10-pixel border.")
    parser.add_argument("--geotif", required=True, help="Path to the GeoTIFF file.")
    parser.add_argument("--shapefile", required=True, help="Path to the shapefile.")
    args = parser.parse_args()

    output_path = "output_cropped.tif"  # You can customize the output path if needed
    crop_geotiff(args.geotif, args.shapefile, output_path)
