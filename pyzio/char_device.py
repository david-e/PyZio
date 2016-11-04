"""
@author: Federico Vaga <federico.vaga@gmail.com>
@copyright: Federico Vaga 2012
@license: GPLv2
"""

import os
import selectors

from pyzio.ctrl import ZioCtrl
from pyzio.interface import ZioInterface


class ZioCharDevice(ZioInterface):
    """
    This class represent the Char Device interface of ZIO. It has two char
    devices: one for control and one for data. The have both the same file
    permission.
    """

    def __init__(self, zobj):
        """
        Initialize ZioCharDevice class. The zobj parameter is the object
        which use this interface. This object should be a channel
        """
        ZioInterface.__init__(self, zobj)
        self.lastctrl = None
        self.__fdc = None
        self.__fdd = None
        # Set data and ctrl char devices
        self.ctrlfile = os.path.join(self.zio_interface_path, \
                                     self.interface_prefix + "-ctrl")
        self.datafile = os.path.join(self.zio_interface_path, \
                                     self.interface_prefix + "-data")
        self.__poll = selectors.DefaultSelector()

    def fileno_ctrl(self):
        """
        Return ctrl char device file descriptor
        """
        return self.__fdc

    def fileno_data(self):
        """
        Return data char device file descriptor
        """
        return self.__fdd

    def open_ctrl_data(self, perm=None):
        self.open_ctrl()
        self.open_data(perm)

    def open_data(self, perm=None):
        """
        Open data char device
        """
        if self.__fdd:
            return self.__fdd
        if not perm:
            if self.is_data_writable():
                perm = os.O_R
            elif self.is_data_readable():
                perm = os.O_RDONLY
            else:
                raise IOError('Data not readable or writable')
        evt = selectors.EVENT_WRITE if self.is_data_writable() \
            else selectors.EVENT_WRITE
        self.__fdd = os.open(self.datafile, perm)
        self.__poll.register(self.__fdd, evt)
        return self.__fdd
    
    def open_ctrl(self, perm=None):
        """
        Open ctrl char device
        """
        if self.__fdc:
            return
        if not perm:
            if self.is_data_writable():
                perm = os.O_R
            elif self.is_data_readable():
                perm = os.O_RDONLY
            else:
                raise IOError('Ctrl not readable or writable')
        self.__fdc = os.open(self.ctrlfile, perm)
        self.__poll.register(self.__fdc, selectors.EVENT_READ)

    def close_ctrl_data(self):
        self.close_ctrl()
        self.close_data()

    def close_data(self):
        """
        Close data char device
        """
        if self.__fdd == None:
            return
        self.__poll.unregister(self.__fdd)
        os.close(self.__fdd)
        self.__fdd = None

    def close_ctrl(self):
        """
        Close ctrl char device
        """
        if self.__fdc == None:
            return
        self.__poll.unregister(self.__fdc)
        os.close(self.__fdc)
        self.__fdc = None

    def read_ctrl(self):
        """
        If the control char device is open and it is readable, then it reads
        the control structure. Every time it internally store the control; it
        will be used as default when no control is provided
        """
        if self.__fdc == None or not self.is_ctrl_readable():
            raise IOError
        # Read the control
        bin_ctrl = os.read(self.__fdc, ZioCtrl.BASE_SIZE)
        self.lastctrl = ZioCtrl(bin_ctrl)
        return self.lastctrl

    def read_data(self, ctrl=None, unpack=True):
        """
        If the data char device is open and it is readable, then it reads
        the data
        """
        if self.__fdd == None or not self.is_data_readable():
            raise IOError
        if ctrl == None:
            if self.lastctrl == None:
                _ctrl = self.read_ctrl()
            _ctrl = self.lastctrl
        else:
            _ctrl = ctrl

        data_tmp = os.read(self.__fdd, _ctrl.ssize * _ctrl.nsamples)
        if unpack:
            return self._unpack_data(data_tmp, _ctrl.nsamples, _ctrl.ssize)
        else:
            return data_tmp

    def read_block(self, rctrl=True, rdata=True, unpack=True):
        """
        It read the control and the samples of a block from char devices.
        It stores the last control in self.lastCtrl. The parameter rctrl and
        rdata are boolean value: if True they acquire the associated
        information
        """
        ctrl = None
        samples = None

        if rctrl:
            ctrl = self.read_ctrl()
        if rdata:  # Read the data
            data = self.read_data(ctrl, unpack)
        return ctrl, data

    def write_ctrl(self, ctrl):
        raise NotImplementedError

    def write_data(self, samples):
        raise NotImplementedError

    def write_block(self, ctrl, samples):
        raise NotImplementedError

    def is_device_ready(self, timeout = 0):
        in_ready = False
        out_ready = False
        events = self.poll(timeout)
        if len(events) == 0:  # Check if it is possible to access device
            return False, False
        for __fd, flags in events:
            if flags & (selectors.EVENT_READ):
                in_ready = True
            elif flags & selectors.EVENT_WRITE:
                out_ready = True
        return in_ready, out_ready

    def poll(self, timeout=None):
        """
        It poll() both control and data. It return the Python's list of the
        events occurred on control or data
        """
        return self.__poll.select(timeout)