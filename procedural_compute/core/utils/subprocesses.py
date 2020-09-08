###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

"""
Module for managing forked subprocesses that run the relevant
base-program such as EnergyPlus, Radiance or OpenFOAM.

DATA:
    p = dict: A dictionary of subprocesses accessed by name

"""

import bpy
import subprocess

p = {}


def bashForWindows(cmd):
    if 'Windows' in bpy.app.build_platform.decode():
        cmd = cmd.replace('"', '\\"')
        cmd = 'bash -i -c -l "%s"'%(cmd)
    print(cmd)
    return cmd


def itWaitOUTPUT(iterable, cmd, cwd=None, shell=True):
    P = subprocess.Popen(cmd, cwd=cwd, shell=shell, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for line in iterable:
        P.stdin.write(("%s\n"%line).encode('ascii'))
    (out, err) = P.communicate()
    return (out, err)


def waitSTDOUT(cmd, cwd=None, shell=True):
    cmd = bashForWindows(cmd)
    P = subprocess.Popen(cmd, cwd=cwd, shell=shell)
    P.wait()
    print("Done")
    return None


def waitOUTPUT(cmd, cwd=None, shell=True):
    cmd = bashForWindows(cmd)
    P = subprocess.Popen(cmd, cwd=cwd, shell=shell, stdout=subprocess.PIPE)
    (out, err) = P.communicate()
    return (out, err)


def newProcess(name='bash'):
    """Start a new process"""
    p[name] = subprocess.Popen("", executable=getExecutable(), stdin=subprocess.PIPE)
    return None


def cleanWindowsOutput(out):
    """
    Remove the junk header and footer info from
    a Windows command line call
    """
    t = out[out.find("\r\n\r\n") + 4:]
    t = t[t.find("\n") + 1:]
    t = t[:t.find("\r\n\r\n")]
    return t


def execCommand(n, cmd):
    """
    Execute a command on a running process and return immediately.
    ie. Do not wait for the output and/or process to terminate
    """
    cmd = str(cmd) + '\n'
    print("Issuing shell command on subProcess %s: %s"%(str(n), cmd[:-1]))
    p[n].stdin.write(cmd.encode('ascii'))
    p[n].stdin.flush()
    return None


def returnCommand(cmd):
    """
    Run a single command on a new subprocess, return the
    piped output and then kill the process. (ie. DO wait
    for the output and/or process to terminate)
    """
    pl = bpy.app.build_platform.decode()
    P = subprocess.Popen('', executable=getExecutable(), stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    cmd = '%s\n'%(str(cmd))
    print("Issuing shell command: %s"%(cmd))
    P.stdin.write(cmd.encode('ascii'))
    (out, err) = P.communicate()
    if err:
        raise Exception
    return out


def endProcess(n):
    """Terminate a running process"""
    p[n].terminate()
    p.pop(n)
    return None


def getExecutable():
    pl = bpy.app.build_platform.decode()
    if 'Linux' in pl or 'Darwin' in pl:
        return '/bin/bash'
    else:
        print('WARNING: You are using a system other than Linux, Windows or Mac(Darwin).  System calls may not work.')
        return None
    return None
