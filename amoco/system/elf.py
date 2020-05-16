# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2019 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
system/elf.py
=============

The system elf module implements Elf classes for both 32/64bits executable format.
"""
from amoco.system.core import BinFormat
from amoco.system.structs import Consts, StructDefine
from amoco.system.structs import StructFormatter, token_constant_fmt, token_address_fmt

from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")

class ElfError(Exception):
    """
    ElfError is raised whenever Elf object instance fails
    to decode required structures.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)

# ------------------------------------------------------------------------------

class Elf(BinFormat):
    """
    This class takes a DataIO object (ie an opened file of BytesIO instance)
    and decodes all ELF structures found in it.

    Attributes:
        entrypoints (list of int): list of entrypoint addresses.
        filename (str): binary file name.
        Ehdr (Ehdr): the ELF header structure.
        Phdr (list of Phdr): the list of ELF Program header structures.
        Shdr (list of Shdr): the list of ELF Section header structures.
        dynamic (Bool): True if the binary wants to load dynamic libs.
        basemap (int): base address for this ELF image.
        functions (list): a list of function names gathered from internal
                          definitions (if not stripped) and import names.
        variables (list): a list of global variables' names (if found.)
    """
    is_ELF = True

    @property
    def entrypoints(self):
        return [self.Ehdr.e_entry]

    @property
    def filename(self):
        return self.__file.name

    @property
    def header(self):
        return self.Ehdr

    def __init__(self, f):
        self.__file = f
        self.Ehdr = Ehdr(f)
        x64 = self.Ehdr.e_ident.EI_CLASS == ELFCLASS64
        lbe = ">" if (self.Ehdr.e_ident.EI_DATA == ELFDATA2MSB) else None
        self.dynamic = False
        # read program header table: should not raise any errors
        self.Phdr = []
        if self.Ehdr.e_phoff:
            offset = self.Ehdr.e_phoff
            n, l = self.Ehdr.e_phnum, self.Ehdr.e_phentsize
            for pht in range(n):
                P = Phdr(f, offset, lbe, x64)
                offset += l
                if P.p_type == PT_LOAD:
                    if not self.basemap:
                        self.basemap = P.p_vaddr
                    self.Phdr.append(P)
                elif P.p_type == PT_INTERP:
                    self.dynamic = True
                    self.Phdr.append(P)
                elif not P.p_type in Consts.All["p_type"].keys():
                    logger.verbose("invalid segment detected (removed)")
                else:
                    self.Phdr.append(P)

        # read section header table: unused by loader, can raise error
        self.Shdr = []
        if self.Ehdr.e_shoff:
            try:
                offset = self.Ehdr.e_shoff
                n, l = self.Ehdr.e_shnum, self.Ehdr.e_shentsize
                for sht in range(n):
                    S = Shdr(f, offset, lbe, x64)
                    offset += l
                    if S.sh_type in Consts.All["sh_type"].keys():
                        self.Shdr.append(S)
                    else:
                        logger.verbose("unknown sh_type: %d" % S.sh_type)
            except Exception:
                logger.verbose("exception raised while parsing section(s)")

        # read section's name string table:
        n = self.Ehdr.e_shstrndx
        if n != SHN_UNDEF and n in range(len(self.Shdr)):
            S = self.Shdr[self.Ehdr.e_shstrndx]
            if S.sh_type != SHT_STRTAB:
                logger.verbose("section names not a string table")
                for i, s in enumerate(self.Shdr):
                    s.name = ".s%d" % i
            else:
                from codecs import decode

                offset = S.sh_offset
                data = f[offset : offset + S.sh_size]
                for s in self.Shdr:
                    name = data[s.sh_name :].split(b"\0")[0]
                    s.name = decode(name)

        self.__sections = {}
        self.functions = self.__functions()
        self.variables = self.__variables()

    def getsize(self):
        "total file size of all the Program headers"
        total = sum([s.p_filesz for s in self.Phdr])
        return total

    def getinfo(self, target):
        """
        target is either an address provided as str or int,
        or a symbol str searched in the functions dictionary.

        Returns a triplet with:
            - section index (0 is error, -1 is a dynamic call)
            - offset into section  (idem)
            - base virtual address (0 for dynamic calls)
        """
        addr = None
        if isinstance(target, str):
            try:
                addr = int(target, 16)
            except ValueError:
                for a, f in iter(self.functions.items()):
                    if f[0] == target:
                        addr = int(a, 16)
                        break
        elif isinstance(target, int):
            addr = target
        if addr is None:
            # target is propably a symbol not found in functions
            return None, 0, 0
        # now we have addr so we can see in which section/segment it is...
        # sections are smaller than segments so we try first with Shdr
        # but this may lead to errors because what really matters are segments
        # loaded by the kernel binfmt_elf.c loader.
        if self.Shdr:
            for s in reversed(self.Shdr):
                if s.sh_type != SHT_PROGBITS:
                    continue
                if s.sh_addr <= addr < s.sh_addr + s.sh_size:
                    return s, addr - s.sh_addr, s.sh_addr
        elif self.Phdr:
            for s in reversed(self.Phdr):
                if s.p_type != PT_LOAD:
                    continue
                if s.p_vaddr <= addr < s.p_vaddr + s.p_filesz:
                    return s, addr - s.p_vaddr, s.p_vaddr
        return None, 0, 0

    def data(self, target, size):
        "returns 'size' bytes located at target virtual address"
        return self._readcode(target, size)[0]

    def _readcode(self, target, size=None):
        s, offset, base = self.getinfo(target)
        data = b""
        if s:
            if isinstance(s, Phdr):
                c = self.readsegment(s)
            else:
                c = self.readsection(s)
            if c:
                if size != None:
                    if isinstance(c, Str):
                        c = c.data
                    data = c[offset : offset + size]
                else:
                    data = c[offset:]
        return data, 0, base + offset

    def getfileoffset(self, target):
        "converts given target virtual address back to offset in file"
        s, offset, base = self.getinfo(target)
        if s != None:
            result = s.p_offset + offset
        else:
            result = None
        return result

    def readsegment(self, S):
        "returns segment S data padded to S.p_memsz"
        self.__file.seek(S.p_offset)
        return self.__file.read(S.p_filesz).ljust(S.p_memsz, b"\x00")

    def loadsegment(self, S, pagesize=None):
        """
        If S is of type PT_LOAD, returns a dict {base: bytes}
        indicating that segment data bytes (extended to pagesize boundary)
        need to be mapped at virtual base address.
        (Returns None if not a PT_LOAD segment.)
        """
        if S.p_type == PT_LOAD:
            self.__file.seek(S.p_offset)
            if S.p_align > 1 and (S.p_offset != (S.p_vaddr % S.p_align)):
                logger.verbose(
                    "wrong p_vaddr/p_align [%08x/%0d]" % (S.p_vaddr, S.p_align)
                )
            base = S.p_vaddr
            bytes_ = self.__file.read(S.p_filesz).ljust(S.p_memsz, b"\x00")
            if pagesize:
                # note: bytes are not truncated, only extended if needed...
                bytes_ = bytes_.ljust(pagesize, b"\x00")
            return {base: bytes_}
        else:
            logger.error("segment not a PT_LOAD [%08x/%0d]" % (S.p_vaddr, S.p_align))
            return None

    def readsection(self, sect):
        "returns the given section data bytes from file."
        S = None
        if isinstance(sect, str):
            for st in self.Shdr:
                if st.name == sect:
                    S = st
                    break
        elif isinstance(sect, int):
            S = self.Shdr[sect]
        else:
            S = sect
        if S:
            if S.name in self.__sections:
                return self.__sections[S.name]
            if S.sh_type in (SHT_SYMTAB, SHT_DYNSYM):
                s = self.__read_symtab(S)
            elif S.sh_type == SHT_STRTAB:
                s = self.__read_strtab(S)
            elif S.sh_type in (SHT_REL, SHT_RELA):
                s = self.__read_relocs(S)
            elif S.sh_type == SHT_DYNAMIC:
                s = self.__read_dynamic(S)
            else:
                self.__file.seek(S.sh_offset)
                s = self.__file.read(S.sh_size)
            self.__sections[S.name] = s
            return s

    def __read_symtab(self, section):
        if section.sh_type not in (SHT_SYMTAB, SHT_DYNSYM):
            logger.warning("not a symbol table section")
            return None
        x64 = self.Ehdr.e_ident.EI_CLASS == ELFCLASS64
        lbe = ">" if (self.Ehdr.e_ident.EI_DATA == ELFDATA2MSB) else None
        # read the section:
        self.__file.seek(section.sh_offset)
        data = self.__file.read(section.sh_size)
        # and parse it into Sym objects:
        l = section.sh_entsize
        if (section.sh_size % l) != 0:
            raise ElfError("symbol table size mismatch")
        else:
            n = section.sh_size // l
        symtab = []
        offset = 0
        for i in range(n):
            symtab.append(Sym(data, offset, lbe, x64))
            offset += l
        return symtab

    def __read_strtab(self, section):
        if section.sh_type != SHT_STRTAB:
            raise ElfError("not a string table section")
        self.__file.seek(section.sh_offset)
        data = self.__file.read(section.sh_size)
        x64 = self.Ehdr.e_ident.EI_CLASS == ELFCLASS64
        strtab = StrTable(data, x64)
        return strtab

    def __read_relocs(self, section):
        if section.sh_type not in (SHT_REL, SHT_RELA):
            logger.warning("not a relocation table section")
            return None
        self.__file.seek(section.sh_offset)
        data = self.__file.read(section.sh_size)
        l = section.sh_entsize
        if (section.sh_size % l) != 0:
            raise ElfError("relocation table size mismatch")
        else:
            n = section.sh_size // l
        reltab = []
        x64 = self.Ehdr.e_ident.EI_CLASS == ELFCLASS64
        lbe = ">" if (self.Ehdr.e_ident.EI_DATA == ELFDATA2MSB) else None
        offset = 0
        if section.sh_type == SHT_REL:
            rcls = Rel
        elif section.sh_type == SHT_RELA:
            rcls = Rela
        for i in range(n):
            reltab.append(rcls(data, offset, lbe, x64))
            offset += l
        return reltab

    def __read_dynamic(self, section):
        if section.sh_type != SHT_DYNAMIC:
            logger.warning("not a dynamic linking section")
            return None
        # read the section:
        self.__file.seek(section.sh_offset)
        data = self.__file.read(section.sh_size)
        # and parse it into Dyn objects:
        l = section.sh_entsize
        if (section.sh_size % l) != 0:
            raise ElfError("dynamic linking size mismatch")
        else:
            n = section.sh_size // l
        dyntab = []
        x64 = self.Ehdr.e_ident.EI_CLASS == ELFCLASS64
        lbe = ">" if (self.Ehdr.e_ident.EI_DATA == ELFDATA2MSB) else None
        offset = 0
        for i in range(n):
            dyntab.append(Dyn(data, offset, lbe, x64))
            offset += l
        return dyntab

    def __read_note(self, section):
        if section.sh_type != SHT_NOTE:
            logger.warning("not a note section")
            return None
        self.__file.seek(section.sh_offset)
        data = self.__file.read(section.sh_size)
        x64 = self.Ehdr.e_ident.EI_CLASS == ELFCLASS64
        lbe = ">" if (self.Ehdr.e_ident.EI_DATA == ELFDATA2MSB) else None
        note = Note(data, lbe, x64)
        return note

    def __functions(self, fltr=None):
        D = self.__symbols(STT_FUNC)
        # fltr applies to section name only :
        if fltr:
            for k, v in iter(D.items()):
                if self.Shdr[v[2]].name != fltr:
                    D.pop(k)
        if self.dynamic:
            D.update(self.__dynamic(STT_FUNC))
        return D

    def __variables(self, fltr=None):
        D = self.__symbols(STT_OBJECT)
        # fltr applies also to section name :
        if fltr:
            for k, v in iter(D.items()):
                if self.Shdr[v[2]].name != fltr:
                    D.pop(k)
        return D

    def __symbols(self, t):
        D = {}
        symtab = self.readsection(".symtab") or []
        strtab = self.readsection(".strtab")
        if strtab:
            for sym in symtab:
                if sym.st_type == t and sym.st_value:
                    D[sym.st_value] = (
                        str(strtab[sym.st_name].decode()),
                        sym.st_size,
                        sym.st_info,
                        sym.st_shndx,
                    )
        return D

    def __dynamic(self, type=None):
        D = {}
        self.readsection(".dynamic")
        dynsym = self.readsection(".dynsym") or []
        dynstr = self.readsection(".dynstr")
        if dynstr:
            for s in self.Shdr:
                if s.sh_type in (SHT_REL, SHT_RELA):
                    for r in self.readsection(s):
                        if r.r_offset:
                            sym = dynsym[r.r_sym]
                            D[r.r_offset] = str(dynstr[sym.st_name].decode())
        return D

    def checksec(self):
        "check for usual security features."
        R = {}
        R["Canary"] = 0
        R["Fortify"] = 0
        for f in iter(self.functions.values()):
            if isinstance(f, tuple):
                f = f[0]
            if f.startswith("__stack_chk_fail"):
                R["Canary"] = 1
            elif f.endswith("_chk@GLIBC"):
                R["Fortify"] = 1
        R["NX"] = 0
        R["Partial RelRO"] = 0
        for p in self.Phdr:
            if p.p_type == PT_GNU_STACK:
                if not (p.p_flags & PF_X):
                    R["NX"] = 1
            elif p.p_type == PT_GNU_RELRO:
                R["Partial RelRO"] = 1
        R["PIE"] = 0
        if self.Ehdr.e_type != ET_EXEC:
            R["PIE"] = 1
        R["Full RelRO"] = 0
        for d in self.readsection(".dynamic") or []:
            if d.d_tag == DT_BIND_NOW or\
              (d.d_tag == DT_FLAGS and d.d_un==DF_BIND_NOW):
                R["Full RelRO"] = 1
                break
        return R

    def __str__(self):
        ss = ["ELF header:"]
        tmp = self.Ehdr.pfx
        self.Ehdr.pfx = "\t"
        ss.append(self.Ehdr.__str__())
        self.Ehdr.pfx = tmp
        ss += ["\nSections:"]
        for s in self.Shdr:
            tmp = s.pfx
            s.pfx = "\t"
            ss.append(s.__str__())
            ss.append("---")
            s.pfx = tmp
        ss += ["\nSegments:"]
        for s in self.Phdr:
            tmp = s.pfx
            s.pfx = "\t"
            ss.append(s.__str__())
            ss.append("---")
            s.pfx = tmp
        return "\n".join(ss)


