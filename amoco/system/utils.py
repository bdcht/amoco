# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
system/utils.py
===============

The system utils module implements various binary file format like
Intel HEX or Motorola SREC, commonly used for programming MCU, EEPROMs, etc.
"""

import struct
from amoco.system.core import DataIO, BinFormat
from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")

from amoco.ui.render import Token, highlight

from collections import defaultdict
import codecs

# our exception handler:
class FormatError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


##

# ------------------------------------------------------------------------------
# formatting facilities:

# init of reverse dict to get constant name from value.
# This dict is updated by using 'with' statement of Consts.
HEX_CONSTS = defaultdict(dict)


class Consts(object):
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        HEX_CONSTS[self.name] = {}
        self.globnames = set(globals().keys())

    def __exit__(self, exc_type, exc_value, traceback):
        G = globals()
        for k in set(G.keys()) - self.globnames:
            HEX_CONSTS[self.name][G[k]] = k


def token_address_fmt(k, x, cls=None, fmt=None):
    return highlight([(Token.Address, "0x%04x" % x)])


def token_constant_fmt(k, x, cls=None, fmt=None):
    try:
        s = x.pp__()
    except AttributeError:
        s = str(x)
    return highlight([(Token.Constant, s)],fmt)


def token_name_fmt(k, x, cls=None, fmt=None):
    try:
        return highlight([(Token.Name, HEX_CONSTS[k][x])],fmt)
    except KeyError:
        return token_constant_fmt(k, x, cls, fmt)


# The HEX Constants.
# ------------------------------------------------------------------------------

with Consts("HEXcode"):
    Data = 0
    EndOfFile = 1
    ExtendedSegmentAddress = 2
    StartSegmentAddress = 3
    ExtendedLinearAddress = 4
    StartLinearAddress = 5

# ------------------------------------------------------------------------------


class HEX(BinFormat):
    is_HEX = True
    def __init__(self, f, offset=0):
        self.L = []
        self._filename = f.name
        self._entrypoint = 0
        for line in f.readlines():
            l = HEXline(line)
            if l.HEXcode == StartSegmentAddress:
                self._entrypoint = (l.cs, l.ip)
            elif l.HEXcode == StartLinearAddress:
                self.entrypoint = l.eip
            self.L.append(l)

    @property
    def entrypoints(self):
        return [self._entrypoint]

    @property
    def filename(self):
        return self._filename

    def load_binary(self, mmap=None):
        seg = 0
        ela = 0
        mem = []
        for l in self.L:
            if l.HEXcode == ExtendedSegmentAddress:
                seg = l.base
            elif l.HEXcode == ExtendedLinearAddress:
                ela = l.ela
            elif l.HEXcode == Data:
                if ela:
                    address = (ela << 16) + l.address
                elif seg:
                    address = (seg * 16) + l.address
                else:
                    address = l.address
                mem.append((address, l.data))
        if mmap is not None:
            for k, v in mem:
                mmap.write(k, v)
        return mem

    def __str__(self):
        return "\n".join((str(l) for l in self.L))


# ------------------------------------------------------------------------------


class HEXline(object):
    def __init__(self, data):
        self.HEXcode = None
        self.set(data.strip())

    def set(self, line):
        try:
            assert line[0:1] == b":"
            self.count = int(line[1:3], 16)
            self.address = int(line[3:7], 16)
            self.HEXcode = int(line[7:9], 16)
            c = 9 + 2 * self.count
            self.data = codecs.decode(line[9:c], "hex")
            s = codecs.decode(line[1:-2], "hex")
            if isinstance(s, str):
                s = (ord(x) for x in s)
            cksum = -(sum(s) & 0xFF)
            self.cksum = cksum & 0xFF
            assert self.cksum == int(line[-2:], 16)
        except (AssertionError, ValueError):
            raise FormatError(line)
        v = codecs.encode(self.data, "hex")
        if self.HEXcode == ExtendedSegmentAddress:
            assert self.count == 2
            self.base = int(v, 16)
        if self.HEXcode == StartSegmentAddress:
            assert self.count == 4
            self.cs = int(v[:4], 16)
            self.ip = int(v[4:], 16)
        if self.HEXcode == ExtendedLinearAddress:
            assert self.count == 2
            self.ela = int(v, 16)
        if self.HEXcode == StartLinearAddress:
            assert self.count == 4
            self.eip = int(v, 16)

    def pack(self):
        s = ":%02X%04X%02X" % (self.count, self.address, self.HEXcode)
        s += codecs.encode(self.data, "hex").upper()
        s += "%02X" % self.cksum
        return s

    def __str__(self):
        h = token_name_fmt("HEXcode", self.HEXcode)
        if self.HEXcode == Data:
            return "[%s] %s: '%s'" % (
                h,
                token_address_fmt(None, self.address),
                codecs.encode(self.data, "hex"),
            )
        if self.HEXcode == EndOfFile:
            return "[%s]" % h
        if self.HEXcode == ExtendedSegmentAddress:
            return "[%s] %s" % (h, token_address_fmt(None, self.base))
        if self.HEXcode == StartSegmentAdress:
            return "[%s] %s:%s" % (
                h,
                token_address_fmt(None, self.cs),
                token_address_fmt(None, self.ip),
            )
        if self.HEXcode == ExtendedLinearAddress:
            return "[%s] %s" % (h, token_address_fmt(None, self.ela))


# ------------------------------------------------------------------------------

# The SREC Constants.
# ------------------------------------------------------------------------------

with Consts("SREC"):
    Header = 0
    Data16 = 1
    Data24 = 2
    Data32 = 3

    Count16 = 5
    Count24 = 6
    Start32 = 7
    Start24 = 8
    Start16 = 9

# ------------------------------------------------------------------------------


class SREC(BinFormat):
    is_SREC = True
    def __init__(self, f, offset=0):
        self.L = []
        self._entrypoint = 0
        self._filename = f.name
        for line in f.readlines():
            count = 0
            l = SRECline(line)
            if l.SRECtype == Header:
                self.name = l.data
            elif l.SRECtype in (Start16, Start24, Start32):
                self.entrypoint = l.address
            elif l.SRECtype in (Count16, Count24):
                assert count == l.address
            else:
                count += 1
            self.L.append(l)

    @property
    def entrypoints(self):
        return [self._entrypoint]

    @property
    def filename(self):
        return self._filename

    def load_binary(self, mmap=None):
        mem = []
        for l in self.L:
            mem.append((l.address, l.data))
        if mmap:
            for (k, v) in mem:
                mmap.write(k, v)
        return mem

    def __str__(self):
        return "\n".join((str(l) for l in self.L))


# ------------------------------------------------------------------------------


class SRECline(object):
    def __init__(self, data):
        self.SRECtype = None
        self.set(data.strip())

    def set(self, line):
        try:
            assert line[0:1] == b"S"
            # type:
            self.SRECtype = int(line[1:2], 10)
            # byte count:
            self.count = int(line[2:4], 16)
            # address:
            l = [4, 4, 6, 8, 0, 4, 6, 8, 6, 4][self.SRECtype]
            self.size = l
            self.address = int(line[4 : 4 + l], 16)
            # data:
            # c = 4+l+2*self.count
            self.data = codecs.decode(line[4 + l : -2], "hex")
            assert self.count == (l / 2) + len(self.data) + 1
            # checksum:
            s = codecs.decode(line[2:-2], "hex")
            if isinstance(s, str):
                s = (ord(x) for x in s)
            cksum = sum(s) & 0xFF
            self.cksum = cksum ^ 0xFF
            assert self.cksum == int(line[-2:], 16)
        except (AssertionError, ValueError):
            raise FormatError(line)

    def pack(self):
        s = "S%1d%02X" % (self.SRECtype, self.count)
        fa = "%%0%dX" % self.size
        s += fa % self.address
        s += codecs.encode(self.data, "hex").upper()
        s += "%02X" % self.cksum
        return s

    def __str__(self):
        h = token_name_fmt("SRECtype", self.SRECtype)
        if self.SRECtype == Header:
            return "[%s] %s: '%s'" % (
                h,
                token_address_fmt(None, self.address),
                self.data,
            )
        if self.SRECtype in (Data16, Data24, Data32):
            return "[%s] %s: '%s'" % (
                h,
                token_address_fmt(None, self.address),
                codecs.encode(self.data, "hex"),
            )
        if self.SRECtype in (Count16, Count24):
            return "[%s] %s" % (h, token_constant_fmt(None, self.address))
        if self.SRECtype in (Start16, Start24, Start32):
            return "[%s] %s" % (h, token_address_fmt(None, self.address))


def read_leb128(data, sign=1):
    result = 0
    shift = 0
    count = 0
    for b in data:
        if isinstance(b, bytes):
            b = ord(b)
        count += 1
        result |= (b & 0x7F) << shift
        shift += 7
        if b & 0x80 == 0:
            break
    if sign < 0 and (b & 0x40):
        result |= ~0 << shift
    return result, count


def read_uleb128(data):
    return read_leb128(data)


def read_sleb128(data):
    return read_leb128(data, -1)
