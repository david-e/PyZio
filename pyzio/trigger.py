"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""
import os

from pyzio.attribute import ZioAttribute
from pyzio.object import ZioObject


class ZioTrig(ZioObject):
    """
    It describes the zio_ti object from the ZIO framework.
    """

    def __init__(self, path, name):
        """
        It calls the __init__ function from zObject for a generic
        initialization; then it looks for attributes in its directory. All
        valid files within trigger directory are attributes.
        """
        ZioObject.__init__(self, path, name)
        for tmp in os.listdir(self.fullpath):
            if not self.is_valid_sysfs_element(tmp):
                continue
            self._attrs[tmp] = self.set_attribute(tmp)
