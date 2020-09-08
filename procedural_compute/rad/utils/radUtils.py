###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

def formatName(obname):
    obname = obname.replace(' ','_')
    # Remove numbers at the beginning of the name
    nums = ['0','1','2','3','4','5','6','7','8','9']
    if obname[0] in nums:
        obname = '_' + obname
    return obname
