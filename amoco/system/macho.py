# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
system/macho.py
================

The system macho module implements the Mach-O executable format parser.
"""
from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")

from collections import defaultdict

# our exception handler:
class MachOError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


# ------------------------------------------------------------------------------
from amoco.system.core import BinFormat, DataIO
from amoco.system.utils import read_uleb128


class MachO(BinFormat):
    is_MachO = True

    @property
    def entrypoints(self):
        if self.__entry:
            return [self.__entry]
        for c in self.cmds:
            if c.cmd in (LC_THREAD, LC_UNIXTHREAD):
                try:
                    self.__entry = c.entrypoint
                except AttributeError:
                    pass
            if c.cmd == LC_MAIN:
                base = self.base_address()
                # remplacement for thread commands
                self.__entry = base + c.entryoff
                break
        return [self.__entry]

    @property
    def filename(self):
        return self.__file.name

    def __init__(self, f):
        self.__file = f
        self.__entry = None
        self._is_fat = False
        try:
            self.header = struct_mach_header(f)
        except:
            raise MachOError("not a Mach-O header")
        if self.header.magic == MH_MAGIC_64:
            self.header = struct_mach_header_64(f)
        elif self.header.magic == FAT_CIGAM:
            self.header = struct_fat_header(f)
            self._is_fat = True
        else:
            if not self.header.magic == MH_MAGIC:
                raise MachOError("not a Mach-O header")
        offset = len(self.header)
        if self._is_fat:
            self.archs = []
            for i in range(self.header.nfat_arch):
                a = struct_fat_arch(f, offset)
                offset += len(a)
                self.archs.append(a)
                self.read_fat_arch(a)
        else:
            self.cmds = self.read_commands(offset)
            for c in self.cmds:
                if c.cmd in (LC_THREAD, LC_UNIXTHREAD):
                    c.getstate(self.header.cputype)
                elif c.cmd == LC_SYMTAB:
                    self.symtab = self.__read_symtab(c)
                elif c.cmd == LC_DYSYMTAB:
                    self.dysymtab = self.__read_dysymtab(c)
                elif c.cmd in (LC_DYLD_INFO, LC_DYLD_INFO_ONLY):
                    self.dyld_info = self.__read_dyld_info(c)
                elif c.cmd == LC_FUNCTION_STARTS:
                    self.function_starts = self.__read_funcstarts(c)
            self.la_symbol_ptr = self.__la_bindings()
            self.nl_symbol_ptr = self.__nl_bindings()

    def read_fat_arch(self, a):
        self.__f.seek(a.offset)
        data = self.__f.read(a.size)
        a.bin = MachO(DataIO(data))

    def read_commands(self, offset):
        cmds = []
        lcsize = 0
        f = self.__file
        f.seek(0)
        while lcsize < self.header.sizeofcmds:
            cmd = struct_load_command(f, offset)
            data = f[offset : offset + cmd.cmdsize]
            offset += cmd.cmdsize
            lcsize += cmd.cmdsize
            if cmd.cmd in CMD_TABLE:
                try:
                    cmd = CMD_TABLE[cmd.cmd](data)
                except:
                    raise MachOError("bad load command:\n%s" % cmd)
            cmds.append(cmd)
        return cmds

    def getsize(self):
        total = 0
        for c in self.cmds:
            if c.cmd in (LC_SEGMENT, LC_SEGMENT_64,):
                total += c.vmsize
        return total

    def getinfo(self, target):
        """getinfo return a triplet (s,off,vaddr) with segment, offset
        into segment, and segment virtual base address that contains the
        target argument.
        """
        res = (None, 0, 0)
        for c in self.cmds:
            if c.cmd in (LC_SEGMENT, LC_SEGMENT_64,):
                if c.vmaddr <= target <= (c.vmaddr + c.vmsize):
                    res = (c, (target - c.vmaddr), c.vmaddr)
                    break
        return res

    def data(self, target, size):
        return self.readcode(target, size)[0]

    def readcode(self, target, size):
        s, offset, _ = self.getinfo(target)
        data = self.readsegment(s)
        return data[offset : offset + size]

    def getfileoffset(self, target):
        s, offset, _ = self.getinfo(target)
        return s.fileoffset + offset

    def readsegment(self, S):
        self.__file.seek(S.fileoffset)
        return self.__file.read(S.filesize)

    def loadsegment(self, S, pagesize=None):
        s = self.readsegment(S)
        if pagesize is None:
            pagesize = S.vmsize
        n, r = divmod(S.vmsize, pagesize)
        if r > 0:
            n += 1
        return s.ljust(n * pagesize, b"\0")

    def readsection(self, s):
        pass

    def __read_table(self, off, elt, count, sz=0):
        tab = []
        if count > 0:
            self.__file.seek(off)
            if sz == 0:
                sz = elt.size()
            for n in range(count):
                data = self.__file.read(sz)
                tab.append(elt(data))
        return tab

    def __read_symtab(self, s):
        if self.header.magic == MH_MAGIC_64:
            el = struct_nlist64
        elif self.header.magic == MH_MAGIC:
            el = struct_nlist
        else:
            raise NotImplementedError
        dylibs = []
        for c in self.cmds:
            if c.cmd == LC_LOAD_DYLIB:
                self.dynamic = True
                dylibs.append(c)
        symtab = self.__read_table(s.symoff, el, s.nsyms)
        strtab = self.__read_strtab(s)
        for x in symtab:
            sta = x.n_strx
            sto = strtab.index(b"\0", sta)
            x.strx = strtab[sta:sto]
            if self.header.flags & MH_TWOLEVEL:
                i = (x.n_desc & 0xFF00) >> 8
                if i > 0:
                    x.strx = b"%s::%s" % (dylibs[i - 1].dylib.name, x.strx)
        return symtab

    def __read_strtab(self, s):
        self.__file.seek(s.stroff)
        data = self.__file.read(s.strsize)
        return data

    def __read_dyld_info(self, cmd):
        t = type("container", (object,), {})
        # rebase opcodes (raw):
        self.__file.seek(cmd.rebase_off)
        t.rebase = self.__file.read(cmd.rebase_size)
        # bind opcodes (as a list of binding records):
        self.__file.seek(cmd.bind_off)
        rawbind = self.__file.read(cmd.bind_size)
        t.bind = self.__read_bind_opcodes(rawbind)
        # weak_bind opcodes (as a list of binding records):
        self.__file.seek(cmd.weak_bind_off)
        weak_bind = self.__file.read(cmd.weak_bind_size)
        t.weak_bind = self.__read_bind_opcodes(weak_bind)
        # lazy_bind opcodes (as a list of binding records):
        # see source code: the record type is POINTER by default...
        self.__file.seek(cmd.lazy_bind_off)
        lazy_bind = self.__file.read(cmd.lazy_bind_size)
        t.lazy_bind = self.__read_bind_opcodes(lazy_bind, BIND_TYPE_POINTER)
        # exports (raw):
        self.__file.seek(cmd.export_off)
        t.export = self.__file.read(cmd.export_size)
        return t

    # see dyld source: ImageLoaderMachOCompressed.cpp.
    def __read_bind_opcodes(self, raw, default_type=0):
        r = record(0, 0, 0, default_type, 0, 0)
        L = []
        cur = 0
        l = 8 if self.header.magic == MH_MAGIC_64 else 4
        while cur < len(raw):
            op = raw[cur] & BIND_OPCODE_MASK
            im = raw[cur] & BIND_IMMEDIATE_MASK
            cur += 1
            if op == BIND_OPCODE_DONE:
                r = record(0, 0, 0, 0, 0, 0)
            elif op == BIND_OPCODE_SET_DYLIB_ORDINAL_IMM:
                r.lib_ordinal = im
            elif op == BIND_OPCODE_SET_DYLIB_ORDINAL_ULEB:
                val, cnt = read_uleb128(raw[cur:])
                r.lib_ordinal = val
                cur += cnt
            elif op == BIND_OPCODE_SET_ADDEND_SLEB:
                val, cnt = read_sleb128(raw[cur:])
                r.addend = val
                cur += cnt
            elif op == BIND_OPCODE_SET_DYLIB_SPECIAL_IMM:
                r.lib_ordinal = (0, -1, -2)[im]
            elif op == BIND_OPCODE_SET_SYMBOL_TRAILING_FLAGS_IMM:
                r.flags = im
                nulchar = raw.find(b"\0", cur)
                if nulchar > cur:
                    r.symbol = raw[cur:nulchar]
                cur = nulchar + 1
            elif op == BIND_OPCODE_SET_TYPE_IMM:
                r.type = im
            elif op == BIND_OPCODE_SET_SEGMENT_AND_OFFSET_ULEB:
                r.seg_index = im
                val, cnt = read_uleb128(raw[cur:])
                r.seg_offset = val
                cur += cnt
            elif op == BIND_OPCODE_DO_BIND:
                L.append(r.as_list())
                r.seg_offset += l
            elif op == BIND_OPCODE_ADD_ADDR_ULEB:
                val, cnt = read_uleb128(raw[cur:])
                r.seg_offset += val
                cur += cnt
            elif op == BIND_OPCODE_DO_BIND_ADD_ADDR_ULEB:
                L.append(r.as_list())
                val, cnt = read_uleb128(raw[cur:])
                r.seg_offset += l + val
                cur += cnt
            elif op == BIND_OPCODE_DO_BIND_ADD_ADDR_IMM_SCALED:
                L.append(r.as_list())
                r.seg_offset += im * l + l
                cur += cnt
            elif op == BIND_OPCODE_DO_BIND_ULEB_TIMES_SKIPPING_ULEB:
                count, cnt = read_uleb128(raw[cur:])
                skip, cnt2 = read_uleb128(raw[cur + cnt :])
                for i in range(count):
                    L.append(r.as_list())
                    r.seg_offset += skip + l
                cur += cnt + cnt2
            else:
                raise NotImplementedError
        return L

    def __read_dysymtab(self, cmd):
        t = type("container", (object,), {})
        # read table of contents:
        t.toc = self.__read_table(cmd.tocoff, struct_dylib_table_of_contents, cmd.ntoc)
        # read module table:
        if self.header.magic == MH_MAGIC_64:
            elt = struct_dylib_module_64
        elif self.header.magic == MH_MAGIC:
            elt = struct_dylib_module
        else:
            raise MachOError("module table error")
        t.modtab = self.__read_table(cmd.modtaboff, elt, cmd.nmodtab)
        t.extrefsym = self.__read_table(
            cmd.extrefsymoff, struct_dylib_reference, cmd.nextrefsyms
        )
        t.indirectsym = self.__read_table(
            cmd.indirectsymoff, struct_indirect_entry, cmd.nindirectsyms
        )
        t.extrel = self.__read_table(cmd.extreloff, struct_relocation_info, cmd.nextrel)
        t.locrel = self.__read_table(cmd.locreloff, struct_relocation_info, cmd.nlocrel)
        return t

    def __la_bindings(self):
        segs = [c for c in self.cmds if c.cmd in (LC_SEGMENT, LC_SEGMENT_64)]
        libs = [c for c in self.cmds if c.cmd == LC_LOAD_DYLIB]
        D = {}
        if hasattr(self, "dyld_info"):
            for b in self.dyld_info.lazy_bind:
                r = record(*b)
                addr = segs[r.seg_index].vmaddr + r.seg_offset + r.addend
                name = b"%s::%s" % (libs[r.lib_ordinal - 1].dylib.name, r.symbol)
                D[addr] = name
        return D

    def __nl_bindings(self):
        segs = [c for c in self.cmds if c.cmd in (LC_SEGMENT, LC_SEGMENT_64)]
        libs = [c for c in self.cmds if c.cmd == LC_LOAD_DYLIB]
        D = {}
        if hasattr(self, "dyld_info"):
            for b in self.dyld_info.bind:
                r = record(*b)
                addr = segs[r.seg_index].vmaddr + r.seg_offset + r.addend
                name = b"%s::%s" % (libs[r.lib_ordinal - 1].dylib.name, r.symbol)
                D[addr] = name
        return D

    def base_address(self):
        fbaseaddr = None
        for c in self.cmds:
            if c.cmd in (LC_SEGMENT, LC_SEGMENT_64):
                if c.fileoffset == 0 and c.filesize > 0:
                    fbaseaddr = c.vmaddr
        return fbaseaddr

    # source: https://opensource.apple.com/source/ld64/ld64-127.2/src/other/dyldinfo.cpp
    def __read_funcstarts(self, fs):
        fbaseaddr = self.base_address()
        addr = fbaseaddr
        F = []
        if fs is not None:
            self.__file.seek(fs.dataoff)
            data = self.__file.read(fs.datasize)
            p = 0
            while p < len(data):
                delta, shift = 0, 0
                more = True
                while more:
                    b = data[p]
                    p += 1
                    delta |= (b & 0x7F) << shift
                    shift += 7
                    if b < 0x80:
                        addr += delta
                        F.append(addr)
                        more = False
        return F

    def __str__(self):
        S = []
        line = "\n" + ("-" * 80)
        S.append(str(self.header) + line)
        for c in self.cmds:
            S.append(str(c) + line)
        return "\n".join(S)


# ------------------------------------------------------------------------------
from amoco.system.structs import Consts, StructFormatter, default_formatter
from amoco.system.structs import StructDefine, UnionDefine


@StructDefine(
    """
