import bpy
import mathutils
import logging
from mathutils import Vector

from procedural_compute.core.operators.utils import explode_polygons_to_mesh, color_polygons

logger = logging.getLogger(__name__)


def object_face_centers(obj):
    return [(obj.matrix_world @ p.center).to_tuple() for p in obj.data.polygons]


def object_to_set(obj):
    return {
        "name": obj.name,
        "points": object_face_centers(obj)
    }


def get_sets_from_selected():
    return [object_to_set(obj) for obj in bpy.context.selected_objects if obj.type == "MESH"]


def _scale(value, scale=[0, 1]):
    if value < scale[0]:
        return 0
    elif value > scale[1]:
        return 1
    else:
        value = (value - scale[0]) / (scale[1] - scale[0])
    return value


def _value_to_vector(values):
    # Get the raw value (NOTE! even scalars are saved as a vector)
    if not len(values) > 1:
        values = [values[0], 0, 0]
    return Vector(values)


def point_and_value_vectors(line: str):
    parts = [float(i) for i in line.split()]
    return parts[:3], _value_to_vector(parts[3:])


def map_to_polygons(obj, point_values, default=Vector([0, 0, 0]), warning_tol=1e-3):
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
            logger.info(
                f"Point {point} not within {warning_tol} of face center.  Got distance {dist} to polygon {index} at {co}")
        face_values[index] = value

    # Return the face values
    return face_values


def _flatten(vectors: list):
    return [i for v in vectors for i in v]


def _value(vector, field_type="vector"):
    return vector.magnitude if field_type == "vector" else vector[0]


def face_attr_to_scaled_values(obj, scale=[0, 1], attr_name="probe_result"):
    field_type = obj.get("probe_field_type", "vector")
    values = [_value(i.vector, field_type=field_type) for i in obj.data.attributes[attr_name].data]
    return [_scale(i, scale=scale) for i in values]


def color_vertices_from_face_attr(obj, alpha=1.0, scale=[0, 1], attr_name="probe_result"):
    # Color the vertices from raw values set as face attributes
    logger.info(f"Scaling face values from object {obj.name} [scale={scale}]")
    scale_values = face_attr_to_scaled_values(obj, scale=scale)

    # Save the scale properties as a custom property on this object
    obj["probe_scale_min"] = scale[0]
    obj["probe_scale_max"] = scale[1]

    logger.info(f"Setting color of object vertices {obj.name} [alpha={alpha}]")
    color_polygons(obj, values=scale_values, alpha=alpha)


def color_object(obj, lines, scale=[0, 1], alpha=1.0):
    attr_name = "probe_result"

    # Explode the mesh object to individual faces
    explode_polygons_to_mesh(obj)

    # Set a custom property that tags the object type
    field_type = "vector" if len(lines[0].split()) > 4 else "scale"
    obj["probe_field_type"] = field_type

    # Get the face values as vectors
    logger.info(f"Converting strings to points and values [scale={scale}]")
    point_values = [point_and_value_vectors(line) for line in lines]
    logger.info(f"Got points and values for {len(point_values)}")

    # Match the points to the polygon centers (because openfoam crops them out)
    logger.info("Mapping points and values to polygon centers")
    face_values = map_to_polygons(obj, point_values)
    logger.info("Done mapping points and values to polygon centers")

    # Get the values in the strings as floats
    logger.info(f"Setting face attributes {attr_name} on object: {obj.name}")
    obj.data.attributes.new(name=attr_name, type='FLOAT_VECTOR', domain='FACE')
    obj.data.attributes[attr_name].data.foreach_set(
        'vector', _flatten(face_values))
    logger.info(f"Done setting raw face attributes")

    # Color the vertices from raw values set as face attributes
    color_vertices_from_face_attr(
        obj, alpha=alpha, scale=scale, attr_name=attr_name)
    logger.info(f"Done coloring object")
