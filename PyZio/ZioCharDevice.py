"""
@author: Federico Vaga <federico.vaga@gmail.com>
@copyright: Federico Vaga 2012
@license: GPLv2
"""

import os
import struct
import select

from PyZio.ZioInterface import ZioInterface
from PyZio.ZioCtrl import ZioCtrl

class ZioCharDevice(ZioInterface):
    """This class represent the Char Device interface of ZIO. It has to char
    device: one for control and one for data. The have both the same file
    permission."""

    def __init__(self, zobj):
        """Initialize ZioCharDevice class. The zobj parameter is the object
        which use this interface. This object should be a channel"""
        ZioInterface.__init__(self, zobj)

        self.fdc = None
        self.fdd = None
        # Set data and ctrl char devices
        self.ctrlfile = os.path.join(self.zio_interface_path, \
                                     self.interface_prefix + "-ctrl")
        self.datafile = os.path.join(self.zio_interface_path, \
                                     self.interface_prefix + "-data")

        self.lastctrl = None


    def fileno_ctrl(self):
        """Return ctrl char device file descriptor"""
        return self.fdc
    def fileno_data(self):
        """Return data char device file descriptor"""
        return self.fdd

    def open_ctrl_data(self, perm):
        self.open_ctrl(perm)
        self.open_data(perm)

    def open_data(self, perm):
        """Open data char device"""
        if self.fdd == None:
            self.fdd = os.open(self.datafile, perm)
        else:
            print("File already open")
    def open_ctrl(self, perm):
        """Open ctrl char device"""
        if self.fdc == None:
            self.fdc = os.open(self.ctrlfile, perm)
        else:
            print("File already open")

    def close_ctrl_data(self):
        self.close_ctrl()
        self.close_data()

    def close_data(self):
        """Close data char device"""
        if self.fdd != None:
            os.close(self.fdd)
            self.fdd = None
    def close_ctrl(self):
        """Close ctrl char device"""
        if self.fdc != None:
            os.close(self.fdc)
            self.fdc = None


    def read_ctrl(self):
        """If the control char device is open and it is readable, then it reads
        the control structure. Every time it internally store the control; it
        will be used as default when no control is provided"""
        if self.fdc == None or not self.is_ctrl_readable():
            return None
        # Read the control
        bin_ctrl = os.read(self.fdc, 512)

        ctrl = ZioCtrl()
        self.lastctrl = ctrl
        ctrl.unpack_to_ctrl(bin_ctrl)
        return ctrl

    def read_data(self, ctrl = None, unpack = True):
        """If the data char device is open and it is readable, then it reads
        the data"""
        if self.fdd == None or not self.is_data_readable():
            return None

        if ctrl == None:
            if self.lastCtrl == None:
                print("WARNING: you never read control, then only 16byte will be read")
                tmpctrl = ZioCtrl()
                tmpctrl.ssize = 1
                tmpctrl.nsamples = 16
            else:
                tmpctrl = self.lastCtrl
        else:
            tmpctrl = ctrl

        data_tmp = os.read(self.fdd, tmpctrl.ssize * tmpctrl.nsamples)
        if unpack:
            return self.__unpack_data(data_tmp, tmpctrl.nsamples, tmpctrl.ssize)
        else:
            return data_tmp

    def read_block(self, rctrl, rdata, unpack = True):
        """It read the control and the samples of a block from char devices.
        It stores the last control in self.lastCtrl. The parameter rctrl and
        rdata are boolean value: if True they acquire the associated
        information"""
        ctrl = None
        samples = None

        if self.fdc == None:
            self.open_ctrl(os.O_RDONLY)
        if self.fdd == None:
            self.open_data(os.O_RDONLY)

        if rctrl:
            ctrl = self.read_ctrl()

        if rdata: # Read the data
            samples = self.read_data(ctrl, unpack)

        return ctrl, samples


    def is_device_ready(self, timeout = 0):
        ret = self.select(True, True, timeout)
        if ret == None:  # Check if it is possible to access device
            return False

        for l in ret:
            if len(l) > 0:  # If a list is not empty, then device is ready
                return True

        return False

    def select(self, rctrl, rdata, timeout = None):
        """It select() both control and data. It returns None if it is not
        possibile to select() char devices; otherwise, it returns the select()
        output"""
        lst = []

        if rctrl:
            lst.append(self.fdc)
        if rdata:
            lst.append(self.fdd)

        if self.is_ctrl_writable() and self.is_data_writable():
            return select.select([], lst, [], timeout)
        elif self.is_ctrl_readable() and self.is_data_readable():
            return select.select(lst, [], [], timeout)
        else:
            return None
    # # # # # PRIVATE FUNCTIONS # # # # #
    def __unpack_data(self, data, nsamples, ssize):
        """It unpacks data in a list of nsamples elements"""
        fmt = "b"
        if ssize == 1:
            fmt = "B"
        elif ssize == 2:
            fmt = "H"
        elif ssize == 4:
            fmt = "I"
        elif ssize == 8:
            fmt = "Q"
        return struct.unpack((str(nsamples) + fmt), data)
