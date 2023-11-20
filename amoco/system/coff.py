# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2023 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
system/coff.py
==============

The system coff module implements COFF classes for 32bits executable format.
"""
from amoco.system.core import BinFormat
from amoco.system.structs import Consts, StructDefine, UnionDefine, StructureError
from amoco.system.structs import struct, StructFormatter, token_constant_fmt, token_datetime_fmt

from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")

class COFFError(Exception):
    """
    COFFError is raised whenever COFF object instance fails
    to decode required structures.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)

# ------------------------------------------------------------------------------

class COFF(BinFormat):
    """
    This class takes a DataIO object (ie an opened file of BytesIO instance)
    and decodes all COFF structures found in it.

    Attributes:
        entrypoints (list of int): list of entrypoint addresses.
        filename (str): binary file name.
        Fhdr (Fhdr): the COFF header structure.
        Shdr (list of Shdr): the list of COFF Section header structures.
        basemap (int): base address for this COFF image.
        functions (list): a list of function names gathered from internal
                          definitions (if not stripped) and import names.
        variables (list): a list of global variables' names (if found.)
    """
    is_COFF = True

    @property
    def entrypoints(self):
        return [self.OptHdr.entry]

    @property
    def filename(self):
        return self.__file.name

    @property
    def header(self):
        return self.Fhdr

    @property
    def dataio(self):
        return self.__file

    def __init__(self, f):
        self.__file = f
        self.Fhdr = FILEHDR(f)
        offset = self.Fhdr.size()
        offmax = f.size()-1
        if self.Fhdr.f_opthdr > 0:
            sz = self.Fhdr.f_opthdr
            try:
                self.OptHdr = AOUTHDR(f,offset)
                assert self.OptHdr.size() == (sz:=self.Fhdr.f_opthdr)
            except AssertionError:
                self.OptHdr = f[offset:offset+sz]
            offset += sz
        self.Shdr = []
        # read sections headers:
        for _ in range(self.Fhdr.f_nscns):
            s = SCNHDR(f,offset)
            self.Shdr.append(s)
            offset += s.size()
            if offset>=offmax:
                logger.warn("no symbol/string tables found")
                return
        # read symbol table
        self.symbols = []
        for _ in range(self.Fhdr.f_nsyms):
            e = SYMENT(f,offset)
            self.symbols.append(e)
            offset += e.size_with_aux()
            if offset>=offmax:
                logger.warn("no string table found")
                return
        # read string table
        if offset+4>=offmax:
            logger.warn("no string table found")
            self.strings = b''
            return
        try:
            sz = struct.unpack("<I",f[offset:offset+4])[0]
            self.strings = f[offset+4:offset+4+sz].split(b"\0")
        except struct.error as e:
            raise COFFError(str(e))

    def getsize(self):
        "total file size of all the Section headers"
        total = sum([s.s_size for s in self.Shdr])
        return total

    def __str__(self):
        ss = ["COFF header:"]
        tmp = self.Fhdr.pfx
        self.Fhdr.pfx = "\t"
        ss.append(self.Fhdr.__str__())
        self.Fhdr.pfx = tmp
        ss += ["\nSections:"]
        for s in self.Shdr:
            tmp = s.pfx
            s.pfx = "\t"
            ss.append(s.__str__())
            ss.append("---")
            s.pfx = tmp
        ss += ["\nSymbols:"]
        for e in self.symbols:
            tmp = e.pfx
            e.pfx = "\t"
            ss.append(e.__str__())
            ss.append("---")
            e.pfx = tmp
        ss += ["\nStrings:"]
        ss.extend(self.strings)
        return "\n".join(ss)

# ------------------------------------------------------------------------------
# COFF header

@StructDefine(
"""
H : f_magic  ; magic number specifying target machine
H : f_nscns  ; number of sections
i : f_timdat ; time and date stamp
i : f_symptr ; file ptr to symbol table
i : f_nsyms  ; number entries in the symbol table
H : f_opthdr ; size of optional header
H : f_flags  
"""
)
class FILEHDR(StructFormatter):
    def __init__(self, data=None):
        self.name_formatter("f_magic")
        self.func_formatter(f_timdat=token_datetime_fmt)
        self.flag_formatter("f_flags")
        if data:
            self.unpack(data)

# legal values for f_magic (object file type):
with Consts("f_magic"):
    I386MAGIC     = 0x14c
    I386PTXMAGIC  = 0x154
    I386AIXMAGIC  = 0x175
    LYNXCOFFMAGIC = 0o415      # LynxOS executables
    OCOFFMAGIC    = 0o514      # I386/LynxOS objects 
    MCOFFMAGIC    = 0o520      # Motorola
    XCOFFMAGIC    = 0o737      # PPC

