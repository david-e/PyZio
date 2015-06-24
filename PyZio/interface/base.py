"""
@author: Federico Vaga <federico.vaga@gmail.com>
@copyright: Federico Vaga 2012
@license: GPLv2
"""
import logging
import os
import struct


class CtrlAttr(object):
    """
    It represent the python version of the zio_ctrl_attr structure
    """
    def __init__(self, sm, em, sattr, eattr):
        self.std_mask = sm
        self.ext_mask = em
        self.std_val = list(sattr)
        self.ext_val = list(eattr)

    def __eq__(self, other):
        if not isinstance(other, CtrlAttr):
            return False

        ret = True
        ret = ret and self.std_mask == other.std_mask
        ret = ret and self.ext_mask == other.ext_mask
        for val1, val2 in zip(self.std_val, other.std_val):
            ret = ret and val1 == val2
        for val1, val2 in zip(self.ext_val, other.ext_val):
            ret = ret and val1 == val2

        return ret

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        out = "Ctrl: standard mask " + hex(self.std_mask) + "\n"
        i = -1
        for val in self.std_val:
            i = i + 1
            if not self.std_mask & (1 << i):
                continue
            out = out + "Ctrl: std attr {0} \t{1} \t{2}\n".format(i, hex(val), val)

        out = out + "Ctrl: extended mask " + hex(self.ext_mask) + "\n"
        i = -1
        for val in self.ext_val:
            i = i + 1
            if not self.ext_mask & (1 << i):
                continue
            out = out + "Ctrl: ext attr {0} \t{1} \t{2}\n".format(i, hex(val), val)

        return out


class Tlv(object):
    """
    It represent the python version of the zio_tlv structure
    """
    def __init__(self, t, l, v):
        self.type = t
        self.len = l
        self.val = v


class Address(object):
    """
    It represent the python version of the zio_addr structure
    """
    def __init__(self, fam, htype, hid, did, cset, chan, dev):
        self.sa_family = fam
        self.host_type = htype
        self.hostid = hid
        self.dev_id = did
        self.cset_i = cset
        self.chan_i = chan
        self.devname = dev.replace("\x00", "")

    def __eq__(self, other):
        if not isinstance(other, Address):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        out = "dev {0}-{1}, cset {2}, chan {3}".format(
            self.devname, self.dev_id, self.cset_i, self.chan_i)
        return out


class TimeStamp(object):
    """
    It represent the python version of the zio_timestamp structure
    """
    def __init__(self, s, t, b):
        self.secs = s
        self.ticks = t
        self.bins = b

    def __eq__(self, other):
        if not isinstance(other, TimeStamp):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "{0}.{1} ({2})".format(self.secs, self.ticks, self.bins)


