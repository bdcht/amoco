# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.core import BinFormat, DataIO
from amoco.system.memory import MemoryMap

from amoco.logger import Log
logger = Log(__name__)
logger.debug("loading module")

from .formatters import *
import codecs

# our exception handler:
class HEXError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


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
        self.__lines = None
        self.__dataio = None

    @property
    def entrypoints(self):
        return [self._entrypoint]

    @property
    def filename(self):
        return self._filename

    def load_binary(self, mmap=None):
        if self.__lines is None:
            self.decode()
        if mmap is not None:
            for k, v in self.__lines:
                mmap.write(k, v)

    def decode(self):
        seg = 0
        ela = 0
        lines = []
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
                lines.append((address, l.data))
        m = MemoryMap()
        self.__lines = lines
        for k, v in lines:
            m.write(k, v)
        if len(m._zones)==1:
            self.__dataio = DataIO(m._zones[None].dump())

    @property
    def dataio(self):
        if self.__dataio is None:
            self.decode()
        return self.__dataio

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
            raise HEXError(line)
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