# legal values for f_flags:
with Consts("f_flags"):
    F_RELFLG = 1
    F_EXEC = 2
    F_LNNO = 4
    F_LSYMS = 0x10
    F_AR16WR = 0x200
    F_AR32WR = 0x400

# ------------------------------------------------------------------------------
# Optional Header (Unix System V case)

@StructDefine(
"""
h : magic      ; magic number
h : vstamp     ; version stamps
i : tsize      ; size of text (in bytes)
i : dsize      ; size of data (in bytes)
i : bsize      ; size of uninitialized data (in bytes)
I : entry      ; entry point
i : text_start ; base of text for this file
i : data_start ; base of data for this file
"""
)
class AOUTHDR(StructFormatter):
    def __init__(self, data=None, offset=0):
        self.address_formatter("entry")
        self.func_formatter(vstamp=token_datetime_fmt)
        self.func_formatter(tsize=token_constant_fmt)
        self.func_formatter(dsize=token_constant_fmt)
        self.func_formatter(bsize=token_constant_fmt)
        if data:
            self.unpack(data,offset)

# ------------------------------------------------------------------------------
# Sections:

@StructDefine(
"""
c*8 : s_name
I : s_paddr
I : s_vaddr
I : s_size
i : s_scnptr
i : s_relptr
i : s_lnnoptr
H : s_nreloc
H : s_nlnno
i : s_flags
"""
)
class SCNHDR(StructFormatter):
    def __init__(self, data=None, offset=0):
        self.name_formatter("s_name")
        self.address_formatter("s_paddr","s_vaddr")
        self.flag_formatter("s_flags")
        self.func_formatter(s_size=token_constant_fmt)
        if data:
            self.unpack(data, offset)
            self._v.raw_data = self.get_raw_data(data)
            self._v.relocs = self.get_relocs(data)
            self._v.lnnos = self.get_lnnos(data)
        else:
            self._v.raw_data = None
            self._v.relocs = None
            self._v.lnnos = None

    def get_raw_data(self,data):
        if hasattr(self._v,"raw_data"):
            return self._v.raw_data
        else:
            return data[self._v.s_scnptr:self._v.s_scnptr + self._v.s_size]

    def get_relocs(self,data):
        if hasattr(self._v,"relocs"):
            return self._v.relocs
        else:
            relocs = []
            offset = self._v.s_relptr
            for _ in range(self._v.s_nreloc):
                r = RELOC(data,offset)
                relocs.append(r)
                offset += r.size()
            return relocs

    def get_lnnos(self,data):
        if hasattr(self._v,"lnnos"):
            return self._v.lnnos
        else:
            lnnos = []
            offset = self._v.s_lnnoptr
            for _ in range(self._v.s_nlnno):
                l = LINENO(data,offset)
                lnnos.append(l)
                offset += l.size()
            return lnnos


with Consts("s_flags"):
    STYP_REG    = 0x00
    STYP_DSECT  = 0x01
    STYP_NOLOAD = 0x02
    STYP_GROUP  = 0x04
    STYP_PAD    = 0x08
    STYP_COPY   = 0x10
    STYP_TEXT   = 0x20
    STYP_DATA   = 0x40
    STYP_BSS    = 0x80
    STYP_INFO   = 0x200
    STYP_OVER   = 0x400
    STYP_LIB    = 0x800

# ------------------------------------------------------------------------------
# Relocations:

@StructDefine(
"""
i : r_vaddr
i : r_symndx
H : r_type
"""
)
class RELOC(StructFormatter):
    def __init__(self, data=None, offset=0):
        self.name_formatter("s_name")
        self.address_formatter("s_paddr","s_vaddr")
        self.flag_formatter("s_flags")
        self.func_formatter(s_size=token_constant_fmt)
        if data:
            self.unpack(data, offset)

# ------------------------------------------------------------------------------
# Line numbers:

@UnionDefine(
"""
i : l_symndx
i : l_paddr
"""
)
class ln_loc(StructFormatter):
    def __init__(self, data=None, offset=0):
        self.address_formatter("l_paddr")
        self.func_formatter(l_symndx=token_constant_fmt)
        if data:
            self.unpack(data, offset)

@StructDefine(
"""
ln_loc : l_addr
H      : l_lnno
"""
)
class LINENO(StructFormatter):
    def __init__(self, data=None, offset=0):
        self.func_formatter(l_lnno=token_constant_fmt)
        if data:
            self.unpack(data, offset)

# ------------------------------------------------------------------------------
# Symbols:

