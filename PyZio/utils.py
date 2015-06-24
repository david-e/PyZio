"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""

import logging
import os
import select

from .config import AVAILABLE_BUFFERS, BUS_PATH, DEVICES, DEVICES_PATH, AVAILABLE_TRIGGERS
from . import Channel, Cset, Device

def is_loaded():
    """It returns true if ZIO is loaded correctly, otherwise it returns false.
    It considers ZIO correctly loaded if the path to zio in sysfs exists, and
    if the bus attribute available_buffers and available_triggers exists"""
    if not os.path.exists(BUS_PATH):
        logging.error("ZIO is not loaded")
        return False

    if not os.access(BUS_PATH + "/available_buffers", os.R_OK) and \
       not os.access(BUS_PATH + "/available_triggers", os.R_OK):
        logging.error("ZIO is not loaded correctly")
        return False
    return True


def list_devices():
    """It updates the internal list of available devices"""
    del DEVICES[:]
    for zdev in os.listdir(DEVICES_PATH):
        if "hw-" in zdev:
            continue
        p = os.path.join(DEVICES_PATH, zdev)
        DEVICES.append(Device(p))
    return DEVICES


def list_buffers_type():
    """It updates the internal list of available buffers"""
    del AVAILABLE_BUFFERS[:]
    with open(BUS_PATH + "/available_buffers", "r") as f:
        for line in f:
            AVAILABLE_BUFFERS.append(line.rstrip('\n'))
    return AVAILABLE_BUFFERS


def list_triggers_type():
    """It updates the internal list of available triggers"""
    del AVAILABLE_TRIGGERS[:]
    with open(BUS_PATH + "/available_triggers", "r") as f:
        for line in f:
            AVAILABLE_TRIGGERS.append(line.rstrip('\n'))
    return AVAILABLE_TRIGGERS


def list_all():
    """It updates the internal list of available devices, buffers and triggers"""
    return list_devices(), list_triggers_type(), list_buffers_type()


def _open_device(device):
    csets = {}
    for cset in device.cset:
        csets.update(_open_cset(cset))
    return csets


def _open_cset(cset):
    chans = {}
    for chan in cset.channels:
        chans.update(_open_chan(chan))
    return chans


def _open_chan(chan):
    mode = os.O_RDONLY if chan.parent.direction == 'input' else os.O_WRONLY
    chan_ctrl_fileno = chan.interface.open_ctrl(mode)
    return {
        chan_ctrl_fileno: chan
    }


def _open(zio_object):
    if type(zio_object) is Device:
        return _open_device(zio_object)
    elif type(zio_object) is Cset:
        return _open_cset(zio_object)
    elif type(zio_object) is Channel:
        return _open_chan(zio_object)
    return {}


def open_channels(zio_objects=None):
    chans = {}
    if not zio_objects:
        zio_objects = list_devices()
    if not type(zio_objects) in (list, tuple):
        zio_objects = [zio_objects]
    for obj in zio_objects:
        chans.update(_open(obj))
    return chans


def epoll_register(zio_opened_dict, filter_direction=None):
    ep = select.epoll()
    for fileno, chan in zio_opened_dict.iteritems():
        direction = chan.parent.direction
        if not filter_direction or filter_direction == direction:
            mode = select.EPOLLIN if direction == 'input'else select.EPOLLOUT
            ep.register(fileno, mode)
    return ep


def wait_for_blocks(zio_objects, timeout=0, epoll_obj=None, direction=None):
    zio_opened_dict = open_channels(zio_objects)
    if not epoll_obj or direction:
        epoll_obj = epoll_register(zio_opened_dict, direction)
    while True:
        events = epoll_obj.poll(timeout)
        for fd, ev in events:
            if not (ev & select.EPOLLIN):
                continue
            chan = zio_opened_dict.get(fd, None)
            if not chan:
                continue
            yield chan, chan.read_block()


