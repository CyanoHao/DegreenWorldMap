#!/usr/bin/env python3

import json
import os
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "font/ARLishuU30-Medium.ttf"
font_cache = {}

def generate_text_image(text, output_path, font_size=48):
    canvas_size = (500, 100)
    image = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    if font_size not in font_cache:
        font_cache[font_size] = ImageFont.truetype(FONT_PATH, font_size)
    font = font_cache[font_size]

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (canvas_size[0] - text_width) // 2
    y = (canvas_size[1] - text_height) // 2

    diff_unit = font_size / 80
    glow_diffs = [-8, -6, -4, -2, 0, 2, 4, 6, 8]
    text_diffs = [-1, 0, 1]

    # text glow
    offsets = []
    for dx in glow_diffs:
        for dy in glow_diffs:
            if dx in text_diffs and dy in text_diffs:
                continue
            if dx ** 2 + dy ** 2 >= 10 ** 2:
                continue
            offsets.append((dx, dy))

    # sort by distance
    offsets.sort(key = lambda offset: offset[0]**2 + offset[1]**2, reverse=True)
    for dx, dy in offsets:
        # dist = 2 -> alpha = 255
        # dist = 10 -> alpha = 0
        dist = (dx ** 2 + dy ** 2) ** 0.5
        scale = max(0, 1 - ((dist - 2) / 8) ** 1.4)
        alpha = int(255 * scale)
        glow_color = (255, 215, 0, alpha)
        draw.text((x + dx * diff_unit, y + dy * diff_unit), text, font=font, fill=glow_color)

    # slightly embolden the text
    text_color = (102, 67, 20, 255)
    for dx in text_diffs:
        for dy in text_diffs:
            draw.text((x + dx * diff_unit, y + dy * diff_unit), text, font=font, fill=text_color)

    bbox = image.getbbox()
    if bbox:
        image = image.crop(bbox)

    image.save(output_path, 'PNG')

def composite_text_on_background(background_path, text, output_path, position, font_size=48):
    temp_text_path = 'temp_text.png'
    generate_text_image(text, temp_text_path, font_size)

    background = Image.open(background_path).convert('RGBA')
    text_image = Image.open(temp_text_path).convert('RGBA')

    text_width, text_height = text_image.size
    x, y = position
    paste_position = (int(x - text_width/2), int(y - text_height/2))
    temp_background = background.copy()
    temp_background.paste(text_image, paste_position, text_image)
    background = Image.alpha_composite(background, temp_background)
    background.save(output_path, 'PNG')
    os.remove(temp_text_path)

def process_localization_entries(basename, map_id, localization_info):
    background_dir = 'gallery/background'
    os.makedirs(background_dir, exist_ok=True)
    
    entries = localization_info.get('entries', {})
    languages = localization_info.get('languages', [])
    
    for lang in languages:
        output_dir = f'gallery/{lang}'
        os.makedirs(output_dir, exist_ok=True)
        
        if entries:
            output_path = f'{output_dir}/{basename}.png'
            background_path = f'gallery/background/{basename}.png'

            background = Image.open(background_path).convert('RGBA')

            for entry_name, entry_info in entries.items():
                if lang in entry_info:
                    text = entry_info[lang]
                    position = entry_info['position']
                    font_size = entry_info.get('fontSize', 48)

                    temp_text_path = 'temp_text.png'
                    generate_text_image(text, temp_text_path, font_size)
                    text_image = Image.open(temp_text_path).convert('RGBA')
                    text_width, text_height = text_image.size
                    x, y = position
                    paste_position = (int(x - text_width/2), int(y - text_height/2))
                    # Create a temporary image for pasting with proper alpha blending
                    temp_background = background.copy()
                    temp_background.paste(text_image, paste_position, text_image)
                    
                    # Properly alpha blend the images
                    background = Image.alpha_composite(background, temp_background)

                    os.remove(temp_text_path)

            background.save(output_path, 'PNG')
