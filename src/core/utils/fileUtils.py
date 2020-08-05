###########################################################
# Blender Modelling Environment for Architecture
# Copyright (C) 2011, ods-engineering
# License : ods-engineering license
# Version : 1.2
# Web     : www.ods-engineering.com
###########################################################


import bpy
import os


def getFilesByExtension(ext, relPath):
    """ Get all files at a path by extension
    """
    allFiles = os.listdir(bpy.path.abspath("//" + relPath))
    files = []
    start_point = -1 * len(ext)
    for f in allFiles:
        if f[start_point:] == ext:
            files.append(f)
    files.sort()
    print("Found " + str(len(files)) + " files")
    return files