class Ctrl(object):
    """
    It represent the python verion of the zio_control structure
    """

    def __init__(self, binctrl=None):
        # Description of the control structure field's length
        self.packstring = "4B2I2H1H2B8BI2H12s3Q3I12s2HI16I32I2HI16I32I2I8B"
        #                  ^ ^ ^ ^           ^ ^ ^  ^        ^        ^

        # Control information
        self.major_version = 0
        self.minor_version = 0
        self.alarms_zio = 0
        self.alarms_dev = 0
        self.seq_num = 0
        self.nsamples = 0
        self.ssize = 0
        self.nbits = 0
        self.mem_offset = 0
        self.reserved = 0
        self.flags = 0
        self.triggername = ""
        # ZIO Address
        self.addr = None
        # ZIO Time Stamp
        self.tstamp = None
        # Device and Trigger Attributes
        self.attr_channel = None
        self.attr_trigger = None
        # ZIO TLV
        self.tlv = None

        self.binctrl = binctrl

    def __eq__(self, other):
        if not isinstance(other, Ctrl):
            return False

        ret = True
        # Fields
        ret = ret and self.major_version == other.major_version
        ret = ret and self.minor_version == other.minor_version
        ret = ret and self.alarms_zio == other.alarms_zio
        ret = ret and self.alarms_dev == other.alarms_dev
        ret = ret and self.seq_num == other.seq_num
        ret = ret and self.nsamples == other.nsamples
        ret = ret and self.ssize == other.ssize
        ret = ret and self.nbits == other.nbits
        ret = ret and self.mem_offset == other.mem_offset
        ret = ret and self.reserved == other.reserved
        ret = ret and self.flags == other.flags
        # Objects
        ret = ret and self.addr == other.addr
        ret = ret and self.tstamp == other.tstamp
        ret = ret and self.triggername == other.triggername
        ret = ret and self.attr_channel == other.attr_channel
        ret = ret and self.attr_trigger == other.attr_trigger

        return ret

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        # Line 1
        out = "Ctrl: version {0}.{1}, ".format(self.major_version, \
                                               self.minor_version)
        out = out + "trigger {0}, {1}\n".format(self.triggername, self.addr)
        # line 2
        out = out + "Ctrl: alarms {0} {1}\n".format(hex(self.alarms_zio), \
                                                  hex(self.alarms_dev))
        # line 3
        out = out + "Ctrl: seq {0}, size {1}, bits {2}, flags {3}\n".format(\
                    self.seq_num, self.ssize, self.nbits, hex(self.flags))
        # line 4
        out = out + "Ctrl: stamp {0}\n".format(self.tstamp)
        # channel's attributes
        out = out + "Ctrl: device attributes\n" + str(self.attr_channel)
        # trigger's attributes
        out = out + "Ctrl: trigger attributes\n" + str(self.attr_trigger)

        return out

    def is_valid(self):
        """
        The control must follow some rule. This function check if the value
        in this control are valid
        FIXME ONLY FOR OUTPUT
        """
        # nsamples must be pre_samples + post_samples
        attr_nsamples = self.attr_trigger.std_val[1] + self.attr_trigger.std_val[2]
        if self.nsamples != attr_nsamples:
            return False
        return True

    def unpack(self):
        """
        This function unpack a given binary control to fill the fields of
        this class. It use the self.packstring class attribute to unpack
        """
        ctrl = struct.unpack(self.packstring, self.binctrl)
        # 4B
        self.major_version = ctrl[0]
        self.minor_version = ctrl[1]
        self.alarms_zio = ctrl[2]
        self.alarms_dev = ctrl[3]
        # 2I
        self.seq_num = ctrl[4]
        self.nsamples = ctrl[5]
        # 2H
        self.ssize = ctrl[6]
        self.nbits = ctrl[7]
        # 1H2B8BI2H12s
        # ctrl[10] is a filler
        self.addr = Address(ctrl[8], ctrl[9], ctrl[11:19],
                               ctrl[19], ctrl[20], ctrl[21], ctrl[22])
        # 3Q
        self.tstamp = TimeStamp(ctrl[23], ctrl[24], ctrl[25])
        # 3I
        self.mem_offset = ctrl[26]
        self.reserved = ctrl[27]
        self.flags = ctrl[28]
        # 12s
        self.triggername = ctrl[29].replace("\x00", "")
        # 2HI16I32I
        self.attr_channel = CtrlAttr(ctrl[30], ctrl[32], ctrl[33:49], ctrl[49:81])
        # 2HI16I32I
        self.attr_trigger = CtrlAttr(ctrl[81], ctrl[83], ctrl[84:100], ctrl[100:132])
        self.tlv = Tlv(ctrl[132], ctrl[133], ctrl[134:142])

    def pack(self):
        """This function pack this control into a binary control"""
        pack_list = []
        pack_list.append(self.major_version)
        pack_list.append(self.minor_version)
        pack_list.append(self.alarms_zio)
        pack_list.append(self.alarms_dev)
        pack_list.append(self.seq_num)
        pack_list.append(self.nsamples)
        pack_list.append(self.ssize)
        pack_list.append(self.nbits)
        pack_list.append(self.addr.sa_family)
        pack_list.append(self.addr.host_type)
        pack_list.append(0)  # filler
        pack_list.extend(self.addr.hostid)
        pack_list.append(self.addr.dev_id)
        pack_list.append(self.addr.cset_i)
        pack_list.append(self.addr.chan_i)
        pack_list.append(self.addr.devname)
        pack_list.append(self.tstamp.seconds)
        pack_list.append(self.tstamp.ticks)
        pack_list.append(self.tstamp.bins)
        pack_list.append(self.mem_offset)
        pack_list.append(self.reserved)
        pack_list.append(self.flags)
        pack_list.append(self.triggername)
        pack_list.append(self.attr_channel.std_mask)
        pack_list.append(0)  # filler
        pack_list.append(self.attr_channel.ext_mask)
        pack_list.extend(self.attr_channel.std_val)
        pack_list.extend(self.attr_channel.ext_val)
        pack_list.append(self.attr_trigger.std_mask)
        pack_list.append(0)  # filler
        pack_list.append(self.attr_trigger.ext_mask)
        pack_list.extend(self.attr_trigger.std_val)
        pack_list.extend(self.attr_trigger.ext_val)
        pack_list.append(self.tlv.type)
        pack_list.append(self.tlv.len)
        pack_list.extend(self.tlv.val)
        return struct.pack(self.packstring, *pack_list)

    def clear(self):
        """
        It clears the content of the class
        """
        self.__init__()


