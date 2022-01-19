###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

from math import log
from procedural_compute.cfd.utils.foamUtils import genericFoamFile, selectedObjectsAndNames
import procedural_compute.cfd.utils.foamCaseFiles as foamCaseFiles

class genericBoundaryCondition(genericFoamFile):
    field = 'empty'
    filepath = '0/empty'
    dim = [0,0,0,0,0,0,0]
    intField = [0]
    classType = 'volScalarField'    

    def __init__(self):
        self.getFieldObjName()

    def write(self):
        self.setIntField()
        self.openFile()
        self.writeHeader()
        self.writeDimHeader()
        self.writeObjects()
        self.writeFooter()
        self.closeFile()

    def setIntField(self):
        return None

    def writeObjects(self):
        (objs, names) = selectedObjectsAndNames()
        for i in range(len(objs)):
            self.f.write("    %s\n"%(names[i]))
            self.f.write(objs[i].ODS_CFD.getText(self.field))
        return

    def formatInput(self,s):
        s = str(s)
        s = s.replace(',','')
        s = s.replace('[','')
        s = s.replace(']','')
        return s

    def writeFooter(self):
        self.f.write("\n}\n\n// %s //\n"%("*"*73))
        
    def writeDimHeader(self):
        self.f.write("\ndimensions      [%s];\n\n"%(self.formatInput(self.dim)))
        self.f.write("internalField   uniform ")
        if self.classType == 'volVectorField' or self.classType == 'volTensorField':
            self.f.write("%s"%(self.formatInput(self.intField)))
        else:
            self.f.write(self.formatInput(self.intField))
        self.f.write(";\n\nboundaryField\n{\n")
    
        return None
