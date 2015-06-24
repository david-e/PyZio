"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""
import os

from ..base import ZioBase, BaseMeta, is_zio_object, ZIO_DEVTYPE
from ..base.attribute import StringAttr
from ..channel import Channel
from ..trigger import get_trigger_klass


class CsetMeta(BaseMeta):
    def __new__(cls, name, bases, attrs):
        _attrs = {}
        ch = Channel
        for attr_name, attr_obj in attrs.iteritems():
            if isinstance(attr_obj, type) and issubclass(attr_obj, Channel):
                ch = attr_obj
            else:
                _attrs[attr_name] = attr_obj
        klass = super(CsetMeta, cls).__new__(cls, name, bases, _attrs)
        klass.Channel = ch
        return klass


class Cset(ZioBase):
    """
    ZioCset class describe the zio_cset object from the ZIO framework.
    """

    __metaclass__ = CsetMeta

    current_buffer = StringAttr()
    current_trigger = StringAttr()
    direction = StringAttr()

    def __init__(self, path, parent=None):
        """
        It calls the __init__ function from Base for a generic
        initialization; then it looks for attributes, channels and trigger in
        its directory. Valid directory are channels except the 'trigger'
        directory; all valid files are attributes. The list of children object
        is made of trigger and channels.
        """
        super(Cset, self).__init__(path, parent)  # Initialize zObject
        self.channels = []  # List of channel children

        for e in os.listdir(path):
            pth = os.path.join(path, e)
            zt = is_zio_object(pth)
            if not zt:  # Skip if invalid element
                continue
            elif zt == ZIO_DEVTYPE['chan']:
                chan = Cset.Channel(pth, self)
                self.channels.append(chan)
            elif zt == ZIO_DEVTYPE['trigger']:
                self._update_trigger()
                self._add_children('trigger', self.trigger)
        self._add_children('chan', self.channels)

    def _update_trigger(self):
        Trigger = get_trigger_klass(self.current_trigger)
        self.trigger = Trigger(os.path.join(self.path, 'trigger'), self)
        return self.trigger