I  :> magic
I  :> nfat_arch
"""
)
class struct_fat_header(StructFormatter):
    alt = "mh"

    def __init__(self, data=None):
        self.name_formatter("magic")
        if data:
            self.unpack(data)


@StructDefine(
    """
I  :> cputype
I  :> cpusubtype
I  :> offset
I  :> size
I  :> align
"""
)
class struct_fat_arch(StructFormatter):
    alt = "mh"

    def __init__(self, data=None, offset=0):
        self.name_formatter("cputype")
        self.func_formatter(cpusubtype=self.subtype_fmt)
        if data:
            self.unpack(data, offset)

    def subtype_fmt(self, k, v, cls):
        alt2 = Consts.All["mh.cputype"].get(self.cputype & 0xFF, "")
        cls2 = "%s.%s" % (self.alt, alt2)
        return token_name_fmt(k, v & 0xFF, cls2)


@StructDefine(
    """
I  : magic
i  : cputype
i  : cpusubtype
I  : filetype
I  : ncmds
I  : sizeofcmds
I  : flags
"""
)
class struct_mach_header(StructFormatter):
    alt = "mh"

    def __init__(self, data=None):
        self.name_formatter("magic")
        self.name_formatter("cputype", "filetype")
        self.func_formatter(cpusubtype=self.subtype_fmt)
        self.flag_formatter("flags")
        if data:
            self.unpack(data)

    def subtype_fmt(self, k, v, cls):
        alt2 = Consts.All["mh.cputype"].get(self.cputype & 0xFF, "")
        cls2 = "%s.%s" % (self.alt, alt2)
        return token_name_fmt(k, v & 0xFF, cls2)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I  : magic
I  : cputype
I  : cpusubtype
I  : filetype
I  : ncmds
I  : sizeofcmds
I  : flags
I  : reserved
"""
)
class struct_mach_header_64(StructFormatter):
    alt = "mh"

    def __init__(self, data=None):
        self.name_formatter("magic")
        self.name_formatter("cputype", "filetype")
        self.func_formatter(cpusubtype=self.subtype_fmt)
        self.flag_formatter("flags")
        if data:
            self.unpack(data)

    def subtype_fmt(self, k, v, cls):
        alt2 = Consts.All["mh.cputype"].get(self.cputype & 0xFF, "")
        cls2 = "%s.%s" % (self.alt, alt2)
        return token_name_fmt(k, v & 0xFF, cls2)


