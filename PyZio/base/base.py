"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""

import logging
import os

from .attribute import Attribute, BooleanAttr, StringAttr


ZIO_DEVTYPE = {
    'cset': 'zio_cset_type',
    'chan': 'zio_chan_type',
    'trigger': 'zio_ti_type',
    'buffer': 'buffer',
    'cdev': 'zio-cdev',
}


def is_zio_object(path):
    p = os.path.join(path, 'devtype')
    if not os.path.isdir(path):
        return False
    try:
        f = open(p)
        return f.read().rstrip("\n\r")
    except:
        return False


class BaseMeta(type):

    def __new__(cls, name, bases, attrs):
        _attributes = {}
        klass = super(BaseMeta, cls).__new__(cls, name, bases, attrs)
        for attr_name, attr_obj in attrs.iteritems():
            if isinstance(attr_obj, Attribute):
                attr_obj.name = attr_name.replace('__', '-')
                _attributes[attr_name] = attr_obj
        klass._attributes = _attributes
        return klass


class Base(object):
    __metaclass__ = BaseMeta

    name = StringAttr()
    devname = StringAttr()
    devtype = StringAttr()
    enable = BooleanAttr()

    _children = {}

    def _add_children(self, key, children):
        self._children[key] = children

    @property
    def children(self):
        return self._children

    def __init__(self, path, parent=None):
        self.path = path
        self.parent = parent