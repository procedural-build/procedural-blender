#!/bin/bash

# For development only:
# Symbollically link the source folder into your Blender addons folder.

DEFAULTADDONPATH="$HOME/.config/blender/3.0/scripts/addons"

read -p "Enter path to addon folder [$DEFAULTADDONPATH]:" USERADDONPATH

LINKFOLDER=$DEFAULTADDONPATH
if [-z $USERADDONPATH] then
    LINKFOLDER=$USERADDONPATH
fi
LINKFOLDER="$LINKFOLDER/procedural_compute"

echo "Linking procedurl_compute folder to $LINKFOLDER for development"
ln -s $PWD/procedural_compute $LINKFOLDER
