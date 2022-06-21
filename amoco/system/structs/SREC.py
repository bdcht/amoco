# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.core import BinFormat, DataIO
from amoco.system.memory import MemoryMap

from .formatters import *

from amoco.logger import Log
logger = Log(__name__)
logger.debug("loading module")

import codecs

# our exception handler:
class SRECError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)

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
        count = 0
        i = 0
        for line in f.readlines():
            if not line.strip():
                continue
            l = SRECline(line)
            if l.SRECtype == Header:
                self.name = l.data
            elif l.SRECtype in (Start16, Start24, Start32):
                if l.address:
                    self.entrypoint = l.address
                count = 0
            elif l.SRECtype in (Count16, Count24):
                if count != l.address:
                    logger.error("invalid count in SREC format at line %d"%i)
            elif l.SRECtype in (Data16,Data24,Data32):
                count += 1
            else:
                logger.warn("unknown SRECtype: %d"%l.SRECtype)
            self.L.append(l)
            i += 1
        self.__dataio = None

    @property
    def entrypoints(self):
        return [self._entrypoint]

    @property
    def filename(self):
        return self._filename

    def load_binary(self, mmap=None):
        mem = []
        for l in self.L:
            if l.SRECtype in (Data16,Data24,Data32):
                mem.append((l.address, l.data))
        if mmap is not None:
            for (k, v) in mem:
                mmap.write(k, v)

    def decode(self):
        mem = []
        for l in self.L:
            if l.SRECtype in (Data16,Data24,Data32):
                mem.append((l.address, l.data))
        m = MemoryMap()
        for (k, v) in mem:
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
            if self.SRECtype in (Count16, Count24):
                r = 2*self.count
                if r-2 != l:
                    l = r-2
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
            raise SRECError(line)

    def pack(self):
        s = b"S%1d%02X" % (self.SRECtype, self.count)
        fa = b"%%0%dX" % self.size
        s += fa % self.address
        s += codecs.encode(self.data, "hex").upper()
        s += b"%02X" % self.cksum
        return s

    def __str__(self):
        h = token_name_fmt("SRECtype", self.SRECtype)
        if self.SRECtype == Header:
            return "[%s] %s: %s" % (
                h,
                token_address_fmt(None, self.address),
                self.data,
            )
        if self.SRECtype in (Data16, Data24, Data32):
            return "[%s] %s: %s" % (
                h,
                token_address_fmt(None, self.address),
                self.data,
            )
        if self.SRECtype in (Count16, Count24):
            return "[%s] %s" % (h, token_constant_fmt(None, self.address))
        if self.SRECtype in (Start16, Start24, Start32):
            return "[%s] %s" % (h, token_address_fmt(None, self.address))


