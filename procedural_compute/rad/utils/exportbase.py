###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy
import os
from math import pi, tan, atan2

from procedural_compute.sun.utils.timeFrameSync import getTimeStamp
from procedural_compute.rad.utils.radUtils import formatName

class ExportBase():

    def __init__(self):
        self.materialsList = []
        self.references = []
        self.views = []
        return None

    def getFilename(self,s):
        sc = bpy.context.scene
        return bpy.path.abspath("%s/%s"%(sc.RAD.caseDir, s))

    def createDir(self,dirpath):
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        return None

    def createFile(self,filename, text):
        # Make holding directory if it does not exist
        (path,name) = os.path.split(filename)
        if not os.path.exists(path):
            os.makedirs(path)
        # Write the file and text
        f = open(filename, 'w')
        f.write(text)
        f.close()
        return None

    def prependFile(self, infile, text, outfile):
        f = open(infile)
        orgtext = f.read()
        f.close()
        f = open(outfile, 'w')
        f.write(text)
        # write the original contents
        f.write(orgtext)
        f.close()
        return

    def faceToTriangles(self, face):
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

    def triString(self, tri, matname, obj_name, index):
        text = "\n%s polygon %s_face-%d\n"%(matname, obj_name, index)
        text += "0\n0\n%i\n" %(len(tri)*3)
        for v in tri:
            text += "    %f  %f  %f\n"%(v[0], v[1], v[2])
        return text

    def writeTriangles(self, obj, matname):
        if not obj.type == 'MESH':
            return ""

        if len(obj.data.polygons) == 0:
            return ''

        # Get mesh in global coordinates
        try:
            me = obj.to_mesh()
        except RuntimeError:
            return ""

        me.transform(obj.matrix_world)
        vertices = me.vertices

        poly_text = ''
        index = 0
        me.calc_loop_triangles()
        for face in me.loop_triangles:
            face_vertex_coords = [vertices[index].co.copy() for index in face.vertices]
            tris = self.faceToTriangles(face_vertex_coords)

            # Write faces to text
            for tri in tris:
                poly_text += self.triString(tri, matname, obj.name, index)
                index += 1
        return poly_text

    def exportObject(self, obj, matname="ods_default_material"):
        # Get text to write for triangulated face of each object
        text = self.writeTriangles(obj, formatName(matname))
        filename = self.getFilename('objects/%s.rad'%(obj.name))
        self.createFile(filename, text)
        return None

    def exportmesh(self, obj):
        ## split all selected MESH objects in the scene to individual files
        if not obj.type == 'MESH':
            return None
        if len(obj.data.polygons) == 0:
            return None
        # Get object material name
        # TODO: Change the exporting here to handle two-sided materials
        if len(obj.material_slots) > 0:
            matname = obj.material_slots[0].name
            material = bpy.data.materials[matname]
            if not matname in self.materialsList:
                self.materialsList.append(matname)
        else:
            matname = "ods_default_material"
        # Write triangulated faces of object
        self.exportObject(obj, matname)
        # Create a reference for later xform fields
        self.references.append("!xform -n %s ./objects/%s.rad"%(obj.name,obj.name))
        return None

    def getFoVAngle(self, ang1, side1, side2):
        ang1_rad = ang1*pi/180
        dist = side1 / (2.0*tan(ang1_rad/2.0))
        ang2_rad = 2 * atan2(side2/(2*dist), 1)
        ang2 = (ang2_rad*180.0)/pi
        return ang2

    def createViewFile(self, c, viewname):
        sc = bpy.context.scene

        v = c.location.copy()
        v[0]=0.0;v[1]=0.0;v[2]=-1.0
        vd = c.matrix_world.to_3x3() * v
        v[0]=0.0;v[1]=1.0;v[2]=0.0
        vu = c.matrix_world.to_3x3() * v

        text = " -vp %.3f %.3f %.3f  "%(c.location[0],c.location[1],c.location[2])
        text += " -vd %.3f %.3f %.3f  "%(vd[0], vd[1], vd[2])
        text += " -vu %.3f %.3f %.3f  "%(vu[0], vu[1], vu[2])
        imgW = sc.render.resolution_x
        imgH = sc.render.resolution_y
        aspect = imgW/imgH
        if c.data.type == 'PERSP':
            vtype = '-vtv'
            if aspect > 1.0:
                vh = c.data.angle*180/pi
                vv = self.getFoVAngle(vh, imgW, imgH)
            else:
                vv = c.data.angle*180/pi
                vh = self.getFoVAngle(vv, imgH, imgW)
        else:
            vtype = '-vtl'
            if imgW > imgH:
                vh = c.data.ortho_scale
                vv = vh*imgH/imgW
            else:
                vv = c.data.ortho_scale
                vh = vv*imgW/imgH
        text += "-vv %.3f -vh %.3f" %(vv, vh)
        text = "rvu " + vtype + " " + text

        filename = self.getFilename("views/%s.vf"%viewname)
        self.createFile(filename, text)
        return viewname, "views/%s.vf"%viewname

    def exportcamera(self, obj):
        if not obj.type == "CAMERA":
            return None
        if obj.procedural_compute.rad.radiance or obj.procedural_compute.rad.irrad:
            (viewname,viewfile) = self.createViewFile(obj, "%s_%s"%(getTimeStamp(), obj.name))
            if obj.procedural_compute.rad.radiance:
                self.views.append("view=   %s -vf %s"%(viewname, viewfile))
            if obj.procedural_compute.rad.irrad:
                self.views.append("view=   irrad_%s -vf %s -i"%(viewname, viewfile))
        return None

    def exportSelectedObjects(self, skipNone=True):
        self.materialsList = []
        self.references = []
        self.views = []
        for obj in bpy.context.visible_objects:
            if len(obj.material_slots) > 0:
                matname = obj.material_slots[0].name
                material = bpy.data.materials[matname]
                if skipNone and material.RAD.type == "None":
                    continue
            expdef = 'export%s'%(obj.type.lower())
            if hasattr(self, expdef):
                getattr(self, expdef)(obj)
        return None