# ------------------------------------------------------------------------------


@StructDefine(
"""
B  : ELFMAG0
c*3: ELFMAG
B  : EI_CLASS
B  : EI_DATA
B  : EI_VERSION
B  : EI_OSABI
B  : EI_ABIVERSION
b*7: unused
"""
)
class IDENT(StructFormatter):
    def __init__(self, data=None):
        self.name_formatter("EI_CLASS", "EI_DATA", "EI_OSABI")
        if data:
            self.unpack(data)

    def unpack(self, data, offset=0):
        StructFormatter.unpack(self, data, offset)
        if self.ELFMAG0 != 0x7F or self.ELFMAG != b"ELF":
            raise ElfError("Wrong magic number, not an ELF file ?")
        if self.EI_DATA not in (ELFDATA2LSB, ELFDATA2MSB):
            logger.info("No endianess specified in ELF header.")
        return self


# EI_CLASS values:
with Consts("EI_CLASS"):
    ELFCLASSNONE = 0
    ELFCLASS32 = 1
    ELFCLASS64 = 2
    ELFCLASSNUM = 3

# EI_DATA values:
with Consts("EI_DATA"):
    ELFDATANONE = 0
    ELFDATA2LSB = 1
    ELFDATA2MSB = 2
    ELFDATANUM = 3

