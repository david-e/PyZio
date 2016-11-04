"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""

import os
import stat

from pyzio.config import zio_bus_path, devices_path


def is_loaded():
    """It returns true if ZIO is loaded correctly, otherwise it returns false.
    It considers ZIO correctly loaded if the path to zio in sysfs exists, and
    if the bus attribute available_buffers and available_triggers exists"""
    if not os.path.exists(zio_bus_path):
        print("ZIO is not loaded")
        return False

    if not os.access(zio_bus_path + "/available_buffers", os.R_OK) and \
       not os.access(zio_bus_path + "/available_triggers", os.R_OK):
        print("ZIO is not loaded correctly")
        return False
    return True

def is_readable(path):
    """It returns True if the path is readable"""
    mode = stat.S_IMODE(os.stat(path).st_mode)
    perm = (stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    return True if mode & perm else False


def is_writable(path):
    """It returns if the path is writable"""
    mode = stat.S_IMODE(os.stat(path).st_mode)
    perm = (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
    return True if mode & perm else False
