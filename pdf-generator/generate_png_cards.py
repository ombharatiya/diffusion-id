#!/usr/bin/env python3
"""
PNG Card Generator
Generates 3" x 7" portrait PNG cards with person image, name, QR code, and message.
Uses the same configuration as PDF generator.
"""

import os
import sys
import json
import csv
import traceback
from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image, ImageDraw, ImageFont


class PNGCardGenerator:
    """Generates PNG cards from CSV input and configuration."""

    def __init__(self, config_path: str = "config.json", scale_factor: int = 4):
        """
        Initialize with configuration file.

        Args:
            config_path: Path to JSON configuration file
            scale_factor: Multiplier for resolution (default 4 = 288 DPI equivalent)
        """
        self.config = self._load_config(config_path)
        self.base_dir = Path(__file__).parent
        self.scale_factor = scale_factor  # For high-resolution output

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file '{config_path}' not found.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in configuration file: {e}")
            sys.exit(1)

    def _validate_image(self, image_path: str) -> bool:
        """Validate that image exists and is readable."""
        if not os.path.exists(image_path):
            print(f"Warning: Image not found: {image_path}")
            return False

        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception as e:
            print(f"Warning: Invalid image file {image_path}: {e}")
            return False

    def _read_csv_data(self) -> List[Dict]:
        """Read person data from CSV file."""
        csv_path = self.base_dir / self.config['input_csv']

        if not csv_path.exists():
            print(f"Error: CSV file not found: {csv_path}")
            sys.exit(1)

        data = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)

        return data

    def _paste_centered_image(self, canvas: Image.Image, image_path: str,
                             x: int, y: int, width: int, height: int) -> None:
        """Paste an image centered horizontally, filling the height, maintaining aspect ratio."""
        with Image.open(image_path) as img:
            img = img.convert('RGBA')
            img_width, img_height = img.size

            # Scale to fill the section
            scale_h = height / img_height
            scale_w = width / img_width
            scale = max(scale_w, scale_h)

            # Calculate final dimensions
            final_width = int(img_width * scale)
            final_height = int(img_height * scale)

            # Resize image
            img_resized = img.resize((final_width, final_height), Image.Resampling.LANCZOS)

            # Center horizontally, align to top vertically
            x_offset = x + (width - final_width) // 2
            y_offset = y

            # Paste image (crop if necessary)
            canvas.paste(img_resized, (x_offset, y_offset))

    def _optimal_line_break(self, text: str, char_threshold: int, max_lines: int = 2) -> List[str]:
        """
        Break text into lines optimally based on character threshold.
        Same logic as PDF generator.
        """
        tokens = []
        current_token = ""

        for char in text:
            if char in [' ', ',']:
                if current_token:
                    if char == ',':
                        tokens.append(current_token + ',')
                    else:
                        tokens.append(current_token)
                    current_token = ""
            else:
                current_token += char

        if current_token:
            tokens.append(current_token)

        if len(tokens) == 0:
            return [text]
        if len(tokens) == 1:
            return [text]

        # For 2 lines, find the optimal break point
        if max_lines == 2:
            best_break = 0
            best_first_line_len = 0

            for i in range(1, len(tokens)):
                first_line = ' '.join(tokens[:i])
                first_line_len = len(first_line)

                if first_line_len <= char_threshold:
                    if first_line_len > best_first_line_len:
                        best_first_line_len = first_line_len
                        best_break = i

            if best_break > 0:
                first_line = ' '.join(tokens[:best_break])
                second_line = ' '.join(tokens[best_break:])
                return [first_line, second_line]
            else:
                mid = len(tokens) // 2
                first_line = ' '.join(tokens[:mid])
                second_line = ' '.join(tokens[mid:])
                return [first_line, second_line]

        # For other cases, use simple greedy approach
        lines = []
        current_line = []

        for token in tokens:
            test_line = ' '.join(current_line + [token])
            if len(test_line) <= char_threshold:
                current_line.append(token)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [token]
                else:
                    lines.append(token)

                if len(lines) >= max_lines:
                    break

        if current_line and len(lines) < max_lines:
            lines.append(' '.join(current_line))

        return lines[:max_lines]

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Get a font at the specified size."""
        # Try to use Helvetica-like fonts, fall back to default
        font_paths = [
            '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
            '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/System/Library/Fonts/Helvetica.ttc',
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    pass

        # Fall back to default font
        return ImageFont.load_default()

    def _draw_centered_text(self, draw: ImageDraw.Draw, text: str,
                           x: int, y: int, width: int, height: int,
                           font_size: int, bold: bool = False,
                           text_padding: int = 10, allow_multiline: bool = False,
                           max_lines: int = 1, char_threshold: int = 22) -> None:
        """Draw centered text within a box."""
        font = self._get_font(font_size, bold)

        if not allow_multiline or max_lines == 1:
            # Single line mode
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            max_width = width - (2 * text_padding)

            # Scale font if text is too wide
            if text_width > max_width:
                scale_factor = max_width / text_width
                new_font_size = int(font_size * scale_factor)
                font = self._get_font(new_font_size, bold)
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

            # Center the text
            text_x = x + (width - text_width) // 2
            text_y = y + (height - text_height) // 2
            draw.text((text_x, text_y), text, fill='black', font=font)
        else:
            # Multiline mode
            lines = self._optimal_line_break(text, char_threshold, max_lines)

            # Calculate line height and total height
            line_height = int(font_size * 1.2)
            total_height = len(lines) * line_height
            start_y = y + (height - total_height) // 2

            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                text_x = x + (width - line_width) // 2
                text_y = start_y + (i * line_height)
                draw.text((text_x, text_y), line, fill='black', font=font)

    def _draw_wrapped_text(self, draw: ImageDraw.Draw, text: str,
                          x: int, y: int, width: int, height: int,
                          font_size: int, text_padding: int = 10) -> None:
        """Draw wrapped text centered within a box."""
        font = self._get_font(font_size)

        # Replace <br/> with newlines
        text = text.replace('<br/>', '\n')

        # Split into lines
        lines = text.split('\n')

        # Calculate line height
        line_height = int(font_size * 1.25)
        total_height = len(lines) * line_height
        start_y = y + (height - total_height) // 2

        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            text_x = x + (width - line_width) // 2
            text_y = start_y + (i * line_height)
            draw.text((text_x, text_y), line, fill='black', font=font)

    def _sanitize_filename(self, name: str) -> str:
        """Convert name to safe filename."""
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_'
                           for c in name)
        safe_name = safe_name.strip().replace(' ', '_').lower()
        return safe_name

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def generate_card(self, person_name: str, person_image_path: str,
                     output_path: str) -> bool:
        """Generate a single PNG card."""

        # Validate inputs
        full_image_path = self.base_dir / person_image_path
        if not self._validate_image(full_image_path):
            return False

        qr_code_path = self.base_dir / self.config['qr_code_path']
        if not self._validate_image(qr_code_path):
            print(f"Error: QR code not found: {qr_code_path}")
            return False

        cfg = self.config

        print(f"  Creating PNG...")
        try:
            # Page dimensions (scaled for high resolution)
            page_width = int(cfg['page_width_pt'] * self.scale_factor)
            page_height = int(cfg['page_height_pt'] * self.scale_factor)

            # Scale all dimensions
            def scale(val):
                return int(val * self.scale_factor)

            # Layout parameters
            h_padding = scale(cfg['horizontal_padding_pt'])
            top_padding = scale(cfg.get('top_padding_pt', 0))
            bottom_padding = scale(cfg.get('bottom_padding_pt', 0))
            top_margin = scale(cfg['top_margin_pt'])
            text_padding = scale(cfg.get('text_horizontal_padding_pt', 10))
            content_width = page_width - (2 * h_padding)

            # Debug output
            print(f"  Page: {page_width}px × {page_height}px (scale {self.scale_factor}x)")
            print(f"  Content area: {content_width}px × ?px")

            # Determine name box size based on name length
            name_length_threshold = cfg.get('name_length_threshold', 22)
            is_long_name = len(person_name) > name_length_threshold

            if is_long_name:
                name_height = scale(cfg['name_box_height_pt_long'])
                name_font_size = scale(cfg['name_font_size_pt_long'])
                name_multiline = True
            else:
                name_height = scale(cfg['name_box_height_pt_short'])
                name_font_size = scale(cfg['name_font_size_pt_short'])
                name_multiline = False

            # Section heights
            photo_height = scale(cfg['photo_section_height_pt'])
            qr_height = scale(cfg['qr_section_height_pt'])
            gap_before_msg = scale(cfg['gap_before_message_pt'])
            message_height = scale(cfg['message_box_height_pt'])
            bottom_box_height = scale(cfg.get('bottom_box_height_pt', 0))

            print(f"  Name: '{person_name}' ({len(person_name)} chars)")
            print(f"  Name box: {name_height}px, Font: {name_font_size}px, Multiline: {name_multiline}")

            # Calculate Y positions (top-down for PIL)
            y_photo = top_padding + top_margin
            y_name = y_photo + photo_height
            y_qr = y_name + name_height
            y_message = y_qr + qr_height + gap_before_msg
            y_bottom_box = y_message + message_height

            # Create canvas with background color (or transparent)
            bg_color_str = cfg.get('background_color', '#8DC5FE')
            use_transparent = bg_color_str.lower() in ['transparent', '', 'none']

            if use_transparent:
                # Create transparent background (RGBA with alpha=0)
                canvas = Image.new('RGBA', (page_width, page_height), (0, 0, 0, 0))
                print(f"  Background: Transparent")
            else:
                # Create with solid color background
                bg_color = self._hex_to_rgb(bg_color_str)
                canvas = Image.new('RGBA', (page_width, page_height), bg_color + (255,))
                print(f"  Background: {bg_color_str}")

            draw = ImageDraw.Draw(canvas)

            # 1. Draw photo section
            self._paste_centered_image(
                canvas, str(full_image_path),
                h_padding, y_photo,
                content_width, photo_height
            )

            # 2. Draw name box
            name_h_margin = scale(cfg.get('name_box_horizontal_margin_pt', 0))
            name_box_x = h_padding + name_h_margin
            name_box_width = content_width - (2 * name_h_margin)

            # White background
            draw.rectangle(
                [name_box_x, y_name, name_box_x + name_box_width, y_name + name_height],
                fill='white'
            )

            # Draw borders
            name_border_sides = cfg.get('name_box_border_sides', [])
            name_border_width = scale(cfg.get('name_box_border_width_pt', 2))
            name_border_color = cfg.get('name_box_border_color', '#000000')

            if name_border_sides:
                border_rgb = self._hex_to_rgb(name_border_color)
                if 'left' in name_border_sides:
                    draw.rectangle(
                        [name_box_x, y_name, name_box_x + name_border_width, y_name + name_height],
                        fill=border_rgb
                    )
                if 'right' in name_border_sides:
                    draw.rectangle(
                        [name_box_x + name_box_width - name_border_width, y_name,
                         name_box_x + name_box_width, y_name + name_height],
                        fill=border_rgb
                    )
                if 'top' in name_border_sides:
                    draw.rectangle(
                        [name_box_x, y_name, name_box_x + name_box_width, y_name + name_border_width],
                        fill=border_rgb
                    )
                if 'bottom' in name_border_sides:
                    draw.rectangle(
                        [name_box_x, y_name + name_height - name_border_width,
                         name_box_x + name_box_width, y_name + name_height],
                        fill=border_rgb
                    )

            # Draw name text
            self._draw_centered_text(
                draw, person_name,
                name_box_x, y_name,
                name_box_width, name_height,
                name_font_size,
                bold=False,
                text_padding=text_padding,
                allow_multiline=name_multiline,
                max_lines=cfg.get('name_max_lines', 2),
                char_threshold=name_length_threshold
            )

            # 3. Draw QR section
            # White background
            draw.rectangle(
                [h_padding, y_qr, h_padding + content_width, y_qr + qr_height],
                fill='white'
            )

            # Draw borders
            qr_border_sides = cfg.get('qr_section_border_sides', [])
            qr_border_width = scale(cfg.get('qr_section_border_width_pt', 2))
            qr_border_color = cfg.get('qr_section_border_color', '#000000')

            if qr_border_sides:
                border_rgb = self._hex_to_rgb(qr_border_color)
                if 'left' in qr_border_sides:
                    draw.rectangle(
                        [h_padding, y_qr, h_padding + qr_border_width, y_qr + qr_height],
                        fill=border_rgb
                    )
                if 'right' in qr_border_sides:
                    draw.rectangle(
                        [h_padding + content_width - qr_border_width, y_qr,
                         h_padding + content_width, y_qr + qr_height],
                        fill=border_rgb
                    )
                if 'top' in qr_border_sides:
                    draw.rectangle(
                        [h_padding, y_qr, h_padding + content_width, y_qr + qr_border_width],
                        fill=border_rgb
                    )
                if 'bottom' in qr_border_sides:
                    draw.rectangle(
                        [h_padding, y_qr + qr_height - qr_border_width,
                         h_padding + content_width, y_qr + qr_height],
                        fill=border_rgb
                    )

            # Draw QR code centered
            qr_size = scale(cfg['qr_code_size_pt'])
            qr_x = h_padding + (content_width - qr_size) // 2
            qr_y_pos = y_qr + (qr_height - qr_size) // 2

            with Image.open(qr_code_path) as qr_img:
                qr_img = qr_img.convert('RGBA')
                qr_img_resized = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
                canvas.paste(qr_img_resized, (qr_x, qr_y_pos))

            # 4. Draw message box
            # White background
            draw.rectangle(
                [h_padding, y_message, h_padding + content_width, y_message + message_height],
                fill='white'
            )

            # Draw borders
            msg_border_sides = cfg.get('message_box_border_sides', [])
            msg_border_width = scale(cfg.get('message_box_border_width_pt', 2))
            msg_border_color = cfg.get('message_box_border_color', '#000000')

            if msg_border_sides:
                border_rgb = self._hex_to_rgb(msg_border_color)
                if 'left' in msg_border_sides:
                    draw.rectangle(
                        [h_padding, y_message, h_padding + msg_border_width, y_message + message_height],
                        fill=border_rgb
                    )
                if 'right' in msg_border_sides:
                    draw.rectangle(
                        [h_padding + content_width - msg_border_width, y_message,
                         h_padding + content_width, y_message + message_height],
                        fill=border_rgb
                    )
                if 'top' in msg_border_sides:
                    draw.rectangle(
                        [h_padding, y_message, h_padding + content_width, y_message + msg_border_width],
                        fill=border_rgb
                    )
                if 'bottom' in msg_border_sides:
                    draw.rectangle(
                        [h_padding, y_message + message_height - msg_border_width,
                         h_padding + content_width, y_message + message_height],
                        fill=border_rgb
                    )

            # Draw message text
            message_font_size = scale(cfg['message_font_size_pt'])
            self._draw_wrapped_text(
                draw, cfg['message_text'],
                h_padding, y_message,
                content_width, message_height,
                message_font_size,
                text_padding=text_padding
            )

            # 5. Draw bottom box (if height > 0)
            if bottom_box_height > 0:
                bottom_h_margin = scale(cfg.get('bottom_box_horizontal_margin_pt', 0))
                bottom_box_x = h_padding + bottom_h_margin
                bottom_box_width = content_width - (2 * bottom_h_margin)

                draw.rectangle(
                    [bottom_box_x, y_bottom_box, bottom_box_x + bottom_box_width,
                     y_bottom_box + bottom_box_height],
                    fill='white'
                )

            # Save PNG
            canvas.save(output_path, 'PNG', optimize=True)
            print(f"  ✓ Successfully created: {output_path}")
            return True

        except Exception as e:
            print(f"  ✗ Error creating PNG: {e}")
            traceback.print_exc()
            return False

    def generate_all_cards(self) -> None:
        """Generate PNG cards for all entries in CSV."""

        # Create output directory
        output_dir = self.base_dir / self.config['output_directory']
        output_dir.mkdir(exist_ok=True)

        # Read CSV data
        print("Reading CSV data...")
        data = self._read_csv_data()
        print(f"Found {len(data)} entries to process.\n")

        # Generate cards
        success_count = 0
        fail_count = 0

        for idx, row in enumerate(data, 1):
            person_name = row.get('name', '').strip()
            person_image = row.get('image', '').strip()

            if not person_name or not person_image:
                print(f"[{idx}/{len(data)}] Skipping row with missing data")
                fail_count += 1
                continue

            print(f"[{idx}/{len(data)}] Processing: {person_name}")

            # Generate output filename
            safe_name = self._sanitize_filename(person_name)
            output_filename = f"{safe_name}.png"
            output_path = output_dir / output_filename

            # Generate card
            if self.generate_card(person_name, person_image, str(output_path)):
                success_count += 1
            else:
                fail_count += 1

            print()

        # Summary
        print("=" * 60)
        print(f"GENERATION COMPLETE")
        print(f"  Total: {len(data)}")
        print(f"  Success: {success_count}")
        print(f"  Failed: {fail_count}")
        print(f"  Output directory: {output_dir}")
        print("=" * 60)


def main():
    """Main entry point."""

    # Check for arguments
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    scale_factor = 4  # 4x scale = 288 DPI equivalent

    print("=" * 60)
    print("PNG CARD GENERATOR")
    print("=" * 60)
    print(f"Configuration: {config_file}")
    print(f"Scale factor: {scale_factor}x (for high resolution)\n")

    # Create generator and run
    generator = PNGCardGenerator(config_file, scale_factor)
    generator.generate_all_cards()


if __name__ == "__main__":
    main()
