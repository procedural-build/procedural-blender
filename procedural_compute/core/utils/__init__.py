###########################################################
# Blender Addon for Procedural Cloud-based Design Tools
# Copyright (C) 2020, Procedural (ApS) Denmark
# License : procedural.build license
# Version : 1.2
# Web     : www.procedural.build
###########################################################

"""
Common utility functions used within ODS and its associated sub-modules
"""

import json
import logging
logger = logging.getLogger(__name__)


def make_tuples(items: list):
    return [(x, x, x) for x in items]


def to_json(python_dict, log=True):
    json_str = json.dumps(python_dict, indent=4)
    if log:
        logger.info(json_str)
    return json_str
