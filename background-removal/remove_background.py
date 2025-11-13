#!/usr/bin/env python3
"""
Background Removal Module
Removes specific color backgrounds from images and creates transparent PNGs.
"""

import os
import sys
import argparse
from pathlib import Path
from PIL import Image
import numpy as np


def hex_to_rgb(hex_color):
    """Convert hex color code to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def remove_background(input_path, output_path, bg_color='#8DC5FE', tolerance=30):
    """
    Remove background color from image and create transparent PNG.

    Args:
        input_path (str): Path to input image
        output_path (str): Path to output PNG file
        bg_color (str): Background color to remove (hex format, e.g., '#8DC5FE')
        tolerance (int): Color matching tolerance (0-255). Higher values match more similar colors.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load image
        img = Image.open(input_path)

        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Convert to numpy array for efficient processing
        data = np.array(img)

        # Get RGB values of background color
        bg_rgb = hex_to_rgb(bg_color)

        # Calculate color distance for each pixel
        r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]

        # Calculate Euclidean distance from background color
        color_diff = np.sqrt(
            (r.astype(int) - bg_rgb[0]) ** 2 +
            (g.astype(int) - bg_rgb[1]) ** 2 +
            (b.astype(int) - bg_rgb[2]) ** 2
        )

        # Create mask: pixels within tolerance of background color
        mask = color_diff <= tolerance

        # Set alpha channel to 0 (transparent) for background pixels
        data[:, :, 3] = np.where(mask, 0, a)

        # Convert back to PIL Image
        result = Image.fromarray(data, 'RGBA')

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

        # Save as PNG
        result.save(output_path, 'PNG')

        print(f"✓ Successfully processed: {input_path}")
        print(f"  → Saved to: {output_path}")

        return True

    except Exception as e:
        print(f"✗ Error processing {input_path}: {str(e)}", file=sys.stderr)
        return False


def process_directory(input_dir, output_dir, bg_color='#8DC5FE', tolerance=30):
    """
    Process all images in a directory.

    Args:
        input_dir (str): Input directory path
        output_dir (str): Output directory path
        bg_color (str): Background color to remove
        tolerance (int): Color matching tolerance

    Returns:
        tuple: (success_count, total_count)
    """
    # Supported image formats
    supported_formats = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}

    input_path = Path(input_dir)

    # Get all image files
    image_files = [
        f for f in input_path.iterdir()
        if f.is_file() and f.suffix.lower() in supported_formats
    ]

    if not image_files:
        print(f"No supported image files found in {input_dir}")
        return 0, 0

    print(f"\nProcessing {len(image_files)} images from {input_dir}...")
    print(f"Background color: {bg_color}")
    print(f"Tolerance: {tolerance}")
    print("-" * 60)

    success_count = 0

    for img_file in image_files:
        # Create output filename (always .png)
        output_filename = img_file.stem + '_transparent.png'
        output_path = Path(output_dir) / output_filename

        if remove_background(str(img_file), str(output_path), bg_color, tolerance):
            success_count += 1

    print("-" * 60)
    print(f"\nCompleted: {success_count}/{len(image_files)} images processed successfully")

    return success_count, len(image_files)


def main():
    parser = argparse.ArgumentParser(
        description='Remove specific color backgrounds from images and create transparent PNGs.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single image
  python remove_background.py -i input.png -o output.png

  # Process directory with default settings
  python remove_background.py -d ../input-sample/images -o output/

  # Custom background color and tolerance
  python remove_background.py -i input.png -o output.png -c "#FF0000" -t 50
        """
    )

    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-i', '--input', help='Input image file')
    input_group.add_argument('-d', '--directory', help='Input directory containing images')

    # Output
    parser.add_argument('-o', '--output', required=True,
                        help='Output file path (for single image) or directory (for batch)')

    # Background color
    parser.add_argument('-c', '--color', default='#8DC5FE',
                        help='Background color to remove in hex format (default: #8DC5FE)')

    # Tolerance
    parser.add_argument('-t', '--tolerance', type=int, default=30,
                        help='Color matching tolerance 0-255 (default: 30)')

    args = parser.parse_args()

    # Validate tolerance
    if not 0 <= args.tolerance <= 255:
        print("Error: Tolerance must be between 0 and 255", file=sys.stderr)
        sys.exit(1)

    # Process based on input type
    if args.input:
        # Single file mode
        if not os.path.exists(args.input):
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)

        success = remove_background(args.input, args.output, args.color, args.tolerance)
        sys.exit(0 if success else 1)

    else:
        # Directory mode
        if not os.path.exists(args.directory):
            print(f"Error: Input directory not found: {args.directory}", file=sys.stderr)
            sys.exit(1)

        success_count, total_count = process_directory(
            args.directory, args.output, args.color, args.tolerance
        )

        sys.exit(0 if success_count == total_count else 1)


if __name__ == '__main__':
    main()
