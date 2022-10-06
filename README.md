# Degreen World Map

Temporary workaround until world map localization is complete.

## Usage

Install as an addon.

Note: this addon works by adding enUS map tiles to world map frame and thus may conflict with Fog of War remover.

![Comparison: Dragonflight PTR w/ vs. w/o Degreen World Map](repo/compare.jpg)

## How to Build

This addon can be built on Linux (incl. WSL) or MSYS2. macOS is not supported for the assumption of GNU utils.

Dependencies:
* ImageMagick, image processing tool.
* zip.

Run `./build.sh`. The output is `DegreenWorldMap-<version>.zip`.