with Consts("mh.magic"):
    MH_MAGIC = 0xFEEDFACE
    MH_CIGAM = 0xCEFAEDFE
    MH_MAGIC_64 = 0xFEEDFACF
    MH_CIGAM_64 = 0xCFFAEDFE
    FAT_MAGIC = 0xCAFEBABE
    FAT_CIGAM = 0xBEBAFECA
    FAT_MAGIC_64 = 0xCAFEBABF
    FAT_CIGAM_64 = 0xBFBAFECA

with Consts("mh.cputype"):
    ANY = -1
    VAX = 1
    MC680x0 = 6
    X86 = 7
    X86_64 = 16777223
    MC98000 = 10
    HPPA = 11
    ARM = 12
    MC88000 = 13
    SPARC = 14
    I860 = 15
    POWERPC = 18
    POWERPC64 = 16777234

with Consts("mh.X86.cpusubtype"):
    CPU_SUBTYPE_386 = 3
    CPU_SUBTYPE_486 = 4
    CPU_SUBTYPE_486SX = 0x84
    CPU_SUBTYPE_586 = 5
    CPU_SUBTYPE_X86_64_H = 8
    CPU_SUBTYPE_PENTPRO = 0x16
    CPU_SUBTYPE_PENTII_M3 = 0x36
    CPU_SUBTYPE_PENTII_M5 = 0x56
    CPU_SUBTYPE_CELERON = 0x67
    CPU_SUBTYPE_CELERON_MOBILE = 0x77
    CPU_SUBTYPE_PENTIUM_3 = 0x08
    CPU_SUBTYPE_PENTIUM_3_M = 0x18
    CPU_SUBTYPE_PENTIUM_3_XEON = 0x28
    CPU_SUBTYPE_PENTIUM_M = 0x09
    CPU_SUBTYPE_PENTIUM_4 = 0x0A
    CPU_SUBTYPE_PENTIUM_4_M = 0x1A
    CPU_SUBTYPE_ITANIUM = 0x0B
    CPU_SUBTYPE_ITANIUM_2 = 0x1B
    CPU_SUBTYPE_XEON = 0x0C
    CPU_SUBTYPE_XEON_MP = 0x1C

with Consts("mh.ARM.cpusubtype"):
    CPU_SUBTYPE_ARM_ALL = 0
    CPU_SUBTYPE_ARM_V4T = 5
    CPU_SUBTYPE_ARM_V6 = 6
    CPU_SUBTYPE_ARM_V5 = 7
    CPU_SUBTYPE_ARM_XSCALE = 8
    CPU_SUBTYPE_ARM_V7 = 9
    CPU_SUBTYPE_ARM_V7S = 11
    CPU_SUBTYPE_ARM_V7K = 12
    CPU_SUBTYPE_ARM_V6M = 14
    CPU_SUBTYPE_ARM_V7M = 15
    CPU_SUBTYPE_ARM_V7EM = 16

with Consts("mh.POWERPC.cpusubtype"):
    CPU_SUBTYPE_POWERPC_ALL = 0
    CPU_SUBTYPE_POWERPC_601 = 1
    CPU_SUBTYPE_POWERPC_602 = 2
    CPU_SUBTYPE_POWERPC_603 = 3
    CPU_SUBTYPE_POWERPC_603e = 4
    CPU_SUBTYPE_POWERPC_603ev = 5
    CPU_SUBTYPE_POWERPC_604 = 6
    CPU_SUBTYPE_POWERPC_604e = 7
    CPU_SUBTYPE_POWERPC_620 = 8
    CPU_SUBTYPE_POWERPC_750 = 9
    CPU_SUBTYPE_POWERPC_7400 = 10
    CPU_SUBTYPE_POWERPC_7450 = 11
    CPU_SUBTYPE_POWERPC_970 = 100

with Consts("mh.filetype"):
    MH_OBJECT = 0x1  # relocatable object file
    MH_EXECUTE = 0x2  # executable binary
    MH_FVMLIB = 0x3
    MH_CORE = 0x4  # core dump
    MH_PRELOAD = 0x5
    MH_DYLIB = 0x6  # dynamic library
    MH_DYLINKER = 0x7  # dynamic linker
    MH_BUNDLE = 0x8  # Plug-ins
    MH_DYLIB_STUB = 0x9
    MH_DSYM = 0xA  # symbol file & debug info
    MH_KEXT_BUNDLE = 0xB  # kernel extension

with Consts("mh.flags"):
    MH_NOUNDEFS = 0x1
    MH_INCRLINK = 0x2
    MH_DYLDLINK = 0x4
    MH_BINDATLOAD = 0x8
    MH_PREBOUND = 0x10
    MH_SPLIT_SEGS = 0x20
    MH_LAZY_INIT = 0x40
    MH_TWOLEVEL = 0x80
    MH_FORCE_FLAT = 0x100
    MH_NOMULTIDEFS = 0x200
    MH_NOFIXPREBINDING = 0x400
    MH_PREBINDABLE = 0x800
    MH_ALLMODSBOUND = 0x1000
    MH_SUBSECTIONS_VIA_SYMBOLS = 0x2000
    MH_CANONICAL = 0x4000
    MH_WEAK_DEFINES = 0x8000
    MH_BINDS_TO_WEAK = 0x10000
    MH_ALLOW_STACK_EXECUTION = 0x20000
    MH_ROOT_SAFE = 0x40000
    MH_SETUID_SAFE = 0x80000
    MH_NO_REEXPORTED_DYLIBS = 0x100000
    MH_PIE = 0x200000
    MH_DEAD_STRIPPABLE_DYLIB = 0x400000
    MH_HAS_TLV_DESCRIPTORS = 0x800000
    MH_NO_HEAP_EXECUTION = 0x1000000

# ------------------------------------------------------------------------------
def token_cmd_fmt(k, val, cls=None):
    s = []
    if val & LC_REQ_DYLD:
        s.append(highlight([(Token.Name, "LC_REQ_DYLD")]))
    s.append(token_name_fmt(k, val, "lc"))
    return "+".join(s)


@StructDefine(
    """
I  : cmd
I  : cmdsize
"""
)
class struct_load_command(StructFormatter):
    alt = "lc"

    def __init__(self, data=None, offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)


