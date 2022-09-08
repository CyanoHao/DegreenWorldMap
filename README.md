# Degreen World Map

Temporary workaround until world map localization is complete.

## Usage

Install as an addon.

Note: this addon adds enUS map tiles to world map frame and thus may conflict with Fog of War remover.

## How to Build

This addon is developed on Linux. Building on Windows is not tested.

Dependencies:
* Wine for FidelityFX CLI, AMD’s image upscaling tool based on FidelityFX Super Resolution (FSR).
  * Wine is not required when using WSL – Windows programs will seamlessly run on host OS.
* ImageMagick, image processing tool.

Run `./build.sh`. The output is `DegreenWorldMap-<version>.zip`.