# EI_OSABI values:
with Consts("EI_OSABI"):
    ELFOSABI_NONE = 0
    ELFOSABI_SYSV = 0
    ELFOSABI_HPUX = 1
    ELFOSABI_NETBSD = 2
    ELFOSABI_LINUX = 3
    ELFOSABI_SOLARIS = 6
    ELFOSABI_AIX = 7
    ELFOSABI_IRIX = 8
    ELFOSABI_FREEBSD = 9
    ELFOSABI_TRU64 = 10
    ELFOSABI_MODESTO = 11
    ELFOSABI_OPENBSD = 12
    ELFOSABI_ARM = 97
    ELFOSABI_STANDALONE = 255


@StructDefine(
"""
IDENT :< e_ident
H : e_type
H : e_machine
I : e_version
I : e_entry
I : e_phoff
I : e_shoff
I : e_flags
H : e_ehsize
H : e_phentsize
H : e_phnum
H : e_shentsize
H : e_shnum
H : e_shstrndx
"""
)
class Ehdr(StructFormatter):
    def __init__(self, data=None):
        self.name_formatter("e_type", "e_machine", "e_version")
        self.address_formatter("e_entry")
        self.flag_formatter("e_flags")
        if data:
            self.unpack(data)

    def unpack(self, data, offset=0):
        f0 = self.fields[0]
        self._v.e_ident = f0.unpack(data, offset)
        offset += f0.size()
        # change endianness if necessary:
        if self._v.e_ident.EI_DATA == ELFDATA2MSB:
            for f in self.fields[1:]:
                f.order = ">"
        # change pointers format if necessary:
        if self._v.e_ident.EI_CLASS == ELFCLASS64:
            self.fields[4].typename = "Q"
            self.fields[5].typename = "Q"
            self.fields[6].typename = "Q"
        for f in self.fields[1:]:
            setattr(self._v, f.name, f.unpack(data, offset))
            offset += f.size()
        return self


