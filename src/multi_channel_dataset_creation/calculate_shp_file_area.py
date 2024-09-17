import argparse
from osgeo import ogr
from shapely.wkb import loads  # Import loads for WKB conversion
from shapely.geometry import shape
from shapely.ops import unary_union

# Function to calculate area of the shapefile with overlapping polygons
def calculate_area(shapefile_path):
    # Open the shapefile
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(shapefile_path, 0)  # 0 means read-only mode

    if dataSource is None:
        print("Could not open the shapefile")
        return
    
    # Get the layer
    layer = dataSource.GetLayer()

    # Initialize a list to store all polygons
    polygons = []

    # Loop through the features in the shapefile
    for feature in layer:
        geom = feature.GetGeometryRef()
        # Convert the OGR geometry to Shapely geometry
        wkb = geom.ExportToWkb()
        polygons.append(loads(bytes(wkb)))

    # Perform a union of all the polygons
    merged_polygon = unary_union(polygons)

    # Calculate the area
    area = merged_polygon.area

    # Return the calculated area
    return area

# Main function to handle argparse and run the area calculation
def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Calculate the area covered by a shapefile, with overlapping polygons only counted once.")
    parser.add_argument('--shapefile', type=str, help="Path to the shapefile")

    # Parse the arguments
    args = parser.parse_args()

    # Calculate the area using the provided shapefile path
    area = calculate_area(args.shapefile)

    # Print the result
    if area is not None:
        print(f"The area covered by the shapefile is: {area} square units")
        print("Divided by 1000 000  , we get :"+str(area/(1000000)))

# Run the script
if __name__ == "__main__":
    main()
