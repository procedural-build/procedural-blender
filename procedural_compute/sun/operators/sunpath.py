###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

import bpy
import bgl
import blf

from math import radians, pi, cos, sin
from procedural_compute.sun.utils.suncalcs import Solar_Pos, azElToXYZ, azElToPolar
from procedural_compute.sun.utils.timeFrameSync import frameToTime
import datetime

points = [[(0,0,0)]*24*4]*365
daylines = [[(0,0,0)]*24*4]*12
loops = [[(0,0,0)]*365]*24

def draw_sunpath_callback(self, context):

    def drawLine(points, loop=False, color=(0.1, 0.4, 0.8, 0.8), thickness=2):
        bgl.glLineWidth(thickness)
        bgl.glBlendColor(color[0], color[1], color[2], color[3])
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for p in points:
            bgl.glVertex3f(p[0], p[1], p[2])
        if loop:
            p = points[0]
            bgl.glVertex3f(p[0], p[1], p[2])
        bgl.glEnd()
        return points

    def dayPoints(Month, Day):
        sc = bpy.context.scene
        N = sc.Site.northAxis
        Long = sc.Site.longitude
        Lat = sc.Site.latitude
        TimeZone = sc.Site.timezone
        dt = 4 # timesteps per hour
        coords = [(0.0,0.0,0.0)]*(24*dt)
        i = 0
        for Hour in range(24):
            for T in range(dt):
                Minute = T*(60/dt)
                (Az, El) = Solar_Pos(Long, Lat, TimeZone, Month, Day, Hour, Minute)
                if sc.ODS_SUN.sunpath.flat:
                    if sc.ODS_SUN.sunpath.equi:
                        coords[i] = azElToPolar(radians(Az)+N, radians(El))
                    else:
                        coords[i] = azElToXYZ(radians(Az)+N, radians(El))
                        coords[i][2] = 0.0
                else:
                    coords[i] = azElToXYZ(radians(Az)+N, radians(El))
                # Finally shift the coordinate to the offset centre
                for j in range(3):
                    coords[i][j] += sc.ODS_SUN.sunpath.pos[j]
                i += 1
        return coords

    def drawCompassRose(color=(0.8,0.8,0.8,1.0)):
        def tick(ang,f):
            X = sin(ang); Y = cos(ang);
            return [(R*X+O[0], R*Y+O[1], O[2]), (R*f*X+O[0], R*f*Y+O[1], O[2])]
        sc = bpy.context.scene
        R = sc.ODS_SUN.arcRadius
        N = sc.Site.northAxis
        O = sc.ODS_SUN.sunpath.pos
        T = [N+(i*2*pi/360) for i in range(360)]
        # Draw inner concentric circles
        if sc.ODS_SUN.sunpath.circles:
            for i in range(1,9):
                if sc.ODS_SUN.sunpath.flat and sc.ODS_SUN.sunpath.equi:
                    r = (i*R/9)
                else:
                    r = R*sin((pi/2)*(i/9))
                P = [(r*sin(t)+O[0], r*cos(t)+O[1], O[2]) for t in T]
                drawLine(P, loop=True, color=color, thickness=0.7)
        # Draw the thick outer circle (90 degrees)
        P = [(R*sin(t)+O[0], R*cos(t)+O[1], O[2]) for t in T]
        drawLine(P, loop=True, color=color)
        # Draw the ticks
        drawLine(tick(N,1.2), color=color)
        for i in range(8):
            T = N+(i*2*pi/8)
            drawLine(tick(T,1.1), color=color)
        for i in range(36):
            T = N+(i*2*pi/36)
            drawLine(tick(T,1.05), color=color)
        return

    def calcSunPath():
        datum = datetime.datetime(2010,1,1)
        for day in range(365):
            t = datum + datetime.timedelta(day)
            dp = dayPoints(t.month, t.day)
            points[day] = dp
            if t.day == 1:
                daylines[t.month-1] = dp
        for i in range(0,24):
            loops[i] = [points[day][i*4] for day in range(365)]
        return None

    def getTextLocation():
        context = bpy.context
        scene = bpy.context.scene
        X = 62; Y = 4;
        pos_x = int( (context.region.width ) - X)
        pos_y = int( Y ) #(context.region.height)
        return(pos_x, pos_y)

    def drawTime():
        font_size = 20
        (r,g,b,alpha)=(1.0,1.0,1.0,1.0)
        blf.size(0, font_size, 72)
        (pos_x, pos_y) = getTextLocation()
        blf.position(0, pos_x, pos_y , 0)
        bgl.glBlendColor(r, g, b, alpha)
        (hour,minute) = frameToTime(bpy.context.scene.frame_current)
        if hour >= 24:
            minute = 0
        blf.draw(0, "%02i:%02i"%(min(hour,24),minute))
        return None

    def drawSunPath():
        for line in daylines:
            drawLine(line)
        for line in loops:
            drawLine(line, loop=True, color=(1.0,0.8,0.0,1.0))
        drawCompassRose()
        return None

    # Draw the time
    if bpy.context.scene.ODS_SUN.sunpath.time:
        drawTime()

    if not bpy.context.scene.ODS_SUN.sunpath.path:
        return None

    # Get & convert the Perspective Matrix of the current view/region.
    #bgl.glClear(bgl.GL_COLOR_BUFFER_BIT)
    view3d = bpy.context
    region = view3d.region_data
    perspMatrix = region.perspective_matrix
    tempMat = [perspMatrix[j][i] for i in range(4) for j in range(4)]
    perspBuff = bgl.Buffer(bgl.GL_FLOAT, 16, tempMat)

    # ---
    # Store previous OpenGL settings.
    # Store MatrixMode
    MatrixMode_prev = bgl.Buffer(bgl.GL_INT, [1])
    bgl.glGetIntegerv(2976, MatrixMode_prev)  # bgl.GL_MATRIX_MODE
    MatrixMode_prev = MatrixMode_prev[0]

    # Store projection matrix
    ProjMatrix_prev = bgl.Buffer(bgl.GL_DOUBLE, [16])
    bgl.glGetFloatv(2983, ProjMatrix_prev)  # bgl.GL_PROJECTION_MATRIX

    # Store Line width
    lineWidth_prev = bgl.Buffer(bgl.GL_FLOAT, [1])
    bgl.glGetFloatv(bgl.GL_LINE_WIDTH, lineWidth_prev)
    lineWidth_prev = lineWidth_prev[0]

    # Store GL_BLEND
    blend_prev = bgl.Buffer(bgl.GL_BYTE, [1])
    bgl.glGetFloatv(bgl.GL_BLEND, blend_prev)
    blend_prev = blend_prev[0]

    line_stipple_prev = bgl.Buffer(bgl.GL_BYTE, [1])
    bgl.glGetFloatv(2852, line_stipple_prev)  # bgl.GL_LINE_STIPPLE
    line_stipple_prev = line_stipple_prev[0]

    # Store glColor4f
    color_prev = bgl.Buffer(bgl.GL_FLOAT, [4])
    bgl.glGetFloatv(bgl.GL_COLOR, color_prev)

    # ---
    # Prepare for 3D drawing
    bgl.glLoadIdentity()
    bgl.glMatrixMode(5889)  # bgl.GL_PROJECTION
    bgl.glLoadMatrixf(perspBuff)

    bgl.glEnable(bgl.GL_BLEND)
    bgl.glEnable(bgl.GL_LINE_SMOOTH)
    #bgl.glEnable(bgl.GL_LINE_STIPPLE)
    if not bpy.context.scene.ODS_SUN.sunpath.xray:
        bgl.glEnable(bgl.GL_DEPTH_TEST)

    # Draw the day sunpath lines
    if bpy.context.scene.ODS_SUN.sunpath.recalc:
        calcSunPath()
        drawSunPath()
        bpy.context.scene.ODS_SUN.sunpath.recalc = False
    else:
        drawSunPath()

    # ---
    # Restore previous OpenGL settings
    if not bpy.context.scene.ODS_SUN.sunpath.xray:
        bgl.glDisable(bgl.GL_DEPTH_TEST)
    bgl.glLoadIdentity()
    bgl.glMatrixMode(MatrixMode_prev)
    bgl.glLoadMatrixf(ProjMatrix_prev)
    bgl.glLineWidth(lineWidth_prev)
    if not blend_prev:
        bgl.glDisable(bgl.GL_BLEND)
    if not line_stipple_prev:
        bgl.glDisable(2852)  # bgl.GL_LINE_STIPPLE
    bgl.glBlendColor(
        color_prev[0],
        color_prev[1],
        color_prev[2],
        color_prev[3])

    return None


