"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""

import os

from ..base import ZioBase, BaseMeta, ZIO_DEVTYPE
from ..buffer import get_buffer_klass
from ..interface import CharDevice, Ctrl, Interface


class ChannelMeta(BaseMeta):
    def __new__(cls, name, bases, attrs):
        ifc = Interface
        _attrs = {}
        for attr_name, attr_obj in attrs.iteritems():
            if isinstance(attr_obj, type) and issubclass(attr_obj, Interface):
                ifc = attr_obj
            else:
                _attrs[attr_name] = attr_obj
        klass = super(ChannelMeta, cls).__new__(cls, name, bases, _attrs)
        klass.Interface = ifc
        return klass


class Channel(ZioBase):
    """
    This class describes the zio_channel object from the ZIO framework.
    """

    __metaclass__ = ChannelMeta

    Interface = CharDevice

    def __init__(self, path, parent=None):
        """
        It calls the __init__ function from Base for a generic
        initialization; then it looks for attributes and buffer in its
        directory. All valid files are normal attributes. A directory can be a
        buffer or an interface.
        """
        super(Channel, self).__init__(path, parent)
        self.buffer = None
        self.interface = None

        # Inspect all files and directory
        for e in os.listdir(path):
            # Skip if the element it is not valid
            if e == ZIO_DEVTYPE['cdev']:
                i = Channel.Interface(self)
                self._add_children('interface', i)
                for m in i.expose_methods:
                    setattr(self, m, lambda *a, **k: getattr(i, m)(*a, **k))
                self.interface = i
            elif e == ZIO_DEVTYPE['buffer']:
                self._update_buffer()
                self._add_children('buffer', self.buffer)

    def is_interleaved(self):
        """
        It returns True if this is an interleaved channel
        """
        return True if self.name == "chani" else False

    def _update_buffer(self):
        Buffer = get_buffer_klass(self.parent.current_buffer)
        self.buffer = Buffer(os.path.join(self.path, 'buffer'), self)
        return self.buffer


