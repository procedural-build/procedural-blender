###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2011, ODS-Engineering
# License: ods-engineering license
# Version: 1.2
# Web    : www.ods-engineering.com
###########################################################


import bpy

from procedural_compute.cfd.utils.foamUtils import genericFoamFile

from .potential import potentialFoam


def turbModel():
    sc = bpy.context.scene
    turbModel = sc.ODS_CFD.solver.turbModel
    m = getattr(sc.ODS_CFD.solver, sc.ODS_CFD.solver.turbModel)
    subModel = m.model
    return (turbModel, subModel)


def dropFields(fieldsDictFull):
    fieldsDict = fieldsDictFull.copy()
    (tModel, sModel) = turbModel()
    if tModel == "RAS":
        if sModel == "kEpsilon":
            fieldsDict.pop('omega')
        if "kOmega" in sModel:
            fieldsDict.pop('epsilon')
    return fieldsDict


class simpleFoam(potentialFoam):

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
        },
        'k': {
            'classType': 'volScalarField',
            'dim': [0, 2, -2, 0, 0, 0, 0],
            'default': 0.1
        },
        'epsilon': {
            'classType': 'volScalarField',
            'dim': [0, 2, -3, 0, 0, 0, 0],
            'default': 0.01
        },
        'omega': {
            'classType': 'volScalarField',
            'dim': [0, 0, -1, 0, 0, 0, 0],
            'default': 1.78
        },
        'nut': {
            'classType': 'volScalarField',
            'dim': [0, 2, -1, 0, 0, 0, 0],
            'default': 0.0
        }
    }

    presets = {
        'custom': {
            'U': 'fixedValue',
            'p': 'zeroGradient',
            'k': 'kqRWallFunction',
            'epsilon': 'epsilonWallFunction',
            'omega': 'omegaWallFunction',
            'nut': 'nutkWallFunction'},
        'wall': {
            'U': 'fixedValue',
            'p': 'zeroGradient',
            'k': 'kqRWallFunction',
            'epsilon': 'epsilonWallFunction',
            'omega': 'omegaWallFunction',
            'nut': 'nutkWallFunction'},
        'wallSlip': {
            'U': 'slip',
            'p': 'zeroGradient',
            'k': 'kqRWallFunction',
            'epsilon': 'epsilonWallFunction',
            'omega': 'omegaWallFunction',
            'nut': 'nutkWallFunction'},
        'fixedVelocity': {
            'U': 'fixedValue',
            'p': 'zeroGradient',
            'k': 'kqRWallFunction',
            'epsilon': 'epsilonWallFunction',
            'omega': 'omegaWallFunction',
            'nut': 'nutkWallFunction',
            'draw': ['U']
        },
        'fixedPressure': {
            'U': 'zeroGradient',
            'p': 'fixedValue',
            'k': 'kqRWallFunction',
            'epsilon': 'epsilonWallFunction',
            'omega': 'omegaWallFunction',
            'nut': 'nutkWallFunction',
            'draw': ['p']
        },
        'fixedPressureOutOnly': {
            'U': 'inletOutlet',
            'p': 'fixedValue',
            'k': 'kqRWallFunction',
            'epsilon': 'epsilonWallFunction',
            'omega': 'omegaWallFunction',
            'nut': 'nutkWallFunction',
            'draw': ['p']
        },
    }

    @classmethod
    def fields(self):
        return dropFields(self.fieldsDict)

    class caseFiles(potentialFoam.caseFiles):

        def write(self):
            self.controlDict().write()
            self.fvSchemes().write()
            self.fvSolution().write()
            self.transportProperties().write()
            # Turbulence model
            self.turbulenceProperties().write()
            return

        class turbulenceProperties(genericFoamFile):
            filepath = 'constant/turbulenceProperties'

            def writeBody(self):
                sc = bpy.context.scene
                turbModel = sc.ODS_CFD.solver.turbModel
                if turbModel == "Laminar":
                    self.writeString("simulationType  Laminar", endl=";\n\n")
                else:
                    self.writeString("simulationType  %s"%(turbModel), endl=";\n\n")

                    if turbModel == 'RAS':
                        m = getattr(sc.ODS_CFD.solver, turbModel)
                        subModel = m.model
                        self.writeString("RAS { RASModel %s; turbulence on; printCoeffs off; }" % subModel, endl="\n\n")

        class transportProperties(genericFoamFile):
            filepath = 'constant/transportProperties'

            def writeBody(self):
                sc = bpy.context.scene
                self.writeString("transportModel Newtonian", endl=";\n\n")
                self.writeString("nu              nu [ 0 2 -1 0 0 0 0 ] %f"%(sc.ODS_CFD.solver.nu), endl=";\n\n")

        class RASproperties(genericFoamFile):
            filepath = 'constant/RASProperties'

            def turbOn(self, tmod):
                if tmod == "laminar":
                    return "off"
                return "on"

            def writeBody(self):
                sc = bpy.context.scene
                turbModel = sc.ODS_CFD.solver.turbModel
                m = getattr(sc.ODS_CFD.solver, sc.ODS_CFD.solver.turbModel)
                subModel = m.model
                self.writeString("RASModel %s"%(subModel), endl=";\n\n")
                self.writeString("turbulence      %s"%(self.turbOn(turbModel)), endl=";\n\n")
                self.writeString("printCoeffs     off", endl=";\n\n")

        class fvSchemes(potentialFoam.caseFiles.fvSchemes):

            def setFields(self):
                potentialFoam.caseFiles.fvSchemes.setFields(self)

                # This is for v2
                '''
                self.fields['divSchemes'] = {
                    'default': 'bounded Gauss upwind',
                    'div(phi,U)': 'bounded Gauss linearUpwindV grad(U)',
                    'div(phi,k)': 'bounded Gauss upwind',
                    'div(phi,epsilon)': 'bounded Gauss upwind',
                    'div(phi,omega)': 'bounded Gauss upwind',
                    'div((nuEff*dev(T(grad(U)))))': 'Gauss linear',
                    'div((nuEff*dev(grad(U).T())))': 'Gauss linear'
                }
                '''

                # This is for v5
                self.fields['divSchemes'] = {
                    'default': 'Gauss linear',
                    'div(phi,U)': 'bounded Gauss linearUpwindV grad(U)',
                    'div(phi,k)': 'bounded Gauss upwind',
                    'div(phi,epsilon)': 'bounded Gauss upwind',
                    'div(phi,omega)': 'bounded Gauss upwind',
                    'div((nuEff*dev2(T(grad(U)))))': 'Gauss linear',
                    'div((nuEff*dev2(grad(U).T())))': 'Gauss linear'
                }

        class fvSolution(potentialFoam.caseFiles.fvSolution):

            def setFields(self):
                potentialFoam.caseFiles.fvSolution.setFields(self)

                self.fields['SIMPLE'] = {
                    'nNonOrthogonalCorrectors': 0,
                    '//pRefCell': 0,
                    '//pRefValue': 1e5
                }
                self.fields['solvers']['p'] = {
                    'solver': 'PCG',
                    'preconditioner': 'DIC',
                    'tolerance': 1e-06,
                    'relTol': 0.01
                }
                self.fields['solvers']['U'] = {
                    'solver': 'PBiCG',
                    'preconditioner': 'DILU',
                    'tolerance': 1e-05,
                    'relTol': 0.1
                }
                self.fields['solvers']['k'] = {
                    'solver': 'PBiCG',
                    'preconditioner': 'DILU',
                    'tolerance': 1e-05,
                    'relTol': 0.1
                }
                self.fields['solvers']['epsilon'] = {
                    'solver': 'PBiCG',
                    'preconditioner': 'DILU',
                    'tolerance': 1e-05,
                    'relTol': 0.1
                }
                self.fields['solvers']['omega'] = {
                    'solver': 'PBiCG',
                    'preconditioner': 'DILU',
                    'tolerance': 1e-05,
                    'relTol': 0.1
                }
                self.fields['solvers'] = dropFields(self.fields['solvers'])

                # This is for version 2

                # This is for version 5
                self.fields['relaxationFactors'] = {
                    'p': 0.3,
                    'U': 0.7,
                    'k': 0.7,
                    'epsilon': 0.7,
                    'omega': 0.7
                }

                return None