class VIEW3D_OT_display_sunpath(bpy.types.Operator):
    '''Display the Sun Path'''
    bl_idname = "view3d.display_sunpath"
    bl_label = "Display the Sun Path"
    bl_options = {'REGISTER'}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()
        if event.type == 'TIMER':
            # no input, so no need to change the display
            return {'PASS_THROUGH'}
        if not context.scene.ODS_SUN.sunpath.draw:
            context.region.callback_remove(self._handle)
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        draw = context.scene.ODS_SUN.sunpath.draw
        context.scene.ODS_SUN.sunpath.draw = not draw
        if not context.scene.ODS_SUN.sunpath.draw:
            print("returning cancelled")
            return {'CANCELLED'}
        return self.execute(context)

    def execute(self, context):
        if context.area.type == 'VIEW_3D':
            mgr_ops = context.window_manager.operators.values()
            if not self.bl_idname in [op.bl_idname for op in mgr_ops]:
                # Add the region OpenGL drawing callback
                for WINregion in context.area.regions:
                    if WINregion.type == 'WINDOW':
                        context.window_manager.modal_handler_add(self)
                        self._handle = bpy.types.SpaceView3D.draw_handler_add(
                            draw_sunpath_callback,
                            (self, context),
                            'WINDOW',
                            'POST_PIXEL'
                        )
                        print("Sunpath display callback added")
                        return {'RUNNING_MODAL'}
            return {'CANCELLED'}

        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

