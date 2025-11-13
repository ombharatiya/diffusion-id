# Background Removal Module

**Part of DiffusionID Project**

Removes specific color backgrounds from images and creates transparent PNGs. Designed to remove the blue background (#8DC5FE) from doctor caricature images.

## Visual Examples

| Input (with blue background) | Output (transparent background) |
|:----------------------------:|:--------------------------------:|
| ![Input](examples/input_sample.png) | ![Output](examples/output_transparent.png) |
| Original image with #8DC5FE background | Background removed, transparent PNG |

**Sample images available in:** `examples/` directory

## Features

- **Color-based background removal** with configurable tolerance
- **Multiple colors support** - remove multiple background colors in one pass
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
| `--color` | `-c` | Background color to remove (hex format, can specify multiple times) | `#8DC5FE` |
| `--tolerance` | `-t` | Color matching tolerance (0-255) | `30` |

**Notes:**
- You must specify either `--input` (for single file) OR `--directory` (for batch processing)
- You can specify `-c` multiple times to remove multiple colors in one pass

## How It Works

### Color Matching Algorithm

The module uses Euclidean distance in RGB color space to identify background pixels:

1. **Load image** and convert to RGBA mode
2. **Calculate color distance** for each pixel from the target background color(s)
3. **Apply tolerance threshold** to determine which pixels are background
4. **Combine masks** when multiple colors are specified (uses logical OR)
5. **Set alpha channel** to 0 (transparent) for matched pixels
6. **Save as PNG** with transparency preserved

**Multiple Colors:** When multiple colors are specified, pixels matching ANY of the colors (within tolerance) will be removed.

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

### Example 4: Multiple Colors
```bash
# Remove both blue and white backgrounds
python remove_background.py -i photo.png -o output.png -c "#8DC5FE" -c "#FFFFFF"

# Remove three different background colors
python remove_background.py -i photo.png -o output.png -c "#8DC5FE" -c "#FFFFFF" -c "#000000" -t 25
```

### Example 5: Batch Processing with Multiple Colors
```bash
# Process directory removing both blue and white backgrounds
python remove_background.py -d images/ -o output/ -c "#8DC5FE" -c "#FFFFFF" -t 35
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

### Gradient backgrounds / Color shades at edges
**Problem:** Background has the main color (e.g., #8DC5FE) but also slight variations at corners/edges (e.g., #8CC5FD, #8EC5FF). These leftover pixels become very visible when borders are added.

**Why this happens:**
- Image compression creates color gradients
- Anti-aliasing at edges produces intermediate colors
- Lighting/shadows create subtle color variations

**Solutions:**
1. **Increase tolerance (Recommended):**
   ```bash
   # Try tolerance 40-50 for gradient backgrounds
   python remove_background.py -i input.png -o output.png -t 45

   # For strong gradients, try up to 60
   python remove_background.py -i input.png -o output.png -t 60
   ```

2. **Add multiple similar colors:**
   ```bash
   # Specify main color and lighter/darker variations
   python remove_background.py -i input.png -o output.png -c "#8DC5FE" -c "#8CC5FD" -c "#8EC6FF" -t 30
   ```

**Tip:** Start with `-t 45` for gradient backgrounds. If artifacts remain, increase by 5-10. Monitor the output to ensure foreground isn't affected.

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
├── README.md              # This file
└── examples/              # Sample input/output images
    ├── input_sample.png   # Sample input with blue background
    └── output_transparent.png  # Sample output with transparency
```

---

**Status:** Production-Ready
**Default Background Color:** #8DC5FE (Light Blue)
**Recommended Tolerance:** 30 (flat backgrounds), 45-60 (gradient backgrounds)
