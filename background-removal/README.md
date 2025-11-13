# Background Removal Module

**Part of DiffusionID Project**

Removes specific color backgrounds from images and creates transparent PNGs. Designed to remove the blue background (#8DC5FE) from doctor caricature images.

## Features

- **Color-based background removal** with configurable tolerance
- **Batch processing** for multiple images
- **Transparent PNG output** with preserved image quality
- **Flexible color matching** using Euclidean distance algorithm
- **Command-line interface** for easy integration

## Installation

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Process Single Image

```bash
python remove_background.py -i input.png -o output_transparent.png
```

### Process Directory (Batch Mode)

```bash
# Process all images in a directory
python remove_background.py -d ../input-sample/images -o output/

# With custom settings
python remove_background.py -d ../input-sample/images -o output/ -c "#8DC5FE" -t 40
```

### Command-Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--input` | `-i` | Input image file path | - |
| `--directory` | `-d` | Input directory containing images | - |
| `--output` | `-o` | Output file/directory path | Required |
| `--color` | `-c` | Background color to remove (hex format) | `#8DC5FE` |
| `--tolerance` | `-t` | Color matching tolerance (0-255) | `30` |

**Note:** You must specify either `--input` (for single file) OR `--directory` (for batch processing).

## How It Works

### Color Matching Algorithm

The module uses Euclidean distance in RGB color space to identify background pixels:

1. **Load image** and convert to RGBA mode
2. **Calculate color distance** for each pixel from the target background color
3. **Apply tolerance threshold** to determine which pixels are background
4. **Set alpha channel** to 0 (transparent) for matched pixels
5. **Save as PNG** with transparency preserved

### Tolerance Parameter

- **Lower tolerance (0-20):** Only matches colors very close to the target (more precise)
- **Medium tolerance (20-40):** Balanced matching (recommended: 30)
- **Higher tolerance (40-100):** Matches broader range of similar colors (may remove foreground)

**Tip:** Start with default tolerance (30) and adjust if needed. If background remnants remain, increase tolerance. If foreground is affected, decrease tolerance.

## Supported Image Formats

**Input:** PNG, JPG, JPEG, BMP, TIFF, WebP
**Output:** PNG (with transparency)

## Examples

### Example 1: Default Settings
```bash
# Remove blue background (#8DC5FE) with tolerance 30
python remove_background.py -d ../input-sample/images -o output/
```

### Example 2: Custom Color
```bash
# Remove white background
python remove_background.py -i photo.jpg -o photo_transparent.png -c "#FFFFFF" -t 25
```

### Example 3: Higher Tolerance
```bash
# Remove blue background with higher tolerance for gradient backgrounds
python remove_background.py -d images/ -o output/ -c "#8DC5FE" -t 50
```

## Output

Processed images are saved with `_transparent.png` suffix:
- Input: `Source 1.png` → Output: `Source 1_transparent.png`
- Input: `doctor.jpg` → Output: `doctor_transparent.png`

All output files are saved as PNG format with transparency support.

## Integration with Other Modules

This module works independently but can be chained with other modules:

```bash
# Step 1: Remove background
python background-removal/remove_background.py -d input-sample/images -o temp/

# Step 2: Add border (using border-addition module)
python border-addition/add_border.py -d temp/ -o final/
```

## Technical Details

- **Algorithm:** Euclidean distance color matching in RGB space
- **Precision:** Per-pixel alpha channel manipulation
- **Performance:** Optimized with NumPy array operations
- **Memory:** Efficient in-memory processing with PIL/Pillow

## Troubleshooting

### Background not completely removed
- **Increase tolerance:** Try `-t 40` or `-t 50`
- **Check color code:** Verify the exact hex color of your background

### Foreground being removed
- **Decrease tolerance:** Try `-t 20` or `-t 15`
- **Color similarity:** If foreground has colors similar to background, manual editing may be needed

### Output quality issues
- **Always outputs PNG:** Transparency requires PNG format
- **No quality loss:** Processing preserves original image quality

## Requirements

- Python 3.7+
- Pillow (PIL) 10.0.0+
- NumPy 1.24.0+

## Project Structure

```
background-removal/
├── remove_background.py    # Main processing script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

---

**Status:** Production-Ready
**Default Background Color:** #8DC5FE (Light Blue)
**Recommended Tolerance:** 30
