"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""
import os

from pyzio.object import ZioObject
from pyzio.attribute import ZioAttribute


class ZioBuf(ZioObject):
    """
    This class describes the zio_bi object from the ZIO framework.
    """

    def __init__(self, path, name):
        """
        It calls the __init__ function from ZioObject for a generic
        initialization; then it looks for attributes in its directory: all
        valid files within its directory are buffers's attributes
        """
        ZioObject.__init__(self, path, name)
        self.__flush_attr = None
        # Inspect all files and directory
        for tmp in os.listdir(self.fullpath):
            # Skip if the element it is not valid
            if not self.is_valid_sysfs_element(tmp):
                continue
            # All the valid element are attributes
            self._attrs[tmp] = ZioAttribute(self.fullpath, tmp)

    def flush(self):
        """
        It does 'flush' on the buffer
        """
        if "flush" in self._attrs:
            self._attrs["flush"].set_value(1)
