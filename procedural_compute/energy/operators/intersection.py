from procedural_compute.energy.utils.octree import Octree
from mathutils.geometry import intersect_line_line
from math import pi


def pydata_from_intersections(objects):
    # Build an octree for faster searching
    octree = Octree(edges=True, faces=False, along_edges=True)
    octree.max_vertices_per_box = 10
    octree.max_edges_per_box = 10
    octree.build_tree(objects)

    vertices = []
    edges = []

    for obj in objects:
        (_vertices, _edges) = split_object_edges_at_intersections(
            obj, octree,
            init_edge_index=len(vertices)
        )
        vertices += _vertices
        edges += _edges

    return {"vertices": vertices, "edges": edges}

def split_edge_at_intersections(obj, edge, octree, init_edge_index=0):
    # Get the global edge endpoints
    p1 = octree.global_vertex_cos[obj.name][edge.key[0]]
    p2 = octree.global_vertex_cos[obj.name][edge.key[1]]

    #  Find points of intersection with other edges (octree boxes)
    boxes = octree.master_box.get_edge_boxes(p1, p2)

    # Get all the other edges that are in these boxes
    nearby_edges = list_edge_keys(boxes) #, obj.name)
    intersection_points = [p1, p2]
    for [edge_obj_name, edge_indices] in nearby_edges:
        e1 = octree.global_vertex_cos[edge_obj_name][edge_indices[0]]
        e2 = octree.global_vertex_cos[edge_obj_name][edge_indices[1]]
        intersection_point = lines_intersect(p1, p2, e1, e2)
        if not intersection_point:
            continue
        intersection_points.append( intersection_point )

    # The vertices of the edge with splits all along it.
    vertices = sorted(intersection_points, key=lambda v: (v-p1).length)
    edges = [((init_edge_index + i), (init_edge_index + i + 1)) for i in range(len(vertices)-1)]

    return (vertices, edges)


def split_object_edges_at_intersections(obj, octree, init_edge_index=0):
    vertices = []
    edges = []
    for edge in obj.data.edges:
        (_vertices, _edges) = split_edge_at_intersections(
            obj, edge, octree,
            init_edge_index=init_edge_index + len(vertices)
        )
        vertices += _vertices
        edges += _edges
    return (vertices, edges)


def point_on_line(p, p1, p2):
    L = (p-p1).dot((p2-p1).normalized())
    pL = (p2-p1).length
    # Return true if the point is on an end
    if abs(L) < 1e-3:
        return True
    if abs(L-pL) < 1e-3:
        return True
    # Return false if it is out of bounds
    if L > pL:
        return False
    if L < 0.0:
        return False
    return True

def lines_intersect(p1,p2,e1,e2):
    # First check that lines are not co-linear
    ang = (e2-e1).angle(p2-p1)
    if ang < 1e-2 or abs(abs(ang)-pi) < 1e-2:
        return False
    # If they are not then find their intersection
    (i1,i2) = intersect_line_line(p1,p2,e1,e2)

    # Check that the lines do actually intersect
    if (i2-i1).length > 1e-3:
        return False
    else:
        p = (i1 + i2)*0.5

    # Check that the point is somewhere along the lines
    if not (point_on_line(p,p1,p2) and point_on_line(p,e1,e2)):
        return False

    # Otherwise just return the intersection point
    return p

def list_edge_keys(boxes): #, excObj):
    edgeList = set()
    for box in boxes:
        for o in box.objects:
            for e in box.objects[o].edges:
                edgeList.add( (o, e.key) )
    return list(edgeList)
