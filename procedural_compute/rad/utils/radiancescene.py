###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################


import bpy

from procedural_compute.sun.utils.timeFrameSync import getTimeStamp
from procedural_compute.rad.utils.radiance_entities import RadianceSky
from procedural_compute.rad.utils.material import MaterialContext
from procedural_compute.rad.utils.exportbase import ExportBase

class RadianceScene(ExportBase):

    def exportFrame(self, hour, minute, writeStaticData=True):
        sc = bpy.context.scene
        
        ## Get the timestamp of the current frame
        timestamp = getTimeStamp()
        print("Creating case file for timestamp: %s"%(timestamp))

        ## write sky for this particular frame
        self.skyfile = RadianceSky().export(hour, minute, timestamp)

        ## Write static data objects
        if writeStaticData:
            self.exportStaticObjects(name="%s.rad"%(sc.name))

        ## Add the timestamped skyfile to the static data
        self.prependFile(self.getFilename("%s.rad"%(sc.name)), "!xform %s\n"%(self.skyfile), self.getFilename("%s.rad"%(timestamp)))

        ## Write Rif File (including camera views)
        rifFile = self.createRifFile()

        ## Create these directories (if they do not already exist)
        for d in ["octrees", "images", "ambfiles", "logfiles", "lights", "stencils"]:
            self.createDir(self.getFilename(d))

        # Execute command to execute the RIF file
        text = "rad %s\n"%(rifFile)
        return text

    def exportStaticObjects(self, name="statics.rad"):
        ## export selected geometry
        self.exportSelectedObjects()
        MaterialContext().export(self.materialsList)
        # Create the master .rad file (minus the skyfile)
        self.createMainScene(self.references, name)
        return

    def createMainScene(self, references, name):
        ref_text = "".join([r+'\n' for r in references])
        ## add materials and at top of file (sky is added later for animation compatability)
        ref_text = "!xform ./materials.rad\n" + ref_text
        #ref_text = "!xform " + self.skyfile + "\n" + ref_text
        ref_filename = self.getFilename(name)
        self.createFile(ref_filename, ref_text)
        return ref_filename

    def createRifFile(self):
        timestamp = getTimeStamp()
        text =  "# scene input file for rad\n"
        text += self.getRadOptions()
        text += "\n"
        text += "PICTURE=      images/img\n" 
        text += "OCTREE=       octrees/%s.oct\n"%(timestamp)
        text += "AMBFILE=      ambfiles/%s.amb\n"%(timestamp)
        text += "REPORT=       3 logfiles/%s.log\n"%(timestamp)
        text += "scene=        %s.rad\n"%(timestamp)
        text += "materials=    materials.rad\n\n"
        text += "render=       -av 0 0 0\n"
        text += "%s\n\n"%("".join([v + "\n" for v in self.views]))
        text += "\n"

        filename = self.getFilename("%s.rif"%(timestamp))
        self.createFile(filename, text)
        return "%s.rif"%(timestamp)

    def getRadOptions(self):
        return bpy.context.scene.RAD.getRadOptions()


