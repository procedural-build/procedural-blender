###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
from procedural_compute.cfd.utils import foamUtils
from mathutils.geometry import normal


def porousWriteCheck(obj, writePorous, writeNonPorous):
    passedPorousWriteCheck = True
    if (not writePorous) and (obj.ODS_CFD.porous_isPorous):
        passedPorousWriteCheck = False
    if (not writeNonPorous) and (not obj.ODS_CFD.porous_isPorous):
        passedPorousWriteCheck = False
    return passedPorousWriteCheck


def faceToTriangles(face):
    """ Converts the given face to two triangles or leaves as-is
    if already triangulated.
    """
    if len(face) == 3:
        return [face]
    # If this is a 4-sided face
    if not len(face) == 4:
        raise Exception("Length of vertices describing face should be either 4 or 3")
    return [
        [face[0], face[1], face[2]],
        [face[2], face[3], face[0]]
    ]


def write_triangle(f, tri):
    f.write("facet normal %f %f %f\n" % normal(*tri)[:])
    f.write("  outer loop\n")
    for vert in tri:
        f.write("    vertex %f %f %f\n" % vert[:])
    f.write("  endloop\n")
    f.write("endfacet\n")


def writeObjectsToFile(f, objects = None, writePorous=True, writeNonPorous=True):
    """ Write objects in STL format to a file-like object
    """

    if objects is None:
        objects = bpy.context.visible_objects

    specialNames = ['cfdBoundingBox', 'cfdMeshKeepPoint', 'MinX', 'MaxX', 'MinY', 'MaxY', 'MinZ', 'MaxZ']

    for obj in objects:

        # Check if we should skip this object
        if (not obj.type == 'MESH') or (len(obj.data.polygons) == 0):
            continue

        passedPorousWriteCheck = porousWriteCheck(obj, writePorous, writeNonPorous)

        if obj.type == 'MESH' and (obj.name.split('.')[0] not in specialNames) and passedPorousWriteCheck:
            # Object.to_mesh() is not guaranteed to return a mesh.
            try:
                me = obj.to_mesh()
            except RuntimeError:
                continue

            # Transform to global coordinates and get the vertices
            me.transform(obj.matrix_world)
            vertices = me.vertices

            f.write("solid %s\n"%(foamUtils.formatObjectName(obj.name)))
            me.calc_loop_triangles()
            for face in me.loop_triangles:
                # Get the global coordinates of the vertices
                face_vertex_coords = [vertices[index].co.copy() for index in face.vertices]
                # faceToTriangles: Guarantee the face is a triangle - split if a quad
                for tri in faceToTriangles(face_vertex_coords):
                    # Write faces to file (this is normally only one element in tris
                    # unless faceToTriangles split a quad to 2 triangles)
                    write_triangle(f, tri)
            f.write("endsolid\n")


def writeTriSurface(filename='constant/triSurface/cfdGeom.stl', writePorous=True, writeNonPorous=True):
    sc = bpy.context.scene
    filename = '%s/%s'%(sc.ODS_CFD.system.caseDir, filename)
    print('Starting Ascii STL Export of Selected Objects to: %s...' % bpy.path.abspath(filename))

    f = foamUtils.openFileWrite(filename)
    writeObjectsToFile(f, writePorous=writePorous, writeNonPorous=writeNonPorous)
    f.close()

    print('asciiSTLExport Completed.')
