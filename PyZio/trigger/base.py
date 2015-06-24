"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""

from ..base import Base, BaseMeta
from ..base.attribute import BooleanAttr, IntegerAttr, StringAttr


TRIGGERS = {}


class TriggerMeta(BaseMeta):
    def __new__(cls, name, bases, attrs):
        _attrs = {}
        trig = None
        for attr_name, attr_obj in attrs.iteritems():
            if attr_name == '_type':
                trig = attr_obj
            else:
                _attrs[attr_name] = attr_obj
        klass = super(TriggerMeta, cls).__new__(cls, name, bases, _attrs)
        if trig:
            TRIGGERS[trig] = klass
        return klass


class Trigger(Base):
    """
    It describes the zio_ti object from the ZIO framework.
    """
    __metaclass__ = TriggerMeta


class TrigTimer(Trigger):

    _type = 'timer'

    devtype = StringAttr()
    enable = BooleanAttr()
    ms__period = IntegerAttr()
    ms__phase = IntegerAttr()
    post__samples = IntegerAttr()


def get_trigger_klass(trigger_type):
    return TRIGGERS.get(trigger_type, Trigger)