# legal values for e_type (object file type):
with Consts("e_type"):
    ET_NONE = 0
    ET_REL = 1
    ET_EXEC = 2
    ET_DYN = 3
    ET_CORE = 4
    ET_NUM = 5
    ET_LOOS = 0xFE00
    ET_HIOS = 0xFEFF
    ET_LOPROC = 0xFF00
    ET_HIPROC = 0xFFFF

# legal values for e_machine (architecture):
with Consts("e_machine"):
    EM_NONE = 0
    EM_M32 = 1
    EM_SPARC = 2
    EM_386 = 3
    EM_68K = 4
    EM_88K = 5
    EM_860 = 7
    EM_MIPS = 8
    EM_S370 = 9
    EM_MIPS_RS3_LE = 10

    EM_PARISC = 15
    EM_VPP500 = 17
    EM_SPARC32PLUS = 18
    EM_960 = 19
    EM_PPC = 20
    EM_PPC64 = 21
    EM_S390 = 22

    EM_V800 = 36
    EM_FR20 = 37
    EM_RH32 = 38
    EM_RCE = 39
    EM_ARM = 40
    EM_FAKE_ALPHA = 41
    EM_SH = 42
    EM_SPARCV9 = 43
    EM_TRICORE = 44
    EM_ARC = 45
    EM_H8_300 = 46
    EM_H8_300H = 47
    EM_H8S = 48
    EM_H8_500 = 49
    EM_IA_64 = 50
    EM_MIPS_X = 51
    EM_COLDFIRE = 52
    EM_68HC12 = 53
    EM_MMA = 54
    EM_PCP = 55
    EM_NCPU = 56
    EM_NDR1 = 57
    EM_STARCORE = 58
    EM_ME16 = 59
    EM_ST100 = 60
    EM_TINYJ = 61
    EM_X86_64 = 62
    EM_PDSP = 63

    EM_FX66 = 66
    EM_ST9PLUS = 67
    EM_ST7 = 68
    EM_68HC16 = 69
    EM_68HC11 = 70
    EM_68HC08 = 71
    EM_68HC05 = 72
    EM_SVX = 73
    EM_ST19 = 74
    EM_VAX = 75
    EM_CRIS = 76
    EM_JAVELIN = 77
    EM_FIREPATH = 78
    EM_ZSP = 79
    EM_MMIX = 80
    EM_HUANY = 81
    EM_PRISM = 82
    EM_AVR = 83
    EM_FR30 = 84
    EM_D10V = 85
    EM_D30V = 86
    EM_V850 = 87
    EM_M32R = 88
    EM_MN10300 = 89
    EM_MN10200 = 90
    EM_PJ = 91
    EM_OPENRISC = 92
    EM_ARC_A5 = 93
    EM_XTENSA = 94
    EM_NUM = 95
    EM_ST200 = 100
    EM_MSP430 = 105
    EM_SEP = 108
    EM_M16C = 117
    EM_DSPIC30F = 118
    EM_CE = 119
    EM_M32C = 120
    EM_R32C = 162
    EM_QDSP6 = 164
    EM_AARCH64 = 183
    EM_AVR32 = 185
    EM_STM8 = 186
    EM_CUDA = 190
    EM_Z80 = 220
    EM_AMDGPU = 224
    EM_RISCV = 243
    EM_BPF = 247
    # unofficial values should pick large index:
    EM_ALPHA = 0x9026
    EM_WEBASSEMBLY = 0x4157

