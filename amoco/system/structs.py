# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2016 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
system/structs.py
=================

The system structs module implements classes that allow to easily define,
encode and decode C structures (or unions) as well as formatters to print
various fields according to given types like hex numbers, dates, defined
constants, etc.
This module extends capabilities of :mod:`struct` by allowing formats to
include more than just the basic types and add *named* fields. 
It extends :mod:`ctypes` as well by allowing formatted printing and
"non-static" decoding where the way a field is decoded depends on
previously decoded fields.   

Module :mod:`system.imx6` uses these classes to decode HAB structures and
thus allow for precise verifications on how the boot stages are verified.
For example, the HAB Header class is defined with::

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

import struct
import inspect
import pyparsing as pp
from datetime import datetime
from collections import defaultdict
import ctypes

from amoco.logger import *
logger = Log(__name__)

from amoco.ui.render import Token,highlight

#------------------------------------------------------------------------------

class Consts(object):
    """Provides a contextmanager to map constant values with their names in
     order to build the associated reverse-dictionary."""
    All = defaultdict(dict)
    def __init__(self,name):
        self.name = name
    def __enter__(self):
        where = inspect.stack()[1][0].f_globals
        self.globnames = set(where.keys())
        self.All[self.name] = {}
    def __exit__(self,exc_type,exc_value,traceback):
        where = inspect.stack()[1][0]
        G = where.f_globals
        for k in set(G.keys())-self.globnames:
            self.All[self.name][G[k]] = k

def default_formatter():
    return token_default_fmt

def token_default_fmt(k,x,cls=None):
    return highlight([(Token.Literal,str(x))])

def token_address_fmt(k,x,cls=None):
    return highlight([(Token.Address,hex(x))])

def token_constant_fmt(k,x,cls=None):
    return highlight([(Token.Constant,str(x))])

def token_mask_fmt(k,x,cls=None):
    return highlight([(Token.Constant,hex(x))])

def token_name_fmt(k,x,cls=None):
    pfx = "%s."%cls if cls!=None else ""
    ks = k
    try:
        return highlight([(Token.Name,Consts.All[ks][x])])
    except KeyError:
        return token_constant_fmt(k,x)

def token_flag_fmt(k,x,cls):
    s = []
    pfx = "%s."%cls if cls!=None else ""
    ks = k
    for v,name in Consts.All[ks].items():
        if (x&v): s.append(highlight([(Token.Name,name)]))
    return ','.join(s) if len(s)>0 else token_mask_fmt(k,x)

def token_datetime_fmt(k,x,cls=None):
    return highlight([(Token.Date,str(datetime.utcfromtimestamp(x)))])

#------------------------------------------------------------------------------

