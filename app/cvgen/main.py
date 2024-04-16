import os
from pathlib import Path
import json
import yaml
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import grey, black, Color
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
import argparse
from pathlib import Path
import os

config_path = Path(__file__).parent / 'config/config.json'

pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
#
class ConfLoader:
    def __init__(self, config_filename='template.yaml') -> None:
        self.config_path = Path(__file__).resolve().parent.parent / 'config' / 'config.json'
        self.base_dir = Path(__file__).resolve().parent.parent
        print(f"Base Directory: {self.base_dir}")
        self.config_dir = self.base_dir / 'config'
        self.icon_dir = self.base_dir / 'icons'
        print(f"Config Directory: {self.config_dir}")
        print(f"Icon Directory: {self.icon_dir}")
        self.general_config = self.load_json_config('config.json')
        self.cv_template = self.load_yaml_config(config_filename)
        self.language = self.load_language(self.general_config.get('default_language', 'en'))

 
    def load_json_config(self, filename: str) -> dict:
        config_path = self.config_dir / filename
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Failed to load {filename}: {e}")
            exit(1)

    def load_yaml_config(self, filename: str) -> dict:
        config_path = self.config_dir / filename
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Failed to load {filename}: {e}")
            exit(1)

    def load_language(self, lang: str) -> dict:
        lang_file = f"{lang}.json"
        lang_path = self.config_dir / lang_file
        try:
            with open(lang_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Failed to load language file {lang_file}: {e}")
            exit(1)

def add_personal_info(c, config, loader, width, top_section_height):
    c.setFont("DejaVuSans-Bold", 18)
    c.setFillColor(black)
    name_y = top_section_height + 90
    c.drawString(40, name_y, config['name'])

    contact = config.get('contact', {})
    phone_y = name_y - 30
    email_y = name_y - 55
    location_y = phone_y
    github_y = email_y

    items = [
        ('phone.svg', contact.get('phone', ''), 27, phone_y, 0.4, 40, "DejaVuSans", 10),
        ('envelope.svg', contact.get('email', ''), 27, email_y, 0.4, 40, "DejaVuSans", 10),
        ('location.svg', contact.get('address', ''), 240, location_y, 0.4, 255, "DejaVuSans", 10),
        ('github.svg', contact.get('github', ''), 220, github_y, 0.1, 255, "DejaVuSans", 10)
    ]

    for icon_name, detail, icon_x, icon_y, scale, text_pos_x, font, size in items:
        icon_path = loader.icon_dir / icon_name
        if detail:
            
            adjusted_icon_y = icon_y - 3 if icon_name == 'github.svg' else icon_y
            
            try:
                drawing = svg2rlg(icon_path)
                drawing.scale(scale, scale)
                renderPDF.draw(drawing, c, icon_x, adjusted_icon_y) 
                c.setFont(font, size)
                c.drawString(text_pos_x, icon_y, detail)  
            except Exception as e:
                print(f"Failed to load icon {icon_name} due to: {e}")

    return email_y - 35


def add_section_header(c, text, x, y, loader, icon=None, icon_x_offset=0, icon_y_offset=0, font='DejaVuSans-Bold', size=12, color=black, icon_scale=0.4):
    default_icon = "default.svg"  # Specify the default icon file
    icon_x_offset_fixed = 35  # keep it 30

    if icon:
        icon_path = loader.icon_dir / icon  # Update to use loader.icon_dir
        #icon_path = os.path.join(icon_dir, icon)
        print("Attempting to load icon from:", icon_path)
        try:
            drawing = svg2rlg(icon_path)
            drawing.scale(icon_scale, icon_scale)
            renderPDF.draw(drawing, c, x + icon_x_offset_fixed + icon_x_offset, y + icon_y_offset)
            print("Successfully loaded icon")
            print("Icon position:", x + icon_x_offset_fixed + icon_x_offset, y + icon_y_offset)
        except Exception as e:
            print(f"Failed to load the SVG file due to: {e}")
            icon_path = loader.icon_dir / default_icon  # Use loader.icon_dir for default icon too
            drawing = svg2rlg(icon_path)
            drawing.scale(icon_scale, icon_scale)
            renderPDF.draw(drawing, c, x + icon_x_offset_fixed + icon_x_offset, y + icon_y_offset)
            print("Default icon position:", x + icon_x_offset_fixed + icon_x_offset, y + icon_y_offset)
    
    c.setFillColor(color)
    c.setFont(font, size)
    if '\n' in text:
        lines = text.split('\n')
        line_height = size * 1.2
        for i, line in enumerate(lines):
            c.drawString(x, y - (i * line_height), line)
    else:
        c.drawString(x, y, text)


def draw_separator(c, x1, y, x2, color=grey, line_width=1):
    c.setStrokeColor(color)
    c.setLineWidth(line_width)
    c.line(x1, y, x2, y)

def add_section_text(c, text, x, y, font='DejaVuSans', size=10, bold=False, color=black):
    if bold:
        font += '-Bold'
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, y, text)

