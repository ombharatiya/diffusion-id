#!/usr/bin/env python3
"""
PDF Card Generator
Generates 3" x 7" portrait cards with person image, name, QR code, and message.
"""

import os
import sys
import json
import csv
import traceback
from pathlib import Path
from typing import Dict, List
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from PIL import Image


class CardGenerator:
    """Generates PDF cards from CSV input and configuration."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize with configuration file."""
        self.config = self._load_config(config_path)
        self.base_dir = Path(__file__).parent
        
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
    
    def _get_image_dimensions(self, image_path: str) -> tuple:
        """Get image dimensions."""
        with Image.open(image_path) as img:
            return img.size
    
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
    
    def _draw_centered_image(self, c, image_path: str, x: float, y: float, 
                            width: float, height: float, max_width: float, max_height: float):
        """Draw an image centered horizontally, filling the height, maintaining aspect ratio."""
        img_width, img_height = self._get_image_dimensions(image_path)
        
        # Scale to fill the height completely
        scale_h = max_height / img_height
        scale_w = max_width / img_width
        
        # Use the larger scale to ensure the image fills the section
        # (may crop horizontally if image is wider than section)
        scale = max(scale_w, scale_h)
        
        # Calculate final dimensions
        final_width = img_width * scale
        final_height = img_height * scale
        
        # Center horizontally only, align to bottom vertically
        x_offset = x + (width - final_width) / 2
        y_offset = y  # Align to bottom of section (no vertical centering)
        
        c.drawImage(image_path, x_offset, y_offset, 
                   width=final_width, height=final_height, 
                   preserveAspectRatio=True, mask='auto')
    
    def _optimal_line_break(self, text: str, char_threshold: int, max_lines: int = 2):
        """
        Break text into lines optimally based on character threshold.
        Tries to break as close to threshold as possible without exceeding it.
        Breaks on spaces and commas.
        """
        # Split on space or comma, keeping the delimiter with the preceding token
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
            
            # Try each possible break point
            for i in range(1, len(tokens)):
                first_line = ' '.join(tokens[:i])
                first_line_len = len(first_line)
                
                # Check if this break point is valid (doesn't exceed threshold)
                if first_line_len <= char_threshold:
                    # This is a valid break, check if it's closer to threshold
                    if first_line_len > best_first_line_len:
                        best_first_line_len = first_line_len
                        best_break = i
            
            # If we found a valid break point, use it
            if best_break > 0:
                first_line = ' '.join(tokens[:best_break])
                second_line = ' '.join(tokens[best_break:])
                return [first_line, second_line]
            else:
                # No valid break found, just split in half
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
    
    def _draw_centered_text(self, c, text: str, x: float, y: float, 
                           width: float, height: float, font_size: int, bold: bool = False,
                           text_padding: float = 10, allow_multiline: bool = False, 
                           max_lines: int = 1, char_threshold: int = 22):
        """Draw centered text within a box, with optional multiline support."""
        font = 'Helvetica-Bold' if bold else 'Helvetica'
        c.setFont(font, font_size)
        
        if not allow_multiline or max_lines == 1:
            # Single line mode
            text_width = c.stringWidth(text, font, font_size)
            max_width = width - (2 * text_padding)
            
            if text_width > max_width:
                scale_factor = max_width / text_width
                font_size = int(font_size * scale_factor)
                c.setFont(font, font_size)
                text_width = c.stringWidth(text, font, font_size)
            
            text_x = x + (width - text_width) / 2
            text_y = y + (height - font_size) / 2
            c.drawString(text_x, text_y, text)
        else:
            # Multiline mode - optimal line breaking
            lines = self._optimal_line_break(text, char_threshold, max_lines)
            
            # Draw lines centered
            line_height = font_size * 1.2
            total_height = len(lines) * line_height
            start_y = y + (height - total_height) / 2 + (len(lines) - 1) * line_height
            
            for i, line in enumerate(lines):
                line_width = c.stringWidth(line, font, font_size)
                text_x = x + (width - line_width) / 2
                text_y = start_y - (i * line_height)
                c.drawString(text_x, text_y, line)
    
    def _draw_wrapped_text(self, c, text: str, x: float, y: float, 
                          width: float, height: float, font_size: int, text_padding: float = 10):
        """Draw wrapped text centered within a box."""
        style = ParagraphStyle(
            'centered',
            fontName='Helvetica',
            fontSize=font_size,
            alignment=TA_CENTER,
            leading=font_size * 1.25
        )
        
        para = Paragraph(text, style)
        para_width, para_height = para.wrap(width - (2 * text_padding), height)
        
        # Center vertically
        y_offset = y + (height - para_height) / 2
        para.drawOn(c, x + text_padding, y_offset)
    
    def _sanitize_filename(self, name: str) -> str:
        """Convert name to safe filename."""
        # Remove/replace unsafe characters
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' 
                           for c in name)
        # Replace spaces with underscores and convert to lowercase
        safe_name = safe_name.strip().replace(' ', '_').lower()
        return safe_name
    
    def generate_card(self, person_name: str, person_image_path: str, 
                     output_path: str) -> bool:
        """Generate a single PDF card."""
        
        # Validate inputs
        full_image_path = self.base_dir / person_image_path
        if not self._validate_image(full_image_path):
            return False
        
        qr_code_path = self.base_dir / self.config['qr_code_path']
        if not self._validate_image(qr_code_path):
            print(f"Error: QR code not found: {qr_code_path}")
            return False
        
        cfg = self.config
        
        # Create PDF
        print(f"  Creating PDF...")
        try:
            # Page dimensions in points
            page_width = cfg['page_width_pt']
            page_height = cfg['page_height_pt']
            
            # Layout parameters
            h_padding = cfg['horizontal_padding_pt']
            top_padding = cfg.get('top_padding_pt', 0)
            bottom_padding = cfg.get('bottom_padding_pt', 0)
            top_margin = cfg['top_margin_pt']
            text_padding = cfg.get('text_horizontal_padding_pt', 10)
            content_width = page_width - (2 * h_padding)
            content_height = page_height - top_padding - bottom_padding
            
            # Debug output
            print(f"  Page: {page_width}pt × {page_height}pt")
            print(f"  Content area: {content_width}pt × {content_height}pt")
            print(f"  Margins - H: {h_padding}pt, Top: {top_padding}pt, Bottom: {bottom_padding}pt")
            print(f"  Text padding: {text_padding}pt each side")
            
            # Determine name box size based on name length
            name_length_threshold = cfg.get('name_length_threshold', 22)
            is_long_name = len(person_name) > name_length_threshold
            
            if is_long_name:
                name_height = cfg['name_box_height_pt_long']
                name_font_size = cfg['name_font_size_pt_long']
                name_multiline = True
            else:
                name_height = cfg['name_box_height_pt_short']
                name_font_size = cfg['name_font_size_pt_short']
                name_multiline = False
            
            # Section heights
            photo_height = cfg['photo_section_height_pt']
            qr_height = cfg['qr_section_height_pt']
            gap_before_msg = cfg['gap_before_message_pt']
            message_height = cfg['message_box_height_pt']
            bottom_box_height = cfg.get('bottom_box_height_pt', 0)
            
            # Debug output for name handling
            print(f"  Name: '{person_name}' ({len(person_name)} chars)")
            print(f"  Name box: {name_height}pt, Font: {name_font_size}pt, Multiline: {name_multiline}")
            
            # Calculate Y positions from TOP (convert to bottom-up for ReportLab)
            # Top positions (from top edge, accounting for top padding)
            y_top_photo = top_padding + top_margin
            y_top_name = y_top_photo + photo_height
            y_top_qr = y_top_name + name_height
            y_top_message = y_top_qr + qr_height + gap_before_msg
            y_top_bottom_box = y_top_message + message_height
            
            # Convert to ReportLab coordinates (from bottom, accounting for bottom padding)
            # ReportLab uses bottom-up coordinates, so bottom_padding lifts everything up
            y_photo = page_height - y_top_photo - photo_height - bottom_padding
            y_name = page_height - y_top_name - name_height - bottom_padding
            y_qr = page_height - y_top_qr - qr_height - bottom_padding
            y_message = page_height - y_top_message - message_height - bottom_padding
            y_bottom_box = page_height - y_top_bottom_box - bottom_box_height - bottom_padding
            
            # Create canvas
            c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
            
            # 1. Fill entire page with light blue background
            c.setFillColor(HexColor(cfg['background_color']))
            c.rect(0, 0, page_width, page_height, fill=1, stroke=0)
            
            # 2. Draw photo section
            # Draw person image centered within photo section
            self._draw_centered_image(
                c, str(full_image_path), 
                h_padding, y_photo, 
                content_width, photo_height,
                content_width, photo_height
            )
            
            # 3. Draw name box
            # Calculate name box dimensions with horizontal margins
            name_h_margin = cfg.get('name_box_horizontal_margin_pt', 0)
            name_box_x = h_padding + name_h_margin
            name_box_width = content_width - (2 * name_h_margin)
            
            # White background
            c.setFillColor(HexColor('#FFFFFF'))
            c.rect(name_box_x, y_name, name_box_width, name_height, fill=1, stroke=0)
            
            # Draw borders based on config
            name_border_sides = cfg.get('name_box_border_sides', [])
            name_border_width = cfg.get('name_box_border_width_pt', 2)
            name_border_color = cfg.get('name_box_border_color', '#000000')
            
            c.setStrokeColor(HexColor(name_border_color))
            c.setLineWidth(name_border_width)
            
            if 'left' in name_border_sides:
                c.line(name_box_x, y_name, name_box_x, y_name + name_height)
            if 'right' in name_border_sides:
                c.line(name_box_x + name_box_width, y_name, name_box_x + name_box_width, y_name + name_height)
            if 'top' in name_border_sides:
                c.line(name_box_x, y_name + name_height, name_box_x + name_box_width, y_name + name_height)
            if 'bottom' in name_border_sides:
                c.line(name_box_x, y_name, name_box_x + name_box_width, y_name)
            
            # Draw name text within the narrower box
            c.setFillColor(HexColor('#000000'))
            self._draw_centered_text(
                c, person_name,
                name_box_x, y_name,
                name_box_width, name_height,
                name_font_size,
                bold=False,
                text_padding=text_padding,
                allow_multiline=name_multiline,
                max_lines=cfg.get('name_max_lines', 2),
                char_threshold=name_length_threshold
            )
            
            # 4. Draw QR section
            # White background
            c.setFillColor(HexColor('#FFFFFF'))
            c.rect(h_padding, y_qr, content_width, qr_height, fill=1, stroke=0)
            
            # Draw borders based on config
            qr_border_sides = cfg.get('qr_section_border_sides', [])
            qr_border_width = cfg.get('qr_section_border_width_pt', 2)
            qr_border_color = cfg.get('qr_section_border_color', '#000000')
            
            c.setStrokeColor(HexColor(qr_border_color))
            c.setLineWidth(qr_border_width)
            
            if 'left' in qr_border_sides:
                c.line(h_padding, y_qr, h_padding, y_qr + qr_height)
            if 'right' in qr_border_sides:
                c.line(h_padding + content_width, y_qr, h_padding + content_width, y_qr + qr_height)
            if 'top' in qr_border_sides:
                c.line(h_padding, y_qr + qr_height, h_padding + content_width, y_qr + qr_height)
            if 'bottom' in qr_border_sides:
                c.line(h_padding, y_qr, h_padding + content_width, y_qr)
            
            # Draw QR code centered
            qr_size = cfg['qr_code_size_pt']
            qr_x = h_padding + (content_width - qr_size) / 2
            qr_y = y_qr + (qr_height - qr_size) / 2
            c.drawImage(str(qr_code_path), qr_x, qr_y, 
                       width=qr_size, height=qr_size,
                       preserveAspectRatio=True)
            
            # 5. Draw message box
            # White background
            c.setFillColor(HexColor('#FFFFFF'))
            c.rect(h_padding, y_message, content_width, message_height, fill=1, stroke=0)
            
            # Draw borders based on config
            msg_border_sides = cfg.get('message_box_border_sides', [])
            msg_border_width = cfg.get('message_box_border_width_pt', 2)
            msg_border_color = cfg.get('message_box_border_color', '#000000')
            
            c.setStrokeColor(HexColor(msg_border_color))
            c.setLineWidth(msg_border_width)
            
            if 'left' in msg_border_sides:
                c.line(h_padding, y_message, h_padding, y_message + message_height)
            if 'right' in msg_border_sides:
                c.line(h_padding + content_width, y_message, h_padding + content_width, y_message + message_height)
            if 'top' in msg_border_sides:
                c.line(h_padding, y_message + message_height, h_padding + content_width, y_message + message_height)
            if 'bottom' in msg_border_sides:
                c.line(h_padding, y_message, h_padding + content_width, y_message)
            
            # Draw message text
            c.setFillColor(HexColor('#000000'))
            self._draw_wrapped_text(
                c, cfg['message_text'],
                h_padding, y_message,
                content_width, message_height,
                cfg['message_font_size_pt'],
                text_padding=text_padding
            )
            
            # 6. Draw bottom box (if height > 0)
            if bottom_box_height > 0:
                # Calculate bottom box dimensions with horizontal margins
                bottom_h_margin = cfg.get('bottom_box_horizontal_margin_pt', 0)
                bottom_box_x = h_padding + bottom_h_margin
                bottom_box_width = content_width - (2 * bottom_h_margin)
                
                # White background (no borders)
                c.setFillColor(HexColor('#FFFFFF'))
                c.rect(bottom_box_x, y_bottom_box, bottom_box_width, bottom_box_height, fill=1, stroke=0)
            
            # Remaining space stays blue (already filled)
            
            # Save PDF
            c.save()
            print(f"  ✓ Successfully created: {output_path}")
            return True
            
        except Exception as e:
            print(f"  ✗ Error creating PDF: {e}")
            traceback.print_exc()
            return False
    
    def generate_all_cards(self) -> None:
        """Generate PDF cards for all entries in CSV."""
        
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
            output_filename = f"{safe_name}.pdf"
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
    
    print("=" * 60)
    print("PDF CARD GENERATOR")
    print("=" * 60)
    print(f"Configuration: {config_file}\n")
    
    # Create generator and run
    generator = CardGenerator(config_file)
    generator.generate_all_cards()


if __name__ == "__main__":
    main()
