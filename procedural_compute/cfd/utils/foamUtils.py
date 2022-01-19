###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
import os
from collections import OrderedDict

def openFileWrite(relPath,mode='w'):
    # Get(make) the global path to the current directory
    p = bpy.path.abspath(relPath)
    (p,fileName) = os.path.split(p)
    if not os.path.exists(p):
        os.makedirs(p)
    # Open the file for writing
    fname = '%s/%s'%(p, fileName)
    f = open(fname, mode)
    return f

def formatObjectName(obname):
    specialBCs = ['MinX','MaxX','MinY','MaxY','MinZ','MaxZ']
    if obname.split('.')[0] in specialBCs:
        return obname.split('.')[0]
    # Remove spaces in the name
    obname = obname.replace(' ','_')
    # Remove numbers at the beginning of the name
    nums = [str(i) for i in range(10)]
    if obname[0] in nums:
        obname = '_' + obname
    return obname

def selectedObjectsAndNames():
    nullObjs = ['cfdBoundingBox','cfdMeshKeepPoint']
    specialBCs = ['MinX','MaxX','MinY','MaxY','MinZ','MaxZ']
    names = []
    objects = []
    for o in bpy.context.selected_objects:
        if not o.type == 'MESH':
            continue
        if o.name in nullObjs:
            continue
        if len(o.data.polygons) == 0 and (not o.name.split('.')[0] in specialBCs):
                continue
        names.append(formatObjectName(o.name))
        objects.append(o)
    return (objects, names)

def getNumberOfPatchType(patchType):
    N = 0
    for o in bpy.context.selected_objects:
        if o.ODS_CFD.preset == patchType:
            N += 1
    return N

class emptyFile():
    filepath = 'foamFile'
    classType = 'dictionary'

    def getFieldObjName(self):
        (path, self.fieldObjName) = os.path.split(self.filepath)

    def write(self):
        # Write the file
        self.openFile()
        self.getFieldObjName()
        self.writeHeader()
        self.writeBody()
        self.closeFile()

    def openFile(self,mode='w'):
        sc = bpy.context.scene
        fpath = '%s/%s'%(sc.ODS_CFD.system.caseDir, self.filepath)
        self.f = openFileWrite(fpath, mode)

    def closeFile(self):
        self.f.close()

    def writeAppendString(self,s):
        # Write some stuff and then close the file again.
        self.openFile(mode='a')
        self.f.write(s)
        self.f.close()

    def writeString(self, s, indent=0, endl=""):
        self.f.write(" "*indent + s + endl)

    def writeBody(self):
        return None

    def writeHeader(self):
        return None

    def dictText(self, d, text="", indent=0):
        def writeKey(k, t=""):
            s = d[k]
            if type(s) == dict or type(s) == OrderedDict:
                t += "%s%s\n%s{\n"%(" "*indent, k, " "*indent)
                t += self.dictText(s, indent=indent+4)   # Caution! Recursive call
                t += "%s}\n\n"%(" "*indent)
            elif type(s) != dict:
                t += "%s%s %s;\n"%(" "*indent, k, str(s))
            return t
        if 'default' in d.keys():
            text += writeKey('default')
        for k in d.keys():
            if k == 'default':
                continue
            else:
                text += writeKey(k)
        return text

    def writeDict(self, d, indent=0):
        self.writeString( self.dictText(d) )
        return None

class genericFoamFile(emptyFile):

    def writeHeader(self):
        self.f.write("""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  2.1.1                                 |
|   \\  /    A nd           | Web:      www.OpenFOAM.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       {0};
    object      {1};
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
""".format(self.classType, self.fieldObjName))
        return None
