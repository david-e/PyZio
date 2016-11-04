"""
@author: Davide Silvestri
@copyright: Davide Silvestri 2016
@license: GPLv2
"""
import os

from pyzio.config import devices_path, zio_bus_path
from pyzio.device import ZioDev


def yield_devices():
    """ List available devices """
    for zdev in sorted(os.listdir(devices_path)):
        if "hw-" in zdev:
            continue
        yield ZioDev(devices_path, zdev)


def yield_buffers():
    """ List available buffers """
    with open(zio_bus_path + "/available_buffers", "r") as f:
        for line in f:
            yield line.rstrip('\n')


def yield_triggers():
    """ List of available triggers"""
    with open(zio_bus_path + "/available_triggers", "r") as f:
        for line in f:
            yield line.rstrip('\n')


class ZioManager(object):
    """ It handles all the ZIO resources """

    def __init__(self):
        self.update()
    
    def update(self):
        self.Buffers = list(yield_buffers())
        self._update_devices()
        self.Triggers = list(yield_triggers())
    
    def _update_devices(self):
        devs = {}
        for zdev in yield_devices():
            name, devid = zdev.devname.split('-')
            if not zdev.name in devs:
                devs[zdev.name] = {}     
            devs[zdev.name][int(devid)] = zdev
        self.Devices = devs


def get_manager():
    return ZioManager()

