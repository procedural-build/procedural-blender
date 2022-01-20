import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)-15s %(levelname)8s %(name)s %(message)s'
)

for name in ('blender_id', 'blender_cloud'):
    logging.getLogger(name).setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

bl_info = {
    "name": "Procedural Compute Client",
    "description": "Blender Client for interation with Procedural.build's vertically integrated set of APIs for advanced AEC sustainability",
    "author": "Procedural.build",
    "blender": (3, 0, 0),
    "wiki_url": "https://compute.procedural.build",
    "category": "Object",
}


def register():
    logger.info(f"Registering Compute modules...")
    from .core import register as register_core
    from .cfd import register as register_cfd
    #from .rad import register as register_rad
    #from .sun import register as register_sun
    register_core()
    register_cfd()
    #register_rad()
    #register_sun()
    logger.info(f"Compute modules registered!")


def unregister():
    logger.info(f"Unregistering Compute modules...")
    from .core import unregister as unregister_core
    from .cfd import unregister as unregister_cfd
    #from .rad import unregister as unregister_rad
    #from .sun import unregister as unregister_sun
    unregister_core()
    unregister_cfd()
    #unregister_rad()
    #unregister_sun()
    logger.info(f"Compute modules unregistered!")


if __name__ == "__main__":
    from .core import register as register_core
    register_core()
