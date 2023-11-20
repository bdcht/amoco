# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2016 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

import struct
import pyparsing as pp
from collections import defaultdict

from amoco.logger import Log
logger = Log(__name__)
logger.debug("loading module")

from .core import StructCore

from amoco.ui.render import Token, highlight
from inspect import stack as _stack


# ------------------------------------------------------------------------------


class Consts(object):
    """
    Provides a contextmanager to map constant values with their names in
    order to build the associated reverse-dictionary.

    All revers-dict are stored inside the Consts class definition.
    For example if you declare variables in a Consts('example') with-scope,
    the reverse-dict will be stored in Consts.All['example'].
    When StructFormatter will lookup a variable name matching a given value
    for the attribute 'example', it will get Consts.All['example'][value].

    Note: To avoid attribute name conflicts, the lookup is always prepended
    the stucture class name (or the 'alt' field of the structure class).
    Hence, the above 'tag' constants could have been defined as::

      with Consts('HAB_header.tag'):
          HAB_TAG_IVT = 0xd1
          HAB_TAG_DCD = 0xd2
          HAB_TAG_CSF = 0xd4
          HAB_TAG_CRT = 0xd7
          HAB_TAG_SIG = 0xd8
          HAB_TAG_EVT = 0xdb
          HAB_TAG_RVT = 0xdd
          HAB_TAG_WRP = 0x81
          HAB_TAG_MAC = 0xac

    Or the structure definition could have define an 'alt' attribute::

      @StructDefine(\"\"\"
      B :  tag
      H :> length
      B :  version
      \"\"\")
      class HAB_Header(StructFormatter):
          alt = 'hab'
          [...]

    in which case the variables could have been defined with::

      with Consts('hab.tag'):
      [...]
    """

    All = defaultdict(dict)

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        where = _stack()[1][0].f_globals
        self.globnames = set(where.keys())
        if not self.name in self.All:
            self.All[self.name] = {}

    def __exit__(self, exc_type, exc_value, traceback):
        where = _stack()[1][0]
        G = where.f_globals
        for k in set(G.keys()) - self.globnames:
            self.All[self.name][G[k]] = k


# ------------------------------------------------------------------------------


def default_formatter():
    return token_default_fmt


def token_default_fmt(k, x, cls=None, fmt=None):
    """The default formatter just prints value 'x' of attribute 'k'
    as a literal token python string
    """
    try:
        s = x.pp__()
    except AttributeError:
        s = str(x)
    return highlight([(Token.Literal, s)],fmt)


def token_address_fmt(k, x, cls=None, fmt=None):
    """The address formatter prints value 'x' of attribute 'k'
    as a address token hexadecimal value
    """
    return highlight([(Token.Address, hex(x))],fmt)

def token_version_fmt(k, x, cls=None, fmt=None):
    """The address formatter prints value 'x' of attribute 'k'
    as an hexadecimal string token value
    """
    l = []
    while x:
        l.append("%d"%(x&0xff))
        x = x>>8
    return highlight([(Token.String, '.'.join(l))],fmt)

def token_bytes_fmt(k, x, cls=None, fmt=None):
    """The address formatter prints value 'x' of attribute 'k'
    as an hexadecimal string token value
    """
    l = []
    while x:
        l.append("%02X"%(x&0xff))
        x = x>>8
    return highlight([(Token.String, ' '.join(l))],fmt)

def token_constant_fmt(k, x, cls=None, fmt=None):
    """The constant formatter prints value 'x' of attribute 'k'
    as a constant token decimal value
    """
    try:
        s = x.pp__()
    except AttributeError:
        s = str(x)
    return highlight([(Token.Constant, s)],fmt)


def token_mask_fmt(k, x, cls=None, fmt=None):
    """The mask formatter prints value 'x' of attribute 'k'
    as a constant token hexadecimal value
    """
    return highlight([(Token.Constant, hex(x))],fmt)


def token_name_fmt(k, x, cls=None, fmt=None):
    """The name formatter prints value 'x' of attribute 'k'
    as a name token variable symbol matching the value
    """
    pfx = "%s." % cls if cls != None else ""
    if pfx + k in Consts.All:
        k = pfx + k
    ks = k
    try:
        return highlight([(Token.Name, Consts.All[ks][x])],fmt)
    except KeyError:
        return token_constant_fmt(k, x, cls, fmt)


def token_flag_fmt(k, x, cls, fmt=None):
    """The flag formatter prints value 'x' of attribute 'k'
    as a name token variable series of symbols matching
    the flag value
    """
    s = []
    pfx = "%s." % cls if cls != None else ""
    if pfx + k in Consts.All:
        k = pfx + k
    ks = k
    for v, name in Consts.All[ks].items():
        if x & v:
            s.append(highlight([(Token.Name, name)],fmt))
    return ",".join(s) if len(s) > 0 else token_mask_fmt(k, x, cls, fmt)


def token_datetime_fmt(k, x, cls=None, fmt=None):
    """The date formatter prints value 'x' of attribute 'k'
    as a date token UTC datetime string from timestamp value
    """
    from datetime import datetime

    return highlight([(Token.Date, str(datetime.utcfromtimestamp(x)))],fmt)


# ------------------------------------------------------------------------------


class StructFormatter(StructCore):
    """
    StructFormatter is the Parent Class for all user-defined structures.
    For most of these structures, the fields are created using a StructDefine
    decorator.

    This class inherits the core logic from StructCore Parent and provides all
    formatting facilities to pretty print the structures based on wether
    the field is declared as a named constant, an integer of hex value,
    a pointer address, a string or a date.

    Note: Since it inherits from StructCore, it is mandatory that any child
    class can be instanciated with no arguments.
    """

    pfx = ""
    alt = None

    @classmethod
    def func_formatter(cls, **kargs):
        for key, func in kargs.items():
            cls.fkeys[key] = func

    @classmethod
    def address_formatter(cls, *keys):
        for key in keys:
            cls.fkeys[key] = token_address_fmt

    @classmethod
    def name_formatter(cls, *keys):
        for key in keys:
            cls.fkeys[key] = token_name_fmt

    @classmethod
    def flag_formatter(cls, *keys):
        for key in keys:
            cls.fkeys[key] = token_flag_fmt

    def strkey(self, k, cname, ksz=20, formatter=None):
        fmt = "%%s%%-%ds:%%s" % ksz
        if hasattr(self._v, k):
            val = getattr(self._v, k)
            if isinstance(val,StructFormatter):
                val = val.pp__(formatter)
            elif isinstance(val,list):
                val = "\n".join((e.pp__(formatter) for e in val))
            result = self.fkeys[k](k, val, cls=cname,fmt=formatter)
        else:
            result = "None"
        return fmt % (self.pfx, k, result)

    def pp__(self,fmt=None):
        cname = self.alt or self.__class__.__name__
        ksz = max((len(f.name) for f in self.fields))
        s = []
        for f in self.fields:
            if f.name and f.name!='_':
                fs = self.strkey(f.name, cname, ksz, fmt)
                if fs.count("\n") > 0:
                    fs = fs.replace("\n", "\n " + " " * ksz)
            elif hasattr(f,'subnames'):
                subn = filter(lambda n:n!='_', f.subnames)
                fs = "\n".join((self.strkey(n,cname,ksz,fmt) for n in subn))
            else:
                continue
            s.append(fs)
        s = "\n".join(s)
        return "[%s]\n%s" % (self.__class__.__name__, s)

    def __str__(self):
        return self.pp__()


