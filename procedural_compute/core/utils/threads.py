###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
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
import logging
logger = logging.getLogger(__name__)

queues = {}


def get_or_create_queue(name, length=4):
    if not name in queues:
        queues[name] = queue.Queue(length)
        logger.info(f"Created new queue: {name}")
    return queues[name]


def put_item(_queue, item, args, **kwargs):
    thread = threading.Thread(target=item, args=args, kwargs=kwargs)
    thread.daemon = True
    _queue.put(thread, True)
    thread.start()
    thread.join()
    _queue.get(True)
    _queue.task_done()
    return None


def queue_fun(queue_name, _function, args=(), kwargs={}):
    logger.info(f"Adding function to: {queue_name} [{_function}]")
    _queue = get_or_create_queue(queue_name)
    put_thread = threading.Thread(target=put_item, args=(
        _queue, _function, args), kwargs=kwargs)
    put_thread.daemon = True
    put_thread.start()
    return None


def queue_sys(queue_name, cmd):
    queue_fun(queue_name, os.system(cmd), ())
    return None
