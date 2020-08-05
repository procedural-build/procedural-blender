###########################################################
# Blender Modelling Environment for Architecture
# Copyright (C) 2011, ods-engineering
# License : ods-engineering license
# Version : 1.2
# Web     : www.ods-engineering.com
###########################################################


"""
A bunch of utilities to help blender work out the relationship between
various objects for energyplus.  Things like:
 - Select objects of same construction
 - Select objects of same type (external wall) etc.
 - Select objects of same Zone
 - Orient opening normals same as parent
 - Orient surface normals away from zone
 - Attempt to get Parent object of all openings
 - Attempt to get Zone objects for all surfaces
"""

import bpy
import math


def makeTuples(l):
    ltuples = []
    for x in l:
        ltuples.append((x, x, x))
    return ltuples


def matString(o):
    # String together all the names of the materials
    constName = ''
    mats = []
    for m in o.material_slots:
        mats.append(m.name)
    constName = "".join(mats)
    return constName


def selectObjectsOfSameConstruction(obj):
    sc = bpy.context.scene
    # Search other objects for the same construction
    cName = matString(obj)
    # Deselect all objects
    for o in sc.objects:
        o.select = False
    # Select all objects if objConstName = cName
    for o in sc.objects:
        objConstName = matString(o)
        if objConstName == cName:
            o.select = True
    obj.select = True
    sc.objects.active = obj
    return None


def selectObjectsOfSameType(obj):
    sc = bpy.context.scene
    # Deselect all objects
    for o in sc.objects:
        o.select = False
    # Select all objects of same type (Zone,Surface,Opening) and subtype (Window,Shade,Door,ExternalWall, etc.)
    for o in sc.objects:
        if o.ODS_EP.objectType == obj.ODS_EP.objectType:
            if obj.ODS_EP.objectType == 'Zone':
                o.select = True
            elif obj.ODS_EP.objectType == 'Surface':
                if (o.ODS_EP.Surface.surfaceType == obj.ODS_EP.Surface.surfaceType) and (o.ODS_EP.Surface.outBC == obj.ODS_EP.Surface.outBC):
                    o.select = True
            elif obj.ODS_EP.objectType == 'Opening':
                if o.ODS_EP.Opening.openingType == obj.ODS_EP.Opening.openingType:
                    o.select = True
    obj.select = True
    sc.objects.active = obj
    return None


def nameInChildOfTargets(name, obj, cons=["parentObject1", "parentObject2"]):
    nameIsTarget = False
    for c in cons:
        if c in obj.constraints:
            if not obj.constraints[c].target is None:
                if obj.constraints[c].target.name == name:
                    nameIsTarget = True
    return nameIsTarget


def selectObjectsOfZone(obj):
    if obj.ODS_EP.objectType != 'Zone':
        print('Selected object is not of type ZONE.')
        return None
    sc = bpy.context.scene
    # Get Zone name
    zoneName = obj.name
    # Deselect all objects
    for o in sc.objects:
        o.select = False
    for o in sc.objects:
        if o.ODS_EP.objectType == 'Surface':
            if nameInChildOfTargets(zoneName, o):
                o.select = True
                surfName = o.name
                for oo in sc.objects:
                    if oo.ODS_EP.objectType == 'Opening':
                        if nameInChildOfTargets(surfName, oo):
                            oo.select = True
    obj.select = True
    sc.objects.active = obj
    return None
