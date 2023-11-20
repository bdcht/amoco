# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2016 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
system/structs
==============

The system structs package implements metaclasses that allow to easily define
Python classes that can encode and decode C structures (or unions).
It also provides formatters to print various fields according to given types
like hex numbers, dates, defined constants, etc.

This package extends the capabilities of :mod:`struct` by allowing formats to
include more than just the basic types and by adding *named* fields.
It extends :mod:`ctypes` as well by allowing formatted printing and "non-static"
decoding where the way a field is decoded depends on a specific terminating
condition or on the value of previously decoded fields of the same structure.

For example, module :mod:`system.imx6` uses these metaclasses to decode
HAB structures and thus allow for precise verifications on how the boot stages
are verified. The HAB Header class is thus defined by::

   @StructDefine(\"\"\"
   B :  tag
   H :> length
   B :  version
   \"\"\")
   class HAB_Header(StructFormatter):
       def __init__(self,data="",offset=0):
           self.name_formatter('tag')
           self.func_formatter(version=self.token_ver_format)
           if data:
               self.unpack(data,offset)
       @staticmethod
       def token_ver_format(k,x,cls=None):
           return highlight([(Token.Literal,"%d.%d"%(x>>4,x&0xf))])

Here, the :class:`StructDefine` decorator is used to provide the definition of
fields of the HAB Header structure to the HAB_Header class.

The *tag* :class:`Field` is an unsigned byte and the :class:`StructFormatter`
utilities inherited by the class set it as a :meth:`name_formatter` allow
the decoded byte value from data to be represented by its constant name.
This name is obtained from constants defined with::

    with Consts('tag'):
        HAB_TAG_IVT = 0xd1
        HAB_TAG_DCD = 0xd2
        HAB_TAG_CSF = 0xd4
        HAB_TAG_CRT = 0xd7
        HAB_TAG_SIG = 0xd8
        HAB_TAG_EVT = 0xdb
        HAB_TAG_RVT = 0xdd
        HAB_TAG_WRP = 0x81
        HAB_TAG_MAC = 0xac

The *length* field is a bigendian short integer with default formatter,
and the *version* field is an unsigned byte with a dedicated formatter
function that extracts major/minor versions from the byte nibbles.

This allows to decode and print the structure from provided data::

    In [3]: h = HAB_Header(\'\\xd1\\x00\\x0a\\x40\')
    In [4]: print(h)
    [HAB_Header]
    tag                 :HAB_TAG_IVT
    length              :10
    version             :4.0
"""

import pyparsing as pp
from collections import defaultdict

from .core import *
from .fields import *
from .formatters import *

# ------------------------------------------------------------------------------

class StructDefine(object):
    """
    StructDefine is a decorator class used for defining structures
    by parsing a simple intermediate language input decorating
    a StructFormatter class.

    A decorator instance is created by parsing an input "format"
    string that is ultimately used to define the fields the StructCore class
    on which it is called. The overall idea is to write::

        @StructDefine(fmt)
        class Name(StructCore):
           [...]

    The format string syntax is line-oriented. Each line defines a field.
    The syntax for a field is divided in 3 parts: *T*:[*N*][;C]

      - *T* is the name of the type
      - [*N*] is the name of the field
      - [;C] is an optional comment

    The name of the field *N* can be prepended by a literal symbol '<' or '>'
    to indicate that its encoding uses little or big endian (if relevant.)

    The name of the type *T* encodes several things in the form::

        T := typename[*length]

    In most cases, *typename* is the struct package letter for decoding a "raw"
    type ie. a byte, a string, an integer, etc.
    For example::

        "I :> x ; something"

    produces a field named 'x' of type uint32 encoded in big-endian.
    (Anything that follows ';' is just a comment associated with the field.)

    The name of type can also be the name of a previously defined
    class that inherits StructCore, in which case the previous class is used
    for decoding the field value when unpacking occurs.
    The length indicator [*length] is optional and is either

      - a numeric value: the field is an array of elements of type *T*,
      - the string "%leb128" that indicates a Leb128Field,
      - a string in the form ".name" that matches the name of a previous field
        in the structure (see :class:`BindField`,)
      - a special indicator that starts with symbol '#' followed by numeric
        values separated by '/', in which case the field is a BitField
      - a special indicator that starts with symbol '~', in which case the
        field is a :class:`VarField` or a :class:`CntField` if the symbol
        is followed by a counter size indicator, ie one of [bBhHiI].
    """

    rawtypes = (
        "x",
        "c",
        "b",
        "B",
        "h",
        "H",
        "i",
        "I",
        "l",
        "L",
        "f",
        "d",
        "s",
        "n",
        "N",
        "p",
        "P",
        "q",
        "Q",
    )
    alignments = {
        "x": 1,
        "c": 1,
        "b": 1,
        "B": 1,
        "s": 1,
        "h": 2,
        "H": 2,
        "i": 4,
        "I": 4,
        "l": 0,
        "L": 0,
        "f": 4,
        "q": 8,
        "Q": 8,
        "d": 8,
        "P": 0,
    }
    integer = pp.Regex(r"[0-9][0-9]*")
    integer.setParseAction(lambda r: int(r[0]))
    bitslen = pp.Group(pp.Suppress("#") + pp.delimitedList(integer,delim='/'))
    symbol = pp.Regex(r"[A-Za-z_][A-Za-z0-9_/$]*")
    special = pp.Regex(r"[.%][A-Za-z_][A-Za-z0-9_/]*")
    comment = pp.Suppress(";") + pp.restOfLine
    fieldname = pp.Suppress(":") + pp.Group(
        pp.Optional(pp.Literal(">") | pp.Literal("<"), default=None) + symbol
    )
    inf = pp.Regex(r"~[bBhHiI]?")
    length = integer | special | inf | bitslen
    typename = pp.Group(symbol + pp.Optional(pp.Suppress("*") + length, default=0))
    structfmt = pp.OneOrMore(
        pp.Group(typename + fieldname + pp.Optional(comment, default=""))
    )

    def __init__(self, fmt, **kargs):
        self.fields = []
        self.source = fmt
        self.packed = kargs.get("packed", False)
        if "alignments" in kargs:
            self.alignments = kargs["alignments"]
        # lets parse the input format and add corresponding fields:
        # the top-level definition is given by structfmt (see above):
        for l in self.structfmt.parseString(fmt, True).asList():
            # we get a typename, a fieldname and optional comment:
            f_type, f_name, f_comment = l
            # the fieldname is a group of order literal and a symbol:
            f_order, f_name = f_name
            # the typename is a symbol and optional length:
            f_type, f_count = f_type
            if f_order is None and "order" in kargs:
                f_order = kargs["order"]
            # if the typename symbol is a raw type, then the field
            # can be a RawField, a BitField, or one of the VarField(s):
            if f_type in self.rawtypes:
                f_cls = RawField
                if isinstance(f_count, list):
                    # a BitField is defined from a 'bitlen' f_count length
                    # ie a string of values separated by '/'.
                    f_cls = BitField
                    # In that case, the name should also be a "list" of
                    # names spearated by '/':
                    f_name = f_name.split('/')
                elif isinstance(f_count, str):
                    if f_count.startswith("~"):
                        f_cls = VarField
                        if len(f_count)==2 and (f_count[1:2] in "bBhHiI"):
                            f_cls = CntField
                    elif f_count.startswith("."):
                        f_cls = BindedField
                    elif f_count=="%leb128":
                        f_cls = Leb128Field
                        f_count = 0
                f_align = self.alignments[f_type]
            else:
                f_cls = Field
                if isinstance(f_count, list):
                    f_cls = BitFieldEx
                    f_name = f_name.split('/')
                f_type = kargs.get(f_type, f_type)
                f_align = 0
            f = f_cls(f_type, f_count, f_name, f_order, f_align, f_comment)
            # if this is a bitfield with only one subfield, we want to
            # concatenate it with a previous bitfield if possible:
            if f_cls in (BitField,BitFieldEx):
                if len(f_count)==len(f_name)==1:
                    if len(self.fields)>0:
                        prev = self.fields[-1]
                        if isinstance(prev,(BitField,BitFieldEx)):
                            try:
                                prev.concat(f)
                            except TypeError:
                                # concat raises TypeError if prev is
                                # already "full" or if f would exceed
                                # its size...
                                pass
                            else:
                                # concat suceeded, so we don't append f
                                continue
            self.fields.append(f)

    def __call__(self, cls):
        # Alltypes is a global dict located in structs.core module
        Alltypes[cls.__name__] = cls
        cls.fields = self.fields
        cls.source = self.source
        cls.packed = self.packed
        cls.fkeys = defaultdict(default_formatter)
        return cls


# ------------------------------------------------------------------------------


class UnionDefine(StructDefine):
    """
    UnionDefine is a decorator class based on StructDefine,
    used for defining unions.
    """

    def __call__(self, cls):
        # Alltypes is a global dict located in structs.core module
        Alltypes[cls.__name__] = cls
        cls.fields = self.fields
        cls.source = self.source
        cls.union = -1
        try:
            s = [f.size() for f in cls.fields]
            cls.union = s.index(max(s))
        except AttributeError:
            pass
        return cls


# ------------------------------------------------------------------------------


def TypeDefine(newname, typebase, typecount=0, align_value=0):
    t = StructFactory(newname, "%s : _"%typebase)
    t.typedef = True
    if typecount:
        t.fields[0].count = typecount
    if align_value:
        t.fields[0]._align_value = align_value
    return t

# ------------------------------------------------------------------------------


class StructMaker(StructFormatter):
    """
    The StructMaker class is a StructFormatter equipped with methods that
    allow to interactively define and adjust fields at some given offsets
    or when some given sample bytes match a given value.
    """

    fields = []

    @property
    def source(cls):
        return "\n".join((x.source for x in cls.fields))

    @classmethod
    def define(cls, fmt, offset=-1, atvalue=None, indata=b""):
        d = StructDefine(fmt)
        if len(d.fields) > 1:
            logger.warning("can't define more than one field at a time...")
        f = d.fields[0]
        if atvalue != None:
            s = f.pack(atvalue)
            offset = indata.find(s)
            logger.info("value found at offset %d" % offset)
        if offset >= 0:
            newf = []
            pos = 0
            for x in cls.fields:
                lx = pos + len(x)
                if pos <= offset < lx:
                    if x.name == "#undef":
                        count = offset - pos
                        if count > 0:
                            newf.append(RawField("s", count, "#undef"))
                        newf.append(f)
                        count = lx - (offset + len(f))
                        if count > 0:
                            newf.append(RawField("s", count, "#undef"))
                    else:
                        logger.error("can't overlap existing field!")
                        return None
                else:
                    newf.append(x)
                pos = lx
            if offset >= pos:
                count = offset - pos
                if count > 0:
                    newf.append(RawField("s", count, "#undef"))
                newf.append(f)
            cls.fields = newf
            return f
        else:
            return None


# ------------------------------------------------------------------------------


def StructFactory(name, fmt, **kargs):
    "Returns a StructFormatter class build with name and format"
    return StructDefine(fmt, **kargs)(type(name, (StructFormatter,), {}))


def UnionFactory(name, fmt, **kargs):
    "Returns a StructFormatter (union) class build with name and format"
    return UnionDefine(fmt, **kargs)(type(name, (StructFormatter,), {}))


# ------------------------------------------------------------------------------

