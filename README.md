# Blender (2.82+) Python addons for Procedural APIs

Scripts, components and utilities for Blender 2.82 (or higher)

## Installing the addon

Install the addon in Blender with the following steps

* Go to the latest *stable* [here](https://github.com/procedural-build/procedural-blender/releases/latest):
* Go to Blender -> Edit -> Preferences -> Addons -> Install... and select the .zip package


## Build distributable zip package

Build a zip package for distributing the Blender addon with:
```
./make.sh
```

This will make the zip file `./bin/procedural_compute.zip` which can be distributed and installed
into Blender as per the instructions above.

## Linking code for development

### On Linux

For development you can symbolically link the module source code directly into your
blender scripts folder with the command:
```
./link.sh
```

### On Windows 

Open `Powershell` or a `Command Prompt` **as Administrator**.  Then run the bat script:
```
./link.bat
```