class Field(object):
    """A Field object defines an element of a structure, associating a name
    to a structure typename and a count. A count of 0 means that the element
    is an object of type typename, a count>0 means that the element is a list
    of objects of type typename of length count.

    Attributes:
        typename (str) : name of a Structure type for this field.
        count (int=0)  : A count of 0 means that the element
            is an object of type typename, a count>0 means that the element is a list
            of length count of objects of type typename
        name (str)     : the name associated to this field.
        type (StructFormatter) : getter for the type associated with the field's typename.
        size (int) : number of bytes eaten by this field.
        comment (str) : comment, useful for pretty printing field usage
        order (str) : forces the endianness of this field.

    Methods:
        format (): format string that allows to struct.(un)pack the field as a
                       string of bytes.
        unpack (data,offset=0,order='<') : unpacks a data from given offset using
            the provided byte ordering. Returns the object (if count is 0) or the
            list of objects of type typename.
        get (data,offset=0,order='<') : returns the field name and the unpacked value
            for this field.
        pack (value,order='<') : packs the value with the given order and returns the
            byte string according to type typename.
    """
    def __init__(self,ftype,fcount=0,fname=None,forder=None,falign=0,fcomment=''):
        self.typename = ftype
        self.type_private = isinstance(ftype,(StructCore))
        self.count = fcount
        self.name = fname
        self.order = forder or '<'
        self._align_value = None
        if falign:
            self.align_value = falign
        self.comment = fcomment
    @property
    def type(self):
        if self.type_private:
            return self.typename
        try:
            cls = StructDefine.All[self.typename]
        except KeyError:
            return None
        else:
            return cls()
    def format(self):
        sz = self.size()
        return '%ds'%sz
    def size(self):
        sz = self.type.size()
        if self.count>0: sz = sz*self.count
        return sz
    @property
    def source(self):
        res = "%s"%self.typename
        if self.count>0: res += "*%d"%self.count
        res += ": %s"%self.name
        if self.comment: res += " ;%s"%self.comment
        return res
    def __len__(self):
        return self.size()
    @property
    def align_value(self):
        if self._align_value: return self._align_value
        if isinstance(self.type,Field): return self.type.align_value
        return self.type.align_value()
    @align_value.setter
    def align_value(self,val):
        self._align_value = val
    def align(self,offset):
        A = self.align_value
        r = offset%A
        if r==0: return offset
        return offset+(A-r)
    def unpack(self,data,offset=0):
        blob = self.type.unpack(data,offset)
        sz = self.type.size()
        count = self.count
        if count>0:
            blob = [blob]
            count -= 1
            offset += sz
            while count>0:
                blob.append(self.type.unpack(data,offset))
                offset += sz
                count -= 1
        return blob
    def get(self,data,offset=0):
        return (self.name,self.unpack(data,offset))
    def pack(self,value):
        if self.count>0:
            return b''.join([self.type.pack(v) for v in value])
        return self.type.pack(value)
    def __call__(self):
        return self
    def __repr__(self):
        try:
            fmt = self.type.format()
        except KeyError:
            fmt = '?'
        r = '<Field %s {%s}'%(self.name,fmt)
        if self.count>0: r += '*%d'%self.count
        r += ' (%s)>'%self.comment if self.comment else '>'
        return r

#------------------------------------------------------------------------------

class RawField(Field):
    """A RawField is a Field associated to a *raw* type, i.e. an internal type
    matching a standard C type (u)int8/16/32/64, floats/double, (u)char.
    """
    def format(self):
        fmt = self.typename
        if self.count==0: return fmt
        return '%d%s'%(sz,fmt)
    def size(self):
        sz = struct.calcsize(self.typename)
        if self.count>0: sz = sz*self.count
        return sz
    def unpack(self,data,offset=0):
        pfx = '%d'%self.count if self.count>0 else ''
        res = struct.unpack(self.order+pfx+self.typename,data[offset:offset+self.size()])
        if self.count==0 or self.typename=='s': return res[0]
        return res
    def pack(self,value):
        pfx = '%d'%self.count if self.count>0 else ''
        res = struct.pack(self.order+pfx+self.typename,value)
        return res
    def __repr__(self):
        fmt = self.typename
        r = '<Field %s [%s]'%(self.name,fmt)
        if self.count>0: r += '*%d'%self.count
        r += ' (%s)>'%self.comment if self.comment else '>'
        return r

#------------------------------------------------------------------------------

