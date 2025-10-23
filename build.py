#!/usr/bin/env python3

import json
import math
import os
import shutil
from PIL import Image

from add_translation import process_localization_entries

os.environ['DXVK_LOG_LEVEL'] = 'none'

def clean():
  shutil.rmtree('DegreenWorldMap/Tiles', ignore_errors = True)

def generate_override_map_list_lua(map_info):
  with open('DegreenWorldMap/OverrideMapList.lua', 'w') as f:
    f.write('OverrideMapList = {\n')
    for item in map_info:
      f.write('  [%d] = {\n' % item['id'])
      f.write('    enable = true,\n')
      if 'localization' in item:
        for locale in item['localization'].get('languages', []):
          f.write('    %s = true,\n' % locale)
      f.write('  },\n')
    f.write('}\n')

def generate_map_tile(map_id, basename, locale=None):
  if locale:
    input_path = f'gallery/{locale}/{basename}.png'
    out_dir = f'DegreenWorldMap/Tiles/{map_id}/{locale}'
  else:
    input_path = f'gallery/{basename}.png'
    out_dir = f'DegreenWorldMap/Tiles/{map_id}'

  img = Image.open(input_path)
  img = img.convert('RGB')
  width, height = img.size

  os.makedirs(out_dir, exist_ok=True)

  tile_width, tile_height = 256, 256
  if height == 2560:
    # 3840×2560, split to 15x10 256x256 tiles
    cols = width // tile_width
    rows = height // tile_height

    for row in range(rows):
      for col in range(cols):
        left = col * tile_width
        upper = row * tile_height
        right = left + tile_width
        lower = upper + tile_height
        tile = img.crop((left, upper, right, lower))
        tile.save(f'{out_dir}/{row * cols + col}.jpg', 'JPEG', quality=80)
  else:
    # 1002×668, split to 4x3 256x256 tiles
    cols = math.ceil(width / tile_width)
    rows = math.ceil(height / tile_height)

    for row in range(rows):
      for col in range(cols):
        left = col * tile_width
        upper = row * tile_height
        right = left + tile_width
        lower = upper + tile_height
        tile = img.crop((left, upper, right, lower))
        tile.save(f'{out_dir}/{row * cols + col}.jpg', 'JPEG', quality=80)

def generate_all_map(map_info):
  for i, item in enumerate(map_info):
    generate_map_tile(item['id'], item["basename"])

    if 'localization' in item:
      # 处理本地化条目，生成合成图片
      process_localization_entries(item["basename"], item['id'], item['localization'])
      
      # 为每种语言生成地图瓦片
      languages = item['localization'].get('languages', [])
      for locale in languages:
        generate_map_tile(item['id'], item["basename"], locale)

def package():
  # read version from toc
  with open('DegreenWorldMap/DegreenWorldMap.toc', 'r') as f:
    for line in f:
      if line.startswith('## Version:'):
        version = line.strip().split(' ')[2]
        break

  package_file = f'DegreenWorldMap-{version}.zip'

  if os.path.exists(package_file):
    os.remove(package_file)
  
  shutil.make_archive(f'DegreenWorldMap-{version}', 'zip', '.', 'DegreenWorldMap')

def main():
  map_info = json.load(open('map-info.json'))
  clean()
  generate_override_map_list_lua(map_info)
  generate_all_map(map_info)
  package()

if __name__ == '__main__':
  main()
