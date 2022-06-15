###########################################################
# Blender Modelling Environment for Architecture
# Copyright (C) 2011, ods-engineering
# License : ods-engineering license
# Version : 1.2
# Web     : www.ods-engineering.com
###########################################################

"""
Generate an octree of blender mesh data to speed up searching for
edges and faces that are connected to vertices and edges (upward search)

Required for some complex search algorithms that would be O(N^2) like
concave hull searching.

"""

from mathutils import Vector
from random import random

import logging
logger = logging.getLogger(__name__)


class ObjectElements():

    def __init__(self):
        self.vertices = []
        self.edges = []
        self.faces = []

class OctreeBox():

    def __init__(self, tree, center=(0.0,0.0,0.0), length=0.0, level=0):
        self.center = Vector(center)
        self.length = length
        self.level = level
        self.objects = {}
        self.treeVertListIndex = []
        self.children = [None]*8
        self.tree = tree
        self.hasChildren = False

    def add_child(self, index):
        c = self.center.copy()
        A = self.index_to_list(index)
        c = [c[i] + (A[i]*2-1)*self.length/4.0 for i in range(3)]
        self.children[index] = OctreeBox(self.tree, center=c, length=self.length/2.0, level=self.level+1)

    def index_to_list(self, index):
        ilist = [False, False, False]
        for i in range(3):
            c = 2**(2-i)
            if index >= c:
                ilist[i] = True
                index -= c
        return ilist

    def split(self):
        # Add children of this box
        for i in range(8):
            self.add_child(i)
        self.hasChildren = True
        # Give the elements from this box to the children and pop from this box
        for obj_name in self.objects:
            for v in self.objects[obj_name].vertices:
                gCo = self.tree.global_vertex_cos[obj_name][v.index]
                childIndex = self.get_child_index(gCo)
                self.children[childIndex].add_vertex(obj_name, v)
            # Give the edges from this box to the children
            #pdb.set_trace()
            for e in self.objects[obj_name].edges:
                gCo1 = self.tree.global_vertex_cos[obj_name][e.key[0]]
                gCo2 = self.tree.global_vertex_cos[obj_name][e.key[1]]
                childIndexes = self.get_edge_child_indexes(gCo1, gCo2)
                for c in childIndexes:
                    self.children[c].add_edge(obj_name, e)
        # Clear this box dictionary of object data
        self.objects.clear()
        return

    def get_child_index(self, p):
        # The bool(int()) statement ensures nothing is greater than one (just in case)
        index = [ (p[i] - self.center[i]) >= 0.0 for i in range(3)]
        return sum([index[i]*(2**(2-i)) for i in range(3)])

    def get_edge_child_indexes(self, p1, p2):
        # Get children quadrants
        q1 = self.get_child_index(p1)
        q2 = self.get_child_index(p2)
        # If both ends of the edge are in one child
        if q1 == q2:
            return [q1]
        # Now do a more rigorous check of all children box-intersections
        childrenIntersected = []
        for ci in range(8):
            child = self.children[ci]
            if child.intersects_line(p1, p2):
                childrenIntersected.append(ci)
        return childrenIntersected

    def intersects_line(self, p1, p2, stopAt=1):
        N = 0
        pointList = [Vector() for i in range(2)]
        for axis in range(3):
            for plane in [-1, 1]:
                p = self.intersect_line_plane(axis, (self.center[axis]+(plane*self.length/2.0)), p1, p2)
                if p == False:
                    continue
                if self.point_on_face(p, axis):
                    pointList[N] = p
                    N += 1
                    if N >= stopAt:
                        return pointList
        return False

    def point_on_face(self, p, axis):
        halfL = self.length/2.0
        for a in [-1, -2]:
            if not abs(p[axis+a]-self.center[axis+a]) < halfL:
                return False
        return True

    def intersect_line_plane(self, axis, plane, p1, p2):
        if (p1[axis]>plane)==(p2[axis]>plane):
            return False
        r = (plane - p1[axis])/(p2[axis] - p1[axis])
        return r*(p2-p1) + p1

    def get_point_box(self, p):
        # If this box has children then return from that box
        if self.hasChildren:
            childIndex = self.get_child_index(p)
            return self.children[childIndex].get_point_box(p)
        # Otherwise return this box
        return self

    def get_edge_boxes(self, p0, p1):
        # If this box has children then get the children that the line passes through
        bList = []
        if self.hasChildren:
            childIndexes = self.get_edge_child_indexes(p0,p1)
            for ci in childIndexes:
                bList += self.children[ci].get_edge_boxes(p0, p1)
            return bList
        # Otherwise append this box to the boxList and return
        return [self]

    def add_vertex(self, obj_name, vertex):
        # If there are children then recursively drop into them
        if self.hasChildren:
            gCo = self.tree.global_vertex_cos[obj_name][vertex.index]
            childIndex = self.get_child_index(gCo)
            self.children[childIndex].add_vertex(obj_name, vertex)
            return
        # Otherwise just add the vertex to this box
        if not obj_name in self.objects:
            self.objects[obj_name] = ObjectElements()
        self.objects[obj_name].vertices.append(vertex)
        # If there are too many vertices or edge in this box then
        # split this box and distribute points to children
        if (self.length/2.0 < self.tree.min_box_size):
            return
        if (self.n_vertices>self.tree.max_vertices_per_box) or (self.n_edges>self.tree.max_edges_per_box):
            self.split()
        return

    def add_edge(self, obj_name, edge):
        # If there are children then recursively drop into them
        if self.hasChildren:
            gCo1 = self.tree.global_vertex_cos[obj_name][edge.key[0]]
            gCo2 = self.tree.global_vertex_cos[obj_name][edge.key[1]]
            childIndexes = self.get_edge_child_indexes(gCo1, gCo2)
            for ci in childIndexes:
                self.children[ci].add_edge(obj_name, edge)
            return
        # Otherwise just add the edge to this box
        if not obj_name in self.objects:
            self.objects[obj_name] = ObjectElements()
        self.objects[obj_name].edges.append(edge)
        # If there are too many vertices or edge in this box then
        # split this box and distribute points to children
        if (self.length/2.0 < self.tree.min_box_size):
            return
        if (self.n_vertices>self.tree.max_vertices_per_box) or (self.n_edges>self.tree.max_edges_per_box):
            self.split()
        return

    def add_edge_at_verts(self, obj_name, edge):
        for vi in edge.key:
            gCo = self.tree.global_vertex_cos[obj_name][vi]
            box = self.get_point_box(gCo)
            box.objects[obj_name].edges.append(edge)
        return

    def add_face_at_verts(self, obj_name, face):
        s = set()
        # Get set of unique vertex indices of this face
        for ei in face.edge_keys:
            for vi in ei:
                s.add(vi)
        # Add a pointer to this face in each vertex octree-box
        for vi in s:
            gCo = self.tree.global_vertex_cos[obj_name][vi]
            box = self.get_point_box(gCo)
            box.objects[obj_name].faces.append(face)
        return

    def add_edge_at_edge(self, obj_name, edge):
        e = edge.key
        v0 = self.tree.global_vertex_cos[obj_name][e[0]]
        v1 = self.tree.global_vertex_cos[obj_name][e[1]]
        boxes = self.get_edge_boxes(v0,v1)
        for box in boxes:
            if not obj_name in box.objects:
                box.objects[obj_name] = ObjectElements()
            if not edge in box.objects[obj_name].edges:
                box.objects[obj_name].edges.append(edge)
        return

    def add_face_at_edges(self, obj_name, face):
        for e in face.edge_keys:
            v0 = self.tree.global_vertex_cos[obj_name][e[0]]
            v1 = self.tree.global_vertex_cos[obj_name][e[1]]
            boxes = self.get_edge_boxes(v0,v1)
            for box in boxes:
                if not obj_name in box.objects:
                    box.objects[obj_name] = ObjectElements()
                if not face in box.objects[obj_name].faces:
                    box.objects[obj_name].faces.append(face)
        return

    @property
    def n_vertices(self):
        return sum([len(o.vertices) for o in self.objects.values()])

    @property
    def n_edges(self):
        return sum([len(o.edges) for o in self.objects.values()])