bpy.utils.register_class(VIEW3D_OT_display_sunpath)


class VIEW3D_PT_sunpath(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Sun Path"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        # Only display this panel in the object and edit mode 3D view.
        mode = context.mode
        if (context.area.type == 'VIEW_3D' and
            (mode == 'EDIT_MESH' or mode == 'OBJECT')):
            return 1
        return 0

    def draw(self, context):
        layout = self.layout
        sc = context.scene

        if sc.ODS_SUN.sunpath.draw:
            layout.operator("view3d.display_sunpath", text="Stop Drawing")
        else:
            layout.operator("view3d.display_sunpath", text="Draw")
            return None

        row = layout.row()
        row.prop(sc.ODS_SUN.sunpath, "time", text="Show time")
        row.prop(sc.ODS_SUN.sunpath, "path", text="Sun Path")
        if sc.ODS_SUN.sunpath.path:
            row = layout.row()
            row.prop(sc.ODS_SUN.sunpath, "flat", text="Flatten")
            row.prop(sc.ODS_SUN.sunpath, "xray", text="Over")
            row = layout.row()
            row.prop(sc.ODS_SUN.sunpath, "circles", text="Circles")
            if sc.ODS_SUN.sunpath.flat:
                row.prop(sc.ODS_SUN.sunpath, "equi", text="Equidistant")
        layout.row().prop(sc.ODS_SUN, "arcRadius", text="Radius")
        layout.row().prop(sc.ODS_SUN.sunpath, "pos", text="")

        return None
bpy.utils.register_class(VIEW3D_PT_sunpath)
