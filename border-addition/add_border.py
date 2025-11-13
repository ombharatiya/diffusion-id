#!/usr/bin/env python3
"""
Border Addition Module
Adds colored borders around the subject silhouette in transparent PNG images.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from PIL import Image
import numpy as np
from scipy.ndimage import binary_dilation


def load_config(config_path='config.json'):
    """
    Load configuration from JSON file.

    Args:
        config_path (str): Path to config file

    Returns:
        dict: Configuration dictionary or empty dict if file doesn't exist
    """
    # Get script directory to find config.json
    script_dir = Path(__file__).parent

    # Check if config_path is absolute or relative
    if not Path(config_path).is_absolute():
        config_path = script_dir / config_path

    if not os.path.exists(config_path):
        return {}

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            # Filter out comment keys
            return {k: v for k, v in config.items() if not k.startswith('_')}
    except json.JSONDecodeError as e:
        print(f"Warning: Error parsing config file {config_path}: {e}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"Warning: Error loading config file {config_path}: {e}", file=sys.stderr)
        return {}


def hex_to_rgb(hex_color):
    """Convert hex color code to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def add_border_to_subject(input_path, output_path, border_color='#FF0000', border_width=2):
    """
    Add border around the subject silhouette (following the contour) in transparent PNG.

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

        # Convert to numpy array
        data = np.array(img)

        # Get alpha channel
        alpha = data[:, :, 3]

        # Create binary mask of non-transparent pixels (subject)
        subject_mask = alpha > 0

        if not subject_mask.any():
            print(f"⚠ Warning: No non-transparent pixels found in {input_path}")
            # Still save the image (no border added)
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            img.save(output_path, 'PNG')
            return True

        # Dilate the subject mask to expand it by border_width pixels
        # Use a circular structuring element for smooth borders
        structure = np.ones((3, 3), dtype=bool)
        dilated_mask = subject_mask.copy()
        for _ in range(border_width):
            dilated_mask = binary_dilation(dilated_mask, structure=structure)

        # Border pixels are: dilated - original
        border_mask = dilated_mask & ~subject_mask

        # Create output image starting from input
        result_data = data.copy()

        # Convert border color to RGBA
        border_rgb = hex_to_rgb(border_color)
        border_rgba = border_rgb + (255,)

        # Apply border color to border pixels
        result_data[border_mask] = border_rgba

        # Convert back to PIL Image
        result = Image.fromarray(result_data, 'RGBA')

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

        # Save as PNG
        result.save(output_path, 'PNG')

        border_pixel_count = np.sum(border_mask)
        print(f"✓ Successfully processed: {input_path}")
        print(f"  → Border: {border_color} ({border_width}px) around subject silhouette")
        print(f"  → Border pixels added: {border_pixel_count}")
        print(f"  → Saved to: {output_path}")

        return True

    except Exception as e:
        print(f"✗ Error processing {input_path}: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
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
        description='Add colored borders around subject silhouettes in transparent PNG images.',
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

  # Use custom config file
  python add_border.py --config custom_config.json -d input/ -o output/
        """
    )

    # Config file
    parser.add_argument('--config', default='config.json',
                        help='Path to config file (default: config.json)')

    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('-i', '--input', help='Input PNG file')
    input_group.add_argument('-d', '--directory', help='Input directory containing PNG files')

    # Output
    parser.add_argument('-o', '--output',
                        help='Output file path (for single image) or directory (for batch)')

    # Border color
    parser.add_argument('-c', '--color',
                        help='Border color in hex format')

    # Border width
    parser.add_argument('-w', '--width', type=int,
                        help='Border width in pixels (1-100)')

    args = parser.parse_args()

    # Load config file
    config = load_config(args.config)

    # Apply config defaults, CLI args override
    if args.color is None:
        args.color = config.get('border_color', '#FF0000')

    if args.width is None:
        args.width = config.get('border_width', 2)

    if args.output is None:
        # Use config output_directory for batch mode
        if args.directory:
            args.output = config.get('output_directory', 'output')
        else:
            print("Error: --output is required for single file mode", file=sys.stderr)
            sys.exit(1)

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