class Octree():

    def __init__(self, edges=False, faces=False, along_edges=False):
        self.include_edges = edges
        self.include_faces = faces
        self.along_edges = along_edges
        self.global_vertex_cos = {}
        self.master_box = OctreeBox(self)
        self.max_vertices_per_box = 3
        self.max_edges_per_box = 2
        self.min_box_size = 0.01

    def vertex_edges(self, obj_name, vertex):
        gCo =  self.global_vertex_cos[obj_name][vertex.index]
        box = self.master_box.get_point_box(gCo)
        return [edge for edge in box.objects[obj_name].edges if vertex.index in edge.key]

    def vertex_objects(self, obj_name, vertex):
        global_coordinate =  self.global_vertex_cos[obj_name][vertex.index]
        box = self.master_box.get_point_box(global_coordinate)
        return [o for o in box.objects if o != obj_name]

    def resize_master_box(self):
        # Intialize the min and max vectors from the first vertex we can find
        min_vector = self.global_vertex_cos[list(self.global_vertex_cos.keys())[0]][0].copy()
        max_vector = self.global_vertex_cos[list(self.global_vertex_cos.keys())[0]][0].copy()
        objects = self.master_box.objects
        for obj_name in objects:
            for v in objects[obj_name].vertices:
                vco = self.global_vertex_cos[obj_name][v.index]
                for i in range(3):
                    if vco[i] < min_vector[i]:
                        min_vector[i] = vco[i]
                    if vco[i] > max_vector[i]:
                        max_vector[i] = vco[i]
        # Set the size of the box (randomly up to 5% bigger than needed to avoid edge-alignment errors)
        tightLength = max(max_vector - min_vector)
        addLength = tightLength*(random()*0.025)
        self.master_box.center = (max_vector + min_vector)/2.0 + Vector([(random()-0.5)*addLength for i in range(3)])
        self.master_box.length = tightLength + addLength*2.0
        return

    def build_tree(self, obs):
        # Add object vertices to tree
        for o in obs:
            matrix = o.matrix_world

            # Create a new container for the object element data
            self.global_vertex_cos[o.name] = []
            self.master_box.objects[o.name] = ObjectElements()

            # Add object vertex data to master box
            for v in o.data.vertices:
                self.master_box.objects[o.name].vertices.append( v )
                # Store global coordinate data in this root tree object for use later
                # (to save doing lots of obj.matrix * v.co )
                self.global_vertex_cos[o.name].append( matrix @ v.co )

            # Add object edge data to master box
            if self.along_edges:
                for e in o.data.edges:
                    self.master_box.objects[o.name].edges.append( e )

        # Redefine master box to surround all added vertices
        self.resize_master_box()

        # Split the master-box : this is recursive and generates the tree
        if self.master_box.n_vertices > self.max_vertices_per_box:
            self.master_box.split()

        # Add edge and face information to the octree if desired (only at vertex box points)
        if self.include_edges and not self.along_edges:
            for o in obs:
                for e in o.data.edges:
                    self.master_box.add_edge_at_verts(o.name, e)

        if self.include_faces and not self.along_edges:
            for o in obs:
                for f in o.data.polygons:
                    self.master_box.add_face_at_verts(o.name, f)

        if self.include_edges and self.along_edges:
            for o in obs:
                for e in o.data.edges:
                    self.master_box.add_edge_at_edge(o.name, e)

        if self.include_faces and self.along_edges:
            for o in obs:
                for f in o.data.polygons:
                    self.master_box.add_face_at_edges(o.name, f)

        return None
