import asyncio
import time
import bpy
import random
from procedural_compute.core.utils.addRemoveMeshObject import addCubeObject
from procedural_compute.core.utils.threads import queues, get_or_create_queue, queue_fun
from procedural_compute.core.utils.compute.auth import get_current_user

"""
Threading cannot call any blender code from threads other than the
main thread.  So we can't use that to update the blender viewport dynamically.

So instead we use asyncio to start a thread which makes the http request with
urllib.  The http request thread will put the response into a cache dictionary
and the asyncio task will wait until data is available in that object.  It will
then perform the required function to render that data in the viewport.

Test queuing an asyncio task like this:
from procedural_compute.core.operators import fetch_async
fetch_async("http://blender.org")
"""

RESPONSE_CACHE = {}

timer = None


def clear_mesh(mesh):
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode = 'OBJECT')


def add_face(size=0.1, center=(0,0,0), rotation=(0,0,0)):
    bpy.ops.mesh.primitive_plane_add(
        size=size,
        enter_editmode=False,
        align='WORLD',
        location=(0.14, 0.09, 0.65),
        rotation=(0.0279253, 0, 0)
    )


def add_grid(min=(0,0,0), max=(1,1,0), n_divs=10):
    bpy.ops.object.mode_set(mode = 'EDIT')
    dx = (max[0] - min[0]) / n_divs
    dy = (max[1] - min[1]) / n_divs
    for x in range(n_divs):
        for y in range(n_divs):
            add_face(size=dx, center=(dx*x, dy*y, 0))
    bpy.ops.object.mode_set(mode = 'OBJECT')


def handle_data(data):
    """ A synchronous function that handles the response data.  This is called
    by the callback from async fetch_page
    """
    print("Handling the response data", data)
    time.sleep(2)
    #addCubeObject(f"test_cube", 1, [0, 1, 0.5])
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0))
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.subdivide(number_cuts=4)
    bpy.ops.object.editmode_toggle()

    obj = bpy.context.selected_objects[0]
    mesh = obj.data

    if not mesh.vertex_colors.get("Col"):
        mesh.vertex_colors.new()
    color_layer = mesh.vertex_colors["Col"]

    i = 0
    for polygon in mesh.polygons:
        for idx in polygon.loop_indices:
            (r, g, b) = [random.random() for i in range(3)]
            color_layer.data[i].color = (r, g, b, 1.0)
            i += 1

        bpy.ops.object.mode_set(mode='VERTEX_PAINT')

    print("Done handling response data")

def fetch_async(*args, **kwargs):
    asyncio.ensure_future(
        fetch_data(*args, **kwargs)
    )
    bpy.ops.asyncio.loop()

def fetch_sync(*args, **kwargs):
    # Simulate some time to fetch the data
    User = get_current_user()
    print("FETCHING DATA", args, kwargs)
    # Fetch the url as requested
    response = User.request(*args, **kwargs)
    # Set the RESPONSE_CACHE
    response_data = None
    if isinstance(response, dict):
        response_data = response
    else:
        response_data = getattr(response, 'read_content', None)
    #print("GOT RESPONSE FROM fetch_sync", response_data)
    url = args[1]
    RESPONSE_CACHE[url] = response_data

async def fetch_data(url, method='GET', callback=None, timeout=20, clear_cache_after=False, **kwargs):
    ''' Queue a task on another thread to get the data with urllib then
    await until the data is available and call the callback to handle the
    response data. The callback will render objects, meshes, etc) as required
    to view the results.

    This will **not** block the UI while retreiving the data (which may be large
    files) - but it will block while the callback does whatever it does to
    handle the data.  So if the handler does some large operations such as making
    large/complex objects - then the UI will block during that step.
    '''
    # Clear the cache that holds the response data
    RESPONSE_CACHE[url] = None
    # Queue up the thread that will get the data
    queue_fun('requests', fetch_sync, args=(method, url), kwargs=kwargs)
    # Now loop for timeout seconds waiting for data
    response_data = None
    for i in range(timeout):
        print("Awaiting for response data from thread", i)
        await asyncio.sleep(1)
        response_data = RESPONSE_CACHE[url]
        if response_data is not None:
            break
    # Call the callback that handles the response data
    callback(response_data)
    # Clear the cache after handling the response
    if clear_cache_after:
        del RESPONSE_CACHE[url]

#task = asyncio.ensure_future(fetch_page("http://blender.org"))
#asyncio.get_event_loop().run_until_complete(task)

class AsyncLoop(bpy.types.Operator):
    bl_idname = "asyncio.loop"
    bl_label = "Runs the asyncio main loop"
    command: bpy.props.EnumProperty(
        name="Command",
        description="Command being issued to the asyncio loop",
        default='TOGGLE',
        items=[
            ('START', "Start", "Start the loop"),
            ('STOP', "Stop", "Stop the loop"),
            ('TOGGLE', "Toggle", "Toggle the loop state")
        ]
    )
    period: bpy.props.FloatProperty(
        name="Period",
        description="Time between two asyncio beats",
        default=0.01,
        subtype="UNSIGNED",
        unit="TIME"
    )

    def execute(self, context):
        return self.invoke(context, None)

    def invoke(self, context, event):
        global timer
        wm = context.window_manager
        if timer and self.command in ('STOP', 'TOGGLE'):
            wm.event_timer_remove(timer)
            timer = None
            return {'FINISHED'}
        elif not timer and self.command in ('START', 'TOGGLE'):
            wm.modal_handler_add(self)
            timer = wm.event_timer_add(self.period, window=context.window)
            return {'RUNNING_MODAL'}
        else:
            return {'CANCELLED'}

    def modal(self, context, event):
        global timer
        if not timer:
            return {'FINISHED'}
        elif event.type != 'TIMER':
            return {'PASS_THROUGH'}
        else:
            loop = asyncio.get_event_loop()
            loop.stop()
            loop.run_forever()
            return {'RUNNING_MODAL'}

bpy.utils.register_class(AsyncLoop)