with Consts("lc.cmd"):
    LC_REQ_DYLD = 0x80000000
    LC_SEGMENT = 0x1
    LC_SYMTAB = 0x2
    LC_SYMSEG = 0x3
    LC_THREAD = 0x4
    LC_UNIXTHREAD = 0x5
    LC_LOADFVMLIB = 0x6
    LC_IDFVMLIB = 0x7
    LC_IDENT = 0x8
    LC_FVMFILE = 0x9
    LC_PREPAGE = 0xA
    LC_DYSYMTAB = 0xB
    LC_LOAD_DYLIB = 0xC  # load dynamic lib
    LC_ID_DYLIB = 0xD  # id of a dynamic lib
    LC_LOAD_DYLINKER = 0xE
    LC_ID_DYLINKER = 0xF
    LC_PREBOUND_DYLIB = 0x10
    LC_ROUTINES = 0x11
    LC_SUB_FRAMEWORK = 0x12
    LC_SUB_UMBRELLA = 0x13
    LC_SUB_CLIENT = 0x14
    LC_SUB_LIBRARY = 0x15
    LC_TWOLEVEL_HINTS = 0x16
    LC_PREBIND_CKSUM = 0x17
    LC_LOAD_WEAK_DYLIB = 0x18 | LC_REQ_DYLD
    LC_SEGMENT_64 = 0x19
    LC_ROUTINES_64 = 0x1A
    LC_UUID = 0x1B
    LC_RPATH = 0x1C | LC_REQ_DYLD
    LC_CODE_SIGNATURE = 0x1D
    LC_SEGMENT_SPLIT_INFO = 0x1E
    LC_REEXPORT_DYLIB = 0x1F | LC_REQ_DYLD
    LC_LAZY_LOAD_DYLIB = 0x20  # defered load dynamic lib
    LC_ENCRYPTION_INFO = 0x21
    LC_DYLD_INFO = 0x22
    LC_DYLD_INFO_ONLY = 0x22 | LC_REQ_DYLD
    LC_LOAD_UPWARD_DYLIB = 0x23 | LC_REQ_DYLD
    LC_VERSION_MIN_MACOSX = 0x24
    LC_VERSION_MIN_IPHONEOS = 0x25
    LC_FUNCTION_STARTS = 0x26  # compressed table of funcs addr
    LC_DYLD_ENVIRONMENT = 0x27
    LC_MAIN = 0x28 | LC_REQ_DYLD
    LC_DATA_IN_CODE = 0x29
    LC_SOURCE_VERSION = 0x2A
    LC_DYLIB_CODE_SIGN_DRS = 0x2B
    LC_ENCRYPTION_INFO_64 = 0x2C
    LC_LINKER_OPTION = 0x2D
    LC_LINKER_OPTIMIZATION_HINT = 0x2E
    LC_VERSION_MIN_TVOS = 0x2F
    LC_VERSION_MIN_WATCHOS = 0x30
    LC_NOTE = 0x31
    LC_BUILD_VERSION = 0x32

# ------------------------------------------------------------------------------


class MachoFormatter(StructFormatter):
    fkeys = defaultdict(default_formatter)

    def pack(self, data=None):
        res = StructFormatter.pack(self, data)
        return res.ljust(self.cmdsize, b"\0")


