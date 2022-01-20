###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
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
        return False

    def toStr(self, V):
        return "uniform ( %s )"%(" ".join([str(u) for u in V]))

    def formatFields(self, fieldList):
        t = ""
        for f in fieldList:
            t += "%s%s %s;\n"%(" " * 8, str(f[0]), str(f[1]))
        return " " * 4 + "{\n" + t + " " * 4 + "}\n"

    def getText(self):
        return None


class OBJECT_PROPS_COMPUTE_CFD_PATCH_VECTOR_slip(bpy.types.PropertyGroup, defaultPatch):
    def getText(self):
        fieldList = [("type", "slip")]
        return self.formatFields(fieldList)


bpy.utils.register_class(OBJECT_PROPS_COMPUTE_CFD_PATCH_VECTOR_slip)


class OBJECT_PROPS_COMPUTE_CFD_PATCH_VECTOR_zeroGradient(bpy.types.PropertyGroup, defaultPatch):
    def getText(self):
        fieldList = [("type", "zeroGradient")]
        return self.formatFields(fieldList)


bpy.utils.register_class(OBJECT_PROPS_COMPUTE_CFD_PATCH_VECTOR_zeroGradient)


class OBJECT_PROPS_COMPUTE_CFD_PATCH_VECTOR_other(bpy.types.PropertyGroup, defaultPatch):

    value: bpy.props.StringProperty(name="value", default="{type zeroGradient;}")

    def draw(self, layout):
        layout.row().prop(self, "value")
        return False

    def getText(self):
        return self.value


bpy.utils.register_class(OBJECT_PROPS_COMPUTE_CFD_PATCH_VECTOR_other)


class OBJECT_PROPS_COMPUTE_CFD_PATCH_VECTOR_inletOutlet(bpy.types.PropertyGroup, defaultPatch):

    inletValue: bpy.props.FloatVectorProperty(name="Value", default=(0.0, 0.0, 0.0))
    value: bpy.props.FloatVectorProperty(name="Value", default=(0.0, 0.0, 0.0))

    def draw(self, layout):
        layout.row().prop(self, "value")
        layout.row().prop(self, "inletValue")
        return True

    def getText(self):
        fieldList = [
            ("type", "inletOutlet"),
            ("inletValue", self.toStr(self.inletValue)),
            ("value", self.toStr(self.value))
        ]
        return self.formatFields(fieldList)


bpy.utils.register_class(OBJECT_PROPS_COMPUTE_CFD_PATCH_VECTOR_inletOutlet)


class OBJECT_PROPS_COMPUTE_CFD_PATCH_VECTOR_fixedValue(bpy.types.PropertyGroup, defaultPatch):
    value: bpy.props.FloatVectorProperty(name="Value", default=(0.0, 0.0, 0.0))

    def setValue(self, value, var='value'):
        setattr(self, var, value)

    def draw(self, layout):
        layout.row().prop(self, "value")
        return True

    def getText(self):
        fieldList = [("type", "fixedValue"), ("value", self.toStr(self.value))]
        return self.formatFields(fieldList)


bpy.utils.register_class(OBJECT_PROPS_COMPUTE_CFD_PATCH_VECTOR_fixedValue)


class OBJECT_PROPS_COMPUTE_CFD_PATCH_VECTOR(bpy.types.PropertyGroup):
    slip: bpy.props.PointerProperty(type=OBJECT_PROPS_COMPUTE_CFD_PATCH_VECTOR_slip)
    zeroGradient: bpy.props.PointerProperty(type=OBJECT_PROPS_COMPUTE_CFD_PATCH_VECTOR_zeroGradient)
    fixedValue: bpy.props.PointerProperty(type=OBJECT_PROPS_COMPUTE_CFD_PATCH_VECTOR_fixedValue)
    inletOutlet: bpy.props.PointerProperty(type=OBJECT_PROPS_COMPUTE_CFD_PATCH_VECTOR_inletOutlet)
    other: bpy.props.PointerProperty(type=OBJECT_PROPS_COMPUTE_CFD_PATCH_VECTOR_other)

    items_list = make_tuples([
        "fixedValue",
        "zeroGradient",
        "inletOutlet",
        "slip",
        "other"])
    patchType: bpy.props.EnumProperty(name="patchType", items=items_list, description="patchType", default="fixedValue")

    localCoords: bpy.props.BoolProperty(name="localCoords", description="localCoords", default=False)
    flowRate: bpy.props.BoolProperty(name="flowRate", description="flowRate", default=False)

    def setValue(self, value, var='value'):
        return getattr(self, self.patchType).setValue(value, var=var)

    def draw(self, layout, header=True):
        if header:
            layout.row().prop(self, "patchType")
        c = getattr(self, self.patchType)
        if c.draw(layout):
            # Draw settings for local coordinates
            split = layout.split()
            col = split.column()
            col.prop(self, "localCoords", text="Local Coordinates")
            col = split.column()
            col.prop(self, "flowRate", text="Total Flux")
        return None

    def getText(self):
        return getattr(self, self.patchType).getText()


bpy.utils.register_class(OBJECT_PROPS_COMPUTE_CFD_PATCH_VECTOR)
