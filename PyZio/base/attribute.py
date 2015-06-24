"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""
import logging
import os

class Attribute(object):
    """
    This class handles a single ZIO attribute. It allows only two operations:
    read and write. Class' methods do not handle exceptions, so higher classes
    that use this one must handle errors.
    """
    name = None

    def __get__(self, instance, owner):
        """
        It reads the sysfs file of the attribute and it returns the value
        """
        path = os.path.join(instance.path, self.name)
        with open(path, "r") as f:
            return f.read().rstrip("\n\r")

    def __set__(self, instance, value):
        """
        It writes the sysfs attribute with val.
        """
        path = os.path.join(instance.path, self.name)
        with open(path, "w") as f:
            f.write(str(value))


class StringAttr(Attribute):
    """
    """


class IntegerAttr(Attribute):
    def __get__(self, instance, owner):
        return int(super(IntegerAttr, self).__get__(instance, owner))


class BooleanAttr(Attribute):
    def __get__(self, instance, owner):
        return bool(int(super(BooleanAttr, self).__get__(instance, owner)))

    def __set__(self, instance, value):
        super(BooleanAttr, self).__set__(instance, int(value))


class ListAttr(Attribute):
    def __init__(self, type=str):
        self.type = type

    def __get__(self, instance, owner):
        return map(self.type, super(BooleanAttr, self).__get__(instance, owner).strip())

    def __set__(self, instance, value):
        super(BooleanAttr, self).__set__(instance, ' '.join(map(str, value)))
