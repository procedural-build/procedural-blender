import bpy

from procedural_compute.cfd.properties.object import OBJECT_PROPS_COMPUTE_CFD
from procedural_compute.energy.properties.object import OBJECT_PROPS_COMPUTE_ENERGY


class OBJECT_PROPS_COMPUTE_CORE(bpy.types.PropertyGroup):
    CFD: bpy.props.PointerProperty(type=OBJECT_PROPS_COMPUTE_CFD)
    Energy: bpy.props.PointerProperty(type=OBJECT_PROPS_COMPUTE_ENERGY)


bpy.utils.register_class(OBJECT_PROPS_COMPUTE_CORE)

# Pointer
bpy.types.Object.Compute = bpy.props.PointerProperty(type=OBJECT_PROPS_COMPUTE_CORE)
