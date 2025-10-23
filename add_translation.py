#!/usr/bin/env python3

import json
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_PATH = "font/ARLishuU30-Medium.ttf"
font_cache = {}

def generate_text_image(text, output_path, font_size=48, is_title=False):
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

    padding = 20
    diff_unit = font_size / 80

    if is_title:
        shadow_color = (64, 32, 16, 255)
        mask_color = (255, 255, 255, 255)

        # shadow with gaussian blur
        shadow_size = (text_width + padding * 2, text_height + padding * 2)
        shadow_img = Image.new('RGBA', shadow_size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        shadow_draw.text((padding + diff_unit, padding + diff_unit), text, font=font, fill=shadow_color, stroke_width= 6 * diff_unit, stroke_fill = shadow_color)
        blurred_shadow = shadow_img.filter(ImageFilter.GaussianBlur(radius = 3 * diff_unit))
        image.paste(blurred_shadow, (x - padding, y - padding), blurred_shadow)

        # main text (as mask)
        text_mask = Image.new('RGBA', (text_width + 2 * padding, text_height + 2 * padding), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_mask)
        text_draw.text((padding, padding), text, font=font, fill=mask_color, stroke_width=diff_unit, stroke_fill=mask_color)

        mask_bbox = text_mask.getbbox()
        mask_width = mask_bbox[2] - mask_bbox[0]
        mask_height = mask_bbox[3] - mask_bbox[1]
        mask_left = mask_bbox[0]
        mask_top = mask_bbox[1]

        # gradient
        # 0%: (240, 208, 16)
        # 65%: (240, 152 ,16)
        # 100%: (208, 144, 16)
        gradient = Image.new('RGBA', (mask_width, mask_height), (0, 0, 0, 0))
        grad_draw = ImageDraw.Draw(gradient)
        for i in range(mask_height):
            gradient_factor = i / mask_height
            if gradient_factor <= 0.65:
                # From 0% to 65%: (240, 208, 16) to (240, 152, 16)
                factor = gradient_factor / 0.65
                r = int(240)
                g = int(208 - (208 - 152) * factor)
                b = int(16)
            else:
                # From 65% to 100%: (240, 152, 16) to (208, 144, 16)
                factor = (gradient_factor - 0.65) / 0.35
                r = int(240 - (240 - 208) * factor)
                g = int(152 - (152 - 144) * factor)
                b = int(16)
            grad_draw.line([(0, i), (mask_width, i)], fill=(r, g, b, 255))

        # text with gradient
        gradient_padded = Image.new('RGBA', (text_width + 2 * padding, text_height + 2 * padding), (0, 0, 0, 0))
        gradient_padded.paste(gradient, (mask_left, mask_top))
        final_text = Image.composite(gradient_padded, Image.new('RGBA', (text_width + 2 * padding, text_height + 2 * padding), (0, 0, 0, 0)), text_mask)
        image.paste(final_text, (x - padding, y - padding), final_text)
    else:
        scale = (font_size - 16) / (96 - 16)
        glow_color = (255, 224, 0, 224)
        text_color = (102, 67, 20, 255)

        # glow (heavy stroke + gaussian blur)
        glow_size = (text_width + padding * 2, text_height + padding * 2)
        glow_img = Image.new('RGBA', glow_size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_img)
        glow_draw.text((padding, padding), text, font=font, fill=glow_color, stroke_width = (12 - 6 * scale) * diff_unit, stroke_fill=glow_color)
        blurred = glow_img.filter(ImageFilter.GaussianBlur(radius = (4 - 2 * scale) * diff_unit))
        image.paste(blurred, (x - padding, y - padding), blurred)

        # main text
        text_img = Image.new('RGBA', (text_width + 2 * padding, text_height + 2 * padding), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_img)
        text_draw.text((padding, padding), text, font=font, fill=text_color, stroke_width = diff_unit, stroke_fill=text_color)
        image.paste(text_img, (x - padding, y - padding), text_img)

    bbox = image.getbbox()
    if bbox:
        image = image.crop(bbox)

    image.save(output_path, 'PNG')

def composite_text_on_background(background_path, text, output_path, position, font_size=48, is_title=False):
    temp_text_path = 'temp_text.png'
    generate_text_image(text, temp_text_path, font_size, is_title)

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
                    is_title = entry_info.get('title', False)  # Check if this is a title

                    temp_text_path = 'temp_text.png'
                    generate_text_image(text, temp_text_path, font_size, is_title)
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
