# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2016 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.logger import Log
logger = Log(__name__)
logger.debug("loading module")

#------------------------------------------------------------------------------

class StructCore(object):
    """
    A StructCore child class represents a C struct or union declaration. It is
    also used to represent a typedef declaration. It is the Parent class for all
    user-defined structures based on a StructDefine format.
    It contains essentially the packing and unpacking logic of the structure
    allowing an instance of such class to be "unpacked" from given bytes (or
    "packed" from given values.)

    Each instance of a StructCore child class has its own fields copy and a
    new "container" for associated attributes' names & unpacked values.

    Attributes:
        packed (Bool=False): Unless the "packed" attribute is set to True,
                             it will use usual padding rules from C.
        union (False or int): is set to an int if it represents a C union,
                             in which case the int value is the index of
                             the largest of its fields.
        typedef (Bool=False): indicates that the class represents a typedef.
        fields (list): list of Field objects that define this structure.
        _v (container): when a structure is unpacked, the resulting values
                        are stored in this generic object.
                        These values are accessed from the S structure instance
                        using S['fieldname'] or for convinience using
                        S.fieldname if the fieldname doesn't conflict with a
                        StructCore attribute or method name.

    Note:
    It is mandatory that any class that inherits from StructCore can be
    instanciated with no arguments.
    """

    packed = False
    union  = False
    typedef = False

    def __new__(cls, *args, **kargs):
        obj = super(StructCore, cls).__new__(cls)
        obj.fields = [f.copy(obj) for f in cls.fields]
        t = type("container", (object,), {})
        obj._v = t()
        return obj

    def __getitem__(self, fname):
        return getattr(self._v, fname)

    def __setitem__(self, fname, x):
        setattr(self._v, fname, x)

    def update(self,kv):
        k,v = kv
        setattr(self._v,k,v)

    def __getattr__(self, attr):
        if attr not in self.__dict__:
            return getattr(self._v, attr)
        else:
            return self.__dict__[attr]

    @classmethod
    def format(cls):
        """
        The format of a StructCore is the join of its fields formats,
        or its "largest" field if it's a union.
        """
        if cls.union is False:
            return "".join((f.format() for f in cls.fields))
        else:
            return cls.fields[cls.union].format()

    @classmethod
    def size(cls):
        """
        This is a class method that basically computes the sum of
        the sizes of fields (or the largest field if a union) while
        taking into account the possible alignements constraints.
        It uses the *class* fields instances so that the resulting
        value is infinite if any of these field is a VarField.
        """
        A = cls.align_value()
        sz = 0
        for f in cls.fields:
            if cls.union is False and not cls.packed:
                sz = f.align(sz)
            fsz = f.size()
            if cls.union is False:
                sz += fsz
            elif fsz > sz:
                sz = fsz
        r = sz % A
        if (not cls.packed) and r > 0:
            sz += A - r
        return sz

    def __len__(self):
        """
        This is an instance method that computes the
        the actual size of the structure instance using the
        instance's fields. This makes a difference from size()
        in the case of a structure with variable-length fields
        that have been unpacked.
        """
        A = self.align_value()
        sz = 0
        for f in self.fields:
            # adjust current size with alignment constraints:
            # and add field size:
            if self.union is False and not self.packed:
                sz = f.align(sz)
            if f.instance is None:
                continue
            fsz = f.size()
            if fsz==float('Infinity'):
                continue
            if self.union is False:
                sz += fsz
            elif fsz > sz:
                sz = fsz
        r = sz % A
        if (not self.packed) and r > 0:
            sz += A - r
        return sz

    def __eq__(self, other):
        if (
            (self.packed == other.packed)
            and (self.union == other.union)
            and (self.typdef == other.typedef)
            and len(self.fields) == len(other.fields)
            and all((sf == of for sf, of in zip(self.fields, other.fields)))
        ):
            return True
        else:
            return False

    @classmethod
    def align_value(cls):
        return max([f.align_value for f in cls.fields])

    def unpack(self, data, offset=0):
        for f in self.fields:
            if self.union is False and not self.packed:
                offset = f.align(offset)
            try:
                value = f.unpack(data, offset)
            except Exception:
                name = self.__class__.__name__
                logger.error("error unpacking %s %s"%(name,str(f)))
                raise StructureError(name)
            else:
                # if the structure is a typedef, it has only one field
                # and unpacking returns its value:
                if self.typedef:
                    return value
                # otherwise, unless its a bitfield, it has a name:
                if f.name:
                    setattr(self._v, f.name, value)
                elif hasattr(f,'subnames'):
                    # its a bitfield so the unpacked value
                    # is a dict with subnames/subvalues:
                    self._v.__dict__.update(value)
            if self.union is False:
                offset += f.size()
        return self

    def pack(self, data=None):
        if data is None:
            data = []
            for f in self.fields:
                # unless its a bitfield, it has a name:
                if f.name:
                    data.append(getattr(self._v, f.name))
                elif hasattr(f,'subnames'):
                    D = {}
                    for x in self.subnames:
                        D[x] = getattr(self._v,x)
                    data.append(D)
        parts = []
        offset = 0
        for f, v in zip(self.fields, data):
            p = f.pack(v)
            if not self.packed:
                pad = f.align(offset) - offset
                p = b"\0" * pad + p
            parts.append(p)
        if self.union is False:
            res = b"".join(parts)
            if not self.packed:
                res = res.ljust(self.size(), b"\0")
            return res
        else:
            return parts[self.union]

    def offset_of(self, name):
        if self.union is not False:
            return 0
        o = 0
        for f in self.fields:
            if f.name == name:
                return o
            o = f.align(o) + f.size()
        raise AttributeError(name)

# ------------------------------------------------------------------------------


# our data structures exception handler:
class StructureError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


# ------------------------------------------------------------------------------


Alltypes = {}
