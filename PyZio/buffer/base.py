"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""

from ..base import Base, BaseMeta, BooleanAttr, IntegerAttr


BUFFERS = {}


class BufferMeta(BaseMeta):
    def __new__(cls, name, bases, attrs):
        _attrs = {}
        trig = None
        for attr_name, attr_obj in attrs.iteritems():
            if attr_name == '_type':
                trig = attr_obj
            else:
                _attrs[attr_name] = attr_obj
        klass = super(BufferMeta, cls).__new__(cls, name, bases, _attrs)
        if trig:
            BUFFERS[trig] = klass
        return klass


class Buffer(Base):
    """
    This class describes the zio_bi object from the ZIO framework.
    """
    __metaclass__ = BufferMeta

    allocated__buffer_len = IntegerAttr()
    max__buffer__len = IntegerAttr()
    prefer__new = BooleanAttr()

    def __init__(self, path, name):
        """
        It calls the __init__ function from Base for a generic
        initialization; then it looks for attributes in its directory: all
        valid files within its directory are buffers's attributes
        """
        Base.__init__(self, path, name)
    #     self.__flush_attr = None
    #     # Inspect all files and directory
    #     for tmp in os.listdir(self.fullpath):
    #         # Skip if the element it is not valid
    #         if not self._is_valid_sysfs_element(tmp):
    #             continue
    #         # All the valid element are attributes
    #         self._set_attribute(self.fullpath, tmp)
    #
    # def flush(self):
    #     """
    #     It does 'flush' on the buffer
    #     """
    #     if "flush" in self._attributes:
    #         self._attributes["flush"].set_value(1)

class BufKmalloc(Buffer):
    _type = 'kmalloc'


def get_buffer_klass(buffer_type):
    return BUFFERS.get(buffer_type, Buffer)