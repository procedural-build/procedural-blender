import bpy
from procedural_compute.core.utils import make_tuples


class SCENE_PROPS_COMPUTE_CORE_TASK(bpy.types.PropertyGroup):
    # Project and task get or create
    project_name: bpy.props.StringProperty(name="Project Name", default='', description="Project name")
    project_number: bpy.props.StringProperty(name="Project Number", default='', description="Project number (optional)")
    project_id: bpy.props.StringProperty(name="Project ID", default='', description="Project ID")
    project_data: bpy.props.StringProperty(name="Project data", default='', description="Project data")
    task_name: bpy.props.StringProperty(name="Task Name", default='', description="Task name")
    task_id: bpy.props.StringProperty(name="Task ID", default='', description="Task ID")
    task_data: bpy.props.StringProperty(name="Task data", default='', description="Task data")

    def draw_menu(self, layout):
        L = layout.box()
        L.row().label(text="Project/Task")

        L.row().prop(self, "project_name")
        row = L.row()
        row.prop(self, "project_id")
        row.enabled = False

        L.row().prop(self, "task_name")
        row = L.row()
        row.prop(self, "task_id")
        row.enabled = False

        L.row().operator("scene.compute_operators_core", text="Get or Create").command = "get_or_create_project_and_task"

bpy.utils.register_class(SCENE_PROPS_COMPUTE_CORE_TASK)