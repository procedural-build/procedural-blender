import bpy


class OBJECT_PT_COMPUTE_CORE(bpy.types.PropertyGroup):
    pass


bpy.utils.register_class(OBJECT_PT_COMPUTE_CORE)

# Pointer
bpy.types.Object.Compute = bpy.props.PointerProperty(type=OBJECT_PT_COMPUTE_CORE)
