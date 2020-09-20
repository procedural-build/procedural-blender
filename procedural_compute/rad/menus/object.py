###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2011, ODS-Engineering
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


def drawBasic(self, context):
    # Skip this menu if the mainMenu is not pointing to CFD
    if context.scene.ODS.mainMenu != "Radiance":
        return
    context.object.RAD.drawMenu(self.layout)
