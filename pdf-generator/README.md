# PDF Card Generator

**Part 2 of DiffusionID Project**

Generates 3" x 7" portrait PDF cards with person images, names, QR codes, and custom messages. Features intelligent text wrapping, conditional layouts, and fully configurable dimensions.

## Installation

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Edit `config.json` to customize all aspects of the PDF layout. All dimensions are in **PostScript points** (1 inch = 72 points).

### Key Configuration Options

**Page & Layout:**
- `page_width_pt`, `page_height_pt`: Page dimensions (default: 216 × 504 pt = 3" × 7")
- `horizontal_padding_pt`: Left/right page margins
- `top_margin_pt`: Top margin before photo section

**Section Heights:**
- `photo_section_height_pt`: Photo area height (default: 320pt)
- `name_box_height_pt_short`: Name box height for short names (≤ threshold)
- `name_box_height_pt_long`: Name box height for long names (> threshold)
- `qr_section_height_pt`: QR code section height
- `message_box_height_pt`: Message section height

**Conditional Name Handling:**
- `name_length_threshold`: Character count to trigger multiline layout (default: 26)
- `name_font_size_pt_short`: Font size for short names
- `name_font_size_pt_long`: Font size for long names (multiline)
- `name_max_lines`: Maximum lines for long names (default: 2)

**Borders & Styling:**
- `name_box_border_sides`: Array of sides to draw borders (e.g., `["left", "right", "top", "bottom"]`)
- `qr_section_border_sides`, `message_box_border_sides`: Border configuration per section
- Border width and color configurable per section

**Spacing:**
- `name_box_horizontal_margin_pt`: Margin outside name box (default: 25pt each side)
- `text_horizontal_padding_pt`: Internal text padding
- `gap_before_message_pt`: Gap between QR and message sections

**Content:**
- `input_csv`: Path to CSV file with person data
- `qr_code_path`: Path to QR code image
- `message_text`: Custom message (supports `<br/>` for line breaks)
- `background_color`: Background color (hex, e.g., `#8DC5FE`)

## Usage

```bash
# Use default config.json
python generate_cards.py

# Use custom config file
python generate_cards.py my_config.json
```

## Input CSV Format

```csv
name,image
RUPALI CHANDANE,input-sample/images/person1.png
Dr Pravin Jadhav,input-sample/images/person2.png
"SARENA MOHAN VARGHESE,MBBS,DCH,DNB",input-sample/images/person3.png
```

**Note:** Names with commas should be quoted. The generator intelligently breaks long names into multiple lines at word/comma boundaries.

## Image Requirements

**Recommended photo dimensions:**
- **Minimum:** 900 × 1333 pixels (300 DPI)
- **Recommended:** 1200 × 1778 pixels (400 DPI)
- **Best:** 1800 × 2667 pixels (600 DPI)
- **Aspect ratio:** ~0.67:1 (portrait)

Images are automatically scaled and centered to fit the photo section while maintaining aspect ratio.

## Features

### Intelligent Text Handling
- **Conditional layout:** Automatically switches to multiline layout for names exceeding threshold
- **Optimal line breaking:** Breaks text at word/comma boundaries closest to threshold
- **Auto-scaling:** Font size reduces if text still doesn't fit

### Flexible Borders
- Configure borders independently for each section (name, QR, message)
- Choose which sides to draw (top, bottom, left, right)
- Customizable width and color per section

### Print-Ready Output
- 300 DPI equivalent quality (216pt × 504pt = 3" × 7" at 72 DPI base)
- Precise point-based positioning
- Professional PDF generation with ReportLab

## Output

PDFs are saved to the output directory with sanitized filenames:
- `rupali_chandane_card.pdf`
- `dr_pravin_jadhav_card.pdf`
- `sarena_mohan_varghese_mbbs_dch_dnb_card.pdf`

## Example Configuration

See `config.json` for a complete example with comments explaining each parameter.
