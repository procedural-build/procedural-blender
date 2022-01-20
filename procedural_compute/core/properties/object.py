import bpy

from procedural_compute.cfd.properties.object import OBJECT_PROPS_COMPUTE_CFD


class OBJECT_PROPS_COMPUTE_CORE(bpy.types.PropertyGroup):
    CFD: bpy.props.PointerProperty(type=OBJECT_PROPS_COMPUTE_CFD)


bpy.utils.register_class(OBJECT_PROPS_COMPUTE_CORE)

# Pointer
bpy.types.Object.Compute = bpy.props.PointerProperty(type=OBJECT_PROPS_COMPUTE_CORE)
