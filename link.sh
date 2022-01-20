#!/bin/bash

# For development only:
# Symbollically link the source folder into your Blender addons folder.

DEFAULTADDONPATH="$HOME/.config/blender/3.0/scripts/addons"

read -p "Enter path to addon folder [$DEFAULTADDONPATH]:" USERADDONPATH

LINKFOLDER=$DEFAULTADDONPATH
if [ ! -z "$USERADDONPATH" ]; then
    LINKFOLDER=$USERADDONPATH
fi

LINKFOLDER=$LINKFOLDER/procedural_compute

if [ -d "$LINKFOLDER" ]; then
    read -p "Directory already exists at path. Delete and re-link? (y/n) [y] " RELINK
    RELINK=${RELINK:-y}
    if [ "$RELINK" == "y" ]; then
        rm -v $LINKFOLDER
    else
        echo "Doing nothing because linked folder already exists and you selected to not delete it"
        exit 0
    fi
fi

echo "Linking procedurl_compute folder to $LINKFOLDER for development"
ln -s $PWD/procedural_compute $LINKFOLDER
