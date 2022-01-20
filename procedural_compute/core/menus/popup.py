import bpy

# This class is the actual dialog that pops up to create the cube
class ConfirmDialogue(bpy.types.Operator):
    bl_idname = "scene.confirm_popup"
    bl_label = "Confirm Dialogue"

    # Here you declare everything you want to show in the dialog 
    confirmed: bpy.props.BoolProperty(name = "Confirm?", default = True)

    # This is the method that is called when the ok button is pressed
    # which is what calls the AddCube() method 
    def execute(self, context):        
        self.report({'INFO'}, f"Confirmed = {self.confirmed}")
        return {'FINISHED'}

    # This is called when the operator is called, this "shows" the dialog 
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


