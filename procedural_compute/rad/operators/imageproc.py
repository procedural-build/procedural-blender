###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

import bpy
import os
from math import floor

from procedural_compute.core.utils.subprocesses import waitOUTPUT
from procedural_compute.rad.operators.ops import getOutsideAmb


class imageops(bpy.types.Operator):
    bl_label = "falsecolor"
    bl_idname = "image.falsecolor"
    bl_description = "falsecolor"

    command: bpy.props.StringProperty(name="Command", description="parse String", default="")

    @classmethod
    def poll(self, context):
        return context.space_data.type == "IMAGE_EDITOR"

    def invoke(self, context, event):
        if hasattr(self,self.command):
            c = getattr(self, self.command)
            c(context)
        else:
            print(self.command + ": Attribute not found!")
        return{'FINISHED'}

    def getDFMult(self, context):
        extamb = getOutsideAmb()
        if extamb == 0:
            self.report({'ERROR'},'COULD NOT FIND SKYFILE! \n \
Check that skyfile exists for current frame(time).\n \
Using default value of 20. Results will not be accurate.')
            extamb = 20
        sc = context.scene
        sc.procedural_compute.rad.falsecolor.mult = (100/3.14159265358979)/extamb
        sc.procedural_compute.rad.falsecolor.label = "DF"
        return{'FINISHED'}

    def threshold(self, context):
        sc = context.scene
        p = sc.procedural_compute.rad.falsecolor

        im = context.space_data.image
        radpath = bpy.path.abspath("%s/"%(sc.procedural_compute.rad.caseDir))
        filepath = bpy.path.abspath(im.filepath)
        (fpath, fname) = os.path.split(filepath)

        outpath = "%s/%s"%(fpath,p.output)
        if os.path.exists(outpath):
            os.remove(outpath)

        # Get the number of pixels above the threshold
        if not 'Windows' in bpy.app.build_platform.decode():
            cmd  = "pvalue -h -H -o %s "%(filepath)
            cmd += "| rcalc -e '$1=($3*0.265+$4*0.67+$5*0.065)*%s' "%(p.mult)
            cmd += "| rcalc -e '$1=if($1-%f,1,0)' | total"%(p.limit)
        else:
            cmd  = "pvalue -h -H -o %s "%(filepath)
            cmd += "| rcalc -e \"$1=($3*0.265+$4*0.67+$5*0.065)*%s\" "%(p.mult)
            cmd += "| rcalc -e \"$1=if($1-%f,1,0)\" | total"%(p.limit)
        (out1,err) = waitOUTPUT(cmd, cwd=fpath)
        out1 = out1.decode("utf-8")

        # Get the total number of pixels
        if not 'Windows' in bpy.app.build_platform.decode():
            cmd = "getinfo -d %s | rcalc -e '$1=$3*$5'"%(filepath)
        else:
            cmd = "getinfo -d %s | rcalc -e \"$1=$3*$5\""%(filepath)
        (out2,err) = waitOUTPUT(cmd, cwd=fpath)
        out2 = out2.decode("utf-8")

        # Do the calculation of percentage area above threshold
        nPixelsAbove = float(out1)
        nPixels = float(out2)
        tArea = 100*(nPixels - nPixelsAbove)/nPixels
        text = 'Threshold percentage = %f'%(tArea)
        print(text)
        self.report({'INFO'},text)

        # Create the threshold image
        cmd = "pcomb -o %s | pcompos -t %f - 0 0 | pfilt -e %u -1 > %s"\
                %(filepath, (p.limit/p.mult), sc.procedural_compute.rad.falsecolor.exposure, outpath)
        waitOUTPUT(cmd, cwd=fpath)

        # Load the new image into the image editor
        im = bpy.data.images.load(outpath)
        context.space_data.image = im
        bpy.ops.image.reload()

        return{'FINISHED'}

    def falsecolor(self, context):
        sc = context.scene
        p = sc.procedural_compute.rad.falsecolor

        # Get the image filename and path
        im = context.space_data.image
        radpath = bpy.path.abspath("%s/"%(sc.procedural_compute.rad.caseDir))
        filepath = bpy.path.abspath(im.filepath)
        (fpath, fname) = os.path.split(filepath)

        tmpdir = "%s/tmp"%fpath
        if not os.path.exists(tmpdir):
            os.makedirs(tmpdir)

        outpath = "%s/%s"%(fpath,p.output)
        if os.path.exists(outpath):
            os.remove(outpath)

        picpath = bpy.path.abspath(p.overlaypic)

        # Removed exporting of environment variables for windows compatibility
        loff = 0
        scale = p.scale
        cpict = picpath

        # Get the auto-scale by a hack using max/min extrema values
        # (not elegant but should do the trick for now)
        if p.scale == 0:
            (out,err) = waitOUTPUT("pextrem -o %s"%(filepath), cwd=fpath)
            out = out.decode("utf-8")
            # We have to clean up the junky output in Windows
            #if 'Windows' in bpy.app.build_platform.decode():
            #    out = subprocesses.cleanWindowsOutput(out)
            # Now actually do the calc
            (minx,miny,minr,ming,minb, maxx,maxy,maxr,maxg,maxb) = out.split()
            maxv = (float(maxr)*0.265+float(maxg)*0.67+float(maxb)*0.065)*p.mult
            scale = maxv
            #cmd = "export scale=`rcalc -e '$1=($3*.27+$4*.67+$5*.06)*'\"$mult\" %s/extrema \
            #| sed -e 1d -e 's/\\(\\.[0-9][0-9][0-9]\\)[0-9]*/\\1/'`\n"%(tmpdir)
            #waitOUTPUT(cmd, cwd=fpath)

        # Write the .cal files
        self.writeP0Cal(tmpdir,scale,p.mult,p.ndivs)
        self.writeP1Cal(tmpdir)
        pc0args = "-f %s/pc0.cal"%(tmpdir)
        pc1args = "-f %s/pc1.cal"%(tmpdir)

        if p.contours == "Lines":
            pc0args +=" -e \"in=isconta\""
            loff = 12
        elif p.contours == "Bands":
            pc0args +=" -e \"in=iscontb\""
            loff=13

        # if decade != 0 then (log scale) otherwise linear scale
        if p.decades != 0:
            pc1args += " -e \"map(x)=if(x-10^-%u,log10(x)/%u+1,0)\""%(p.decades,p.decades)
            imap = "imap(y)=10^((y-1)*%u)"%(p.decades)
        else:
            imap="imap(y)=y"

        # Make the legend
        legwidth = p.legwidth;
        legheight = p.legheight;
        if legwidth > 20 and legheight > 40:
            # Remember here that Windows doesn't like to mix \" and \' characters
            cmd = "pcomb %s -e \"v=(y+.5)/yres;vleft=v;vright=v\" "%(pc0args)
            cmd+= "-e \"vbelow=(y-.5)/yres;vabove=(y+1.5)/yres\" "
            cmd+= "-x %s -y %s > %s/scol.hdr"%(legwidth, legheight, tmpdir)
            waitOUTPUT(cmd, cwd=fpath)

            if not 'Windows' in bpy.app.build_platform.decode():
                cmd = "( echo %s; cnt %u "%(p.label,p.ndivs)
                cmd+= "| rcalc -e '$1='\"(%f)*imap((%u-.5-\"'$1'\")/%u)\" "%(scale,p.ndivs,p.ndivs)
                cmd+= "-e \"%s\" | sed -e 's/\(\.[0-9][0-9][0-9]\)[0-9]*/\\1/' ) "%(imap)
                cmd+= "| psign -s -.15 -cf 1 1 1 -cb 0 0 0 "
                cmd+= "-h `ev \"floor(%u/%u+.5)\"` > %s/slab.hdr"%(legheight,p.ndivs,tmpdir)
                waitOUTPUT(cmd, cwd=fpath)
            else:
                # Not quite so easy in windows - create separately then pcompos them together
                charheight = floor(legheight/p.ndivs+0.5)
                # Make the label
                cmd = "psign -s -.15 -cf 1 1 1 -cb 0 0 0 -h %u %s > %s/label.hdr"%(charheight,p.label,tmpdir)
                waitOUTPUT(cmd, cwd=fpath)
                # Now make the numbers
                cmd = "cnt %u "%(p.ndivs)
                cmd+= "| rcalc -e \"$1=(%f)*imap((%u-.5-$1)/%u)\" -e \"%s\" "%(scale,p.ndivs,p.ndivs,imap)
                cmd+= "| psign -s -.15 -cf 1 1 1 -cb 0 0 0 -h %f > %s/numbers.hdr"%(charheight,tmpdir)
                waitOUTPUT(cmd, cwd=fpath)
                # Now pcompos the two together
                cmd = "pcompos -a 1 %s/numbers.hdr %s/label.hdr > %s/slab.hdr"%(tmpdir,tmpdir,tmpdir)
                waitOUTPUT(cmd, cwd=fpath)
        else:
            legwidth=0;legheight=0
            cmd = "(echo \"\" ; echo \"-Y 1 +X 1\" ; echo \"aaa\" ) > %s/scol.hdr"%(tmpdir)
            waitOUTPUT(cmd, cwd=fpath)
            #cmd = "cp %s/scol.hdr %s/slab.hdr"%(tmpdir)
            cmd = "(echo \"\" ; echo \"-Y 1 +X 1\" ; echo \"aaa\" ) > %s/slab.hdr"%(tmpdir)
            waitOUTPUT(cmd, cwd=fpath)

        # Make the false color image
        if not 'Windows' in bpy.app.build_platform.decode():
            # This actually does the color conversion
            cmd = " pcomb %s %s %s %s "%(pc0args,pc1args,filepath,cpict)
            # This now pipes to pcompos to add the legend
            cmd+= "| pcompos %s/scol.hdr 0 0 +t .1 \"!pcomb -e 'lo=1-gi(1)' %s/slab.hdr\" "%(tmpdir,tmpdir)
            cmd+= "`ev 2 %u-1` -t .5 %s/slab.hdr 0 %u - %u 0 > %s\n"%(loff,tmpdir,loff,legwidth,outpath)
            waitOUTPUT(cmd, cwd=fpath)
        else:
            # First we need to explicity create the negative image of the legend text
            cmd = "pcomb -e \"lo=1-gi(1)\" %s/slab.hdr > %s/nslab.hdr"%(tmpdir,tmpdir)
            waitOUTPUT(cmd, cwd=fpath)
            # Its probably a good idea to explicity create the falscolor image too
            cmd = "pcomb %s %s %s %s > %s/fc.hdr"%(pc0args,pc1args,filepath,cpict,tmpdir)
            waitOUTPUT(cmd, cwd=fpath)
            # Now we can actually combine the images
            cmd = "pcompos %s/scol.hdr 0 0 +t 0.1 %s/nslab.hdr 0 %u -t 0.5 %s/slab.hdr 0 %u %s/fc.hdr %u 0 > %s"\
                    %(tmpdir,tmpdir,loff,tmpdir,loff,tmpdir,legwidth,outpath)
            waitOUTPUT(cmd, cwd=fpath)

        # Load the new image into the image editor
        im = bpy.data.images.load(outpath)
        context.space_data.image = im
        bpy.ops.image.reload()
        return{'FINISHED'}

    def load(self, context):
        sc = context.scene
        p = sc.procedural_compute.rad.falsecolor

        im = context.space_data.image
        filepath = bpy.path.abspath(im.filepath)
        (fpath, fname) = os.path.split(filepath)
        outpath = fpath+p.output

        im = bpy.data.images.load(outpath)
        context.space_data.image = im
        bpy.ops.image.reload()
        return{'FINISHED'}

    def writeP0Cal(self,tmpdir,scale,mult,ndivs):
        f = open(tmpdir+"/pc0.cal",'w')
        f.write("""
PI : 3.14159265358979323846 ;
scale : %f ;
mult : %f ;
ndivs : %u ;

or(a,b) : if(a,a,b);
EPS : 1e-7;
neq(a,b) : if(a-b-EPS,1,b-a-EPS);
btwn(a,x,b) : if(a-x,-1,b-x);
clip(x) : if(x-1,1,if(x,x,0));
frac(x) : x - floor(x);
boundary(a,b) : neq(floor(ndivs*a+.5),floor(ndivs*b+.5));

old_red(x) = 1.6*x - .6;
old_grn(x) = if(x-.375, 1.6-1.6*x, 8/3*x);
old_blu(x) = 1 - 8/3*x;

interp_arr2(i,x,f):(i+1-x)*f(i)+(x-i)*f(i+1);
interp_arr(x,f):if(x-1,if(f(0)-x,interp_arr2(floor(x),x,f),f(f(0))),f(1));
def_redp(i):select(i,0.18848,0.05468174,
0.00103547,8.311144e-08,7.449763e-06,0.0004390987,0.001367254,
0.003076,0.01376382,0.06170773,0.1739422,0.2881156,0.3299725,
0.3552663,0.372552,0.3921184,0.4363976,0.6102754,0.7757267,
0.9087369,1,1,0.9863);
def_red(x):interp_arr(x/0.0454545+1,def_redp);
def_grnp(i):select(i,0.0009766,2.35501e-05,
0.0008966244,0.0264977,0.1256843,0.2865799,0.4247083,0.4739468,
0.4402732,0.3671876,0.2629843,0.1725325,0.1206819,0.07316644,
0.03761026,0.01612362,0.004773749,6.830967e-06,0.00803605,
0.1008085,0.3106831,0.6447838,0.9707);
def_grn(x):interp_arr(x/0.0454545+1,def_grnp);
def_blup(i):select(i,0.2666,0.3638662,0.4770437,
0.5131397,0.5363797,0.5193677,0.4085123,0.1702815,0.05314236,
0.05194055,0.08564082,0.09881395,0.08324373,0.06072902,
0.0391076,0.02315354,0.01284458,0.005184709,0.001691774,
2.432735e-05,1.212949e-05,0.006659406,0.02539);
def_blu(x):interp_arr(x/0.0454545+1,def_blup);

isconta = if(btwn(0,v,1),or(boundary(vleft,vright),boundary(vabove,vbelow)),-1);
iscontb = if(btwn(0,v,1),btwn(.4,frac(ndivs*v),.6),-1);

ra = 0;
ga = 0;
ba = 0;

in = 1;

ro = if(in,clip(def_red(v)),ra);
go = if(in,clip(def_grn(v)),ga);
bo = if(in,clip(def_blu(v)),ba);
"""%(scale,mult,ndivs))
        f.close()
        return

    def writeP1Cal(self,tmpdir):
        f = open(tmpdir+"/pc1.cal",'w')
        f.write("""
norm : mult/scale/le(1);

v = map(li(1)*norm);

vleft = map(li(1,-1,0)*norm);
vright = map(li(1,1,0)*norm);
vabove = map(li(1,0,1)*norm);
vbelow = map(li(1,0,-1)*norm);

map(x) = x;

ra = ri(nfiles);
ga = gi(nfiles);
ba = bi(nfiles);
""")
        f.close()
        return


bpy.utils.register_class(imageops)
