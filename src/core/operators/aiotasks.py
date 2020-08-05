import asyncio
import time
import bpy
from procedural_compute.core.utils.addRemoveMeshObject import addCubeObject
from procedural_compute.core.utils.threads import queues, get_or_create_queue, queue_fun

"""
Threading cannot call any blender code from threads other than the
main thread.  So we can't use that to update the blender viewport dynamically.

So instead we use asyncio to start a thread which makes the http request with
urllib.  The http request thread will put the response into a cache dictionary
and the asyncio task will wait until data is available in that object.  It will
then perform the required function to render that data in the viewport.

Test queuing an asyncio task like this:
from procedural_compute.core.operators import asyncio_queue_task
asyncio_queue_task("http://blender.org")
"""

RESPONSE_CACHE = {}

timer = None

def handle_data(data):
    """ A synchronous function that handles the response data.  This is called
    by the callback from async fetch_page
    """
    print("Handling the response data", data)
    time.sleep(2)
    addCubeObject(f"test_cube", 1, [0, 1, 0.5])
    print("Done handling response data")

def asyncio_queue_task(url):
    asyncio.ensure_future(
        fetch_data(url, callback=handle_data)
    )
    bpy.ops.asyncio.loop()

def fetch_data_sync(url):
    # Simulate some time to fetch the data
    for i in range(10):
        print("Fetching data with threading", i)
        time.sleep(1)
    # Set the RESPONSE_CACHE
    RESPONSE_CACHE[url] = '{"data": "hello world"}'

async def fetch_data(url, callback=None, timeout=20, clear_cache_after=False):
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
    queue_fun('requests', fetch_data_sync, args=(url,))
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
