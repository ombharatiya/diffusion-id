#!/usr/bin/env python3
"""
Border Addition Module
Adds colored borders around the subject (non-transparent area) in transparent PNG images.
"""

import os
import sys
import argparse
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np


def hex_to_rgb(hex_color):
    """Convert hex color code to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_subject_bbox(img):
    """
    Get bounding box of non-transparent pixels (the subject).

    Args:
        img: PIL Image in RGBA mode

    Returns:
        tuple: (left, top, right, bottom) or None if no non-transparent pixels found
    """
    # Convert to numpy array
    data = np.array(img)

    # Get alpha channel
    alpha = data[:, :, 3]

    # Find non-transparent pixels (alpha > 0)
    non_transparent = alpha > 0

    # Find rows and columns with non-transparent pixels
    rows = np.any(non_transparent, axis=1)
    cols = np.any(non_transparent, axis=0)

    if not rows.any() or not cols.any():
        return None

    # Get bounding box
    row_indices = np.where(rows)[0]
    col_indices = np.where(cols)[0]

    top = row_indices[0]
    bottom = row_indices[-1]
    left = col_indices[0]
    right = col_indices[-1]

    return (left, top, right, bottom)


def add_border_to_subject(input_path, output_path, border_color='#FF0000', border_width=2):
    """
    Add border around the subject (non-transparent area) in transparent PNG.

    Args:
        input_path (str): Path to input PNG file (with transparency)
        output_path (str): Path to output PNG file
        border_color (str): Border color in hex format (e.g., '#FF0000' for red)
        border_width (int): Border width in pixels

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load image
        img = Image.open(input_path)

        # Ensure RGBA mode
        if img.mode != 'RGBA':
            print(f"⚠ Warning: {input_path} is not in RGBA mode. Converting...")
            img = img.convert('RGBA')

        # Get bounding box of subject
        bbox = get_subject_bbox(img)

        if bbox is None:
            print(f"⚠ Warning: No non-transparent pixels found in {input_path}")
            # Still save the image (no border added)
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            img.save(output_path, 'PNG')
            return True

        # Create a copy to draw on
        result = img.copy()
        draw = ImageDraw.Draw(result)

        # Convert border color to RGB
        border_rgb = hex_to_rgb(border_color)

        # Draw border around the bounding box
        left, top, right, bottom = bbox

        # Draw multiple rectangles for border width
        for i in range(border_width):
            # Outer rectangle coordinates
            x0 = left - i
            y0 = top - i
            x1 = right + i
            y1 = bottom + i

            # Ensure coordinates are within image bounds
            x0 = max(0, x0)
            y0 = max(0, y0)
            x1 = min(img.width - 1, x1)
            y1 = min(img.height - 1, y1)

            # Draw rectangle outline
            draw.rectangle([x0, y0, x1, y1], outline=border_rgb + (255,), width=1)

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

        # Save as PNG
        result.save(output_path, 'PNG')

        print(f"✓ Successfully processed: {input_path}")
        print(f"  → Border: {border_color} ({border_width}px) around subject at bbox {bbox}")
        print(f"  → Saved to: {output_path}")

        return True

    except Exception as e:
        print(f"✗ Error processing {input_path}: {str(e)}", file=sys.stderr)
        return False


def process_directory(input_dir, output_dir, border_color='#FF0000', border_width=2):
    """
    Process all PNG images in a directory.

    Args:
        input_dir (str): Input directory path
        output_dir (str): Output directory path
        border_color (str): Border color in hex format
        border_width (int): Border width in pixels

    Returns:
        tuple: (success_count, total_count)
    """
    input_path = Path(input_dir)

    # Get all PNG files
    png_files = [f for f in input_path.iterdir() if f.is_file() and f.suffix.lower() == '.png']

    if not png_files:
        print(f"No PNG files found in {input_dir}")
        return 0, 0

    print(f"\nProcessing {len(png_files)} PNG images from {input_dir}...")
    print(f"Border color: {border_color}")
    print(f"Border width: {border_width}px")
    print("-" * 60)

    success_count = 0

    for img_file in png_files:
        # Create output filename
        output_filename = img_file.stem + '_bordered.png'
        output_path = Path(output_dir) / output_filename

        if add_border_to_subject(str(img_file), str(output_path), border_color, border_width):
            success_count += 1

    print("-" * 60)
    print(f"\nCompleted: {success_count}/{len(png_files)} images processed successfully")

    return success_count, len(png_files)


def main():
    parser = argparse.ArgumentParser(
        description='Add colored borders around subjects in transparent PNG images.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single image with default settings (red border, 2px)
  python add_border.py -i input.png -o output.png

  # Process directory
  python add_border.py -d input/ -o output/

  # Custom border color and width
  python add_border.py -i input.png -o output.png -c "#00FF00" -w 5

  # Thick red border for batch processing
  python add_border.py -d ../background-removal/output -o output/ -w 3
        """
    )

    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-i', '--input', help='Input PNG file')
    input_group.add_argument('-d', '--directory', help='Input directory containing PNG files')

    # Output
    parser.add_argument('-o', '--output', required=True,
                        help='Output file path (for single image) or directory (for batch)')

    # Border color
    parser.add_argument('-c', '--color', default='#FF0000',
                        help='Border color in hex format (default: #FF0000 - red)')

    # Border width
    parser.add_argument('-w', '--width', type=int, default=2,
                        help='Border width in pixels (default: 2)')

    args = parser.parse_args()

    # Validate border width
    if args.width < 1 or args.width > 100:
        print("Error: Border width must be between 1 and 100 pixels", file=sys.stderr)
        sys.exit(1)

    # Process based on input type
    if args.input:
        # Single file mode
        if not os.path.exists(args.input):
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)

        success = add_border_to_subject(args.input, args.output, args.color, args.width)
        sys.exit(0 if success else 1)

    else:
        # Directory mode
        if not os.path.exists(args.directory):
            print(f"Error: Input directory not found: {args.directory}", file=sys.stderr)
            sys.exit(1)

        success_count, total_count = process_directory(
            args.directory, args.output, args.color, args.width
        )

        sys.exit(0 if success_count == total_count else 1)


if __name__ == '__main__':
    main()
