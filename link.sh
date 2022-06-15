#!/bin/bash

# For development only:
# Symbollically link the source folder into your Blender addons folder.

DEFAULTADDONPATH="$HOME/.config/blender/3.1/scripts/addons"

read -p "Enter path to addon folder [$DEFAULTADDONPATH]:" USERADDONPATH

LINKFOLDER=$DEFAULTADDONPATH
if [ ! -z "$USERADDONPATH" ]; then
    LINKFOLDER=$USERADDONPATH
fi

# If the base folder we are linking to doesn't exist then offer to make it
if [ -d "$LINKFOLDER" ]; then
    read -p "Folder does not exist.  Would you like to create it? (y/n) [y] " MAKEBASEPATH
    MAKEBASEPATH=${MAKEBASEPATH:-y}
    if [ "$MAKEBASEPATH" == "y" ]; then
        mkdir -p -v $MAKEBASEPATH
    fi
fi

# Here this is the actual folder we will link
LINKFOLDER=$LINKFOLDER/procedural_compute

# If the target link exists then offer to delete it and re-link
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
