

bl_info = {
    "name": "Procedural Build - API Client",
    "description": "Blender Client for interation with Procedural.build's vertically integrated set of APIs for advanced AEC sustainability",
    "author": "Procedural.build",
    "blender": (2, 80, 0),
    "wiki_url": "https://discourse.procedural.build",
    "category": "Object",
}


def register():
    from .core import register as register_core
    from .cfd import register as register_cfd
    from .rad import register as register_rad
    from .sun import register as register_sun
    register_core()
    register_cfd()
    register_rad()
    register_sun()


def unregister():
    from .core import unregister as unregister_core
    from .cfd import unregister as unregister_cfd
    from .rad import unregister as unregister_rad
    from .sun import unregister as unregister_sun
    unregister_core()
    unregister_cfd()
    unregister_rad()
    unregister_sun()


if __name__ == "__main__":
    from .core import register as register_core
    register_core()
