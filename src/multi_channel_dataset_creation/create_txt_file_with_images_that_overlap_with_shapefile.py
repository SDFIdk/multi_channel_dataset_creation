from osgeo import gdal
import argparse
import sys
import os
import overlap



def create_txt_file_with_files_overlapping_with_shp_file(shape_file,folder,output_txt):
    print("Listing all .tif files...")
    tif_files = [f for f in os.listdir(folder) if f.endswith('.tif')]
    print("filtering away geotiff files that dont overlap with .shp file...")
    overlapping_tif_files= [f for f in tif_files if overlap.shp_geotif_overlap(shp_path=shape_file,tiff_path=f)]
    print("saving the filenames of all overlapping geotiffs to : "+str(output_txt)+ " ...")
    with open(output_txt, 'w') as f:
        f.write('\n'.join(overlapping_tif_files))
    print("printed the filenames to the file : " + output_txt)








if __name__ == "__main__":
    usage_example= "python create_txt_file_with_images_that_overlap_with_shapefile.py --shapefile path/to/file.shp --folder path/to/images/ --output_txt path/to/filenames.txt"
    # Initialize parser
    parser = argparse.ArgumentParser(
        epilog=usage_example,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("--shapefile", required=True, help="Path to the shapefile.")
    parser.add_argument('--folder', help='Path to the root folder of the TIFF files.')
    parser.add_argument('--output_txt', help='Path to the txt were we should save all filenames')
    args = parser.parse_args()


    #### RUN ####
    create_txt_file_with_files_overlapping_with_shp_file(shape_file=args.shapefile,folder=args.folder,output_txt=args.output_txt)
