###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


def drawBasic(self, context):
    # Skip this menu if the mainMenu is not pointing to CFD
    if context.scene.Compute.mainMenu != "CFD":
        return
    context.scene.ODS_CFD.drawMenu(self.layout)
