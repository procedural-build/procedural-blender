###########################################################
# Blender Modelling Environment for Architecture
# Copyright (C) 2011, ods-engineering
# License : ods-engineering license
# Version : 1.2
# Web     : www.ods-engineering.com
###########################################################


import bpy

################################
# SCENE OPERATORS
################################


class SCENE_OT_cleannames(bpy.types.Operator):
    bl_label = "Clean Names"
    bl_idname = "scene.cleannames"
    bl_description = "Cleans the name of objects"

    def execute(self, context):
        for o in bpy.context.selected_objects:
            o.name = o.name.replace(' ', '_')
        return {'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}


bpy.utils.register_class(SCENE_OT_cleannames)


class SCENE_OT_collectionOps(bpy.types.Operator):
    bl_label = "Collection Operators"
    bl_idname = "scene.collectionops"
    bl_description = "Generic Collection Operations"

    command: bpy.props.StringProperty(name="Command", description="parse String", default="")

    def execute(self, context):
        s = self.command.split('.')
        baseType = s[0]
        collectionPath = s[1:-1]
        action = s[-1]
        # Get the base collection object
        o = getattr(context, baseType)
        collection = o.path_resolve(".".join(collectionPath))
        # Run the command
        if hasattr(self, action):
            a = getattr(self, action)
            a(collection)
        else:
            print(self.command + ": Method not found in collectionOps!")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}

    def getBaseObject(self, o):
        path = o.path_from_id()
        # Check there are not square brackets in path
        if "[" in path:
            (p1, p2) = path.split("[")
            p2 = p2.split("]")[1]
            path = p1 + p2
        # Now get the base object
        path = path.split('.')[0:-1]
        b = o.id_data.path_resolve(".".join(path))
        return b

    def nameUnique(self, nameRoot, keys):
        for i in range(1000):
            ntmp = nameRoot + ".%03d"%i
            if ntmp not in keys:
                return ntmp
        return ntmp

    def getName(self, collection):
        name  = collection.path_from_id().split('.')[-1]
        return name

    def add(self, collection):
        t = collection.add()
        t.name = self.nameUnique(self.getName(collection), collection.keys())
        #setattr(self.getBaseObject(collection), "active_%s_index"%(self.getName(collection)), len(collection)-1)
        setattr(collection.data, "active_%s_index"%(self.getName(collection)), len(collection) - 1)
        return{'FINISHED'}

    def remove(self, collection):
        i = getattr(self.getBaseObject(collection), "active_%s_index"%(self.getName(collection)))
        collection.remove(i)
        if i >= len(collection):
            #setattr(self.getBaseObject(collection), "active_%s_index"%(self.getName(collection)), len(collection)-1)
            setattr(collection.data, "active_%s_index"%(self.getName(collection)), len(collection) - 1)
        return{'FINISHED'}


bpy.utils.register_class(SCENE_OT_collectionOps)