@StructDefine(
    """
I    : cmd
I    : cmdsize
s*16 : segname
I    : vmaddr
I    : vmsize
I    : fileoffset
I    : filesize
i    : maxprot
i    : initprot
I    : nsects
I    : flags
"""
)
class struct_segment_command(MachoFormatter):
    alt = "sg"

    def __init__(self, data=None, offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        self.func_formatter(segname=self.segname_fmt)
        self.flag_formatter("flags")
        self.address_formatter("vmaddr", "vmsize")
        self.address_formatter("fileoffset", "filesize")
        if data:
            self.unpack(data, offset)
            offset += len(self)
            self.sections = []
            for i in range(self.nsects):
                s = struct_section(data, offset)
                offset += len(s)
                self.sections.append(s)

    def segname_fmt(self, k, x, cls=None):
        return highlight([(Token.String, str(x.strip(b"\0")))])


# ------------------------------------------------------------------------------


@StructDefine(
    """
I    : cmd
I    : cmdsize
s*16 : segname
Q    : vmaddr
Q    : vmsize
Q    : fileoffset
Q    : filesize
i    : maxprot
i    : initprot
I    : nsects
I    : flags
"""
)
class struct_segment_command_64(MachoFormatter):
    alt = "sg"

    def __init__(self, data=None, offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        self.func_formatter(segname=self.segname_fmt)
        self.flag_formatter("flags")
        self.address_formatter("vmaddr", "vmsize")
        self.address_formatter("fileoffset", "filesize")
        if data:
            self.unpack(data, offset)
            offset += len(self)
            self.sections = []
            for i in range(self.nsects):
                s = struct_section_64(data, offset)
                offset += len(s)
                self.sections.append(s)

    def segname_fmt(self, k, x, cls=None):
        return highlight([(Token.String, str(x.strip(b"\0")))])


# ------------------------------------------------------------------------------
with Consts("sg.flags"):
    SG_HIGHVM = 0x1
    SG_FVMLIB = 0x2
    SG_NORELOC = 0x4
    SG_PROTECTED_VERSION_1 = 0x8


@StructDefine(
    """
B   : type
B*3 : attr
"""
)
class SFLG(MachoFormatter):
    alt = "sflg"

    def __init__(self, data=None, offset=0):
        self.name_formatter("type")
        self.func_formatter(attr=self.attr_fmt)
        if data:
            self.unpack(data, offset)

    @staticmethod
    def attr_fmt(k, val, cls=None):
        v = val[0] | (val[1] << 8) | (val[2] << 16)
        return token_flag_fmt(k, v, cls)


with Consts("sflg.type"):
    S_REGULAR = 0x0
    S_ZEROFILL = 0x1
    S_CSTRING_LITERALS = 0x2
    S_4BYTE_LITERALS = 0x3
    S_8BYTE_LITERALS = 0x4
    S_LITERAL_POINTERS = 0x5
    S_NON_LAZY_SYMBOL_POINTERS = 0x6
    S_LAZY_SYMBOL_POINTERS = 0x7
    S_SYMBOL_STUBS = 0x8
    S_MOD_INIT_FUNC_POINTERS = 0x9
    S_MOD_TERM_FUNC_POINTERS = 0xA
    S_COALESCED = 0xB
    S_GB_ZEROFILL = 0xC
    S_INTERPOSING = 0xD
    S_16BYTE_LITERALS = 0xE
    S_DTRACE_DOF = 0xF
    S_LAZY_DYLIB_SYMBOL_POINTERS = 0x10
    S_THREAD_LOCAL_REGULAR = 0x11
    S_THREAD_LOCAL_ZEROFILL = 0x12
    S_THREAD_LOCAL_VARIABLES = 0x13
    S_THREAD_LOCAL_VARIABLE_POINTERS = 0x14
    S_THREAD_LOCAL_INIT_FUNCTION_POINTERS = 0x15

with Consts("sflg.attr"):
    SECTION_ATTRIBUTES_USR = 0xFF000000
    S_ATTR_PURE_INSTRUCTIONS = 0x80000000
    S_ATTR_NO_TOC = 0x40000000
    S_ATTR_STRIP_STATIC_SYMS = 0x20000000
    S_ATTR_NO_DEAD_STRIP = 0x10000000
    S_ATTR_LIVE_SUPPORT = 0x08000000
    S_ATTR_SELF_MODIFYING_CODE = 0x04000000
    S_ATTR_DEBUG = 0x02000000
    SECTION_ATTRIBUTES_SYS = 0x00FFFF00
    S_ATTR_SOME_INSTRUCTIONS = 0x00000400
    S_ATTR_EXT_RELOC = 0x00000200
    S_ATTR_LOC_RELOC = 0x00000100


@StructDefine(
    """
s*16 : sectname
s*16 : segname
I    : addr
I    : size_
I    : offset
I    : align
I    : reloff
I    : nreloc
SFLG : flags
I    : reserved1
I    : reserved2
"""
)
class struct_section(MachoFormatter):
    alt = "s"

    def __init__(self, data=None, offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        self.address_formatter("addr")
        self.address_formatter("offset")
        self.address_formatter("reloff")
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
s*16 : sectname
s*16 : segname
Q    : addr
Q    : size_
I    : offset
I    : align
I    : reloff
I    : nreloc
SFLG : flags
I    : reserved1
I    : reserved2
I    : reserved3
"""
)
class struct_section_64(MachoFormatter):
    alt = "s"

    def __init__(self, data=None, offset=0):
        self.func_formatter(cmd=token_cmd_fmt, offset=0)
        self.address_formatter("addr")
        self.address_formatter("offset")
        self.address_formatter("reloff")
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@UnionDefine(
    """
I     : offset
P     : header_addr
"""
)
class lc_str(MachoFormatter):
    def __init__(self, data=None, offset=0):
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I     : offset
I     : minor_version
I     : header_addr
"""
)
class struct_fvmlib(MachoFormatter):
    def __init__(self, data=None, offset=0):
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
struct_fvmlib : fvmlib
"""
)
class struct_fvmlib_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)
            sta = offset + self.fvmlib.offset
            i = data.find(b"\0", sta)
            if i != -1:
                self.fvmlib.name = data[sta:i]


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : offset
I : timestamp
I : current_version
I : compatibility_version
"""
)
class struct_dylib(MachoFormatter):
    def __init__(self, data="", offset=0):
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
struct_dylib : dylib
"""
)
class struct_dylib_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)
            sta = offset + self.dylib.offset
            i = data.find(b"\0", sta)
            if i != -1:
                self.dylib.name = data[sta:i]


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : offset
"""
)
class struct_sub_framework_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)
            sta = offset + self._v.offset
            i = data.find(b"\0", sta)
            if i != -1:
                self.umbrella = data[sta:i]


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : offset
"""
)
class struct_sub_client_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)
            sta = offset + self._v.offset
            i = data.find(b"\0", sta)
            if i != -1:
                self.client = data[sta:i]


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : offset
"""
)
class struct_sub_umbrella_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)
            sta = offset + self._v.offset
            i = data.find(b"\0", sta)
            if i != -1:
                self.sub_umbrella = data[sta:i]


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : offset
"""
)
class struct_sub_library_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)
            sta = offset + self._v.offset
            i = data.find(b"\0", sta)
            if i != -1:
                self.sub_library = data[sta:i]


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : offset
I : nmodules
I : linked_modules
"""
)
class struct_prebound_dylib_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)
            sta = offset + self._v.offset
            i = data.find(b"\0", sta)
            if i != -1:
                self.name = data[sta:i]


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : offset
"""
)
class struct_dylinker_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)
            sta = offset + self._v.offset
            i = data.find(b"\0", sta)
            if i != -1:
                self.name = data[sta:i]


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : flavor
I : count
"""
)
class struct_thread_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.name_formatter("flavor")
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)
            offset += 16
            self.data = data[offset : offset + self.cmdsize - 16]

    def getstate(self, cputype):
        if cputype in (X86, X86_64):
            self.alt = "lc.x86"
            if self.flavor == x86_THREAD_STATE32:
                self.state = struct_x86_thread_state32(self.data)
                self.entrypoint = self.state["eip"]
            elif self.flavor == x86_THREAD_STATE64:
                self.state = struct_x86_thread_state64(self.data)
                self.entrypoint = self.state["rip"]
        elif cputype in (ARM,):
            self.alt = "lc.arm"
            if self.flavor == ARM_THREAD_STATE32:
                self.state = struct_x86_thread_state32(self.data)
            elif self.flavor == ARM_THREAD_STATE64:
                self.state = struct_x86_thread_state64(self.data)
            self.entrypoint = self.state["pc"]
        return self.state


with Consts("lc.x86.flavor"):
    x86_THREAD_STATE32 = 1
    x86_FLOAT_STATE32 = 2
    x86_EXCEPTION_STATE32 = 3
    x86_THREAD_STATE64 = 4
    x86_FLOAT_STATE64 = 5
    x86_EXCEPTION_STATE64 = 6
    x86_THREAD_STATE = 7
    x86_FLOAT_STATE = 8
    x86_EXCEPTION_STATE = 9
    x86_DEBUG_STATE32 = 10
    x86_DEBUG_STATE64 = 11
    x86_DEBUG_STATE = 12
    x86_THREAD_STATE_NONE = 13
    x86_AVX_STATE32 = 16
    x86_AVX_STATE64 = x86_AVX_STATE32 + 1
    x86_AVX_STATE = x86_AVX_STATE32 + 2
    x86_AVX512_STATE32 = 19
    x86_AVX512_STATE64 = x86_AVX512_STATE32 + 1
    x86_AVX512_STATE = x86_AVX512_STATE32 + 2

with Consts("lc.arm.flavor"):
    ARM_THREAD_STATE = 1
    ARM_VFP_STATE = 2
    ARM_EXCEPTION_STATE = 3
    ARM_DEBUG_STATE = 4
    ARM_THREAD_STATE_NONE = 5
    ARM_THREAD_STATE64 = 6
    ARM_EXCEPTION_STATE64 = 7
    ARM_THREAD_STATE32 = 9
    ARM_DEBUG_STATE32 = 14
    ARM_DEBUG_STATE64 = 15
    ARM_NEON_STATE = 16
    ARM_NEON_STATE64 = 17
    ARM_CPMU_STATE64 = 18
    ARM_SAVED_STATE32 = 20
    ARM_SAVED_STATE64 = 21
    ARM_NEON_SAVED_STATE32 = 20
    ARM_NEON_SAVED_STATE64 = 21


@StructDefine(
    """
I: eax;
I: ebx;
I: ecx;
I: edx;
I: edi;
I: esi;
I: ebp;
I: esp;
I: e8;
I: e9;
I: e10;
I: e11;
I: e12;
I: e13;
I: e14;
I: e15;
I: eip;
I: eflags;
I: cs;
I: fs;
I: gs;
"""
)
class struct_x86_thread_state32(MachoFormatter):
    def __init__(self, data="", offset=0):
        for f in self.fields:
            self.address_formatter(f.name)
        if data:
            self.unpack(data, offset)


@StructDefine(
    """
Q: rax;
Q: rbx;
Q: rcx;
Q: rdx;
Q: rdi;
Q: rsi;
Q: rbp;
Q: rsp;
Q: r8;
Q: r9;
Q: r10;
Q: r11;
Q: r12;
Q: r13;
Q: r14;
Q: r15;
Q: rip;
Q: rflags;
Q: cs;
Q: fs;
Q: gs;
"""
)
class struct_x86_thread_state64(MachoFormatter):
    def __init__(self, data="", offset=0):
        for f in self.fields:
            self.address_formatter(f.name)
        if data:
            self.unpack(data, offset)


