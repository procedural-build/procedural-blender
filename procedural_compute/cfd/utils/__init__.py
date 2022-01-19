###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2021, Procedural
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################
import os
import re


def latestTime(case):
    allNames = os.listdir(case)
    numbers = []
    names = []
    for n in allNames:
        try:
            numbers.append(float(n))
            names.append(n)
        except:
            continue
    latest = names[numbers.index(max(numbers))]
    return "%s/%s"%(case,latest)


def readFile(fname):
    f = open(fname,'r')
    s = f.read()
    f.close()
    return s


def writeFile(fname, text):
    f = open(fname,'w')
    f.write(text)
    f.close()
    return None


def replaceText(fname, regex, replStr):
    s = readFile(fname)
    s = re.sub(regex,replStr,s)
    writeFile(fname, s)
    return None
