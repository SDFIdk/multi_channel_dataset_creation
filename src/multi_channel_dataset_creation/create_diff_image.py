import argparse
import rasterio
import numpy as np
from pathlib import Path

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Generate single-channel GeoTIFF from two input images.")
    parser.add_argument('--pred_im', type=str, required=True, help="Path to the prediction image (image1).")
    parser.add_argument('--label_im', type=str, required=True, help="Path to the label image (image2).")
    parser.add_argument('--output_diff_image', type=str, required=True, help="Path to save the output difference image.")

    args = parser.parse_args()

    # Ensure the output directory exists
    output_path = Path(args.output_diff_image)
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist

    # Load the two images using the provided file paths
    with rasterio.open(args.pred_im) as src1:
        img1 = src1.read(1).astype(int)
        profile = src1.profile

    with rasterio.open(args.label_im) as src2:
        img2 = src2.read(1).astype(int)

    # find images that are the same
    correct = img1 == img2

    # Generate unique values for each pair (img1, img2)
    unique_values = img1 * 10 + img2
    unique_values[correct] = 0


    # Prepare the profile for the new image
    profile.update(dtype=rasterio.int8, count=1)  # Single-channel image with integer values

    # Save the unique values as a single-channel GeoTIFF to the specified output path
    with rasterio.open(args.output_diff_image, 'w', **profile) as dst:
        dst.write(unique_values, 1)  # Write to the first (and only) band

if __name__ == "__main__":
    main()