@StructDefine(
"""
i : _n_zeroes
i : _n_offset
"""
)
class u_n(StructFormatter):
    def __init__(self, data=None, offset=0):
        self.func_formatter(_n_offset=token_constant_fmt)
        if data:
            self.unpack(data, offset)

@UnionDefine(
"""
c*8 : _n_name
u_n : _n_n
i*2 : _n_nptr
"""
)
class sym_n(StructFormatter):
    def __init__(self, data=None, offset=0):
        if data:
            self.unpack(data, offset)

@StructDefine(
"""
sym_n : _n        ; symbol ref
I     : n_value   ; symbol value
h     : n_scnum   ; section number of symbol
H     : n_type    ; basic and derived type spec
b     : n_sclass  ; storage class of symbol
B     : n_numaux  ; nbr of auxiliary entries
"""
)
class SYMENT(StructFormatter):
    def __init__(self, data=None, offset=0):
        self.name_formatter("n_sclass","n_scnum")
        self.func_formatter(n_numaux=token_constant_fmt)
        if data:
            self.unpack(data, offset)
            self.aux = self.get_aux(data,offset)

    def get_fundamental_type(self):
        return self._v.n_type&0xf
    def get_derived_types(self):
        dt = []
        v = self._v.n_type>>4
        for _ in range(6):
          dt.append(v&0x3)
          v = v>>2
        return dt

    def get_aux(self,data,offset=0):
        aux = []
        for _ in range(self._v.n_numaux):
            x = AUXENT(data,offset)
            aux.append(x)
            offset += x.size()
        return aux

    def size_with_aux(self):
        return self.size() + sum((a.size() for a in self.aux),0)

with Consts("n_scnum"):
    N_DEBUG = -2
    N_ABS   = -1
    N_UNDEF = 0

with Consts("n_sclass"):
    C_EFCN    = -1
    C_NULL    =  0
    C_AUTO    =  1   # for .target,                              value means stack offset in bytes
    C_EXT     =  2   #                                           value means relocatable address
    C_STAT    =  3   # for .text .data and .bss                  value means relocatable address
    C_REG     =  4   #                                           value means register number
    C_EXTDEF  =  5
    C_LABEL   =  6   #                                           value means relocatable address
    C_ULABEL  =  7
    C_MOS     =  8   #                                           value means offset in bytes
    C_ARG     =  9   #                                           value means stack offset in bytes
    C_STRARG  =  10
    C_MOU     =  11
    C_UNTAG   =  12
    C_TPDEF   =  13
    C_USTATIC =  14
    C_ENTAG   =  15
    C_MOE     =  16  #                                           value means enumeration value
    C_REGPARM =  17  #                                           value means register number
    C_FIELD   =  18  #                                           value means bit displacement
    C_BLOCK   =  100 # for .bb and .eb                           value means relocatable address
    C_FCN     =  101 # for .bf and .ef                           value means relocatable address
    C_EOS     =  102 # for .eos                                  value means size
    C_FILE    =  103 # for .file
    C_LINE    =  104
    C_ALIAS   =  105 # generated by cprs (compress utility)      value means tag index
    C_HIDDEN  =  106 # not used by any unix system tools         value means relocatable address

# auxiliary entries:

@StructDefine(
"""
H : x_lnno
H : x_size
"""
)
class lnsz(StructFormatter):
    pass

@UnionDefine(
"""
lnsz : x_lnsz
i    : x_fsize
"""
)
class aux_misc(StructFormatter):
    pass

@StructDefine(
"""
i : x_lnnoptr
i : x_endndx
"""
)
class fcn(StructFormatter):
    pass

@StructDefine(
"""
H*4 : x_dimen
"""
)
class ary(StructFormatter):
    pass

@UnionDefine(
"""
fcn : x_fcn
ary : x_ary
"""
)
class u_fcnary(StructFormatter):
    pass

@UnionDefine(

"""
i        : x_tagndx
aux_misc : x_misc
u_fcnary : x_fcnary
H        : x_tvndx
"""
)
class aux_sym(StructFormatter):
    pass

@StructDefine(
"""
c*14 : x_fname
"""
)
class aux_file(StructFormatter):
    pass

@StructDefine(
"""
i : x_scnlen
H : x_nreloc
H : x_nlinno
"""
)
class aux_scn(StructFormatter):
    pass

@StructDefine(
"""
i   : x_tvfill
H   : x_tvlen
H*2 : x_tvran
"""
)
class aux_tv(StructFormatter):
    pass

@StructDefine(
"""
aux_sym   : x_sym
aux_file  : x_file
aux_scn   : x_scn
aux_tv    : x_tv
"""
)
class AUXENT(StructFormatter):
    pass

