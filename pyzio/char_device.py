"""
@author: Federico Vaga <federico.vaga@gmail.com>
@copyright: Federico Vaga 2012
@license: GPLv2
"""

import mmap
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
        self._fdc = None
        self._fdd = None
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
        fdc = self.open_ctrl()
        fdd = self.open_data(perm)
        return fdc, fdd

    def open_data(self, perm=None):
        """
        Open data char device
        """
        if self._fdd:
            return self._fdd
        if not perm:
            if self.is_data_writable():
                perm = 'wb'
            elif self.is_data_readable():
                perm = 'rb'
            else:
                raise IOError('Data not readable or writable')
        evt = selectors.EVENT_WRITE if self.is_data_writable() \
            else selectors.EVENT_WRITE
        self.__fdd = open(self.datafile, perm)
        try:  # mmap is more efficient then file, but requires zio-buf-vmalloc
            self.__fdm = mmap.mmap(self.__fdd.fileno(), 0)
        except:
            self.__fdm = None
        self._fdd = self.__fdm or self.__fdd
        self.__poll.register(self.__fdd, evt)
        return self._fdd

    def open_ctrl(self, perm=None):
        """
        Open ctrl char device
        """
        if self._fdc:
            return self._fdc
        if not perm:
            if self.is_data_writable():
                perm = 'wb'
            elif self.is_data_readable():
                perm = 'rb'
            else:
                raise IOError('Ctrl not readable or writable')
        self.__fdc = open(self.ctrlfile, perm)
        try:  # mmap is more efficient then file, but requires zio-buf-vmalloc
            self.__fcm = mmap.mmap(self.__fdc.fileno(), 0)
        except:
            self.__fcm = None
        self._fdc = self.__fcm or self.__fdc
        self.__poll.register(self.__fdc, selectors.EVENT_READ)
        return self._fdc

    def close_ctrl_data(self):
        self.close_ctrl()
        self.close_data()

    def close_data(self):
        """
        Close data char device
        """
        if self.__fdm:
            self.__fdm.close()
        if self._fdd is None:
            return
        self.__poll.unregister(self.__fdd)
        os.close(self.__fdd)
        self.__fdd = self._fd = None

    def close_ctrl(self):
        """
        Close ctrl char device
        """
        if self.__fcm:
            self.__fcm.close()
        if self._fdc is None:
            return
        self.__poll.unregister(self.__fdc)
        os.close(self.__fdc)
        self.__fdc = self._fdc = None

    def read_ctrl(self):
        """
        If the control char device is open and it is readable, then it reads
        the control structure. Every time it internally store the control; it
        will be used as default when no control is provided
        """
        #if self.__fdc == None or not self.is_ctrl_readable():
        #    raise IOError
        # Read the control
        bin_ctrl = self._fdc.read(ZioCtrl.BASE_SIZE)
        ctrl = ZioCtrl(bin_ctrl)
        self.lastctrl = ctrl
        return ctrl

    def read_data(self, ctrl=None, unpack=True):
        """
        If the data char device is open and it is readable, then it reads
        the data
        """
        #if self.__fdd == None or not self.is_data_readable():
        #    raise IOError
        ctrl = ctrl or self.lastctrl or self.read_ctrl()
        data_tmp = self._fdd.read(ctrl.ssize * ctrl.nsamples)
        if not unpack:
            return data_tmp
        return self._unpack_data(data_tmp, ctrl.nsamples, ctrl.ssize)

    def read_block(self, unpack=True):
        """
        It read the control and the samples of a block from char devices.
        It stores the last control in self.lastCtrl. The parameter rctrl and
        rdata are boolean value: if True they acquire the associated
        information
        """
        ctrl = self.read_ctrl()
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