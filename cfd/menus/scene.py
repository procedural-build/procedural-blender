###########################################################
# Blender Modelling Environment for Architecture
# Copyright (C) 2011, ODS-Engineering
# License : ods-engineering license
# Version : 1.2
# Web     : www.ods-engineering.com
###########################################################


def drawBasic(self, context):
    # Skip this menu if the mainMenu is not pointing to CFD
    if context.scene.ODS.mainMenu != "CFD":
        return
    context.scene.ODS_CFD.drawMenu(self.layout)
