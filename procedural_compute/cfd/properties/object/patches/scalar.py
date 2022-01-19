###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2011, ODS-Engineering
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

import bpy
from procedural_compute.core.utils import make_tuples


class defaultPatch():
    def setValue(self, value, var='value'):
        return None

    def draw(self, layout):
        return None

    def toStr(self, V):
        return "uniform %f"%(V)

    def formatFields(self, fieldList):
        t = ""
        for f in fieldList:
            t += "%s%s %s;\n"%(" " * 8, str(f[0]), str(f[1]))
        return " " * 4 + "{\n" + t + " " * 4 + "}\n"

    def getText(self):
        return None


class ODS_CFD_PATCH_SCALAR_zeroGradient(bpy.types.PropertyGroup, defaultPatch):
    def getText(self):
        fieldList = [("type", "zeroGradient")]
        return self.formatFields(fieldList)


bpy.utils.register_class(ODS_CFD_PATCH_SCALAR_zeroGradient)


class ODS_CFD_PATCH_SCALAR_other(bpy.types.PropertyGroup, defaultPatch):

    value: bpy.props.StringProperty(name="value", default="{type zeroGradient;}")

    def draw(self, layout):
        layout.row().prop(self, "value")

    def getText(self):
        return "%s\n"%(self.value)


bpy.utils.register_class(ODS_CFD_PATCH_SCALAR_other)


class ODS_CFD_PATCH_SCALAR_inletOutlet(bpy.types.PropertyGroup, defaultPatch):

    inletValue: bpy.props.FloatProperty(name="inletValue", default=0.0)
    value: bpy.props.FloatProperty(name="value", default=0.0)

    def draw(self, layout):
        row = layout.row()
        row.prop(self, "value")
        row.prop(self, "inletValue")

    def getText(self):
        fieldList = [("type", "inletOutlet"), ("inletValue", self.toStr(self.inletValue)), ("value", self.toStr(self.value))]
        return self.formatFields(fieldList)


bpy.utils.register_class(ODS_CFD_PATCH_SCALAR_inletOutlet)


class ODS_CFD_PATCH_SCALAR_kqRWallFunction(bpy.types.PropertyGroup, defaultPatch):
    value: bpy.props.FloatProperty(name="Value", default=0.0)

    def setValue(self, value, var='value'):
        setattr(self, var, value)

    def draw(self, layout):
        layout.row().prop(self, "value")

    def getText(self):
        fieldList = [("type", "kqRWallFunction"), ("value", self.toStr(self.value))]
        return self.formatFields(fieldList)


bpy.utils.register_class(ODS_CFD_PATCH_SCALAR_kqRWallFunction)


class ODS_CFD_PATCH_SCALAR_epsilonWallFunction(bpy.types.PropertyGroup, defaultPatch):
    value: bpy.props.FloatProperty(name="Value", default=0.0)

    def setValue(self, value, var='value'):
        setattr(self, var, value)

    def draw(self, layout):
        layout.row().prop(self, "value")

    def getText(self):
        fieldList = [("type", "epsilonWallFunction"), ("value", self.toStr(self.value))]
        return self.formatFields(fieldList)


bpy.utils.register_class(ODS_CFD_PATCH_SCALAR_epsilonWallFunction)


class ODS_CFD_PATCH_SCALAR_omegaWallFunction(bpy.types.PropertyGroup, defaultPatch):
    value: bpy.props.FloatProperty(name="Value", default=0.0)

    def setValue(self, value, var='value'):
        setattr(self, var, value)

    def draw(self, layout):
        layout.row().prop(self, "value")

    def getText(self):
        fieldList = [("type", "omegaWallFunction"), ("value", self.toStr(self.value))]
        return self.formatFields(fieldList)


bpy.utils.register_class(ODS_CFD_PATCH_SCALAR_omegaWallFunction)


class ODS_CFD_PATCH_SCALAR_nutkWallFunction(bpy.types.PropertyGroup, defaultPatch):
    value: bpy.props.FloatProperty(name="Value", default=0.0)

    def setValue(self, value, var='value'):
        setattr(self, var, value)

    def draw(self, layout):
        layout.row().prop(self, "value")

    def getText(self):
        fieldList = [("type", "nutkWallFunction"), ("value", self.toStr(self.value))]
        return self.formatFields(fieldList)


bpy.utils.register_class(ODS_CFD_PATCH_SCALAR_nutkWallFunction)


class ODS_CFD_PATCH_SCALAR_fixedValue(bpy.types.PropertyGroup, defaultPatch):
    value: bpy.props.FloatProperty(name="Value", default=0.0)

    def setValue(self, value, var='value'):
        setattr(self, var, value)

    def draw(self, layout):
        layout.row().prop(self, "value")

    def getText(self):
        fieldList = [("type", "fixedValue"), ("value", self.toStr(self.value))]
        return self.formatFields(fieldList)


bpy.utils.register_class(ODS_CFD_PATCH_SCALAR_fixedValue)


class ODS_CFD_PATCH_SCALAR(bpy.types.PropertyGroup):
    zeroGradient: bpy.props.PointerProperty(type=ODS_CFD_PATCH_SCALAR_zeroGradient)
    fixedValue: bpy.props.PointerProperty(type=ODS_CFD_PATCH_SCALAR_fixedValue)
    kqRWallFunction: bpy.props.PointerProperty(type=ODS_CFD_PATCH_SCALAR_kqRWallFunction)
    epsilonWallFunction: bpy.props.PointerProperty(type=ODS_CFD_PATCH_SCALAR_epsilonWallFunction)
    omegaWallFunction: bpy.props.PointerProperty(type=ODS_CFD_PATCH_SCALAR_omegaWallFunction)
    nutkWallFunction: bpy.props.PointerProperty(type=ODS_CFD_PATCH_SCALAR_nutkWallFunction)
    inletOutlet: bpy.props.PointerProperty(type=ODS_CFD_PATCH_SCALAR_inletOutlet)
    other: bpy.props.PointerProperty(type=ODS_CFD_PATCH_SCALAR_other)

    items_list = make_tuples([
        "fixedValue",
        "zeroGradient",
        "inletOutlet",
        "kqRWallFunction",
        "epsilonWallFunction",
        "omegaWallFunction",
        "nutkWallFunction",
        "other"])
    patchType: bpy.props.EnumProperty(name="patchType", items=items_list, description="patchType", default="fixedValue")

    def setValue(self, value, var='value'):
        return getattr(self, self.patchType).setValue(value, var=var)

    def draw(self, layout, header=True):
        if header:
            layout.row().prop(self, "patchType")
        c = getattr(self, self.patchType)
        c.draw(layout)
        return None

    def getText(self):
        return getattr(self, self.patchType).getText()


bpy.utils.register_class(ODS_CFD_PATCH_SCALAR)
