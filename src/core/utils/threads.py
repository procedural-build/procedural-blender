###########################################################
# Blender Modelling Environment for Architecture
# Copyright (C) 2011, ods-engineering
# License : ods-engineering license
# Version : 1.2
# Web     : www.ods-engineering.com
###########################################################

"""
Module for managing thrads that run the relevant
base-program such as EnergyPlus, Radiance or OpenFOAM.

DATA:
    q = queue: A queue of threads
"""

import threading
import queue
import os

queues = {}


def get_or_create_queue(name, length=4):
    if not name in queues:
        queues[name] = queue.Queue(length)
    return queues[name]


def put_item(_queue, item, args):
    thread = threading.Thread(target=item, args=args)
    thread.daemon = True
    _queue.put(thread, True)
    thread.start()
    thread.join()
    _queue.get(True)
    _queue.task_done()
    return None


def queue_fun(queue_name, _function, args=()):
    _queue = get_or_create_queue(queue_name)
    put_thread = threading.Thread(target=put_item, args=(_queue, _function, args))
    put_thread.daemon = True
    put_thread.start()
    return None


def queue_sys(queue_name, cmd):
    queue_fun(queue_name, os.system(cmd), ())
    return None
