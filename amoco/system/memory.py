# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2007-2019 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
system/memory.py
================

This module defines all Memory related classes.

The main class of amoco's Memory model is :class:`MemoryMap`.
It provides a way to represent both concrete and abstract symbolic values
located in the virtual memory space of a process.
In order to allow addresses to be symbolic as well, the MemoryMap is
organised as a collection of :class:`MemoryZone`.
A zone holds values located at addresses that are integer offsets
related to a symbolic expression. A default zone with related address set
to ``None`` holds values at concrete (virtual) addresses in every MemoryMap.
"""


from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")

from bisect import bisect_left
from amoco.cas.expressions import exp

# ------------------------------------------------------------------------------
class MemoryMap(object):
    """Provides a way to represent concrete and abstract symbolic values
    located in the virtual memory space of a process.
    A MemoryMap is organised as a collection of :class:`MemoryZone`.

    Attributes:
        _zones : dictionary of zones, keys are the related address expressions.

    Methods:
        newzone(label): creates a new memory zone with the given label related
            expression.

        locate(address): returns the memory object that maps the provided
            address expression.

        reference(address): returns a couple (rel,offset) based on the given
            address, an integer, a string or an expression allowing to find
            a candidate zone within memory.

        read(address,l): reads l bytes at address. returns a list of
            datadiv values.

        write(address,expr,endian=1): writes given expression at
            given (possibly symbolic) address. Default endianness is 'little'.
            Use endian=-1 to indicate big endian convention.

        restruct(): optimize all zones to merge contiguous raw bytes into single
            mo objects.

        grep(pattern): find all occurences of the given regular expression in
            the raw bytes objects of all memory zones.

        merge(other): update this MemoryMap with a new MemoryMap, merging
            overlapping zones with values from the new map. 
    """

    __slots__ = ["_zones", "misc"]

    def __init__(self):
        self._zones = {None: MemoryZone()}
        self.misc = {}

    def newzone(self, label):
        z = MemoryZone()
        z.rel = label
        self._zones[label] = z
        return z

    def reference(self, address):
        if isinstance(address, int):
            return (None, address)
        elif isinstance(address, str):
            return (address, 0)
        try:
            r, a = (address.base, address.disp)
            if r._is_cst:
                return (None, (r + a).v)
            return (r, a)
        except AttributeError:
            if address._is_cst:
                return (None, address.v)
        raise MemoryError(address)

    def __len__(self):
        sta, sto = self._zones[None].range()
        return sto - sta

    def __str__(self):
        return "\n".join([str(z) for z in self._zones.values()])

    def read(self, address, l):
        r, o = self.reference(address)
        if r in self._zones:
            return self._zones[r].read(o, l)
        else:
            raise MemoryError(address)

    def write(self, address, expr, endian=1):
        r, o = self.reference(address)
        if r is not None and not r._is_def:
            # write to undefined (top):
            raise MemoryError(address)
        if not r in self._zones:
            z = self.newzone(r)
        else:
            z = self._zones[r]
        z.write(o, expr, endian)

    def __getitem__(self, i):
        sta, sto = self._zones[None].range()
        address, sto, _ = i.indices(sto)
        res = self.read(address, sto - address)
        try:
            return b"".join(res)
        except Exception:
            return res

    def restruct(self):
        for z in iter(self._zones.values()):
            z.restruct()

    def grep(self, pattern):
        res = []
        for z in iter(self._zones.values()):
            zres = z.grep(pattern)
            if z.rel is not None:
                zres = [z.rel + r for r in zres]
            res.extend(zres)
        return res

    def copy(self):
        mm = self.__class__()
        for k, z in self._zones.items():
            mm._zones[k] = z.copy()
        return mm

    def merge(self, other):
        for r, z in other._zones.items():
            if r in self._zones:
                for o in z._map:
                    self._zones[r].addtomap(o)
            else:
                self._zones[r] = z


# ------------------------------------------------------------------------------
class MemoryZone(object):
    """A MemoryZone contains mo objects at addresses that are integer offsets
    related to a symbolic expression. A default zone with related address set
    to None holds values at concrete addresses in every :class:`MemoryMap`.

    Args:
        rel (exp): the relative symbolic expression, defaults to None.

    Attributes:
        rel : the relative symbolic expression, or None.
        _map : the ordered list of mo objects of this zone.

    Methods:
        range(): returns the lowest and highest addresses currently used by
            mo objects of this zone.

        locate(vaddr): if the given address is within range, return the
            index of the corresponding mo object in _map, otherwise
            return None.

        read(vaddr,l): reads l bytes starting at vaddr. returns a list of
            datadiv values, unmapped areas are returned as *bottom* exp.

        write(vaddr,data): writes data expression or
            bytes at given (offset) address.

        addtomap(z): add (possibly overlapping) :class:`mo` object z to the
            _map, eventually adjusting other objects.

        restruct(): optimize the zone to merge contiguous raw bytes into single
            mo objects.

        shift(offset): shift all mo objects by a given offset.

        grep(pattern): find all occurences of the given regular expression in
            the raw bytes objects of the zone.
    """

    __slots__ = ["rel", "_map", "__cache", "__hist"]

    def __init__(self, rel=None):
        self.rel = rel
        self._map = []
        self.__cache = []  # speedup locate method
        self.__hist = []

    def range(self):
        try:
            return (self._map[0].vaddr, self._map[-1].end)
        except IndexError:
            return (0, 0)

    def __str__(self):
        l = ["<MemoryZone rel=%s :" % str(self.rel)]
        for z in self._map:
            l.append("\t %s" % str(z))
        return "\n".join(l) + ">"

    def __update_cache(self):
        self.__cache = [z.vaddr for z in self._map]

    def copy(self):
        z = MemoryZone(self.rel)
        z._map = [o.copy() for o in self._map]
        z.restruct()
        return z

    def locate(self, vaddr):
        p = self.__cache
        if vaddr in p:
            return p.index(vaddr)
        i = bisect_left(p, vaddr)
        if i == 0:
            return None
        else:
            return i - 1

    def read(self, vaddr, l):
        void = exp
        res = []
        i = self.locate(vaddr)
        if i is None:
            if len(self._map) == 0:
                return [void(l * 8)]
            v0 = self._map[0].vaddr
            # Don't test if (vaddr+l)<=v0 because we need the test to be
            # true if vaddr or v0 contain label/symbols
            if not (v0 < (vaddr + l)):
                return [void(l * 8)]
            res.append(void((v0 - vaddr) * 8))
            l = (vaddr + l) - v0
            vaddr = v0
            i = 0
        ll = l
        while ll > 0:
            try:
                data, ll = self._map[i].read(vaddr, ll)
            except IndexError:
                res.append(void(ll * 8))
                ll = 0
                break
            if data is None:
                vi = self.__cache[i]
                if vaddr < vi:
                    l = min(vaddr + ll, vi) - vaddr
                    data = void(l * 8)
                    ll -= l
                    i -= 1
            if data is not None:
                vaddr += len(data)
                res.append(data)
            i += 1
        assert ll == 0
        return res

    def read_history(self, vaddr, l):
        H = []
        z = MemoryZone(self.rel)
        for h in self.__hist:
            z._map = h
            z.restruct()
            H.append(z.read(vaddr, l))
        return H

    def write(self, vaddr, data, endian=1):
        self.addtomap(mo(vaddr, data, endian))

    def addtomap(self, z):
        i = self.locate(z.vaddr)
        j = self.locate(z.end)
        # h = []
        if j is None:
            assert i is None or i == 0
            self._map.insert(0, z)
            self.__update_cache()
            return
        if j == i:
            ii = self._map[i].copy()
            ii.trim(z.vaddr)
            # h.insert(0,ii)
            Z = self._map[i].write(z.vaddr, z.data.val, z.data.endian)
            i += 1
            for newz in Z:
                self._map.insert(i, newz)
                i += 1
            self.__update_cache()
            return
        # i!=j cases:
        if i is not None:
            assert j >= i
        # delete & update every overwritten zones
        # by adjusting [i,j]:
        if z.end in self._map[j]:
            jj = self._map[j].copy()
            jj.setlen(z.end - z.vaddr)
            # h.insert(0,jj)
            self._map[j].trim(z.end)
        else:
            j += 1
        Z = [z]
        if i is None:
            i = -1
        elif z.vaddr <= self._map[i].end:
            ii = self._map[i].copy()
            ii.trim(z.vaddr)
            # h.insert(0,ii)
            # overright data:
            Z = self._map[i].write(z.vaddr, z.data.val, z.data.endian)
        i += 1
        # h = self._map[i:j]+h
        del self._map[i:j]
        # insert new zones:
        for newz in Z:
            self._map.insert(i, newz)
            i += 1
        # if len(h)>0: self.__hist.insert(0,h)
        self.__update_cache()

    def restruct(self):
        if len(self._map) == 0:
            return
        m = [self._map.pop(0)]
        for z in self._map:
            rawtype = z.data._is_raw & m[-1].data._is_raw
            if rawtype and (z.vaddr == m[-1].end):
                try:
                    m[-1].data.val += z.data.val
                except TypeError:
                    m.append(z)
            else:
                m.append(z)
        self._map = m
        self.__update_cache()

    def shift(self, offset):
        for z in self._map:
            z.vaddr += offset
        self.__update_cache()

    def grep(self, pattern):
        import re

        g = re.compile(pattern)
        res = []
        for z in self._map:
            if z.data._is_raw:
                off = 0
                for s in g.findall(z.data.val):
                    off = z.data.val.index(s, off)
                    res.append(z.vaddr + off)
                    off += len(s)
        return res


# ------------------------------------------------------------------------------
class mo(object):
    """A mo object essentially associates a datadiv with a memory offset, and
    provides methods to detect if an address is located within this object,
    to read or write bytes at a given address. The offset is relative to the
    start of the :class:`MemoryZone` in which the mo object is stored.

    Attributes:
        vaddr : a python integer that represents the offset within the memory
            zone that contains this memory object (mo).
        data : the datadiv object located at this offset.

    Methods:
        trim(vaddr): if this mo contains data at given offset, cut out this
            data and points current object to this offset. Note that a trim is
            generally the result of data being overwritten by another mo.

        read(vaddr,l): returns the list of datadiv objects at given offset so
            that the total length is at most l, and the number of bytes missing
            if the total length is less than l.

        write(vaddr,data): updates current mo to reflect the writing of data at
            given offset and returns the list of possibly new mo objects to be
            inserted in the zone.
    """

    __slots__ = ["vaddr", "data"]

    def __init__(self, vaddr, data, endian=1):
        self.vaddr = vaddr
        self.data = datadiv(data, endian)

    @property
    def end(self):
        return self.vaddr + len(self.data)

    def __contains__(self, vaddr):
        return self.vaddr <= vaddr < self.end

    def __repr__(self):
        data = str(self.data)
        if len(data) > 32:
            data = data[:32] + "..."
            if self.data._is_raw:
                data += "'"
        return "<mo [%08x,%08x] data:%s>" % (self.vaddr, self.end, data)

    def trim(self, vaddr):
        if vaddr in self:
            l = vaddr - self.vaddr
            if l > 0:
                self.data.cut(l)
            self.vaddr = vaddr

    def setlen(self, l):
        self.data.setlen(l)

    def read(self, vaddr, l):
        if vaddr in self:
            return self.data.getpart(vaddr - self.vaddr, l)
        else:
            return (None, l)

    def write(self, vaddr, data, endian):
        if vaddr in self or vaddr == self.end:
            parts = self.data.setpart(vaddr - self.vaddr, data, endian)
            self.data = parts[0]
            O = []
            vaddr = self.end
            for p in parts[1:]:
                O.append(mo(vaddr, p.val, p.endian))
                vaddr += len(p)
            return O
        else:
            return [mo(vaddr, data, endian)]

    def copy(self):
        return mo(self.vaddr, self.data.val, self.data.endian)


# ------------------------------------------------------------------------------
class datadiv(object):
    """
    A datadiv represents any data within memory, including symbolic expressions.

    Args:
        data   : either a string of bytes or an amoco expression.
        endian : either [-1,1], used when data is any symbolic expression.
                 1 is for little-endian, -1 for big-endian.

    Attributes:
        val : the reference to the data object.
        _is_raw : a flag indicating that the data object is a string of bytes.

    Methods:
        cut(l): cut out the first l bytes of the current data, keeping only
            the remaining part of the data.

        setlen(l): cut out trailing bytes of the current data, keeping only
            the first l bytes.

        getpart(o,l): returns a pair (result, counter) where result is a part
            of data of length at most l located at offset o (relative to the
            beginning of the data bytes), and counter is the number of bytes
            missing (l-len(result)) if the current data length is less than l.

        setpart(o,data): returns a list of contiguous datadiv objects that
            correspond to overwriting self with data at offset o (possibly
            extending the current datadiv length).
    """

    __slots__ = ["val", "endian"]

    def __init__(self, data, endian):
        self.val = data
        self.endian = endian

    @property
    def _is_raw(self):
        return not hasattr(self.val, "_is_def")

    def __len__(self):
        return len(self.val)

    def __repr__(self):
        s = repr(self.val)
        if len(s) > 32:
            s = s[:32] + "..."
            if isinstance(self.val, bytes):
                s += "'"
        return "<datadiv:%s>" % s

    def __str__(self):
        return repr(self.val) if self._is_raw else str(self.val)

    def cut(self, l):
        if self._is_raw:
            self.val = self.val[l:]
        else:
            self.val = self.val.bytes(sta=l, endian=self.endian)

    def setlen(self, l):
        if self._is_raw:
            self.val = self.val[:l]
        else:
            self.val = self.val.bytes(sto=l, endian=self.endian)

    def getpart(self, o, l):
        try:
            assert o >= 0 and l >= 0
            if not self._is_raw:
                s = self.val.size
                assert s % 8 == 0
        except AssertionError:
            logger.error("invalid fetch (o=%s,l=%s) in %s" % (o, l, repr(self)))
            raise ValueError
        lv = len(self)
        if o == 0 and l == lv:
            return (self.val, 0)
        if self._is_raw:
            res = self.val[o : o + l]
            return (res, l - len(res))
        if o >= lv:
            return (None, l)
        res = self.val.bytes(o, o + l, self.endian)
        return (res, l - res.length)

    def setpart(self, o, data, endian):
        assert 0 <= o <= len(self)
        P = [datadiv(data, endian)]
        olv = o + len(data)
        endl = len(self) - olv
        if endl > 0:
            P.append(datadiv(self.getpart(olv, endl)[0], self.endian))
        if o > 0:
            P.insert(0, datadiv(self.getpart(0, o)[0], self.endian))
        # now merge contiguous parts if they have same type:
        return mergeparts(P)


# ------------------------------------------------------------------------------
def mergeparts(P):
    """This function will detect every contiguous raw datadiv objects in the
    input list P, and will return a new list where these objects have been
    merged into a single raw datadiv object.

    Args:
        P (list): input list of datadiv objects.

    Returns:
        list: the list after raw datadiv objects have been merged.
    """
    parts = [P.pop(0)]
    while len(P) > 0:
        p = P.pop(0)
        if parts[-1]._is_raw and p._is_raw:
            try:
                parts[-1].val += p.val
            except TypeError:
                parts.append(p)
        else:
            parts.append(p)
    return parts