@StructDefine(
    """
I*13: r
I   : sp
I   : lr
I   : pc
I   : cpsr
"""
)
class struct_arm_thread_state32(MachoFormatter):
    def __init__(self, data="", offset=0):
        for f in self.fields:
            self.address_formatter(f.name)
        if data:
            self.unpack(data, offset)


@StructDefine(
    """
Q*29: x
Q   : fp
Q   : lr
Q   : sp
Q   : pc
I   : cpsr
I   : pad
"""
)
class struct_arm_thread_state64(MachoFormatter):
    def __init__(self, data="", offset=0):
        for f in self.fields:
            self.address_formatter(f.name)
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : init_address
I : init_module
I : reserved1
I : reserved2
I : reserved3
I : reserved4
I : reserved5
I : reserved6
"""
)
class struct_routines_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
Q : init_address
Q : init_module
Q : reserved1
Q : reserved2
Q : reserved3
Q : reserved4
Q : reserved5
Q : reserved6
"""
)
class struct_routines_command_64(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : symoff
I : nsyms
I : stroff
I : strsize
"""
)
class struct_symtab_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.address_formatter("symoff")
        self.address_formatter("stroff")
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)


@StructDefine(
    """
I : n_strx
B : n_type
B : n_sect
H : n_desc
I : n_value
"""
)
class struct_nlist(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.address_formatter("n_value")
        self.func_formatter(n_type=self.ntype_fmt)
        self.func_formatter(n_desc=self.ndesc_fmt)
        if data:
            self.unpack(data, offset)

    def ntype_fmt(self, k, x, cls=None):
        if x & N_STAB:
            return token_name_fmt(k, x, "lc.stab")
        else:
            l = []
            if x & N_TYPE == 0x0:
                l.append("N_UNDF")
            elif x & N_TYPE == 0x2:
                l.append("N_ABS")
            elif x & N_TYPE == 0xE:
                l.append("N_SECT")
            elif x & N_TYPE == 0xC:
                l.append("N_PBUD")
            elif x & N_TYPE == 0xA:
                l.append("N_INDR")
            if x & N_EXT:
                l.append("N_PEXT")
            s = "+".join(l)
            return highlight([(Token.Name, s)])

    def ndesc_fmt(self, k, x, cls=None):
        s = token_name_fmt(k, x & 0xF, cls)
        if x & 0xF0:
            s += "+" + token_flag_fmt(k, x & 0xF0, "lc.flag")
        return s


@StructDefine(
    """
I : n_strx
B : n_type
B : n_sect
H : n_desc
Q : n_value
"""
)
class struct_nlist64(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.address_formatter("n_value")
        self.func_formatter(n_type=self.ntype_fmt)
        self.func_formatter(n_desc=self.ndesc_fmt)
        if data:
            self.unpack(data, offset)

    def ntype_fmt(self, k, x, cls=None):
        if x & N_STAB:
            return token_name_fmt(k, x, "lc.stab")
        else:
            l = []
            if x & N_PEXT:
                l.append("N_PEXT")
            if x & N_TYPE == 0x0:
                l.append("N_UNDF")
            elif x & N_TYPE == 0x2:
                l.append("N_ABS")
            elif x & N_TYPE == 0xE:
                l.append("N_SECT")
            elif x & N_TYPE == 0xC:
                l.append("N_PBUD")
            elif x & N_TYPE == 0xA:
                l.append("N_INDR")
            if x & N_EXT:
                l.append("N_PEXT")
            s = "+".join(l)
            return highlight([(Token.Name, s)])

    def ndesc_fmt(self, k, x, cls=None):
        s = token_name_fmt(k, x & 0xF, cls)
        if x & 0xF0:
            s += "+" + token_flag_fmt(k, x & 0xF0, "lc.flag")
        return s


with Consts("lc.n_type"):
    N_STAB = 0xE0
    N_PEXT = 0x10
    N_TYPE = 0x0E
    N_EXT = 0x01
    N_UNDF = 0x0
    N_ABS = 0x2
    N_SECT = 0xE
    N_PBUD = 0xC
    N_INDR = 0xA

with Consts("lc.stab.n_type"):
    N_GSYM = 0x20  # global symbol: name,,NO_SECT,type,0
    N_FNAME = 0x22  # procedure name (f77 kludge): name,,NO_SECT,0,0
    N_FUN = 0x24  # procedure: name,,n_sect,linenumber,address
    N_STSYM = 0x26  # static symbol: name,,n_sect,type,address
    N_LCSYM = 0x28  # .lcomm symbol: name,,n_sect,type,address
    N_BNSYM = 0x2E  # begin nsect sym: 0,,n_sect,0,address
    N_AST = 0x32  # AST file path: name,,NO_SECT,0,0
    N_OPT = 0x3C  # emitted with gcc2_compiled and in gcc source
    N_RSYM = 0x40  # register sym: name,,NO_SECT,type,register
    N_SLINE = 0x44  # src line: 0,,n_sect,linenumber,address
    N_ENSYM = 0x4E  # end nsect sym: 0,,n_sect,0,address
    N_SSYM = 0x60  # structure elt: name,,NO_SECT,type,struct_offset
    N_SO = 0x64  # source file name: name,,n_sect,0,address
    N_OSO = 0x66  # object file name: name,,0,0,st_mtime
    N_LSYM = 0x80  # local sym: name,,NO_SECT,type,offset
    N_BINCL = 0x82  # include file beginning: name,,NO_SECT,0,sum
    N_SOL = 0x84  # #included file name: name,,n_sect,0,address
    N_PARAMS = 0x86  # compiler parameters: name,,NO_SECT,0,0
    N_VERSION = 0x88  # compiler version: name,,NO_SECT,0,0
    N_OLEVEL = 0x8A  # compiler -O level: name,,NO_SECT,0,0
    N_PSYM = 0xA0  # parameter: name,,NO_SECT,type,offset
    N_EINCL = 0xA2  # include file end: name,,NO_SECT,0,0
    N_ENTRY = 0xA4  # alternate entry: name,,n_sect,linenumber,address
    N_LBRAC = 0xC0  # left bracket: 0,,NO_SECT,nesting level,address
    N_EXCL = 0xC2  # deleted include file: name,,NO_SECT,0,sum
    N_RBRAC = 0xE0  # right bracket: 0,,NO_SECT,nesting level,address
    N_BCOMM = 0xE2  # begin common: name,,NO_SECT,0,0
    N_ECOMM = 0xE4  # end common: name,,n_sect,0,0
    N_ECOML = 0xE8  # end common (local name): 0,,n_sect,0,address
    N_LENG = 0xFE  # second stab entry with length information
    N_PC = 0x30  # global pascal symbol: name,,NO_SECT,subtype,line

with Consts("lc.n_desc"):
    REFERENCE_FLAG_UNDEFINED_NON_LAZY = 0x0
    REFERENCE_FLAG_UNDEFINED_LAZY = 0x1
    REFERENCE_FLAG_UNDEFINED = 0x2
    REFERENCE_FLAG_PRIVATE_DEFINED = 0x3
    REFERENCE_FLAG_PRIVATE_UNDEFINED_NON_LAZY = 0x4
    REFERENCE_FLAG_PRIVATE_UNDEFINED_LAZY = 0x5
with Consts("lc.flag.n_desc"):
    REFERENCED_DYNAMICALLY = 0x10
    N_DESC_DISCARDED = 0x20
    N_NO_DEAD_STRIP = 0x20
    N_WEAK_REF = 0x40
    N_WEAK_DEF = 0x80

# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : ilocalsym
I : nlocalsym
I : iextdefsym
I : nextdefsym
I : iundefsym
I : nundefsym
I : tocoff
I : ntoc
I : modtaboff
I : nmodtab
I : extrefsymoff
I : nextrefsyms
I : indirectsymoff
I : nindirectsyms
I : extreloff
I : nextrel
I : locreloff
I : nlocrel
"""
)
class struct_dysymtab_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        self.address_formatter(
            "tocoff",
            "modtaboff",
            "extrefsymoff",
            "indirectsymoff",
            "extreloff",
            "locreloff",
        )
        if data:
            self.unpack(data, offset)