class StructDefine(object):
    """StructDefine is a decorator class used for defining structures
    by parsing a simple intermediate language input decorating a StructFormatter class.
    """
    All = {}
    rawtypes   = ('x','c','b','B','h','H','i','I','l','L','f','d','s','n','N','p','P','q','Q')
    alignments = {'x':1, 'c':1, 'b':1, 'B':1, 's':1,
                  'h':2, 'H':2,
                  'i':4, 'I':4, 'l':4, 'L':4, 'f':4,
                  'q':8, 'Q':8, 'd':8,
                  'P':8}
    integer    = pp.Regex(r'[1-9][0-9]*')
    number     = integer
    number.setParseAction(lambda r: int(r[0]))
    symbol     = pp.Regex(r'[A-Za-z_][A-Za-z0-9_]*')
    comment    = pp.Suppress(';')+pp.restOfLine
    fieldname  = pp.Suppress(':')+pp.Group(pp.Optional(pp.Literal('>')|pp.Literal('<'),default=None)+symbol)
    length     = integer|symbol
    typename   = pp.Group(symbol+pp.Optional(pp.Suppress('*')+length,default=0))
    structfmt  = pp.OneOrMore(pp.Group(typename+fieldname+pp.Optional(comment,default='')))

    def __init__(self,fmt,**kargs):
        self.fields = []
        self.source = fmt
        self.packed = kargs.get('packed',False)
        if 'alignments' in kargs:
           self.alignments = kargs['alignments']
        for l in self.structfmt.parseString(fmt,True):
            f_type,f_name,f_comment = l
            f_order,f_name = f_name
            f_type,f_count = f_type
            if f_order is None and 'order' in kargs:
                f_order=kargs['order']
            if f_type in self.rawtypes:
                f_cls = RawField
                f_align = self.alignments[f_type]
            else:
                f_cls = Field
                f_type = kargs.get(f_type,f_type)
                f_align = 0
            self.fields.append(f_cls(f_type,f_count,f_name,f_order,f_align,f_comment))
    def __call__(self,cls):
        self.All[cls.__name__] = cls
        cls.fields = self.fields
        cls.source = self.source
        cls.packed = self.packed
        return cls

class UnionDefine(StructDefine):
    """UnionDefine is a decorator class based on StructDefine, used for defining unions.
    """
    def __call__(self,cls):
        self.All[cls.__name__] = cls
        cls.fields = self.fields
        cls.source = self.source
        s = [f.size() for f in cls.fields]
        cls.union  = s.index(max(s))
        return cls

def TypeDefine(newname, typebase, typecount=0,align_value=0):
    if typebase in StructDefine.rawtypes:
        f_cls = RawField
        f_align = align_value or StructDefine.alignments[typebase]
    else:
        f_cls = Field
        f_align = 0
    StructDefine.All[newname] = f_cls(typebase,fcount=typecount,falign=f_align,fname='typedef')

class StructCore(object):
    """StructCore is a ParentClass for all user-defined structures based on a StructDefine format.
    This class contains essentially the packing and unpacking logic of the structure.

    Note: It is mandatory that any class that inherits from StructCore can be instanciated
    with no arguments.
    """
    packed = False
    union = False

    @classmethod
    def format(cls):
        if cls.union is False:
            return ''.join((f.format() for f in cls.fields))
        else:
            return cls.fields[cls.union].format()
    @classmethod
    def size(cls):
        A = cls.align_value()
        sz = 0
        for f in cls.fields:
            if cls.union is False and not cls.packed:
                sz = f.align(sz)
            if cls.union is False:
                sz += f.size()
            elif f.size>sz:
                sz = f.size()
        r = sz%A
        if (not cls.packed) and r>0:
            sz += (A-r)
        return sz
    def __len__(self):
        return self.size()
    @classmethod
    def align_value(cls):
        return max([f.align_value for f in cls.fields])
    def unpack(self,data,offset=0):
        for f in self.fields:
            if self.union is False and not self.packed:
                offset = f.align(offset)
            setattr(self,f.name,f.unpack(data,offset))
            if self.union is False:
                offset += f.size()
        return self
    def pack(self,data=None):
        if data is None:
            data = [getattr(self,f.name) for f in self.fields]
        parts = []
        offset = 0
        for f,v in zip(self.fields,data):
            p = f.pack(v)
            if not self.packed:
                pad = f.align(offset)-offset
                p = b'\0'*pad + p
            parts.append(p)
        if self.union is False:
            res = b''.join(parts)
            if not self.packed:
                res = res.ljust(self.size(),b'\0')
            return res
        else:
            return parts[self.union]
    def offset_of(self,name):
        if self.union is not False:
            return 0
        o = 0
        for f in self.fields:
            if f.name==name: return o
            o = f.align(o)
        raise AttributeError(name)

