###########################################################
# Blender Modelling Environment for Architecture
# Copyright (C) 2011, ODS-Engineering
# License : ods-engineering license
# Version : 1.2
# Web     : www.ods-engineering.com
###########################################################


import bpy

from procedural_compute.cfd.utils.genericBC import genericBoundaryCondition
from procedural_compute.cfd.utils.foamUtils import genericFoamFile


class potentialFoam():

    fieldsDict = {
        'U': {
            'classType': 'volVectorField',
            'dim': [0, 1, -1, 0, 0, 0, 0],
            'default': (0, 0, 0)
        },
        'p': {
            'classType': 'volScalarField',
            'dim': [0, 2, -2, 0, 0, 0, 0],
            'default': 0.0
        }
    }

    presets = {
        'custom': {
            'U': 'fixedValue',
            'p': 'zeroGradient'
        },
        'wall': {
            'U': 'fixedValue',
            'p': 'zeroGradient'
        },
        'wallSlip': {
            'U': 'slip',
            'p': 'zeroGradient'
        },
        'fixedVelocity': {
            'U': 'fixedValue',
            'p': 'zeroGradient',
            'draw': ['U']
        },
        'fixedPressure': {
            'U': 'zeroGradient',
            'p': 'fixedValue',
            'draw': ['p']
        },
        'fixedPressureOutOnly': {
            'U': 'inletOutlet',
            'p': 'fixedValue',
            'draw': ['p']
        },
    }

    @classmethod
    def fields(self):
        return self.fieldsDict.copy()

    @classmethod
    def patchFields(self, preset):
        fields = self.fields()
        patchTypes = self.presets[preset]
        for f in fields:
            fields[f]['patchType'] = patchTypes[f]
        return fields

    @classmethod
    def writeField(self, f):
        field = self.fields()[f]
        BC = genericBoundaryCondition()
        BC.field = f
        BC.filepath = '0/%s'%(f)
        BC.dim = field['dim']
        BC.intField = field['default']
        BC.classType = field['classType']
        return BC.write()

    def writeCase(self):
        self.caseFiles().write()
        for f in self.fields():
            self.writeField(f)
        return True

    class caseFiles():

        def write(self):
            self.controlDict().write()
            self.fvSchemes().write()
            self.fvSolution().write()
            return

        class controlDict(genericFoamFile):
            filepath = 'system/controlDict'

            def writeBody(self):
                t = bpy.context.scene.ODS_CFD.control.getText()
                self.writeString(t)
                return

        class fvSchemes(genericFoamFile):
            filepath = 'system/fvSchemes'
            name = 'fvSchemes'
            fields = {}

            def __init__(self):
                self.setFields()
                return None

            def setFields(self):
                # Define some basic schemes
                self.fields = {
                    'ddtSchemes': {'default': 'steadyState'},
                    'gradSchemes': {'default': 'Gauss linear'},
                    'divSchemes': {'default': 'Gauss upwind'},
                    'laplacianSchemes': {'default': 'Gauss linear corrected'},
                    'interpolationSchemes': {'default': 'linear'},
                    'snGradSchemes': {'default': 'corrected'},
                    'fluxRequired': {'default': 'no'}
                }
                self.fields['fluxRequired']['p'] = ""
                self.fields['laplacianSchemes']['laplacian(1,p)'] = 'Gauss linear corrected'
                return None

            def writeBody(self):
                sc = bpy.context.scene
                sname = sc.ODS_CFD.solver.name
                fname = "%s.%s"%(self.name, sname)
                if fname in bpy.data.texts:
                    text = bpy.data.texts[fname].as_string()
                else:
                    text = self.dictText(self.fields)
                    btxt = bpy.data.texts.new(fname)
                    btxt.write(text)
                self.writeString(text)
                return None

        class fvSolution(fvSchemes):
            filepath = 'system/fvSolution'
            name = 'fvSolution'

            def setFields(self):
                # Define some basic solvers
                self.fields = {'solvers': {}}
                self.fields['solvers']['p'] = {
                    'solver': 'PCG',
                    'preconditioner': 'DIC',
                    'tolerance': 1e-06,
                    'relTol': 0
                }
                # Added for foam version > 4
                self.fields['solvers']['Phi'] = {
                    'solver': 'GAMG',
                    'preconditioner': 'DIC',
                    'tolerance': 1e-06,
                    'relTol': 0.01
                }
                # 
                self.fields['potentialFlow'] = {'nNonOrthogonalCorrectors': 2}
                return None
