import bpy
import mathutils

from procedural_compute.core.operators.utils import explode_polygons_to_mesh, color_polygons


def object_face_centers(obj):
    return [(obj.matrix_world @ p.center).to_tuple() for p in obj.data.polygons]


def object_to_set(obj):
    return {
        "name": obj.name,
        "points": object_face_centers(obj)
    }


def get_sets_from_selected():
    return [object_to_set(obj) for obj in bpy.context.selected_objects]


def _value(values, scale=[0, 1]):
    # Get the raw value
    value = mathutils.Vector(values).magnitude if (not len(values) == 0) else values[0]
    # Fit it as a fraction within the color scale
    if value < scale[0]:
        value = 0
    elif value > scale[1]:
        value = 1
    else:
        value = (value - scale[0]) / (scale[1] - scale[0])
    return value


def get_point_value(line: str, scale=[0, 1]):
    parts = [float(i) for i in line.split()]
    return parts[:3], _value(parts[3:], scale=scale)


def map_to_polygons(obj, point_values, default=0.0, warning_tol=1e-3):
    mesh = obj.data
    size = len(mesh.polygons)

    # Populate a kdtree with polygon centers
    kd = mathutils.kdtree.KDTree(size)
    for p in mesh.polygons:
        kd.insert(obj.matrix_world @ p.center, p.index)
    kd.balance()

    # Use the kdtree to find the
    face_values = [default]*size
    for point, value in point_values:
        # Get the nearest polygon face to the point
        co, index, dist = kd.find(point)
        if dist > warning_tol:
            print(f"Point {point} not within {warning_tol} of face center.  Got distance {dist} to polygon {index} at {co}")
        face_values[index] = value

    # Return the face values
    return face_values


def color_object(obj, lines, scale=[0, 1]):
    # Get the values in the strings as floats
    print(f"Converting strings to points and values")
    point_values = [get_point_value(line, scale=scale) for line in lines]
    print(f"Got points and values for {len(point_values)}")
    # Match the points to the polygon centers (because openfoam crops them out)
    print("Mapping points and values to polygon centers")
    face_values = map_to_polygons(obj, point_values)
    print("Done mapping points and values to polygon centers")
    # Color the polygons with these values
    print(f"Setting vertex colors on object {obj.name}")
    color_polygons(obj, values = face_values, alpha=1.0)
    print(f"Done coloring object")
