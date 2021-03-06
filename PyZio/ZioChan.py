"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""
import os
from os.path import join, isdir
from PyZio.ZioObject import ZioObject
from PyZio.ZioAttribute import ZioAttribute
from PyZio.ZioBuf import ZioBuf
from PyZio.ZioCtrl import ZioCtrl
from PyZio.ZioCharDevice import ZioCharDevice
from PyZio.ZioError import ZioInvalidControl

class ZioChan(ZioObject):
    """
    This class describes the zio_channel object from the ZIO framework.
    """

    def __init__(self, path, name):
        """
        It calls the __init__ function from ZioObject for a generic
        initialization; then it looks for attributes and buffer in its
        directory. All valid files are normal attributes. A directory can be a
        buffer or an interface.
        """
        ZioObject.__init__(self, path, name)
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
            self.attribute[tmp] = ZioAttribute(self.fullpath, tmp)
        # Update the zObject children list
        self.obj_children.append(self.buffer)
        if self.interface_type == None:
            print("No interface available for " + self.fullpath)
        elif self.interface_type == "cdev":
            # Set the interface to use (at the moment only Char Device)
            self.interface = ZioCharDevice(self)
        elif self.interface_type == "socket":
            pass

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
        try:
            fd_num = os.open(self.cur_ctrl, os.O_RDONLY)
            bin_ctrl = os.read(fd_num, 512)
            os.close(fd_num)
        except:
            raise
        else:
            ctrl = ZioCtrl()
            ctrl.unpack_to_ctrl(bin_ctrl)
            return ctrl

    def set_current_ctrl(self, ctrl):
        """
        It sets the current control.
        """
        if not (isinstance(ctrl, ZioCtrl) and ctrl.is_valid()):
            raise ZioInvalidControl(ctrl)

        try:
            fd_num = os.open(self.cur_ctrl, os.O_WRONLY)
            os.write(fd_num, ctrl.pack_to_bin())
            os.close(fd_num)
        except:
            raise
