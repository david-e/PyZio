"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""
import os

from ..base import ZioBase, BaseMeta, is_zio_object, ZIO_DEVTYPE
from ..base.attribute import StringAttr
from ..cset import Cset


class DeviceMeta(BaseMeta):
    def __new__(cls, name, bases, attrs):
        _attrs = {}
        cs = Cset
        for attr_name, attr_obj in attrs.iteritems():
            if isinstance(attr_obj, Cset):
                cs = attr_obj.__class__
            else:
                _attrs[attr_name] = attr_obj
        klass = super(DeviceMeta, cls).__new__(cls, name, bases, _attrs)
        klass.Cset = cs
        return klass


class Device(ZioBase):
    """
    It describes the zio_device object from the ZIO framework.
    """

    __metaclass__ = DeviceMeta

    devname = StringAttr()
    devtype = StringAttr()

    def __init__(self, path, parent=None):
        """
        It calls the __init__ function from Base for a generic
        initialization; then it looks for attributes and csets in its
        directory. All valid directory are csets, and all valid files are
        attributes. The list of object children is equal to the list of channel
        set.
        """
        super(Device, self).__init__(path)
        self.cset = [] # List of children cset
        for e in os.listdir(path):
            cspath = os.path.join(path, e)
            zt = is_zio_object(cspath)
            if not zt:
                continue
            elif zt == ZIO_DEVTYPE['cset']:
                cs = Device.Cset(cspath, self)
            self.cset.append(cs)
        self._add_children('cset', self.cset) # Update the zObject children list

    def __str__(self):
        return self.name