class Interface(object):
    """
    It is a generic abstraction of a ZIO interface: Char Device and socket.
    """

    _interface_path = "/dev/zio/"

    def __init__(self, parent=None):
        self.parent = parent
        self._interface_prefix = self.parent.devname
        self._ctrlfile = "" # Full path to the control file
        self._datafile = "" # Full path to the data file
        self._lastctrl = None
        self.expose_methods = []
        logging.debug("new %s", self.__class__.__name__)

    def is_ctrl_readable(self):
        """
        It returns if you can read control from device
        """
        return os.access(self._ctrlfile, os.R_OK)

    def is_ctrl_writable(self):
        """
        It returns if you can write control into device
        """
        return os.access(self._ctrlfile, os.W_OK)

    def is_data_readable(self):
        """
        It returns if you can read data from device
        """
        return os.access(self._datafile, os.R_OK)

    def is_data_writable(self):
        """
        It returns if you can write data into device
        """
        return os.access(self._datafile, os.W_OK)

    def is_device_ready(self, timeout = 0):
        """
        It is a mandatory method for the derived class. It must returns two
        boolean value: the first is 'True' if the device is ready to be read;
        the second is 'True if the device is ready to be write'. The optional
        parameter 'timeout' sets the time to wait before return. The '0' value
        mean immediately, 'None' mean infinite, and a different value represent
        the milliseconds to wait.
        """
        raise NotImplementedError

    # Mandatory Open Methods
    def open_ctrl_data(self, perm):
        """
        It is a mandatory method for the derived class. It opens both control
        and data source. The 'perm' parameter set the permission to use during
        open
        """
        raise NotImplementedError

    def open_data(self, perm):
        """
        It is a mandatory method for the derived class. It opens samples's
        source. The 'perm' parameter set the permission to use during open
        """
        raise NotImplementedError

    def open_ctrl(self, perm):
        """
        It is a mandatory method for the derived class. It opens control's
        source. The 'perm' parameter set the permission to use during open
        """
        raise NotImplementedError

    # Mandatory Close Methods
    def close_ctrl_data(self):
        """
        It is a mandatory method for the derived class. It closes both control
        and data source.
        """
        raise NotImplementedError

    def close_data(self):
        """
        It is a mandatory method for the derived class. It closes sample's
        source.
        """
        raise NotImplementedError

    def close_ctrl(self):
        """
        It is a mandatory method for the derived class. It closes control's
        source.
        """
        raise NotImplementedError

    # Mandatory Read/Write Methods
    def read_ctrl(self):
        """
        It is a mandatory method for the derived class. It reads, and returns,
        a control structure from a channel.
        """
        raise NotImplementedError

    def read_data(self, ctrl = None, unpack = True):
        """
        It is a mandatory method for the derived class. It reads, and returns,
        samples from a channel.
        """
        raise NotImplementedError

    def read_block(self, rctrl = True, rdata = True, unpack = True):
        """
        It is a mandatory method for the derived class. It reads, and returns,
        a block from a channel. The block is a python set with control and
        data.
        """
        raise NotImplementedError

    def write_ctrl(self, ctrl):
        """
        It is a mandatory method for the derived class. It writes a control
        to a channel
        """
        raise NotImplementedError

    def write_data(self, samples):
        """
        It is a mandatory method for the derived class. It writes samples to
        a channel
        """
        raise NotImplementedError

    def write_block(self, ctrl, samples):
        """
        It is a mandatory method for the derived class. It writes both control
        and samples to a channel
        """
        raise NotImplementedError

    def _unpack_data(self, data, nsamples, ssize):
        """
        It unpacks 'data' of nsamples elements of the same size 'ssize'
        """
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