# legal values for e_version (version):
with Consts("e_version"):
    EV_NONE = 0
    EV_CURRENT = 1
    EV_NUM = 2


@StructDefine(
    """
I : sh_name
I : sh_type
I : sh_flags
I : sh_addr
I : sh_offset
I : sh_size
I : sh_link
I : sh_info
I : sh_addralign
I : sh_entsize
"""
)
class Shdr(StructFormatter):
    def __init__(self, data=None, offset=0, order=None, x64=False):
        if order:
            for f in self.fields:
                f.order = order
        if x64:
            for i in (2, 3, 4, 5, 8, 9):
                self.fields[i].typename = "Q"
        self.name_formatter("sh_name", "sh_type")
        self.address_formatter("sh_addr")
        self.flag_formatter("sh_flags")
        self.func_formatter(sh_addralign=token_constant_fmt)
        if data:
            self.unpack(data, offset)


with Consts("sh_name"):
    SHN_UNDEF = 0
    SHN_LORESERVE = 0xFF00
    SHN_LOPROC = 0xFF00
    SHN_BEFORE = 0xFF00
    SHN_AFTER = 0xFF01
    SHN_HIPROC = 0xFF1F
    SHN_LOOS = 0xFF20
    SHN_HIOS = 0xFF3F
    SHN_ABS = 0xFFF1
    SHN_COMMON = 0xFFF2
    SHN_XINDEX = 0xFFFF
    SHN_HIRESERVE = 0xFFFF

# legal values for sh_type (section type):
with Consts("sh_type"):
    SHT_NULL = 0
    SHT_PROGBITS = 1
    SHT_SYMTAB = 2
    SHT_STRTAB = 3
    SHT_RELA = 4
    SHT_HASH = 5
    SHT_DYNAMIC = 6
    SHT_NOTE = 7
    SHT_NOBITS = 8
    SHT_REL = 9
    SHT_SHLIB = 10
    SHT_DYNSYM = 11
    SHT_INIT_ARRAY = 14
    SHT_FINI_ARRAY = 15
    SHT_PREINIT_ARRAY = 16
    SHT_GROUP = 17
    SHT_SYMTAB_SHNDX = 18
    SHT_NUM = 19
    SHT_LOOS = 0x60000000
    SHT_GNU_HASH = 0x6FFFFFF6
    SHT_GNU_LIBLIST = 0x6FFFFFF7
    SHT_CHECKSUM = 0x6FFFFFF8
    SHT_LOSUNW = 0x6FFFFFFA
    SHT_SUNW_move = 0x6FFFFFFA
    SHT_SUNW_COMDAT = 0x6FFFFFFB
    SHT_SUNW_syminfo = 0x6FFFFFFC
    SHT_GNU_verdef = 0x6FFFFFFD
    SHT_GNU_verneed = 0x6FFFFFFE
    SHT_GNU_versym = 0x6FFFFFFF
    SHT_HISUNW = 0x6FFFFFFF
    SHT_HIOS = 0x6FFFFFFF
    SHT_LOPROC = 0x70000000
    SHT_HIPROC = 0x7FFFFFFF
    SHT_LOUSER = 0x80000000
    SHT_HIUSER = 0x8FFFFFFF
    SHT_ARM_EXIDX = SHT_LOPROC + 1
    SHT_ARM_PREEMPTMAP = SHT_LOPROC + 2
    SHT_ARM_ATTRIBUTES = SHT_LOPROC + 3

