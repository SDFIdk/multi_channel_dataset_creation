import argparse
import glob
import json
import os
import shutil
import pathlib

def parse_arguments():
    parser = argparse.ArgumentParser(description="Copy files matching tileid from geojson to output folder.")
    parser.add_argument('--input_path', required=True, help='Input path with wildcards (e.g., /mnt/T/mnt/trainingdata/bygningsudpegning/1km_*/output/)')
    parser.add_argument('--output_path', required=True, help='Path to the output folder where files will be copied.')
    parser.add_argument('--geojson', required=True, help='Path to the GeoJSON file.')
    return parser.parse_args()

def load_geojson(geojson_path):
    with open(geojson_path, 'r') as f:
        return json.load(f)

def find_files(input_path_pattern, tileids):
    matching_files = []
    for tileid in tileids:
        search_pattern = os.path.join(input_path_pattern, f"*{tileid}*")
        print(search_pattern)
        matching_files.extend(glob.glob(search_pattern))
    print(matching_files)
    return matching_files

def copy_files(files, output_path):
    os.makedirs(output_path, exist_ok=True)
    for file_path in files:
        if os.path.isfile(file_path):
            print(f"Copying file: {file_path}")
            shutil.copyfile(file_path, pathlib.Path(output_path)/pathlib.Path(file_path).name)

def main():
    args = parse_arguments()
    
    # Load GeoJSON and extract tileids
    geojson_data = load_geojson(args.geojson)
    tileids = [feature['properties']['tileid'] for feature in geojson_data['features']]
    
    # Find files matching the tileids in the input folder pattern
    files_to_copy = find_files(args.input_path, tileids)
    
    if files_to_copy:
        print(files_to_copy)
        print(f"Found {len(files_to_copy)} files to copy.")
        copy_files(files_to_copy, args.output_path)
    else:
        print("No files found matching the tileid pattern.")

if __name__ == "__main__":
    main()
