###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

"""
A set of functions for adding and removing mesh objects in
Blender as required for ODS.
"""

import bpy


def flatten(alist):
    """ Flatten a list of lists or tuples into a single long list.
    """
    return sum([list(a) for a in alist], [])


def addCubeObject(name, dim, loc):
    """ Adds a faceless cube to the scene with name="name", centered at location="loc" and
    with dimension="dim".
    """
    vs = [
        [0.5, 0.5, -0.5],
        [0.5, -0.5, -0.5],
        [-0.5, -0.5, -0.5],
        [-0.5, 0.5, -0.5],
        [0.5, 0.5, 0.5],
        [0.5, -0.5, 0.5],
        [-0.5, -0.5, 0.5],
        [-0.5, 0.5, 0.5]
    ]
    for v in vs:
        for i in range(3):
            v[i] = v[i] * dim + loc[i]
    es = [
        [0, 1], [0, 3], [0, 4], [1, 2], [1, 5], [2, 3],
        [2, 6], [3, 7], [4, 5], [4, 7], [5, 6], [6, 7]
    ]
    addObject(name, vlist=vs, elist=es)
    return None


def addObject(name, vlist=[], elist=[], drawName=False):
    """ Adds a faceless cube to the scene with name="name", centered at location="loc" and
    with dimension="dim
    """
    sc = bpy.context.scene
    mesh = bpy.data.meshes.new(name)
    if len(vlist) > 0:
        #mesh.add_geometry(len(vlist),len(elist),0)
        mesh.vertices.add(len(vlist))
        mesh.vertices.foreach_set("co", flatten(vlist))
        mesh.edges.add(len(elist))
        mesh.edges.foreach_set("vertices", flatten(elist))
    mesh.update(calc_edges_loose=True)
    nobj = bpy.data.objects.new(name, mesh)
    # Add object to the scene and select it
    sc.collection.objects.link(nobj)
    if bpy.context.active_object is None or bpy.context.active_object.mode == 'OBJECT':
        bpy.context.view_layer.objects.active = nobj
    if drawName:
        nobj.show_name = True
    nobj.select_set(True)
    return nobj


def delObject(name):
    """ Deletes the object with name "name" from the current scene
    """
    sc = bpy.context.scene
    ob = bpy.data.objects[name]
    sc.collection.objects.unlink(ob)
    bpy.data.objects.remove(ob)
    return None
