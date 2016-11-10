"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""
import logging
import os

from os.path import join, isdir

from pyzio.attribute import ZioAttribute
from pyzio.buffer import ZioBuf
from pyzio.ctrl import ZioCtrl
from pyzio.char_device import ZioCharDevice
from pyzio.errors import ZioInvalidControl
from pyzio.object import ZioObject


class ZioChan(ZioObject):
    """
    This class describes the zio_channel object from the ZIO framework.
    """

    def __init__(self, path, name, cset):
        """
        It calls the __init__ function from ZioObject for a generic
        initialization; then it looks for attributes and buffer in its
        directory. All valid files are normal attributes. A directory can be a
        buffer or an interface.
        """
        ZioObject.__init__(self, path, name)
        self.cset = cset
        self.update()

    def update(self):
        self.cur_ctrl = None
        self.buffer = None
        self.interface_type = None
        # Inspect all files and directory
        for tmp in os.listdir(self.fullpath):
            # Skip if the element it is not valid
            if not self.is_valid_sysfs_element(tmp):
                continue
            # If the element is "buffer" then create a zBuf instance
            if tmp == "buffer" and isdir(join(self.fullpath, tmp)):
                self.buffer = ZioBuf(self.fullpath, tmp)
                continue
            if tmp == "current-control":
                self.cur_ctrl = join(self.fullpath, tmp)
                continue
            if tmp == "zio-cdev" and isdir(join(self.fullpath, tmp)):
                self.interface_type = "cdev" # Init later, we need attributes
                continue
            # Otherwise it is a generic attribute
            self.set_attribute(tmp)
        # Update the zObject children list
        self._obj_children.append(self.buffer)
        if self.interface_type == None:
            logging.debug("No interface available for " + self.fullpath)
        elif self.interface_type == "cdev":
            # Set the interface to use (at the moment only Char Device)
            self.interface = ZioCharDevice(self)
        elif self.interface_type == "socket":
            pass

    def __enter__(self):
        if not self.enable:
            raise IOError
        if self.interface_type != "cdev":
            raise NotImplementedError
        self.interface.open_ctrl_data()
        return self
    
    def __exit__(self, type, value, tb):
        if self.interface_type != "cdev":
            raise NotImplementedError
        self.interface.close_ctrl_data()

    def __getattribute__(self, name):
        try:
            obj = super(ZioChan, self).__getattribute__(name)
        except AttributeError:
            iface = super(ZioChan, self).__getattribute__('interface')
            if not iface or not hasattr(iface, name):
                raise AttributeError
            obj = getattr(iface, name)
        return obj

    def is_interleaved(self):
        """
        It returns True if this is an interleaved channel
        """
        return True if self.name == "chani" else False

    def update_buffer(self):
        """
        It updates the buffer object for this channel. If user changes the
        current buffer from cset, then channel instance of the buffer must be
        updated
        """
        self.buffer = ZioBuf(self.fullpath, "buffer")

    def get_current_ctrl(self):
        """
        It gets the current control. It is only a wrapper of the setCtrl
        method of zCtrl; user can use directly that method
        """
        fd_num = os.open(self.cur_ctrl, os.O_RDONLY)
        ctrl = ZioCtrl.read(fd_num)
        os.close(fd_num)
        return ctrl

    def set_current_ctrl(self, ctrl):
        """
        It sets the current control.
        """
        
        fd_num = os.open(self.cur_ctrl, os.O_WRONLY)
        ZioCtrl.write(fd_num, ctrl)
        os.close(fd_num)