class StructFormatter(StructCore):
    """StructFormatter is the Parent Class for all user-defined structures based on a StructDefine format.
    It inherits the core logic from StructCore Parent and provides all formatting facilities to pretty
    print the structures based on wether the field is declared as a named constant, an integer of hex value,
    a pointer address, a string or a date.

    Note: Since it inherits from StructCore, it is mandatory that any child class can be instanciated
    with no arguments.
    """
    fkeys = defaultdict(default_formatter)
    pfx   = ''
    ksz   = 20
    @classmethod
    def func_formatter(cls,**kargs):
        for key,func in kargs.items():
            cls.fkeys[key] = func
    @classmethod
    def address_formatter(cls,*keys):
        for key in keys:
            cls.fkeys[key] = token_address_fmt
    @classmethod
    def name_formatter(cls,*keys):
        for key in keys:
            cls.fkeys[key] = token_name_fmt
    @classmethod
    def flag_formatter(cls,*keys):
        for key in keys:
            cls.fkeys[key] = token_flag_fmt

    def strkey(self,k,cname):
        fmt = u'%%s%%-%ds:%%s'%self.ksz
        if hasattr(self,k):
            val = getattr(self,k)
            return fmt%(self.pfx,k,self.fkeys[k](k,val,cls=cname))
        else:
            return fmt%(self.pfx,k,"None")
    def __str__(self):
        cname = self.__class__.__name__
        s = u'\n'.join(self.strkey(f.name,cname) for f in self.fields)
        return u"[%s]\n%s"%(cname,s)

#------------------------------------------------------------------------------

class StructMaker(StructFormatter):
    """The StructMaker class is a StructFormatter equipped with methods that
    allow to interactively define and adjust fields at some given offsets
    or when some given sample bytes match a given value.
    """
    fields = []

    @property
    def source(cls):
        return '\n'.join((x.source for x in cls.fields))

    @classmethod
    def define(cls,fmt,offset=-1,atvalue=None,indata=b""):
        d = StructDefine(fmt)
        if len(d.fields)>1:
            logger.warning("can't define more than one field at a time...")
        f = d.fields[0]
        if atvalue != None:
            s = f.pack(atvalue)
            offset = indata.find(s)
            logger.info("value found at offset %d"%offset)
        if offset>=0:
            newf = []
            pos=0
            for x in cls.fields:
                lx = pos+len(x)
                if pos<=offset<lx:
                    if x.name == "#undef":
                        count = offset-pos
                        if count>0:
                            newf.append(RawField('s',count,'#undef'))
                        newf.append(f)
                        count = lx-(offset+len(f))
                        if count>0:
                            newf.append(RawField('s',count,'#undef'))
                    else:
                        logger.error("can't overlap existing field!")
                        return None
                else:
                    newf.append(x)
                pos = lx
            if offset>=pos:
                count = offset-pos
                if count>0:
                    newf.append(RawField('s',count,'#undef'))
                newf.append(f)
            cls.fields = newf
            return f
        else:
            return None

#------------------------------------------------------------------------------

def StructFactory(name,fmt,**kargs):
    'Returns a StructFormatter class build with name and format'
    return StructDefine(fmt,**kargs)(type(name,(StructFormatter,),{}))

def UnionFactory(name,fmt,**kargs):
    'Returns a StructFormatter (union) class build with name and format'
    return UnionDefine(fmt,**kargs)(type(name,(StructFormatter,),{}))

#------------------------------------------------------------------------------

# our data structures exception handler:
class StructureError(Exception):
    def __init__(self,message):
        self.message = message
    def __str__(self):
        return str(self.message)

