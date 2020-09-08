###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

"""
Generic functions that are used throughout multiple ODS modules
"""
import bpy


def drawCollectionTemplateList(layout, base, collection):
    """ Draws a UI TemplateList for a generic Blender collection type
    """
    row = layout.row()
    row.template_list("UI_UL_list", "custom", base, collection, base, "active_" + collection + "_index", rows=2)
    col = row.column(align=True)
    oType = getBaseObjType(base)

    bPath = base.path_from_id()
    if "[" in bPath:
        (p1, p2) = bPath.split("[")
        p2 = p2.split("]")[1]
        bPath = p1 + p2

    col.operator("scene.collectionops", icon='ZOOM_IN', text="").command = oType + "." + bPath + "." + collection + ".add"
    col.operator("scene.collectionops", icon='ZOOM_OUT', text="").command = oType + "." + bPath + "." + collection + ".remove"
    return None


def getBaseObjType(o):
    """ Gets the type of base object to which the collection object belongs
    """
    t = str(type(o.id_data))
    if "Scene" in t:
        return "scene"
    elif "Object" in t:
        return "object"
    elif "Material" in t:
        return "material"
    else:
        print("Warning: base object id_data type not known")
    return None


def faceToTriangles(face):
    """ Converts the given face to two triangles or leaves as-is
    if already triangulated.
    """
    triangles = []
    if (len(face) == 4):  # quad
        triangles.append([face[0], face[1], face[2]])
        triangles.append([face[2], face[3], face[0]])
    else:
        triangles.append(face)
    return triangles


def faceValues(face, mesh):
    """ Gets the vertex location for a given face in terms of a
    different coordinate system (generally global coordinates)
    by pre-multiplying with a transformation matrix.
    """
    fv = []
    for i in range(len(face.vertices)):
        verti = face.vertices_raw[i]
        fv.append(mesh.vertices[verti].co)
    return fv


def getTriangleProperties(x, y, z):
    """ Returns the area and centroid of a triangle defined by lists
    of x, y and z coordinates
    """
    # Get the x, y and z coordinates of the centroid of the triangle
    xc = (x[0] + x[1] + x[2]) / 3.0
    yc = (y[0] + y[1] + y[2]) / 3.0
    zc = (z[0] + z[1] + z[2]) / 3.0

    # Get the area of the triangle (using Herons formula)
    a = ((x[1] - x[0])**2 + (y[1] - y[0])**2 + (z[1] - z[0])**2)**0.5
    b = ((x[2] - x[1])**2 + (y[2] - y[1])**2 + (z[2] - z[1])**2)**0.5
    c = ((x[0] - x[2])**2 + (y[0] - y[2])**2 + (z[0] - z[2])**2)**0.5
    ar = (((a + b - c) * (a - b + c) * (b + c - a) * (a + b + c))**0.5) / 4.0

    # Add these to the variables for calculating area-weighted centroid of the solid
    ca = [0.0, 0.0, 0.0]
    ca[0] = xc * ar
    ca[1] = yc * ar
    ca[2] = zc * ar

    return ar, ca


def getObjectAreaAndCentroid(obj):
    """ Returns the total area and centroid of an object
    """
    # matrix to hold the coordinates of a triangle
    c = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    Cent = [0.0, 0.0, 0.0]
    tArea = 0.0         # Total surface area (calculated from tris)

    me = obj.to_mesh(bpy.context.scene, False, "PREVIEW")
    me.transform(obj.matrix_world)

    for face in me.faces:
        fv = faceValues(face, me)
        tris = faceToTriangles(fv)
        for t in tris:
            for i in range(3):
                for j in range(3):
                    c[i][j] = t[j][i]
            (a, ca) = getTriangleProperties(c[0], c[1], c[2])
            tArea += a
            for s in range(len(ca)):
                Cent[s] += ca[s]
    # Get the area weighted centroid
    for s in range(len(Cent)):
        Cent[s] = Cent[s] / tArea

    return tArea, Cent
