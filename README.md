# Degreen World Map

Temporary workaround until world map localization is complete.

## Usage

Install as an addon.

Note: this addon works by adding enUS map tiles to world map frame and thus may conflict with Fog of War remover.

![Comparison: Dragonflight PTR w/ vs. w/o Degreen World Map](repo/compare.jpg)

## How to Build

This addon is developed on Linux. Building on Windows is not tested.

Dependencies:
* Wine for FidelityFX CLI, AMD’s image upscaling tool based on FidelityFX Super Resolution (FSR).
  * Wine is not required when using WSL – Windows programs will seamlessly run on host OS.
  * DXVK recommended (while wined3d also work).
* ImageMagick, image processing tool.
* zip.

Run `./build.sh`. The output is `DegreenWorldMap-<version>.zip`.
