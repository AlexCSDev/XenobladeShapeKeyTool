# Xenoblade Shape Key Tool
This is a helper blender addon for [Turk645's Noesis Xenoblade Model Importer](https://github.com/Turk645/Xenoblade-Switch-Model-Importer-Noesis). This addon automatically loads morph names from wimdo file and sets proper shape key names.

Tested to work with models from:
 - Xenoblade 1: Definitive Edition
 - Xenoblade 2
 - Xenoblade 3

## Installation
Install like any other blender addon. The tool panel will appear in object mode.

## Usage
Select face mesh, go to the tool panel, select wimdo file for that model and press the button.

## Known issues
Trying to use the tool on some Xenoblade 3 models (Moebius) might result in "Shape key count is not equal to morphs count" error. This is due to the fact that on those models the shape keys are spread across several meshes. 
One possible solution for this is:
1) Count how many shape keys there are on all meshes other than face mesh.
2) Create that amount of blank shape keys on face mesh. Make sure they are at the end of the list.
3) Run the tool.
4) Remove blank shape keys and manually rename shape keys on other meshes using the names of the deleted shape keys.

Another solution provided by one of the users for Moebius models:
1) Find out the name of last shape key on the face mesh, remember the number it has.
2) Rename shape keys on eyelid mesh so they come after shape keys of the face mesh.
3) Merge face and eyelid meshes together.
4) Run the tool.
5) Separate meshes.