# legal values for sh_flags (section flags):
with Consts("sh_flags"):
    SHF_WRITE = 1 << 0
    SHF_ALLOC = 1 << 1
    SHF_EXECINSTR = 1 << 2
    SHF_MERGE = 1 << 4
    SHF_STRINGS = 1 << 5
    SHF_INFO_LINK = 1 << 6
    SHF_LINK_ORDER = 1 << 7
    SHF_OS_NONCONFORMING = 1 << 8
    SHF_GROUP = 1 << 9
    SHF_TLS = 1 << 10
    SHF_MASKOS = 0x0FF00000
    SHF_MASKPROC = 0xF0000000
    SHF_ORDERED = 1 << 30
    SHF_EXCLUDE = 1 << 31

# section group handling:
GRP_COMDAT = 0x1


@StructDefine(
    """
I : st_name
I : st_value
I : st_size
B : st_info
B : st_other
H : st_shndx
"""
)
class Sym(StructFormatter):
    def __init__(self, data=None, offset=0, order=None, x64=False):
        if order:
            for f in self.fields:
                f.order = order
        if x64:  # need to reorder fields...
            fvalue = self.fields.pop(1)
            fsize = self.fields.pop(1)
            fvalue.typename = fsize.typename = "Q"
            self.fields.append(fvalue)
            self.fields.append(fsize)
        self.name_formatter("st_name", "st_bind", "st_type", "st_visibility")
        if data:
            self.unpack(data, offset)

    def ELF32_ST_BIND(self):
        return self.st_info >> 4

    st_bind = property(ELF32_ST_BIND)

    def ELF32_ST_TYPE(self):
        return self.st_info & 0xF

    st_type = property(ELF32_ST_TYPE)

    def ELF32_ST_INFO(self, bind, type):
        self._v.st_info = bind << 4 + (type & 0xF)

    def ELF32_ST_VISIBILITY(self):
        return self.st_other & 0x03

    st_visibility = property(ELF32_ST_VISIBILITY)

    def __str__(self):
        s = super().__str__() + "\n"
        cname = self.__class__.__name__
        s += self.strkey("st_bind", cname) + "\n"
        s += self.strkey("st_type", cname) + "\n"
        s += self.strkey("st_visibility", cname)
        return s


# legal values for st_bind:
with Consts("st_bind"):
    STB_LOCAL = 0
    STB_GLOBAL = 1
    STB_WEAK = 2
    STB_NUM = 3
    STB_LOOS = 10
    STB_HIOS = 12
    STB_LOPROC = 13
    STB_HIPROC = 15

# legal values for st_type:
with Consts("st_type"):
    STT_NOTYPE = 0
    STT_OBJECT = 1
    STT_FUNC = 2
    STT_SECTION = 3
    STT_FILE = 4
    STT_COMMON = 5
    STT_TLS = 6
    STT_NUM = 7
    STT_LOOS = 10
    STT_HIOS = 12
    STT_LOPROC = 13
    STT_HIPROC = 15

# special index indicating the end end of a chain:
STN_UNDEF = 0

with Consts("st_visibility"):
    STV_DEFAULT = 0
    STV_INTERNAL = 1
    STV_HIDDEN = 2
    STV_PROTECTED = 3


@StructDefine(
    """
I : r_offset
I : r_info
"""
)
class Rel(StructFormatter):
    def __init__(self, data=None, offset=0, order=None, x64=False):
        if order:
            for f in self.fields:
                f.order = order
        if x64:
            for f in self.fields:
                f.typename = "Q"
        self.name_formatter("r_type")
        self.func_formatter(r_sym=token_address_fmt)
        if data:
            self.unpack(data, offset)

    def ELF_R_SYM(self):
        return self.r_info >> (8 if self.fields[1].typename == "I" else 32)

    r_sym = property(ELF_R_SYM)

    def ELF_R_TYPE(self):
        return self.r_info & (0xFF if self.fields[1].typename == "I" else 0xFFFFFFFF)

    r_type = property(ELF_R_TYPE)

    def ELF_R_INFO(self, sym, type):
        if self.fields[1].typename == "I":
            self._v.r_info = sym << 8 + (type & 0xFF)
        else:
            self._v.r_info = sym << 32 + (type & 0xFFFFFFFF)

    def __str__(self):
        s = StructFormatter.__str__(self) + "\n"
        cname = self.__class__.__name__
        s += self.strkey("r_type", cname)
        return s