INDIRECT_SYMBOL_LOCAL = 0x80000000
INDIRECT_SYMBOL_ABS = 0x40000000

# ------------------------------------------------------------------------------
@StructDefine(
    """
I : symbol_index
I : module_index
"""
)
class struct_dylib_table_of_contents(MachoFormatter):
    def __init__(self, data="", offset=0):
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : module_name
I : iextdefsym
I : nextdefsym
I : irefsym
I : nrefsym
I : ilocalsym
I : nlocalsym
I : iextrel
I : nextrel
I : iinit_iterm
I : ninit_nterm
I : objc_module_info_addr
I : objc_module_info_size
"""
)
class struct_dylib_module(MachoFormatter):
    def __init__(self, data="", offset=0):
        self.address_formatter("objc_module_info_addr")
        self.address_formatter("objc_module_info_size")
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : module_name
I : iextdefsym
I : nextdefsym
I : irefsym
I : nrefsym
I : ilocalsym
I : nlocalsym
I : iextrel
I : nextrel
I : iinit_iterm
I : ninit_nterm
I : objc_module_info_size
Q : objc_module_info_addr
"""
)
class struct_dylib_module_64(MachoFormatter):
    def __init__(self, data="", offset=0):
        self.address_formatter("objc_module_info_addr")
        self.address_formatter("objc_module_info_size")
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
B*3 : isym
B   : flags
"""
)
class struct_dylib_reference(MachoFormatter):
    def __init__(self, data="", offset=0):
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : offset
I : nhints
"""
)
class struct_twolevel_hints_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        self.address_formatter("offset")
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
B   : isub_image
B*3 : itoc
"""
)
class twolevel_hint(MachoFormatter):
    def __init__(self, data="", offset=0):
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : cksum
"""
)
class struct_prebind_cksum_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I    : cmd
I    : cmdsize
B*16 : uuid
"""
)
class struct_uuid_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        self.func_formatter(uuid=self.uuid_fmt)
        if data:
            self.unpack(data, offset)

    def uuid_fmt(self, k, x, cls=None):
        return highlight([(Token.String, ".".join(("%02d" % v for v in x)))])


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : offset
"""
)
class struct_rpath_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)
            sta = offset + self._v.offset
            i = data.find(b"\0", sta)
            if i != -1:
                self.path = data[sta:i]


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : dataoff
I : datasize
"""
)
class struct_linkedit_data_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        self.address_formatter("dataoff", "datasize")
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : cryptoff
I : cryptsize
I : cryptid
"""
)
class struct_encryption_info_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        self.address_formatter("cryptoff", "cryptsize")
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : rebase_off
I : rebase_size
I : bind_off
I : bind_size
I : weak_bind_off
I : weak_bind_size
I : lazy_bind_off
I : lazy_bind_size
I : export_off
I : export_size
"""
)
class struct_dyld_info_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.address_formatter("rebase_off", "rebase_size")
        self.address_formatter("bind_off", "bind_size")
        self.address_formatter("weak_bind_off", "weak_bind_size")
        self.address_formatter("lazy_bind_off", "lazy_bind_size")
        self.address_formatter("export_off", "export_size")
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)


class record(object):
    def __init__(self, indx, off, ordinal, typ, flags, addend, s=None):
        self.seg_index = indx
        self.seg_offset = off
        self.lib_ordinal = ordinal
        self.type = typ
        self.flags = flags
        self.addend = addend
        self.symbol = s

    def as_list(self):
        s = (
            self.seg_index,
            self.seg_offset,
            self.lib_ordinal,
            self.type,
            self.flags,
            self.addend,
            self.symbol,
        )
        return s


with Consts("dyld.rebase"):
    REBASE_TYPE_POINTER = 1
    REBASE_TYPE_TEXT_ABSOLUTE32 = 2
    REBASE_TYPE_TEXT_PCREL32 = 3
    REBASE_OPCODE_MASK = 0xF0
    REBASE_IMMEDIATE_MASK = 0x0F
    REBASE_OPCODE_DONE = 0x00
    REBASE_OPCODE_SET_TYPE_IMM = 0x10
    REBASE_OPCODE_SET_SEGMENT_AND_OFFSET_ULEB = 0x20
    REBASE_OPCODE_ADD_ADDR_ULEB = 0x30
    REBASE_OPCODE_ADD_ADDR_IMM_SCALED = 0x40
    REBASE_OPCODE_DO_REBASE_IMM_TIMES = 0x50
    REBASE_OPCODE_DO_REBASE_ULEB_TIMES = 0x60
    REBASE_OPCODE_DO_REBASE_ADD_ADDR_ULEB = 0x70
    REBASE_OPCODE_DO_REBASE_ULEB_TIMES_SKIPPING_ULEB = 0x80

with Consts("dyld.bind"):
    BIND_TYPE_POINTER = 1
    BIND_TYPE_TEXT_ABSOLUTE32 = 2
    BIND_TYPE_TEXT_PCREL32 = 3
    BIND_SPECIAL_DYLIB_SELF = 0
    BIND_SPECIAL_DYLIB_MAIN_EXECUTABLE = -1
    BIND_SPECIAL_DYLIB_FLAT_LOOKUP = -2
    BIND_SYMBOL_FLAGS_WEAK_IMPORT = 0x1
    BIND_SYMBOL_FLAGS_NON_WEAK_DEFINITION = 0x8
    BIND_OPCODE_MASK = 0xF0
    BIND_IMMEDIATE_MASK = 0x0F
    BIND_OPCODE_DONE = 0x00
    BIND_OPCODE_SET_DYLIB_ORDINAL_IMM = 0x10
    BIND_OPCODE_SET_DYLIB_ORDINAL_ULEB = 0x20
    BIND_OPCODE_SET_DYLIB_SPECIAL_IMM = 0x30
    BIND_OPCODE_SET_SYMBOL_TRAILING_FLAGS_IMM = 0x40
    BIND_OPCODE_SET_TYPE_IMM = 0x50
    BIND_OPCODE_SET_ADDEND_SLEB = 0x60
    BIND_OPCODE_SET_SEGMENT_AND_OFFSET_ULEB = 0x70
    BIND_OPCODE_ADD_ADDR_ULEB = 0x80
    BIND_OPCODE_DO_BIND = 0x90
    BIND_OPCODE_DO_BIND_ADD_ADDR_ULEB = 0xA0
    BIND_OPCODE_DO_BIND_ADD_ADDR_IMM_SCALED = 0xB0
    BIND_OPCODE_DO_BIND_ULEB_TIMES_SKIPPING_ULEB = 0xC0

with Consts("dyld.export"):
    EXPORT_SYMBOL_FLAGS_KIND_MASK = 0x03
    EXPORT_SYMBOL_FLAGS_KIND_REGULAR = 0x00
    EXPORT_SYMBOL_FLAGS_KIND_THREAD_LOCAL = 0x01
    EXPORT_SYMBOL_FLAGS_WEAK_DEFINITION = 0x04
    EXPORT_SYMBOL_FLAGS_INDIRECT_DEFINITION = 0x08
    EXPORT_SYMBOL_FLAGS_HAS_SPECIALIZATIONS = 0x10

# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : offset
I : size_
"""
)
class struct_symseg_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
"""
)
class struct_ident_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : offset
I : header_attr
"""
)
class struct_fvmfile_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        if data:
            self.unpack(data, offset)
            sta = offset + self._v.offset
            i = data.find(b"\0", sta)
            if i != -1:
                self.name = data[sta:i]


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
Q : entryoff
Q : stacksize
"""
)
class struct_entry_point_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        self.address_formatter("entryoff")
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : offset
H : length
H : kind
"""
)
class struct_data_in_code_entry(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.name_formatter("kind")
        if data:
            self.unpack(data, offset)


with Consts("lc.kind"):
    DICE_KIND_DATA = 0x0001
    DICE_KIND_JUMP_TABLE8 = 0x0002
    DICE_KIND_JUMP_TABLE16 = 0x0003
    DICE_KIND_JUMP_TABLE32 = 0x0004
    DICE_KIND_ABS_JUMP_TABLE32 = 0x0005

# ------------------------------------------------------------------------------
@StructDefine(
    """
I    : cmd
I    : cmdsize
s*16 : data_owner
Q    : offset
Q    : size
"""
)
class struct_note_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        self.address_formatter("offset")
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
Q : version
"""
)
class struct_source_version_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        self.func_formatter(version=self.version_fmt)
        if data:
            self.unpack(data, offset)

    def version_fmt(self, k, v, cls=None):
        A = v >> 40
        B = (v >> 30) & 0x3FF
        C = (v >> 20) & 0x3FF
        D = (v >> 10) & 0x3FF
        E = v & 0x3FF
        return highlight([(Token.String, "%d.%d.%d.%d.%d" % (A, B, C, D, E))])


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : version
I : sdk
"""
)
class struct_version_min_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        self.func_formatter(version=self.version_fmt)
        self.func_formatter(sdk=self.version_fmt)
        if data:
            self.unpack(data, offset)

    def version_fmt(self, k, v, cls=None):
        x = (v & 0xFFFF0000) >> 16
        y = (v & 0x0000FF00) >> 8
        z = v & 0xFF
        return highlight([(Token.String, "%d.%d.%d" % (x, y, z))])


