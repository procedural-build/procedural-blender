###########################################################
# Blender Modelling Environment for Architecture
# Copyright (C) 2011, ods-engineering
# License : ods-engineering license
# Version : 1.2
# Web     : www.ods-engineering.com
###########################################################

import bpy

from math import pi
from mathutils import Vector

from ..utils.octree import Octree

import logging
logger = logging.getLogger(__name__)

def get_object_axes(obj):
    Nv = len(obj.data.vertices)
    M = obj.matrix_world
    X = M*obj.data.vertices[1].co - M*obj.data.vertices[0].co
    Xlen = X.length
    for i in range(2, Nv):
        e2 = M*obj.data.vertices[i].co - M*obj.data.vertices[0].co
        Z = X.cross(e2)
        if Z.length > (Xlen*1e-2):
            X.normalize()
            Z.normalize()
            Y = (X.cross(Z)).normalized()
            return (X,Y,Z)
        else:
            continue
    return None

def polygon_vertices_edges(obj, edges, left_list, octree):
    logger.info(f"Making fill object from object: {obj.name} with {len(edges)} out of {len(obj.data.edges)} edges")

    # Get the list of vertices started
    vertIndexList = [obj.data.edges[edges[0]].key[i] for i in range(2)]
    if not left_list[0]:
        vertIndexList.reverse()

    # Now add the vertices as we move around the edges
    for i in range(1, len(edges)-1):
        keyIndex = int(left_list[i])
        vertIndexList.append( obj.data.edges[edges[i]].key[keyIndex] )

    # Now get the list of actual coordinates and edge-indices
    vList = [octree.global_vertex_cos[obj.name][i] for i in vertIndexList]
    eList = [ (i,i+1) for i in range(len(vertIndexList)-1) ] + [(len(vertIndexList)-1,0)]

    return {
        "vertices": vList,
        "edges": eList
    }


def edge_loop_polygons(obj):
    logger.info(f"Running fill and separate on object: {obj.name}")
    # Build the octree that will be used for searching
    octree = Octree(edges=True)
    octree.max_vertices_per_box = 1
    octree.build_tree([obj])

    # Get global vertex coordinates in terms of planar (xy) coordinates
    #A = get_object_axes(o)
    #xy_axes = [ Vector( ( v.dot(A[0]), v.dot(A[1]) ) ) for v in octree.globalVertCoords[obj.name] ]

    # Actually - Just use the global x-y axes for now - surfaces must be horizontal (or close to horizontal)
    xy_axes = [ Vector( ( v[0], v[1] ) ) for v in octree.global_vertex_cos[obj.name] ]

    # Set up a left and right search list (2d analogy of findZones)
    leftSearchList = [e.index for e in obj.data.edges]
    rightSearchList = [e.index for e in obj.data.edges]

    # Now start searching edges
    nLoops = 0
    loopList = []
    N = len(leftSearchList)
    for i in range(2*N):
        # Get the current edge under consideration
        if i < N:
            edge = leftSearchList[i]
            searchLeft = True
        else:
            edge = rightSearchList[i-N]
            searchLeft = False

        # If we have already traced this side of this object then skip searching from here
        if edge < 0:
            continue

        # Find the connected edges
        #logger.info('Searching from edge: {edge}')
        (edgeList, leftList, makesLoop, avAngle) = get_connected(obj, edge, octree, xy_axes, searchLeft)

        # If we have found a loop then make a new object that fills it
        if makesLoop and (avAngle < pi):
            loopList.append( [edgeList, leftList] )
            nLoops += 1

        # Remove searched edges from search lists
        for i in range(len(edgeList)):
            e = edgeList[i]
            if leftList[i]:
                leftSearchList[e] = -1
            else:
                rightSearchList[e] = -1

    # Create the filled objects
    logger.info(f'Making filled objects in {nLoops} loops from object {obj.name}...')
    return [polygon_vertices_edges(obj, loop[0], loop[1], octree) for loop in loopList]


def min_connected_edge(obj, edgeIndex, octree, xy_axes, left=True):
    k1 = int(left)
    k0 = int(not left)

    oneDegree = pi/180.0
    edgeKey = obj.data.edges[edgeIndex].key
    edgeVector = xy_axes[edgeKey[k1]] - xy_axes[edgeKey[k0]]
    edgeYaxis = Vector( ( -1.0*edgeVector[1], edgeVector[0] ) )
    searchVert = obj.data.vertices[edgeKey[k1]]

    candidateEdges = octree.vertex_edges( obj.name, searchVert )
    minAngle = 10.0
    minEdgeIndex = -1
    minPointsAway = True
    for ce in candidateEdges:
        # Don't consider the current edges
        if ce.index == edgeIndex:
            continue

        # Make sure that these edges are actually connected
        if not edgeKey[k1] in ce.key:
            continue

        # Check if the edge is pointing towards this vertex
        pointsAway = True
        if not ce.key[0] == edgeKey[int(left)]:
            pointsAway = False
        c1 = int(pointsAway)
        c0 = int(not pointsAway)

        # Get the angle between the two edges
        ceVector = xy_axes[ce.key[c1]] - xy_axes[ce.key[c0]]
        angle = edgeVector.angle(ceVector)
        if edgeYaxis.dot(ceVector) > 0.0:
            angle = -1.0*angle

        # Check the angle and set minimums
        if (angle < minAngle) and (abs(abs(angle)-pi) > oneDegree):
            minAngle = angle
            minEdgeIndex = ce.index
            minPointsAway = pointsAway

    return minEdgeIndex, minPointsAway, (minAngle+pi)

def get_connected(obj, edge, octree, xy_axes, searchLeft=True):
    edgeList = [edge]
    leftList = [searchLeft]
    avAngle = 0.0
    nAngles = 0
    for i in range(len(obj.data.edges)):
        (minEdgeIndex, isLeftSide, angle) = min_connected_edge(obj, edgeList[-1], octree, xy_axes, left=leftList[-1])

        if (minEdgeIndex < 0):
            return (edgeList, leftList, False, avAngle)
        elif (minEdgeIndex == edgeList[0]):
            avAngle += angle;
            nAngles += 1
            return (edgeList, leftList, True, avAngle/nAngles)
        else:
            avAngle += angle
            nAngles += 1
            edgeList.append( minEdgeIndex )
            leftList.append( isLeftSide )

    return (edgeList, leftList, False, avAngle/nAngles)