@StructDefine(
    """
I : r_offset
I : r_info
I : r_addend
"""
)
class Rela(Rel):
    def __init__(self, data=None, offset=0, order=None, x64=False):
        if order:
            for f in self.fields:
                f.order = order
        if x64:
            for f in self.fields:
                f.typename = "Q"
        if data:
            self.unpack(data, offset)


@StructDefine(
    """
I : p_type
I : p_offset
I : p_vaddr
I : p_paddr
I : p_filesz
I : p_memsz
I : p_flags
I : p_align
"""
)
class Phdr(StructFormatter):
    def __init__(self, data=None, offset=0, order=None, x64=False):
        if order:
            for f in self.fields:
                f.order = order
        if x64:
            pflags = self.fields.pop(6)
            self.fields.insert(1, pflags)
            for f in self.fields[2:]:
                f.typename = "Q"
        self.name_formatter("p_type")
        self.address_formatter("p_vaddr", "p_paddr")
        self.flag_formatter("p_flags")
        if data:
            self.unpack(data, offset)


# legal values for p_type (segment type):
with Consts("p_type"):
    PT_NULL = 0
    PT_LOAD = 1
    PT_DYNAMIC = 2
    PT_INTERP = 3
    PT_NOTE = 4
    PT_SHLIB = 5
    PT_PHDR = 6
    PT_TLS = 7
    PT_NUM = 8
    PT_LOOS = 0x60000000
    PT_GNU_EH_FRAME = 0x6474E550
    PT_GNU_STACK = 0x6474E551
    PT_GNU_RELRO = 0x6474E552
    PT_LOSUNW = 0x6FFFFFFA
    PT_SUNWBSS = 0x6FFFFFFA
    PT_SUNWSTACK = 0x6FFFFFFB
    PT_HISUNW = 0x6FFFFFFF
    PT_HIOS = 0x6FFFFFFF
    PT_LOPROC = 0x70000000
    PT_HIPROC = 0x7FFFFFFF
    PT_ARM_EXIDX = PT_LOPROC + 1

# legal values for p_flags (segment flags):
with Consts("p_flags"):
    PF_X = 1 << 0
    PF_W = 1 << 1
    PF_R = 1 << 2
    PF_MASKOS = 0x0FF00000
    PF_MASKPROC = 0xF0000000
    PF_ARM_SB = 0x10000000
    PF_ARM_PI = 0x20000000
    PF_ARM_ABS = 0x40000000