# ------------------------------------------------------------------------------
@StructDefine(
    """
I : cmd
I : cmdsize
I : platform
I : minos
I : sdk
I : ntools
"""
)
class struct_build_version_command(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(cmd=token_cmd_fmt)
        self.name_formatter("platform")
        if data:
            self.unpack(data, offset)
            offset += len(self)
            self.tools = []
            for _ in range(self.ntools):
                x = struct_build_tool_version(data, offset)
                self.tools.append(x)
                offset += len(x)


with Consts("lc.platform"):
    PLATFORM_MACOS = 1
    PLATFORM_IOS = 2
    PLATFORM_TVOS = 3
    PLATFORM_WATCHOS = 4


@StructDefine(
    """
I : tool
I : version
"""
)
class struct_build_tool_version(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        self.func_formatter(version=self.version_fmt)
        self.name_formatter("tool")
        if data:
            self.unpack(data, offset)

    def version_fmt(self, k, v, cls=None):
        x = (v & 0xFFFF0000) >> 16
        y = (v & 0x0000FF00) >> 8
        z = v & 0xFF
        return highlight([(Token.String, "%d.%d.%d" % (x, y, z))])


with Consts("lc.tool"):
    TOOL_CLANG = 1
    TOOL_SWIFT = 2
    TOOL_LD = 3

CMD_TABLE = {
    LC_SEGMENT: struct_segment_command,
    LC_SEGMENT_64: struct_segment_command_64,
    LC_SYMTAB: struct_symtab_command,
    LC_SYMSEG: struct_symseg_command,
    LC_THREAD: struct_thread_command,
    LC_UNIXTHREAD: struct_thread_command,
    LC_LOADFVMLIB: struct_fvmlib_command,
    LC_IDFVMLIB: struct_fvmlib_command,
    LC_IDENT: struct_ident_command,
    LC_FVMFILE: struct_fvmfile_command,
    LC_DYSYMTAB: struct_dysymtab_command,
    LC_LOAD_DYLIB: struct_dylib_command,
    LC_LOAD_WEAK_DYLIB: struct_dylib_command,
    LC_ID_DYLIB: struct_dylib_command,
    LC_REEXPORT_DYLIB: struct_dylib_command,
    LC_LOAD_DYLINKER: struct_dylinker_command,
    LC_ID_DYLINKER: struct_dylinker_command,
    LC_SUB_FRAMEWORK: struct_sub_framework_command,
    LC_SUB_CLIENT: struct_sub_client_command,
    LC_SUB_LIBRARY: struct_sub_library_command,
    LC_SUB_UMBRELLA: struct_sub_umbrella_command,
    LC_TWOLEVEL_HINTS: struct_twolevel_hints_command,
    LC_PREBOUND_DYLIB: struct_prebound_dylib_command,
    LC_PREBIND_CKSUM: struct_prebind_cksum_command,
    LC_UUID: struct_uuid_command,
    LC_RPATH: struct_rpath_command,
    LC_ROUTINES: struct_routines_command,
    LC_ROUTINES_64: struct_routines_command_64,
    LC_DYLD_INFO: struct_dyld_info_command,
    LC_DYLD_INFO_ONLY: struct_dyld_info_command,
    LC_ENCRYPTION_INFO: struct_encryption_info_command,
    LC_CODE_SIGNATURE: struct_linkedit_data_command,
    LC_SEGMENT_SPLIT_INFO: struct_linkedit_data_command,
    LC_FUNCTION_STARTS: struct_linkedit_data_command,
    LC_DATA_IN_CODE: struct_linkedit_data_command,
    LC_DYLIB_CODE_SIGN_DRS: struct_linkedit_data_command,
    LC_VERSION_MIN_MACOSX: struct_version_min_command,
    LC_VERSION_MIN_IPHONEOS: struct_version_min_command,
    LC_SOURCE_VERSION: struct_source_version_command,
    LC_MAIN: struct_entry_point_command,
    LC_NOTE: struct_note_command,
    LC_BUILD_VERSION: struct_build_version_command,
}


@StructDefine(
    """
I : r_address
I : r_symbolnum
"""
)
class struct_relocation_info(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        if data:
            self.unpack(data, offset)


@StructDefine(
    """
I : index
"""
)
class struct_indirect_entry(MachoFormatter):
    alt = "lc"

    def __init__(self, data="", offset=0):
        if data:
            self.unpack(data, offset)
