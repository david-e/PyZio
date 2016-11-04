"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""
import logging
import os

from pyzio.attribute import ZioAttribute


class InstanceDescriptorMixin(object):
    def __getattribute__(self, name):
        value = object.__getattribute__(self, name)
        if hasattr(value, '__get__'):
            value = value.__get__(self, self.__class__)
        return value

    def __setattr__(self, name, value):
        try:
            obj = object.__getattribute__(self, name)
        except AttributeError:
            pass
        else:
            if hasattr(obj, '__set__'):
                return obj.__set__(self, value)
        return object.__setattr__(self, name, value)


class ZioObject(InstanceDescriptorMixin):
    """
    It handles a generic ZIO object. It is an abstract class that export
    generic functions and attributes suitable for every objects.
    """

    def __init__(self, path, name):
        self.name = name
        self.path = path
        self.fullpath = os.path.join(self.path, self.name)
        self._attrs = {}     # Dictionary for boject's attributes
        self._obj_children = []  # List of children attributes
        self.invalid_attrs = ["power", "driver", "subsystem", "uevent"]

        logging.debug("new %s %s", self.__class__.__name__, self.fullpath)

    def __str__(self):
        return self.name

    def is_valid_sysfs_element(self, name):
        """
        It returns if a sysfs name is valid or not
        """
        return not name in self.invalid_attrs

    def get_name(self):
        """
        It returns the name of the object
        """
        return self._attrs["name"].get_value()

    @property
    def oid(self):
        n = self.devname.split('-')[-1]
        try:
            n = int(n)
        except:
            pass
        return n

    def is_enable(self):
        """
        It returns True if this object is enabled, False otherwise
        """
        en = self._attrs["enable"].get_value()
        return (True if en == "1" else False)

    def enable(self, status = True):
        """
        It enables the object. It raise IO exception if the user cannot
        enable the object. You can use this function also to disable an
        object by setting the optional parameter 'status' to 'False'.
        """
        val = 1 if status else 0
        self._attrs["enable"].set_value(val)

    def disable(self, status = True):
        """
        It disable the object. It raise IO exception if the user cannot
        enable the object. You can use this function also to enable an
        object by setting the optional parameter 'status' to 'True'.
        """
        val = 0 if status else 1
        self._attrs["enable"].set_value(val)

    def set_attribute(self, name):
        attr = ZioAttribute(self.fullpath, name)
        self._attrs[name] = attr
        setattr(self, name.replace('-', '_'), attr)
