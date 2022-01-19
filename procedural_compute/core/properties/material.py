import bpy


class MATERIAL_PT_COMPUTE_CORE(bpy.types.PropertyGroup):
    pass


bpy.utils.register_class(MATERIAL_PT_COMPUTE_CORE)

# Pointer
bpy.types.Material.Compute = bpy.props.PointerProperty(type=MATERIAL_PT_COMPUTE_CORE)
