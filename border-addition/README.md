# Border Addition Module

**Part of DiffusionID Project**

Adds colored borders around the subject silhouette in transparent PNG images. Automatically detects the silhouette boundary and draws a configurable border that follows the actual contour of the subject.

## Visual Examples

| Input (transparent PNG) | Output (with red border) |
|:-----------------------:|:------------------------:|
| ![Input](examples/input_transparent.png) | ![Output](examples/output_bordered.png) |
| Transparent background, no border | Red 2px border around subject silhouette |

**Sample images available in:** `examples/` directory

## Features

- **Silhouette contour following** using morphological dilation
- **Configurable border width** (default: 2px)
- **Customizable border color** (default: red #FF0000)
- **Configuration file support** - set defaults via config.json
- **Batch processing** for multiple images
- **Precise boundary detection** around subject shape
- **Preserves transparency** in output

## Installation

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

The module supports configuration via `config.json` file for setting default values. CLI arguments always override config values.

### Creating Configuration File

1. **Copy example config:**
   ```bash
   cp config.example.json config.json
   ```

2. **Edit config.json:**
   ```json
   {
     "border_color": "#FF0000",
     "border_width": 2,
     "output_directory": "output"
   }
   ```

### Configuration Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `border_color` | String | Border color in hex format | `"#FF0000"` (red) |
| `border_width` | Integer | Border width in pixels (1-100) | `2` |
| `output_directory` | String | Default output directory for batch processing | `"output"` |

### Presets

The config includes helpful presets for common scenarios:
- **thin_red**: 1px red border
- **default_red**: 2px red border (default)
- **thick_red**: 5px red border
- **black_border**: 2px black border for light backgrounds
- **white_border**: 3px white border for dark backgrounds
- **blue_border**: 2px blue border

### Using Configuration

```bash
# Use default config.json in module directory
python add_border.py -d images/ -o output/

# Use custom config file
python add_border.py --config my_config.json -d images/ -o output/

# Override config values with CLI arguments
python add_border.py -d images/ -o output/ -w 5  # Override width
python add_border.py -d images/ -o output/ -c "#0000FF"  # Override color
```

**Priority:** CLI arguments > config.json > hardcoded defaults

## Usage

### Process Single Image

```bash
# Default settings: red border, 2px width
python add_border.py -i input.png -o output.png

# Custom border color and width
python add_border.py -i input.png -o output.png -c "#00FF00" -w 5
```

### Process Directory (Batch Mode)

```bash
# Process all PNG images in a directory
python add_border.py -d input/ -o output/

# With custom settings
python add_border.py -d input/ -o output/ -c "#FF0000" -w 3
```

### Command-Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--input` | `-i` | Input PNG file path | - |
| `--directory` | `-d` | Input directory containing PNG files | - |
| `--output` | `-o` | Output file/directory path | Required |
| `--color` | `-c` | Border color (hex format) | `#FF0000` (red) |
| `--width` | `-w` | Border width in pixels (1-100) | `2` |

**Note:** You must specify either `--input` (for single file) OR `--directory` (for batch processing).

## How It Works

### Silhouette Border Algorithm

1. **Load PNG image** with transparency
2. **Analyze alpha channel** to create a binary mask of the subject
3. **Dilate the mask** using morphological dilation to expand subject pixels outward
4. **Calculate border pixels** by subtracting original mask from dilated mask
5. **Apply border color** to border pixels while preserving the original subject
6. **Save result** as PNG with transparency preserved

### Border Drawing Technique

The border follows the **exact contour/silhouette** of the subject using morphological dilation. This creates a border that wraps around the actual shape of the person, not just a rectangular box.

**How dilation works:**
- Each iteration expands the subject by 1 pixel in all directions
- The number of iterations equals the border width
- Border pixels are the difference between dilated and original masks

**Visual representation:**
```
Original subject → Dilated by 2px → Border is the difference

   ●●●●              ▓▓▓▓▓▓           ▓▓▓▓▓▓
  ●●●●●●            ▓▓●●●●●●▓          ▓▓░░░░▓▓
 ●●●●●●●●          ▓▓●●●●●●●●▓        ▓▓░░░░░░▓▓
●●●●●●●●●●        ▓▓●●●●●●●●●●▓      ▓▓░░░░░░░░▓▓
                                    (border pixels)
```

## Supported Formats

**Input:** PNG with transparency (RGBA mode recommended)
**Output:** PNG with transparency

**Note:** If input is not RGBA, it will be automatically converted.

## Examples

### Example 1: Default Red Border
```bash
# Add 2px red border to all transparent PNGs
python add_border.py -d ../background-removal/output -o output/
```

### Example 2: Thick Blue Border
```bash
# Add 5px blue border
python add_border.py -i subject.png -o subject_blue_border.png -c "#0000FF" -w 5
```

### Example 3: Green Border on Batch
```bash
# Process directory with 3px green border
python add_border.py -d images/ -o bordered/ -c "#00FF00" -w 3
```

### Example 4: Custom Colors
```bash
# Orange border
python add_border.py -i image.png -o image_bordered.png -c "#FF8800" -w 2

# Purple border
python add_border.py -i image.png -o image_bordered.png -c "#8800FF" -w 4
```

## Output

Processed images are saved with `_bordered.png` suffix:
- Input: `doctor_transparent.png` → Output: `doctor_transparent_bordered.png`
- Input: `photo.png` → Output: `photo_bordered.png`

## Integration with Background Removal Module

This module is designed to work seamlessly with the background-removal module:

```bash
# Complete pipeline: Remove background → Add border

# Step 1: Remove blue background
cd background-removal
python remove_background.py -d ../input-sample/images -o output/

# Step 2: Add red border around silhouettes
cd ../border-addition
python add_border.py -d ../background-removal/output -o output/
```

## Configuration Options

### Border Width
- **Minimum:** 1px (subtle outline)
- **Default:** 2px (recommended for most uses)
- **Maximum:** 100px (for dramatic effects)

### Border Colors
Common color codes:
- Red: `#FF0000` (default)
- Blue: `#0000FF`
- Green: `#00FF00`
- Black: `#000000`
- White: `#FFFFFF`
- Orange: `#FF8800`
- Purple: `#8800FF`

Use any valid 6-digit hex color code for custom colors.

## Technical Details

- **Algorithm:** Morphological dilation with binary masks (scipy.ndimage)
- **Precision:** Pixel-perfect silhouette contour following
- **Performance:** Optimized with NumPy array operations
- **Transparency:** Fully preserved in output
- **Border style:** Follows actual subject shape, not rectangular bounding box

## Troubleshooting

### No border visible
- **Check transparency:** Input must have transparent areas
- **Increase width:** Try `-w 5` for more visible border
- **Check color:** Ensure border color contrasts with subject

### Border too thick/thin
- **Adjust width:** Use `-w` parameter (1-100)
- **Preview first:** Test on single image before batch processing

### Border clips at edges
- **Image boundaries:** Border may be clipped if subject touches image edges
- **Solution:** Add padding to input image before processing

### Input not transparent
- **Run background removal first:** Use background-removal module
- **Check format:** Input must be PNG with alpha channel

## Requirements

- Python 3.7+
- Pillow (PIL) 10.0.0+
- NumPy 1.24.0+
- SciPy 1.10.0+

## Project Structure

```
border-addition/
├── add_border.py       # Main processing script
├── config.json         # Configuration file (user-created)
├── config.example.json # Example configuration with presets
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── examples/          # Sample input/output images
    ├── input_transparent.png  # Sample transparent PNG input
    └── output_bordered.png    # Sample output with border
```

## Performance

Processing speed depends on image size and border width:
- **Small images (500x500):** ~0.01s per image
- **Medium images (1500x1500):** ~0.05s per image
- **Large images (3000x3000):** ~0.2s per image

Batch processing is highly efficient for directories with many images.

---

**Status:** Production-Ready
**Default Border Color:** #FF0000 (Red)
**Default Border Width:** 2px (Configurable)
**Border Type:** Silhouette contour following
