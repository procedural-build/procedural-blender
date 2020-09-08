###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

from procedural_compute.core.utils.addRemoveMeshObject import addObject

import procedural_compute.sun.utils.suncalcs as suncalcs
import procedural_compute.sun.properties.scene
from procedural_compute.sun.utils import timeFrameSync

# Record keepers to work out if time or frame has changed
global oldFrameNum, oldHour, oldMinute
oldFrameNum = 0; oldHour = 0; oldMinute = 0


################################
# GENERIC SOLAR PATH OPERATORS
################################
class SCENE_OT_calcSolarPath(bpy.types.Operator):
    bl_label = "Calculate Solar Path"
    bl_idname = "scene.calcsolarpath"
    bl_description = "Apply Solar Path to Selected Object"

    def invoke(self, context, event):
        self.execute(context)
        return{'FINISHED'}

    def execute(self, context):
        ob = context.active_object
        suncalcs.applySolarAzElCurves(ob)
        return{'FINISHED'}

bpy.utils.register_class(SCENE_OT_calcSolarPath)


class calcClockHandRotation(bpy.types.Operator):
    bl_label = "Calculate Clock Hand Rotation"
    bl_idname = "scene.calcclockhandrotation"
    bl_description = "Calculate Minute and Hour Hand Rotations for Selected Objects"

    def invoke(self, context, event):
        self.execute(context)
        return{'FINISHED'}

    def execute(self, context):
        sc = context.scene
        obs = context.selected_objects
        if len(obs) == 0:
            self.report({'ERROR'}, 'No objects selected!')
            return{'FINISHED'}
        # Get the minute and hour hand objects
        hasMinuteHand = False
        hasHourHand = False
        for o in obs:
            if "minuteHand" in o.name:
                print("Found minuteHand")
                m = o
                hasMinuteHand = True
            elif "hourHand" in o.name:
                print("Found hourHand")
                h = o
                hasHourHand = True
        # Calculate the positions
        dt = sc.procedural_compute.sun.solarDT
        for Hour in range(24):
            for T in range(dt):
                Minute = T*(60/dt)
                sc.frame_set( timeFrameSync.timeToFrame(Hour, Minute) )
                if hasMinuteHand:
                    rotMin = -1.0*(Minute/60.0)*2.0*3.14159265
                    m.rotation_euler = [0.0, 0.0, rotMin]
                    m.keyframe_insert("rotation_euler")
                if hasHourHand:
                    rotHr = -1.0*(Hour/12.0)*2.0*3.14159265 + rotMin/12.0
                    h.rotation_euler = [0.0, 0.0, rotHr]
                    h.keyframe_insert("rotation_euler")
        return{'FINISHED'}

bpy.utils.register_class(calcClockHandRotation)

################################
# ADD MESH OBJECTS
################################

class addClock(bpy.types.Operator):
    bl_idname = "mesh.add_clock"
    bl_label = "Add Clock"

    def execute(self, context):
        # Deselect everything before adding the new objects
        sc = context.scene
        for ob in sc.objects:
            ob.select = False
        # Add a triangle and line
        clockObj = addObject("clockFace",vlist=[],elist=[])
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.primitive_circle_add(vertices=12, location=(0, 0, 0), rotation=(0, 0, 0))
        bpy.ops.mesh.delete(type='EDGE_FACE')
        bpy.ops.mesh.extrude_vertices_move()
        bpy.ops.transform.resize(value=(0.8,0.8,0.8))
        bpy.ops.mesh.primitive_circle_add(vertices=36, location=(0, 0, 0), rotation=(0, 0, 0))
        bpy.ops.object.mode_set(mode = 'OBJECT')
        minuteHand = addObject("minuteHand",vlist=[[0.0,0.0,0.0],[0.0,0.9,0.0]],elist=[[0,1]])
        minuteHand.parent = clockObj
        hourHand = addObject("hourHand",vlist=[[0.0,0.0,0.0],[0.0,0.5,0.0]],elist=[[0,1]])
        hourHand.parent = clockObj
        # Set clock object as active
        sc.objects.active = clockObj
        # Synchronize the clock hands
        bpy.ops.scene.calcclockhandrotation()
        return{'FINISHED'}

bpy.utils.register_class(addClock)
