"""
@author: Federico Vaga
@copyright: Federico Vaga 2012
@license: GPLv2
"""

BUS_PATH = "/sys/bus/zio/"

DEVICES_PATH = BUS_PATH + "devices/"

AVAILABLE_TRIGGERS = [] # list of available triggers (string)

AVAILABLE_BUFFERS = []  # list of available buffers (string)

DEVICES = []  # list of available devices (zdev object)

# sysfs standard attributes name tuples
DEV_ATTR_NAME = ("gain_factor", "offset", "resolution-bits", "max-sample-rate", "vref-src")

BUF_ATTR_NAME = ("max-buffer-len", "max-buffer-kb")

TRIG_ATTR_NAME = ("re-enable", "pre-samples", "post-samples")


