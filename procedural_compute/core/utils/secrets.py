import bpy
import os
from procedural_compute.core.utils.compute.auth import login_user

import logging
logger = logging.getLogger(__name__)


def get_creds_from_environ():
    return [os.environ.get(i) for i in ['PROCEDURAL_USER', 'PROCEDURAL_PASS']]


def has_creds_in_environ():
    return all(get_creds_from_environ())


def secure_login(host=None):
    auth_settings = bpy.context.scene.Compute.auth

    # Get the username and password firstly from the blender settings
    (uname, pw) = (auth_settings.username, auth_settings.password)
    if not all((uname, pw)):
        # If username or password are not found then try to get from environment varliables
        (uname, pw) = get_creds_from_environ()
        logger.info(f"Trying to get username/password from Environment Variables")
    else:
        logger.warn(f"Got login credentials from Blender Panels this is not secure")
    
    if not all((uname, pw)):
        raise Exception("No credentials in Blender panel or system environment variables: PROCEDURAL_USER, PROCEDURAL_PASS")
    
    user = login_user(uname, pw, host or auth_settings.host)

    auth_settings.access_token = user.token
    auth_settings.expire_time = "%.02f"%(user.token_exp_time)

    logger.info(f"Succesfully got token for user {uname}")

    return user