def create_cv(loader, config_filename):
    """ Create CV document using the loaded configuration and language data from the loader. """
    loader = ConfLoader(config_filename)
    c = canvas.Canvas("example_cv.pdf", pagesize=A4)
    width, height = A4

    # Top gray area
    top_section_height = 100
    c.setFillColor(Color(0.95, 0.95, 0.95))
    c.rect(0, height - top_section_height, width, top_section_height, stroke=0, fill=1)

    # Add personal info
    top_section_height = add_personal_info(c, loader.cv_template, loader, width, height - 120)

    # Initialize y position below the top gray area
    current_y = height - top_section_height + 580

    for section_name, items in loader.cv_template.items():
        if section_name in ['education', 'experience', 'skills', 'interests', 'languages', 'driver']:
            icon_filename = f"{section_name}.svg"
            translated_text = loader.language.get(section_name.capitalize(), section_name.capitalize())
            add_section_header(c, translated_text, 40, current_y, loader, icon=icon_filename, icon_x_offset=-50)
            current_y -= 0 # Spacing after the header before details start

            for item in items:
                if isinstance(item, dict):
                    # Different handling based on section type
                    if section_name == 'education':
                        if 'school' in item:
                            add_section_text(c, item['school'], 140, current_y, size=10, bold=True, color=black)
                            current_y -= 15
                        if 'degree' in item:
                            degree_text = f"{item['degree']}" + (f" - {item['degree_level']}" if 'degree_level' in item else "")
                            add_section_text(c, degree_text, 140, current_y)
                            current_y -= 15
                    elif section_name == 'experience':
                        if 'title' in item:
                            add_section_text(c, item['title'], 140, current_y, size=10, bold=True, color=black)
                            current_y -= 15
                        if 'company' in item:
                            add_section_text(c, item['company'], 140, current_y)
                            current_y -= 15
                    if 'period' in item:
                            add_section_text(c, item['period'], 140, current_y)
                            current_y -= 15
                    if 'details' in item:
                            for detail in item['details'].split('\n'):
                                add_section_text(c, detail.strip(), 140, current_y, size=10, bold=False, color=grey)
                                current_y -= 15
                else:
                    # Simple list items for skills, interests, etc.
                    add_section_text(c, item, 140, current_y)
                    current_y -= 15

            draw_separator(c, 25, current_y, width - 25)
            current_y -= 30  # Additional spacing before the next section

    c.showPage()
    c.save()
    print("PDF Generated Successfully.")

#def main():
#    loader = ConfLoader()
#    create_cv(loader)


def main(config_filename):
    loader = ConfLoader()
    create_cv(loader, config_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='filename')
    parser.add_argument('--conf', type=str, default='template.yaml', help='filename')
    args = parser.parse_args()   
    main(args.conf)

def run_main():
    """entry point for setup tools"""
    parser = argparse.ArgumentParser(description='filename')
    parser.add_argument('--conf', type=str, default='template.yaml', help='filename')
    args = parser.parse_args()   
    main(args.conf)