@StructDefine(
    """
I : namesz
I : descsz
I : n_type
"""
)
class Note(StructFormatter):
    def __init__(self, data=None, offset=0, order=None, x64=False):
        if order:
            for f in self.fields:
                f.order = order
        if x64:
            for f in self.fields:
                f.typename = "Q"
        self.name_formatter("n_type")
        if data:
            self.unpack(data, offset)
            offset += self.size()
            self.name = data[offset : offset + self.namesz]
            offset += self.namesz
            if offset % 4 != 0:
                offset = ((offset + 4) // 4) * 4
            self.desc = data[offset : offset + self.descsz]


# legal values for note segment descriptor types for core files:
with Consts("n_type"):
    NT_PRSTATUS = 1
    NT_FPREGSET = 2
    NT_PRPSINFO = 3
    NT_PRXREG = 4
    NT_TASKSTRUCT = 4
    NT_PLATFORM = 5
    NT_AUXV = 6
    NT_GWINDOWS = 7
    NT_ASRS = 8
    NT_PSTATUS = 10
    NT_PSINFO = 13
    NT_PRCRED = 14
    NT_UTSNAME = 15
    NT_LWPSTATUS = 16
    NT_LWPSINFO = 17
    NT_PRFPXREG = 20

    NT_VERSION = 1


@StructDefine(
    """
I : d_tag
I : d_un
"""
)
class Dyn(StructFormatter):
    def __init__(self, data=None, offset=0, order=None, x64=False):
        if order:
            for f in self.fields:
                f.order = order
        if x64:
            for f in self.fields:
                f.typename = "Q"
        self.name_formatter("d_tag")
        self.address_formatter("d_un")
        if data:
            self.unpack(data, offset)

    def DT_VALTAGIDX(self, tag):
        self.d_un = DT_VALRNGHI - tag

    def DT_ADDRTAGIDX(self, tag):
        self.d_un = DT_ADDRRNGHI - tag


# legal values for d_tag (dynamic entry type):
with Consts("d_tag"):
    DT_NULL = 0
    DT_NEEDED = 1
    DT_PLTRELSZ = 2
    DT_PLTGOT = 3
    DT_HASH = 4
    DT_STRTAB = 5
    DT_SYMTAB = 6
    DT_RELA = 7
    DT_RELASZ = 8
    DT_RELAENT = 9
    DT_STRSZ = 10
    DT_SYMENT = 11
    DT_INIT = 12
    DT_FINI = 13
    DT_SONAME = 14
    DT_RPATH = 15
    DT_SYMBOLIC = 16
    DT_REL = 17
    DT_RELSZ = 18
    DT_RELENT = 19
    DT_PLTREL = 20
    DT_DEBUG = 21
    DT_TEXTREL = 22
    DT_JMPREL = 23
    DT_BIND_NOW = 24
    DT_INIT_ARRAY = 25
    DT_FINI_ARRAY = 26
    DT_INIT_ARRAYSZ = 27
    DT_FINI_ARRAYSZ = 28
    DT_RUNPATH = 29
    DT_FLAGS = 30
    DT_ENCODING = 32
    DT_PREINIT_ARRAY = 32
    DT_PREINIT_ARRAYSZ = 33
    DT_NUM = 34
    DT_LOOS = 0x6000000D
    DT_HIOS = 0x6FFFF000
    DT_LOPROC = 0x70000000
    DT_HIPROC = 0x7FFFFFFF
    DT_GNU_HASH = 0x6FFFFEF5
    DT_VERDEF = 0x6FFFFFFC
    DT_VERDEFNUM = 0x6FFFFFFD
    DT_VERNEED = 0x6FFFFFFE
    DT_VERNEEDNUM = 0x6FFFFFFF
    DT_VERSYM = 0x6FFFFFF0
    DT_RELACOUNT = 0x6FFFFFF9
    DT_RELCOUNT = 0x6FFFFFFA
    DT_FLAGS_1 = 0x6FFFFFFB

# legal values for d_un (union type use here value):
with Consts("d_un"):
    DT_VALRNGLO = 0x6FFFFD00
    DT_GNU_PRELINKED = 0x6FFFFDF5
    DT_GNU_CONFLICTSZ = 0x6FFFFDF6
    DT_GNU_LIBLISTSZ = 0x6FFFFDF7
    DT_CHECKSUM = 0x6FFFFDF8
    DT_PLTPADSZ = 0x6FFFFDF9
    DT_MOVEENT = 0x6FFFFDFA
    DT_MOVESZ = 0x6FFFFDFB
    DT_FEATURE_1 = 0x6FFFFDFC
    DT_POSFLAG_1 = 0x6FFFFDFD
    DT_SYMINSZ = 0x6FFFFDFE
    DT_SYMINENT = 0x6FFFFDFF
    DT_VALRNGHI = 0x6FFFFDFF
    DT_VALNUM = 12

    # legal values for d_un (union type use here address):
    DT_ADDRRNGLO = 0x6FFFFE00
    DT_TLSDESC_PLT = 0x6FFFFEF6
    DT_TLSDESC_GOT = 0x6FFFFEF7
    DT_GNU_CONFLICT = 0x6FFFFEF8
    DT_GNU_LIBLIST = 0x6FFFFEF9
    DT_CONFIG = 0x6FFFFEFA
    DT_DEPAUDIT = 0x6FFFFEFB
    DT_AUDIT = 0x6FFFFEFC
    DT_PLTPAD = 0x6FFFFEFD
    DT_MOVETAB = 0x6FFFFEFE
    DT_SYMINFO = 0x6FFFFEFF
    DT_ADDRRNGHI = 0x6FFFFEFF
    DT_ADDRNUM = 10

    DF_ORIGIN = 0x1
    DF_SYMBOLIC = 0x2
    DF_TEXTREL = 0x4
    DF_BIND_NOW = 0x8
    DF_STATIC_TLS = 0x10


@StructDefine(
    """
  I: l_name
  I: l_time_stamp
  I: l_checksum
  I: l_version
  I: l_flags
"""
)
class Lib(StructFormatter):
    def __init__(self, data=None, offset=0, order=None, x64=False):
        if order:
            for f in self.fields:
                f.order = order
        self.flag_formatter("l_flags")
        if data:
            self.unpack(data, offset)


with Consts("l_flags"):
    LL_IGNORE_INT_VER = 1 << 1
    LL_EXACT_MATCH = 1 << 0
    LL_REQUIRE_MINOR = 1 << 2
    LL_NONE = 0x0
    LL_DELTA = 1 << 5
    LL_EXPORTS = 1 << 3
    LL_DELAY_LOAD = 1 << 4

# String Table entry; provided to deal with C strings and char indexed
# string table sections. This is not a standard structure, it is more
# like a C-string Array class for python.
# ------------------------------------------------------------------------------
class StrTable(object):
    def __init__(self, data, x64=False):
        self.data = data
        self.x64 = x64

    def __getitem__(self, i):
        z = self.data[i:].index(b"\0")
        return self.data[i : i + z]

    def as_dict(self):
        D = {}
        cstrings = self.data.split(b"\0")
        p = 0
        for cs in cstrings:
            D[p] = cs
            p += len(cs) + 1
        return D

    def __str__(self):
        fmt = "0x%" + "%02dx: %%s" % (16 if self.x64 else 8)
        return "\n".join((fmt % (k, v) for (k, v) in iter(self.as_dict().items())))
