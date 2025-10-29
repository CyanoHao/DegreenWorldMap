#!/usr/bin/env python3

import json
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT_PATH = "font/ARLishuU30-Medium.ttf"
font_cache = {}

def calculate_bbox(text, font: ImageFont.FreeTypeFont):
    return font.getbbox(text)

def draw_text_on_image(background, text, position, font_size=48, style="normal"):
    if font_size not in font_cache:
        font_cache[font_size] = ImageFont.truetype(FONT_PATH, font_size)
    font = font_cache[font_size]

    bbox = calculate_bbox(text, font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x, y = position
    text_x = int(x - text_width/2)
    # 0.15 for baseline
    text_y = int(y - text_height/2 - 0.15 * text_height)

    diff_unit = font_size / 80

    if style == "ribbon":
        shadow_color = (64, 32, 16, 255)
        mask_color = (255, 255, 255, 255)

        # shadow with gaussian blur directly on overlay
        overlay = Image.new('RGBA', background.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        shadow_x = text_x + diff_unit
        shadow_y = text_y + diff_unit
        draw.text((shadow_x, shadow_y), text, font = font, fill = shadow_color,
                  stroke_width = 6 * diff_unit, stroke_fill = shadow_color)
        overlay = overlay.filter(ImageFilter.GaussianBlur(radius = 3 * diff_unit))
        draw = ImageDraw.Draw(overlay)

        # text mask for gradient
        padding = int(font_size / 2)
        text_mask = Image.new('RGBA', (text_width + 2 * padding, text_height + 2 * padding), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_mask)
        text_draw.text((padding, padding), text, font = font, fill = mask_color,
                       stroke_width = diff_unit, stroke_fill = mask_color)

        mask_bbox = text_mask.getbbox()
        if mask_bbox:
            mask_width = mask_bbox[2] - mask_bbox[0]
            mask_height = mask_bbox[3] - mask_bbox[1]
            mask_left = mask_bbox[0]
            mask_top = mask_bbox[1]

            # create gradient
            gradient = Image.new('RGBA', (mask_width, mask_height), (0, 0, 0, 0))
            grad_draw = ImageDraw.Draw(gradient)
            for i in range(mask_height):
                gradient_factor = i / mask_height
                if gradient_factor <= 0.65:
                    # from 0% to 65%: (240, 208, 16) to (240, 152, 16)
                    factor = gradient_factor / 0.65
                    r = int(240)
                    g = int(208 - (208 - 152) * factor)
                    b = int(16)
                else:
                    # from 65% to 100%: (240, 152, 16) to (208, 144, 16)
                    factor = (gradient_factor - 0.65) / 0.35
                    r = int(240 - (240 - 208) * factor)
                    g = int(152 - (152 - 144) * factor)
                    b = int(16)
                grad_draw.line([(0, i), (mask_width, i)], fill=(r, g, b, 255))

            # apply gradient to text
            gradient_padded = Image.new('RGBA', (text_width + 2 * padding, text_height + 2 * padding), (0, 0, 0, 0))
            gradient_padded.paste(gradient, (mask_left, mask_top))
            final_text = Image.composite(gradient_padded, Image.new('RGBA', (text_width + 2 * padding, text_height + 2 * padding), (0, 0, 0, 0)), text_mask)

            # Paste final text to overlay
            temp_final_text_canvas = Image.new('RGBA', overlay.size, (0, 0, 0, 0))
            temp_final_text_canvas.paste(final_text, (text_x - padding, text_y - padding))
            overlay = Image.alpha_composite(overlay, temp_final_text_canvas)

    elif style in ['hd', 'hd-glow']:
        glow_color = (255, 224, 128, 128)
        stroke_color = (255, 224, 128, 192)
        text_color = (102, 67, 20, 255)

        # glow (heavy stroke + gaussian blur)
        overlay = Image.new('RGBA', background.size, (*glow_color[:3], 0))
        draw = ImageDraw.Draw(overlay)
        if style == 'hd-glow':
            draw.text((text_x, text_y), text, font = font, fill = glow_color,
                      stroke_width = 40 * diff_unit, stroke_fill = glow_color)
            overlay = overlay.filter(ImageFilter.GaussianBlur(radius = 30 * diff_unit))
            draw = ImageDraw.Draw(overlay)

        # stroke
        draw.text((text_x, text_y), text, font = font, fill = stroke_color,
                  stroke_width = 5 * diff_unit, stroke_fill = stroke_color)

        # main text
        draw.text((text_x, text_y), text, font = font, fill = text_color,
                  stroke_width = diff_unit, stroke_fill = text_color)

    else:  # style == "normal"
        glow_color = (255, 224, 128, 192)
        text_color = (102, 67, 20, 255)

        # glow (heavy stroke + gaussian blur)
        overlay = Image.new('RGBA', background.size, (*glow_color[:3], 0))
        draw = ImageDraw.Draw(overlay)
        draw.text((text_x, text_y), text, font = font, fill = glow_color,
                  stroke_width=40 * diff_unit, stroke_fill = glow_color)
        overlay = overlay.filter(ImageFilter.GaussianBlur(radius = 30 * diff_unit))
        draw = ImageDraw.Draw(overlay)

        # main text
        draw.text((text_x, text_y), text, font=font, fill=text_color, 
                  stroke_width=diff_unit, stroke_fill=text_color)

    # Composite the overlay onto the background
    result = Image.alpha_composite(background, overlay)
    return result

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
                    font_size = entry_info['fontSize']
                    style = entry_info['style']

                    background = draw_text_on_image(background, text, position, font_size, style)

            background.save(output_path, 'PNG')
