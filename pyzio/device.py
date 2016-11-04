"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""
import os

from os.path import join, isdir

from pyzio.attribute import ZioAttribute
from pyzio.channelset import ZioCset
from pyzio.object import ZioObject


class ZioDev(ZioObject):
    """
    It describes the zio_device object from the ZIO framework.
    """

    def __init__(self, path, name):
        """
        It calls the __init__ function from ZioObject for a generic
        initialization; then it looks for attributes and csets in its
        directory. All valid directory are csets, and all valid files are
        attributes. The list of object children is equal to the list of channel
        set.
        """
        ZioObject.__init__(self, path, name)
        self.cset = {}
        self.update()
    
    def __getitem__(self, key):
        return self.cset[key]

    def __str__(self):
        return self.devname
    
    def update(self):
        self.cset.clear()
        self._obj_children.clear()
        for tmp in os.listdir(self.fullpath):
            if not self.is_valid_sysfs_element(tmp): # Skip if invalid element
                continue
            if isdir(join(self.fullpath, tmp)): # Subdirs are csets
                newcset = ZioCset(self.fullpath, tmp)
                self.cset[newcset.oid] = newcset
            else: # otherwise is an attribute
                self.set_attribute(tmp)
        self._obj_children.extend(self.cset) # Update the zObject children list
