"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""
import logging
import os

from pyzio.utils import is_readable, is_writable


class ZioAttribute(object):
    """
    This class handles a single ZIO attribute. It allows only two operations:
    read and write. Class' methods do not handle exceptions, so higher classes
    that use this one must handle errors.
    """

    def __init__(self, path, name):
        self.name = name
        self.path = path
        self.fullpath = os.path.join(path, name)

        logging.debug("new attribute %s", self.fullpath)

    def is_readable(self):
        """
        It returns if the attribute is readable
        """
        return is_readable(self.fullpath)

    def is_writable(self):
        """
        It returns if the attributes is writable
        """
        return is_writable(self.fullpath)

    def __get__(self, obj, objtype):
        return self.get_value()

    def get_value(self):
        """
        It reads the sysfs file of the attribute and it returns the value
        """
        with open(self.fullpath, "r") as f:
            v = f.read().rstrip("\n\r")
            try:
                v = int(v)
            except:
                pass
            return v

    def __set__(self, obj, val):
        return self.set_value(val)

    def set_value(self, val):
        """
        It writes the sysfs attribute with val.
        """
        with open(self.fullpath, "w") as f:
            f.write(str(val))

