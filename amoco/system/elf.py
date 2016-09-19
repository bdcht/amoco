# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

import struct
import pdb
from collections import defaultdict
from amoco.logger import *
from amoco.ui.render import Token,highlight

logger = Log(__name__)

def Elf(filename):
    try:
        return Elf32(filename)
    except ElfError:
        return Elf64(filename)

# our exception handler:
class ElfError(Exception):
    def __init__(self,message):
        self.message = message
    def __str__(self):
        return str(self.message)

#------------------------------------------------------------------------------
# formatting facilities:

# init of reverse dict to get constant name from value.
# This dict is updated by using 'with' statement of Consts.
ELF_CONSTS = defaultdict(dict)

class Consts(object):
    def __init__(self,name):
        self.name = name
    def __enter__(self):
        ELF_CONSTS[self.name] = {}
        self.globnames = set(globals().keys())
    def __exit__(self,exc_type,exc_value,traceback):
        G = globals()
        for k in set(G.keys())-self.globnames:
            ELF_CONSTS[self.name][G[k]] = k

def default_formatter():
    return token_default_fmt

def token_default_fmt(k,x):
    if 'addr'  in k: return token_address_fmt(k,x)
    if 'flags' in k: return token_flag_fmt(k,x)
    return highlight([(Token.Literal,str(x))])

def token_address_fmt(k,x):
    return highlight([(Token.Address,hex(x))])

def token_constant_fmt(k,x):
    return highlight([(Token.Constant,str(x))])

def token_name_fmt(k,x):
    try:
        return highlight([(Token.Name,ELF_CONSTS[k][x])])
    except KeyError:
        return token_constant_fmt(k,x)

def token_flag_fmt(k,x):
    s = []
    for v,name in ELF_CONSTS[k].items():
        if (x&v): s.append(highlight([(Token.Name,name)]))
    return ','.join(s)

#------------------------------------------------------------------------------
class Elfcore(object):
    order = '=' #native order
    pfx = ''
    ksz = 12
    fkeys = defaultdict(default_formatter)
    def set(self,data):
        S = struct.unpack(self.order+self.fmt,data)
        self.__dict__.update(zip(self.keys,S))
    def pack(self):
        return struct.pack(self.order+self.fmt,*(getattr(self,k) for k in self.keys))
    @classmethod
    def func_formatter(cls,**kargs):
        for key,func in kargs.items():
            cls.fkeys[key] = func
    @classmethod
    def name_formatter(cls,*keys):
        for key in keys:
            cls.fkeys[key] = token_name_fmt
    @classmethod
    def flag_formatter(cls,*keys):
        for key in keys:
            cls.fkeys[key] = token_flag_fmt
    def strkey(self,k):
        fmt = '%%s%%-%ds:%%s'%self.ksz
        return fmt%(self.pfx,k,self.fkeys[k](k,getattr(self,k)))
    def __str__(self):
        fmt = '%%s%%-%ds:%%s'%self.ksz
        s = '\n'.join(self.strkey(k) for k in self.keys)
        return "[%s]\n%s"%(self.__class__.__name__,s)

# The ELF file header.
#------------------------------------------------------------------------------
class Elf32_Ehdr(Elfcore):
    # Elfcore is not used for the e_ident dict, only for the following keys:
    fmt = 'HHIIIIIHHHHHH'
    keys = (
        'e_type',
        'e_machine',
        'e_version',
        'e_entry',
        'e_phoff',
        'e_shoff',
        'e_flags',
        'e_ehsize',
        'e_phentsize',
        'e_phnum',
        'e_shentsize',
        'e_shnum',
        'e_shstrndx')
    # overload Elfcore methods to take into account the e_ident dict:
    def __init__(self, data):
        S = struct.unpack('B3sBBBBBxxxxxxx',data[:16])
        if S[0]!=0x7f or S[1]!='ELF':
            raise ElfError('Wrong magic number, not an ELF file ?')
        self.e_ident = dict(zip(EI_KEYS,S))
        try:
            self.order = {ELFDATA2LSB:'<',ELFDATA2MSB:'>'}[self.e_ident['EI_DATA']]
            Elfcore.order = self.order
        except KeyError:
                logger.info("No endianess specified in ELF header.")
        # we need only 32-bit arch here:
        if self.e_ident['EI_CLASS'] == ELFCLASS64 :
            logger.info("Not a 32-bit ELF file")
            raise ElfError(self)
        self.set(data[16:52])
        self.name_formatter('e_type','e_machine','e_version')
        self.func_formatter(e_entry=token_address_fmt)
        self.func_formatter(e_flags=token_address_fmt)

    def pack(self):
        e_ident_s = struct.pack('B3sBBBBBxxxxxxx',*[self.e_ident[k] for k in EI_KEYS])
        return e_ident_s+Elfcore.pack(self)

    # patched Elfcore str to have entrypoint in hex:
    def __str__(self):
        s = list(Elfcore.__str__(self).partition('\n'))
        x = '; '.join([token_name_fmt(k,v) for (k,v) in self.e_ident.iteritems()])
        fmt = '\n%%s%%-%ds:%%s'%self.ksz
        s.insert(1,fmt%(self.pfx,'e_ident',x))
        return ''.join(s)

# keys of the e_ident field:
EI_KEYS = ( 'ELFMAG0',
            'ELFMAG',
            'EI_CLASS',
            'EI_DATA',
            'EI_VERSION',
            'EI_OSABI',
            'EI_ABIVERSION')

# legal values for e_indent:

#EI_CLASS values:
with Consts('EI_CLASS'):
    ELFCLASSNONE=0
    ELFCLASS32=1
    ELFCLASS64=2
    ELFCLASSNUM=3

#EI_DATA values:
with Consts('EI_DATA'):
    ELFDATANONE=0
    ELFDATA2LSB=1
    ELFDATA2MSB=2
    ELFDATANUM=3

#EI_OSABI values:
with Consts('EI_OSABI'):
    ELFOSABI_NONE=0
    ELFOSABI_SYSV=0
    ELFOSABI_HPUX=1
    ELFOSABI_NETBSD=2
    ELFOSABI_LINUX=3
    ELFOSABI_SOLARIS=6
    ELFOSABI_AIX=7
    ELFOSABI_IRIX=8
    ELFOSABI_FREEBSD=9
    ELFOSABI_TRU64=10
    ELFOSABI_MODESTO=11
    ELFOSABI_OPENBSD=12
    ELFOSABI_ARM=97
    ELFOSABI_STANDALONE=255

# legal values for e_type (object file type):
with Consts('e_type'):
    ET_NONE=0
    ET_REL=1
    ET_EXEC=2
    ET_DYN=3
    ET_CORE=4
    ET_NUM=5
    ET_LOOS=0xfe00
    ET_HIOS=0xfeff
    ET_LOPROC=0xff00
    ET_HIPROC=0xffff

# legal values for e_machine (architecture):
with Consts('e_machine'):
    EM_NONE=0
    EM_M32=1
    EM_SPARC=2
    EM_386=3
    EM_68K=4
    EM_88K=5
    EM_860=7
    EM_MIPS=8
    EM_S370=9
    EM_MIPS_RS3_LE=10

    EM_PARISC=15
    EM_VPP500=17
    EM_SPARC32PLUS=18
    EM_960=19
    EM_PPC=20
    EM_PPC64=21
    EM_S390=22

    EM_V800=36
    EM_FR20=37
    EM_RH32=38
    EM_RCE=39
    EM_ARM=40
    EM_FAKE_ALPHA=41
    EM_SH=42
    EM_SPARCV9=43
    EM_TRICORE=44
    EM_ARC=45
    EM_H8_300=46
    EM_H8_300H=47
    EM_H8S=48
    EM_H8_500=49
    EM_IA_64=50
    EM_MIPS_X=51
    EM_COLDFIRE=52
    EM_68HC12=53
    EM_MMA=54
    EM_PCP=55
    EM_NCPU=56
    EM_NDR1=57
    EM_STARCORE=58
    EM_ME16=59
    EM_ST100=60
    EM_TINYJ=61
    EM_X86_64=62
    EM_PDSP=63

    EM_FX66=66
    EM_ST9PLUS=67
    EM_ST7=68
    EM_68HC16=69
    EM_68HC11=70
    EM_68HC08=71
    EM_68HC05=72
    EM_SVX=73
    EM_ST19=74
    EM_VAX=75
    EM_CRIS=76
    EM_JAVELIN=77
    EM_FIREPATH=78
    EM_ZSP=79
    EM_MMIX=80
    EM_HUANY=81
    EM_PRISM=82
    EM_AVR=83
    EM_FR30=84
    EM_D10V=85
    EM_D30V=86
    EM_V850=87
    EM_M32R=88
    EM_MN10300=89
    EM_MN10200=90
    EM_PJ=91
    EM_OPENRISC=92
    EM_ARC_A5=93
    EM_XTENSA=94
    EM_NUM=95
    # unofficial values should pick large index:
    EM_ALPHA=0x9026

# legal values for e_version (version):
with Consts('e_version'):
    EV_NONE=0
    EV_CURRENT=1
    EV_NUM=2

# Section header:
#------------------------------------------------------------------------------
class Elf32_Shdr(Elfcore):
    fmt = 'I'*10
    keys = (
        'sh_name',
        'sh_type',
        'sh_flags',
        'sh_addr',
        'sh_offset',
        'sh_size',
        'sh_link',
        'sh_info',
        'sh_addralign',
        'sh_entsize')
    def __init__(self,data):
        self.set(data[:40])
        self.name_formatter('sh_name','sh_type')
        self.func_formatter(sh_addralign=token_constant_fmt)
    def __str__(self):
        if hasattr(self,'name'):
            self.pfx = '%-20s| '% ('<%s>'%self.name)
        return Elfcore.__str__(self)

with Consts('sh_name'):
    SHN_UNDEF=0
    SHN_LORESERVE=0xff00
    SHN_LOPROC=0xff00
    SHN_BEFORE=0xff00
    SHN_AFTER=0xff01
    SHN_HIPROC=0xff1f
    SHN_LOOS=0xff20
    SHN_HIOS=0xff3f
    SHN_ABS=0xfff1
    SHN_COMMON=0xfff2
    SHN_XINDEX=0xffff
    SHN_HIRESERVE=0xffff

# legal values for sh_type (section type):
with Consts('sh_type'):
    SHT_NULL=0
    SHT_PROGBITS=1
    SHT_SYMTAB=2
    SHT_STRTAB=3
    SHT_RELA=4
    SHT_HASH=5
    SHT_DYNAMIC=6
    SHT_NOTE=7
    SHT_NOBITS=8
    SHT_REL=9
    SHT_SHLIB=10
    SHT_DYNSYM=11
    SHT_INIT_ARRAY=14
    SHT_FINI_ARRAY=15
    SHT_PREINIT_ARRAY=16
    SHT_GROUP=17
    SHT_SYMTAB_SHNDX=18
    SHT_NUM=19
    SHT_LOOS=0x60000000
    SHT_GNU_HASH=0x6ffffff6
    SHT_GNU_LIBLIST=0x6ffffff7
    SHT_CHECKSUM=0x6ffffff8
    SHT_LOSUNW=0x6ffffffa
    SHT_SUNW_move=0x6ffffffa
    SHT_SUNW_COMDAT=0x6ffffffb
    SHT_SUNW_syminfo=0x6ffffffc
    SHT_GNU_verdef=0x6ffffffd
    SHT_GNU_verneed=0x6ffffffe
    SHT_GNU_versym=0x6fffffff
    SHT_HISUNW=0x6fffffff
    SHT_HIOS=0x6fffffff
    SHT_LOPROC=0x70000000
    SHT_HIPROC=0x7fffffff
    SHT_LOUSER=0x80000000
    SHT_HIUSER=0x8fffffff

# legal values for sh_flags (section flags):
with Consts('sh_flags'):
    SHF_WRITE=(1<<0)
    SHF_ALLOC=(1<<1)
    SHF_EXECINSTR=(1<<2)
    SHF_MERGE=(1<<4)
    SHF_STRINGS=(1<<5)
    SHF_INFO_LINK=(1<<6)
    SHF_LINK_ORDER=(1<<7)
    SHF_OS_NONCONFORMING=(1<<8)
    SHF_GROUP=(1<<9)
    SHF_TLS=(1<<10)
    SHF_MASKOS=0x0ff00000
    SHF_MASKPROC=0xf0000000
    SHF_ORDERED=(1<<30)
    SHF_EXCLUDE=(1<<31)

# section group handling:
GRP_COMDAT=0x1

# Symbol Table entry:
#------------------------------------------------------------------------------
class Elf32_Sym(Elfcore):
    fmt = 'IIIBBH'
    keys = (
        'st_name',
        'st_value',
        'st_size',
        'st_info',
        'st_other',
        'st_shndx')
    def __init__(self,data):
        self.set(data[:16])
        self.name_formatter('st_name','st_bind','st_type','st_visibility')
    def ELF32_ST_BIND(self):
        return self.st_info>>4
    st_bind = property(ELF32_ST_BIND)
    def ELF32_ST_TYPE(self):
        return self.st_info&0xf
    st_type = property(ELF32_ST_TYPE)
    def ELF32_ST_INFO(self,bind,type):
        self.st_info = bind<<4 + (type&0xf)
    def ELF32_ST_VISIBILITY(self):
        return self.st_other&0x03
    st_visibility = property(ELF32_ST_VISIBILITY)
    def __str__(self):
        s = Elfcore.__str__(self)+'\n'
        s += self.strkey('st_bind')
        s += self.strkey('st_type')
        s += self.strkey('st_visibility')
        return s

# legal values for elf32_st_bind:
with Consts('st_bind'):
    STB_LOCAL=0
    STB_GLOBAL=1
    STB_WEAK=2
    STB_NUM=3
    STB_LOOS=10
    STB_HIOS=12
    STB_LOPROC=13
    STB_HIPROC=15

# legal values for elf32_st_type:
with Consts('st_type'):
    STT_NOTYPE=0
    STT_OBJECT=1
    STT_FUNC=2
    STT_SECTION=3
    STT_FILE=4
    STT_COMMON=5
    STT_TLS=6
    STT_NUM=7
    STT_LOOS=10
    STT_HIOS=12
    STT_LOPROC=13
    STT_HIPROC=15

# special index indicating the end end of a chain:
STN_UNDEF=0

with Consts('st_visibility'):
    STV_DEFAULT=0
    STV_INTERNAL=1
    STV_HIDDEN=2
    STV_PROTECTED=3

# Relocations:
#------------------------------------------------------------------------------
class Elf32_Rel(Elfcore):
    fmt = 'II'
    keys = ('r_offset','r_info')
    def __init__(self,data):
        self.set(data[:8])
        self.name_formatter('r_type')
        self.func_formatter(r_sym=token_address_fmt)
    def ELF32_R_SYM(self):
        return self.r_info>>8
    r_sym = property(ELF32_R_SYM)
    def ELF32_R_TYPE(self):
        return self.r_info&0xff
    r_type = property(ELF32_R_TYPE)
    def ELF32_R_INFO(self,sym,type):
        self.r_info = sym<<8 + (type&0xff)
    def __str__(self):
        s = Elfcore.__str__(self)+'\n'
        s += self.strkey('r_type')
        return s

class Elf32_Rela(Elf32_Rel):
    fmt = 'III'
    keys = ('r_offset','r_info','r_addend')
    def __init__(self,data):
        self.set(data[:12])

#Intel 80386 specific definitions. #i386 relocs.
with Consts('r_type'):
    R_386_NONE=0
    R_386_32=1
    R_386_PC32=2
    R_386_GOT32=3
    R_386_PLT32=4
    R_386_COPY=5
    R_386_GLOB_DAT=6
    R_386_JMP_SLOT=7
    R_386_RELATIVE=8
    R_386_GOTOFF=9
    R_386_GOTPC=10
    R_386_32PLT=11
    R_386_TLS_TPOFF=14
    R_386_TLS_IE=15
    R_386_TLS_GOTIE=16
    R_386_TLS_LE=17
    R_386_TLS_GD=18
    R_386_TLS_LDM=19
    R_386_16=20
    R_386_PC16=21
    R_386_8=22
    R_386_PC8=23
    R_386_TLS_GD_32=24
    R_386_TLS_GD_PUSH=25
    R_386_TLS_GD_CALL=26
    R_386_TLS_GD_POP=27
    R_386_TLS_LDM_32=28
    R_386_TLS_LDM_PUSH=29
    R_386_TLS_LDM_CALL=30
    R_386_TLS_LDM_POP=31
    R_386_TLS_LDO_32=32
    R_386_TLS_IE_32=33
    R_386_TLS_LE_32=34
    R_386_TLS_DTPMOD32=35
    R_386_TLS_DTPOFF32=36
    R_386_TLS_TPOFF32=37
    R_386_NUM=38

# Program Segment header:
#------------------------------------------------------------------------------
class Elf32_Phdr(Elfcore):
    fmt = 'I'*8
    keys = (
        'p_type',
        'p_offset',
        'p_vaddr',
        'p_paddr',
        'p_filesz',
        'p_memsz',
        'p_flags',
        'p_align')

    def __init__(self, data):
        self.set(data[:32])
        self.name_formatter('p_type')

# legal values for p_type (segment type):
with Consts('p_type'):
    PT_NULL=0
    PT_LOAD=1
    PT_DYNAMIC=2
    PT_INTERP=3
    PT_NOTE=4
    PT_SHLIB=5
    PT_PHDR=6
    PT_TLS=7
    PT_NUM=8
    PT_LOOS=0x60000000
    PT_GNU_EH_FRAME=0x6474e550
    PT_GNU_STACK=0x6474e551
    PT_GNU_RELRO=0x6474e552
    PT_LOSUNW=0x6ffffffa
    PT_SUNWBSS=0x6ffffffa
    PT_SUNWSTACK=0x6ffffffb
    PT_HISUNW=0x6fffffff
    PT_HIOS=0x6fffffff
    PT_LOPROC=0x70000000
    PT_HIPROC=0x7fffffff

# legal values for p_flags (segment flags):
with Consts('p_flags'):
    PF_X=(1<<0)
    PF_W=(1<<1)
    PF_R=(1<<2)
    PF_MASKOS=0x0ff00000
    PF_MASKPROC=0xf0000000

# Note Sections :
#------------------------------------------------------------------------------
class Elf32_Note(Elfcore):
    fmt = 'III'
    keys = ('namesz','descsz','n_type')
    def __init__(self, data):
        self.set(data[:12])
        p = 12+self.namesz
        self.name = data[12:p]
        if p%4<>0: p = ((p+4)/4)*4
        self.desc = data[p:p+self.descsz]

# legal values for note segment descriptor types for core files:
with Consts('n_type'):
    NT_PRSTATUS=1
    NT_FPREGSET=2
    NT_PRPSINFO=3
    NT_PRXREG=4
    NT_TASKSTRUCT=4
    NT_PLATFORM=5
    NT_AUXV=6
    NT_GWINDOWS=7
    NT_ASRS=8
    NT_PSTATUS=10
    NT_PSINFO=13
    NT_PRCRED=14
    NT_UTSNAME=15
    NT_LWPSTATUS=16
    NT_LWPSINFO=17
    NT_PRFPXREG=20

    NT_VERSION=1

# Dynamic Section:
#------------------------------------------------------------------------------
class Elf32_Dyn(Elfcore):
    fmt = 'II'
    keys = ('d_tag','d_un')
    def __init__(self,data):
        self.set(data[:8])
        self.name_formatter('d_tag','d_un')
    def DT_VALTAGIDX(self,tag) :
        self.d_un = DT_VALRNGHI - tag
    def DT_ADDRTAGIDX(self,tag):
        self.d_un = DT_ADDRRNGHI - tag

# legal values for d_tag (dynamic entry type):
with Consts('d_tag'):
    DT_NULL=0
    DT_NEEDED=1
    DT_PLTRELSZ=2
    DT_PLTGOT=3
    DT_HASH=4
    DT_STRTAB=5
    DT_SYMTAB=6
    DT_RELA=7
    DT_RELASZ=8
    DT_RELAENT=9
    DT_STRSZ=10
    DT_SYMENT=11
    DT_INIT=12
    DT_FINI=13
    DT_SONAME=14
    DT_RPATH=15
    DT_SYMBOLIC=16
    DT_REL=17
    DT_RELSZ=18
    DT_RELENT=19
    DT_PLTREL=20
    DT_DEBUG=21
    DT_TEXTREL=22
    DT_JMPREL=23
    DT_BIND_NOW=24
    DT_INIT_ARRAY=25
    DT_FINI_ARRAY=26
    DT_INIT_ARRAYSZ=27
    DT_FINI_ARRAYSZ=28
    DT_RUNPATH=29
    DT_FLAGS=30
    DT_ENCODING=32
    DT_PREINIT_ARRAY=32
    DT_PREINIT_ARRAYSZ=33
    DT_NUM=34
    DT_LOOS=0x6000000d
    DT_HIOS=0x6ffff000
    DT_LOPROC=0x70000000
    DT_HIPROC=0x7fffffff

# legal values for d_un (union type use here value):
with Consts('d_un'):
    DT_VALRNGLO=0x6ffffd00
    DT_GNU_PRELINKED=0x6ffffdf5
    DT_GNU_CONFLICTSZ=0x6ffffdf6
    DT_GNU_LIBLISTSZ=0x6ffffdf7
    DT_CHECKSUM=0x6ffffdf8
    DT_PLTPADSZ=0x6ffffdf9
    DT_MOVEENT=0x6ffffdfa
    DT_MOVESZ=0x6ffffdfb
    DT_FEATURE_1=0x6ffffdfc
    DT_POSFLAG_1=0x6ffffdfd
    DT_SYMINSZ=0x6ffffdfe
    DT_SYMINENT=0x6ffffdff
    DT_VALRNGHI=0x6ffffdff
    DT_VALNUM=12

    # legal values for d_un (union type use here address):
    DT_ADDRRNGLO=0x6ffffe00
    DT_GNU_CONFLICT=0x6ffffef8
    DT_GNU_LIBLIST=0x6ffffef9
    DT_CONFIG=0x6ffffefa
    DT_DEPAUDIT=0x6ffffefb
    DT_AUDIT=0x6ffffefc
    DT_PLTPAD=0x6ffffefd
    DT_MOVETAB=0x6ffffefe
    DT_SYMINFO=0x6ffffeff
    DT_ADDRRNGHI=0x6ffffeff
    DT_ADDRNUM=10

# Version definition sections are not supported.

#------------------------------------------------------------------------------
##
## parse and provide information about ELF files
##
#------------------------------------------------------------------------------

class Elf32(object):

    basemap   = None
    symtab    = None
    strtab    = None
    reltab    = None
    functions = None
    variables = None

    @property
    def entrypoints(self):
        return [self.Ehdr.e_entry]

    @property
    def filename(self):
        return self.__file.name

    def __init__(self,filename):
        try:
            self.__file = file(filename,'rb')
        except (TypeError,IOError):
            from amoco.system.core import DataIO
            self.__file = DataIO(filename)
        data = self.__file.read(52)
        if len(data)<52: data = data.ljust(52,'\x00')
        self.Ehdr   = Elf32_Ehdr(data)

        self.dynamic = False

        # read program header table: should not raise any errors
        self.Phdr = []
        if self.Ehdr.e_phoff:
            self.__file.seek(self.Ehdr.e_phoff)
            n,l = self.Ehdr.e_phnum,self.Ehdr.e_phentsize
            data = self.__file.read(n*l)
            for pht in range(n):
                logger.progress(pht,n,'parsing Phdrs ')
                self.Phdr.append(Elf32_Phdr(data[pht*l:]))
                if self.Phdr[-1].p_type == PT_LOAD:
                    if not self.basemap: self.basemap = self.Phdr[-1].p_vaddr
                elif self.Phdr[-1].p_type == PT_DYNAMIC:
                    self.dynamic = True
                elif not self.Phdr[-1].p_type in ELF_CONSTS['p_type'].keys():
                    logger.verbose('invalid segment detected (removed)')
                    self.Phdr.pop()

        # read section header table: unused by loader, can raise error
        self.Shdr = []
        if self.Ehdr.e_shoff:
            try:
                self.__file.seek(self.Ehdr.e_shoff)
                n,l = self.Ehdr.e_shnum,self.Ehdr.e_shentsize
                data = self.__file.read(n*l)
                for sht in range(n):
                    logger.progress(sht,n,'parsing Shdrs ')
                    S = Elf32_Shdr(data[sht*l:])
                    if S.sh_type in ELF_CONSTS['sh_type'].keys():
                        self.Shdr.append(S)
                    else:
                        raise StandardError
            except :
                logger.verbose('invalid section detected (all Shdr removed)')
                self.Shdr = []

        # read section's name string table:
        n = self.Ehdr.e_shstrndx
        if n!=SHN_UNDEF and n in range(len(self.Shdr)):
            S = self.Shdr[self.Ehdr.e_shstrndx]
            self.__file.seek(S.sh_offset)
            data = self.__file.read(S.sh_size)
            if S.sh_type!=SHT_STRTAB:
                logger.verbose('section names not a string table')
                for s in self.Shdr:
                    s.name = ''
            else:
                for s in self.Shdr:
                    s.name = data[s.sh_name:].split('\0')[0]

        self.functions = self.__functions()
        self.variables = self.__variables()
    ##

    def getsize(self):
        total = sum([s.p_filesz for s in self.Phdr])
        return total

    #  allows to get info about target :
    # - section index (0 is error, -1 is a dynamic call)
    # - offset into section  (idem)
    # - base virtual address (0 for dynamic calls)
    # target can be a virtual address in hex string format or integer,
    # or a symbol string searched in the functions dictionary.
    def getinfo(self,target):
        addr = None
        if isinstance(target,str):
            try:
                addr = int(target,16)
            except ValueError:
                for a,f in self.functions.iteritems():
                    if f[0]==target: addr = int(a,16); break
        elif type(target) in [int,long]:
            addr = target
        if addr is None:
            # target is propably a symbol not found in functions
            return None,0,0

        # now we have addr so we can see in which section/segment it is...
        # sections are smaller than segments so we try first with Shdr
        # but this may lead to errors because what really matters are segments
        # loaded by the kernel binfmt_elf.c loader.
        if self.Shdr:
            for s in self.Shdr[::-1]:
                if s.sh_type == SHT_NULL: continue
                if s.sh_addr <= addr < s.sh_addr+s.sh_size :
                    return s,addr-s.sh_addr,s.sh_addr
            ##
        elif self.Phdr:
            for s in self.Phdr[::-1]:
                if s.p_type != PT_LOAD: continue
                if s.p_vaddr <= addr < s.p_vaddr+s.p_filesz:
                    return s,addr-s.p_vaddr,s.p_vaddr
        return None,0,0
    ##

    def data(self,target,size):
        return self.readcode(target,size)[0]

    def readcode(self,target,size=None):
        s,offset,base = self.getinfo(target)
        data = ''
        if s:
            if isinstance(s,Elf32_Phdr):
                c = self.readsegment(s)
            else:
                c = self.readsection(s)
            if c:
                if size!=None:
                    if isinstance(c,Elf32_Str): c = c.data
                    data = c[offset:offset+size]
                else:
                    data = c[offset:]
        return data,0,base+offset

    def readsegment(self,S):
        if S:
            if S.p_type==PT_LOAD:
                self.__file.seek(S.p_offset)
                return self.__file.read(S.p_filesz).ljust(S.p_memsz,'\x00')
        return None
    ##
    def loadsegment(self,S,pagesize=None):
        if S:
            if S.p_type==PT_LOAD:
                self.__file.seek( S.p_offset )
                if S.p_offset != (S.p_vaddr%S.p_align):
                    logger.verbose('wrong p_vaddr/p_align [%08x/%0d]'%(S.p_vaddr,S.p_align))
                base = S.p_vaddr
                bytes = self.__file.read( S.p_filesz ).ljust(S.p_memsz,'\x00')
                if pagesize:
                    # note: bytes are not truncated, only extended if needed...
                    bytes = bytes.ljust(pagesize,'\x00')
                return {base:bytes}
        return None
    ##

    def readsection(self,sect):
        S = None
        if type(sect)==str:
            for st in self.Shdr:
                if st.name==sect: S=st; break
        elif type(sect) in [int,long]:
            S = self.Shdr[sect]
        else:
            S = sect
        if S:
            if S.sh_type in (SHT_SYMTAB,SHT_DYNSYM):
                return self.__read_symtab(S)
            elif S.sh_type==SHT_STRTAB :
                return self.__read_strtab(S)
            elif S.sh_type in (SHT_REL,SHT_RELA):
                return self.__read_relocs(S)
            elif S.sh_type==SHT_DYNAMIC :
                return self.__read_dynamic(S)
            elif S.sh_type==SHT_PROGBITS:
                self.__file.seek(S.sh_offset)
                return self.__file.read(S.sh_size)
        return None
    ##

    def __read_symtab(self,section):
        if section.sh_type not in (SHT_SYMTAB,SHT_DYNSYM) :
            logger.warning('not a symbol table section')
            return None
        # read the section:
        self.__file.seek(section.sh_offset)
        data = self.__file.read(section.sh_size)
        # and parse it into Elf32_Sym objects:
        l = section.sh_entsize
        if (section.sh_size%l)!=0:
            raise ElfError('symbol table size mismatch')
        else:
            n = section.sh_size/l
        symtab = []
        for i in range(n):
            symtab.append( Elf32_Sym(data[i*l:]) )
        self.symtab = symtab
        return symtab
    ##

    def __read_strtab(self,section):
        if section.sh_type!=SHT_STRTAB:
            raise ElfError('not a string table section')
        self.__file.seek(section.sh_offset)
        data = self.__file.read(section.sh_size)
        strtab = Elf32_Str(data)
        self.strtab = strtab
        return strtab
    ##

    def __read_relocs(self,section):
        if  section.sh_type not in (SHT_REL,SHT_RELA) :
            logger.warning('not a relocation table section')
            return None
        self.__file.seek(section.sh_offset)
        data = self.__file.read(section.sh_size)
        l = section.sh_entsize
        if (section.sh_size%l)!=0:
            raise ElfError('relocation table size mismatch')
        else:
            n = section.sh_size/l
        reltab = []
        if   section.sh_type==SHT_REL:
            for i in range(n):
                reltab.append( Elf32_Rel(data[i*l:]) )
        elif section.sh_type==SHT_RELA:
            for i in range(n):
                reltab.append( Elf32_Rela(data[i*l:]) )
        self.reltab = reltab
        return reltab

    def __read_dynamic(self,section):
        if section.sh_type!=SHT_DYNAMIC :
            logger.warning('not a dynamic linking section')
            return None
        # read the section:
        self.__file.seek(section.sh_offset)
        data = self.__file.read(section.sh_size)
        # and parse it into Elf32_Dyn objects:
        l = section.sh_entsize
        if (section.sh_size%l)!=0:
            raise ElfError('dynamic linking size mismatch')
        else:
            n = section.sh_size/l
        dyntab = []
        for i in range(n):
            dyntab.append( Elf32_Dyn(data[i*l:]) )
        self.dyntab = dyntab
        return dyntab
    ##

    def __read_note(self,section):
        if section.sh_type!=SHT_NOTE:
            logger.warning('not a note section')
            return None
        self.__file.seek(section.sh_offset)
        data = self.__file.read(section.sh_size)
        note = Elf32_Note(data)
        self.note = note
        return note
    ##

    def __functions(self,fltr=None):
        D = self.__symbols(STT_FUNC)
        # fltr applies to section name only :
        if fltr:
            for k,v in D.iteritems():
                if self.Shdr[v[2]].name != fltr: D.pop(k)
        if self.dynamic:
            D.update(self.__dynamic(STT_FUNC))
        return D

    def __variables(self,fltr=None):
        D = self.__symbols(STT_OBJECT)
        # fltr applies also to section name :
        if fltr:
            for k,v in D.iteritems():
                if self.Shdr[v[2]].name != fltr: D.pop(k)
        return D

    def __symbols(self,t):
        if not self.readsection('.symtab') : return {}
        D = {}
        if self.readsection('.strtab'):
            for sym in self.symtab:
                if sym.st_type==t and sym.st_value:
                    D[sym.st_value] = (self.strtab[sym.st_name],
                                       sym.st_size,
                                       sym.st_info,
                                       sym.st_shndx)
        else:
            # need to build a fake strtab with our own symbol names:
            pass #TODO
        return D

    def __dynamic(self,type=STT_FUNC):
        if not self.readsection('.dynsym') : return {}
        D = {}
        if self.readsection('.dynstr'):
            for i,s in enumerate(self.Shdr):
                if s.sh_type in (SHT_REL,SHT_RELA):
                    if self.readsection(i):
                        for r in self.reltab:
                            if r.r_offset:
                                sym = self.symtab[ r.r_sym ]
                                D[r.r_offset] = self.strtab[sym.st_name]
        else:
            # need to build a fake strtab with our own symbol names:
            pass #TODO
        return D

    def __str__(self):
        ss = ['ELF header:']
        tmp = self.Ehdr.pfx
        self.Ehdr.pfx = '\t'
        ss.append(self.Ehdr.__str__())
        self.Ehdr.pfx = tmp
        ss += ['\nSections:']
        for s in self.Shdr:
            tmp = s.pfx
            s.pfx = '\t'
            ss.append(s.__str__()); ss.append('---')
            s.pfx = tmp
        ss += ['\nSegments:']
        for s in self.Phdr:
            tmp = s.pfx
            s.pfx = '\t'
            ss.append(s.__str__()); ss.append('---')
            s.pfx = tmp
        return '\n'.join(ss)

## End of class Elf32


# String Table entry; provided to deal with C strings and char indexed
# string table sections. This is not a standard structure, it is more
# like a C-string Array class for python.
#------------------------------------------------------------------------------
class Elf32_Str:
    def __init__(self,data):
        self.data = data

    def __getitem__(self,i):
        z = self.data[i:].index('\0')
        return self.data[i:i+z]

    def as_dict(self):
        D = {}
        cstrings = self.data.split('\0')
        p=0
        for cs in cstrings:
            D[p] = cs
            p += len(cs)+1
        return D

    def __str__(self):
        return '\n'.join(
             ("0x%08x: %s"%(k,v) for (k,v) in self.as_dict().iteritems()))
## End of class Elf32_Str

# -----------------------------------------------------------------------------
# ELF64 File Format
# -----------------------------------------------------------------------------

# The ELF file header.
#------------------------------------------------------------------------------
class Elf64_Ehdr(Elfcore):
    # Elfcore is not used for the e_ident dict, only for the following keys:
    fmt = 'HHIQQQIHHHHHH'
    keys = (
        'e_type',
        'e_machine',
        'e_version',
        'e_entry',
        'e_phoff',
        'e_shoff',
        'e_flags',
        'e_ehsize',
        'e_phentsize',
        'e_phnum',
        'e_shentsize',
        'e_shnum',
        'e_shstrndx')
    # overload Elfcore methods to take into account the e_ident dict:
    def __init__(self, data):
        S = struct.unpack('B3sBBBBBxxxxxxx',data[:16])
        if S[0]!=0x7f or S[1]!='ELF':
            raise ElfError('Wrong magic number, not an ELF file ?')
        self.e_ident = dict(zip(EI_KEYS,S))
        try:
            self.order = {ELFDATA2LSB:'<',ELFDATA2MSB:'>'}[self.e_ident['EI_DATA']]
            Elfcore.order = self.order
        except KeyError:
                logger.info("No endianess specified in ELF header.")
        # we need only 32-bit arch here:
        if self.e_ident['EI_CLASS'] != ELFCLASS64 :
            logger.warning("not a 64-bit ELF, tried Elf32 ?")
            raise ElfError(self.e_ident['EI_CLASS'])
        self.set(data[16:16+struct.calcsize(self.fmt)])
        self.name_formatter('e_type','e_machine','e_version')
        self.func_formatter(e_entry=token_address_fmt)
        self.func_formatter(e_flags=token_address_fmt)

    def pack(self):
        e_ident_s = struct.pack('B3sBBBBBxxxxxxx',*[self.e_ident[k] for k in EI_KEYS])
        return e_ident_s+Elfcore.pack(self)
    # patched Elfcore str to have entrypoint in hex:
    def __str__(self):
        s = list(Elfcore.__str__(self).partition('\n'))
        x = '; '.join([token_name_fmt(k,v) for (k,v) in self.e_ident.iteritems()])
        fmt = '\n%%s%%-%ds:%%s'%self.ksz
        s.insert(1,fmt%(self.pfx,'e_ident',x))
        return ''.join(s)


# Section header:
#------------------------------------------------------------------------------
class Elf64_Shdr(Elfcore):
    fmt = 'IIQQQQIIQQ'
    keys = (
        'sh_name',
        'sh_type',
        'sh_flags',
        'sh_addr',
        'sh_offset',
        'sh_size',
        'sh_link',
        'sh_info',
        'sh_addralign',
        'sh_entsize')
    def __init__(self,data):
        self.set(data[:struct.calcsize(self.fmt)])
	self.name_formatter('sh_name','sh_type')
    def __str__(self):
        if hasattr(self,'name'):
            self.pfx = '%-20s| '% ('<%s>'%self.name)
        return Elfcore.__str__(self)

# Symbol Table entry:
#------------------------------------------------------------------------------
class Elf64_Sym(Elfcore):
    fmt = 'IBBHQQ'
    keys = (
        'st_name',
        'st_info',
        'st_other',
        'st_shndx',
        'st_value',
        'st_size')
    def __init__(self,data):
        self.set(data[:struct.calcsize(self.fmt)])
        self.name_formatter('st_name','st_bind','st_type','st_visibility')
    def ELF64_ST_BIND(self):
        return self.st_info>>4
    st_bind = property(ELF64_ST_BIND)
    def ELF64_ST_TYPE(self):
        return self.st_info&0xf
    st_type = property(ELF64_ST_TYPE)
    def ELF64_ST_INFO(self,bind,type):
        self.st_info = bind<<4 + (type&0xf)
    def ELF64_ST_VISIBILITY(self):
        return self.st_other&0x03
    st_visibility = property(ELF64_ST_VISIBILITY)
    def __str__(self):
        s = Elfcore.__str__(self)+'\n'
        s += self.strkey('st_bind')
        s += self.strkey('st_type')
        s += self.strkey('st_visibility')
        return s

# Relocations:
#------------------------------------------------------------------------------
class Elf64_Rel(Elfcore):
    fmt = 'QQ'
    keys = ('r_offset','r_info')
    def __init__(self,data):
        self.set(data[:struct.calcsize(self.fmt)])
    def ELF64_R_SYM(self):
        return self.r_info>>32
    r_sym = property(ELF64_R_SYM)
    def ELF64_R_TYPE(self):
        return self.r_info&0xffffffffL
    r_type = property(ELF64_R_TYPE)
    def ELF64_R_INFO(self,sym,type):
        self.r_info = sym<<32 + (type&0xffffffffL)
    def __str__(self):
        s = Elfcore.__str__(self)+'\n'
        s += self.strkey('r_type')
        return s

class Elf64_Rela(Elf64_Rel):
    fmt = 'QQQ'
    keys = ('r_offset','r_info','r_addend')
    def __init__(self,data):
        self.set(data[:struct.calcsize(self.fmt)])

# Program Segment header:
#------------------------------------------------------------------------------
class Elf64_Phdr(Elfcore):
    fmt = 'IIQQQQQQ'
    keys = (
        'p_type',
        'p_flags',
        'p_offset',
        'p_vaddr',
        'p_paddr',
        'p_filesz',
        'p_memsz',
        'p_align')

    def __init__(self, data):
        self.set(data[:struct.calcsize(self.fmt)])
        self.name_formatter('p_type')

# Note Sections :
#------------------------------------------------------------------------------
class Elf64_Note(Elfcore):
    fmt = 'QQQ'
    keys = ('namesz','descsz','n_type')
    def __init__(self, data):
        l = struct.calcsize(self.fmt)
        self.set(data[:l])
        p = l+self.namesz
        self.name = data[l:p]
        if p%8: p = ((p+8)/8)*8
        self.desc = data[p:p+self.descsz]

# Dynamic Section:
#------------------------------------------------------------------------------
class Elf64_Dyn(Elfcore):
    fmt = 'QQ'
    keys = ('d_tag','d_un')
    def __init__(self,data):
        self.set(data[:struct.calcsize(self.fmt)])
    def DT_VALTAGIDX(self,tag) :
        self.d_un = DT_VALRNGHI - tag
    def DT_ADDRTAGIDX(self,tag):
        self.d_un = DT_ADDRRNGHI - tag

#------------------------------------------------------------------------------
##
## parse and provide information about ELF files
##
#------------------------------------------------------------------------------

class Elf64(object):

    basemap   = None
    symtab    = None
    strtab    = None
    reltab    = None
    functions = None
    variables = None

    @property
    def entrypoints(self):
        return [self.Ehdr.e_entry]

    @property
    def filename(self):
        return self.__file.name

    def __init__(self,filename):
        try:
            self.__file = file(filename,'rb')
        except (TypeError,IOError):
            from amoco.system.core import DataIO
            self.__file = DataIO(filename)
        data = self.__file.read(64)
        if len(data)<64: data = data.ljust(64,'\x00')
        self.Ehdr   = Elf64_Ehdr(data)

        self.dynamic = False

        # read program header table: should not raise any errors
        self.Phdr = []
        if self.Ehdr.e_phoff:
            self.__file.seek(self.Ehdr.e_phoff)
            n,l = self.Ehdr.e_phnum,self.Ehdr.e_phentsize
            data = self.__file.read(n*l)
            for pht in range(n):
                logger.progress(pht,n,'parsing Phdrs ')
                self.Phdr.append(Elf64_Phdr(data[pht*l:]))
                if self.Phdr[-1].p_type == PT_LOAD:
                    if not self.basemap: self.basemap = self.Phdr[-1].p_vaddr
                elif self.Phdr[-1].p_type == PT_DYNAMIC:
                    self.dynamic = True
                elif not self.Phdr[-1].p_type in ELF_CONSTS['p_type'].keys():
                    logger.verbose('invalid segment detected (removed)')
                    self.Phdr.pop()

        # read section header table: unused by loader, can raise error
        self.Shdr = []
        if self.Ehdr.e_shoff:
            try:
                self.__file.seek(self.Ehdr.e_shoff)
                n,l = self.Ehdr.e_shnum,self.Ehdr.e_shentsize
                data = self.__file.read(n*l)
                for sht in range(n):
                    logger.progress(sht,n,'parsing Shdrs ')
                    S = Elf64_Shdr(data[sht*l:])
                    if S.sh_type in ELF_CONSTS['sh_type'].keys():
                        self.Shdr.append(S)
                    else:
                        raise StandardError
            except :
                logger.verbose('invalid section detected (all Shdr removed)')
                self.Shdr = []

        # read section's name string table:
        n = self.Ehdr.e_shstrndx
        if n!=SHN_UNDEF and n in range(len(self.Shdr)):
            S = self.Shdr[self.Ehdr.e_shstrndx]
            self.__file.seek(S.sh_offset)
            data = self.__file.read(S.sh_size)
            if S.sh_type!=SHT_STRTAB:
                logger.verbose('section names not a string table')
                for s in self.Shdr:
                    s.name = ''
            else:
                for s in self.Shdr:
                    s.name = data[s.sh_name:].split('\0')[0]

        self.functions = self.__functions()
        self.variables = self.__variables()
    ##

    def getsize(self):
        total = sum([s.p_filesz for s in self.Phdr])
        return total

    #  allows to get info about target :
    # - section index (0 is error, -1 is a dynamic call)
    # - offset into section  (idem)
    # - base virtual address (0 for dynamic calls)
    # target can be a virtual address in hex string format or integer,
    # or a symbol string searched in the functions dictionary.
    def getinfo(self,target):
        addr = None
        if isinstance(target,str):
            try:
                addr = int(target,16)
            except ValueError:
                for a,f in self.functions.iteritems():
                    if f[0]==target: addr = int(a,16); break
        elif type(target) in [int,long]:
            addr = target
        if addr is None:
            # target is propably a symbol not found in functions
            return None,0,0

        # now we have addr so we can see in which section/segment it is...
        # sections are smaller than segments so we try first with Shdr
        # but this may lead to errors because what really matters are segments
        # loaded by the kernel binfmt_elf.c loader.
        if self.Shdr:
            for s in self.Shdr[::-1]:
                if s.sh_type == SHT_NULL: continue
                if s.sh_addr <= addr < s.sh_addr+s.sh_size :
                    return s,addr-s.sh_addr,s.sh_addr
            ##
        elif self.Phdr:
            for s in self.Phdr[::-1]:
                if s.p_type != PT_LOAD: continue
                if s.p_vaddr <= addr < s.p_vaddr+s.p_filesz:
                    return s,addr-s.p_vaddr,s.p_vaddr
        return None,0,0
    ##

    def data(self,target,size):
        return self.readcode(target,size)[0]

    def readcode(self,target,size=None):
        s,offset,base = self.getinfo(target)
        data = ''
        if s:
            if isinstance(s,Elf64_Phdr):
                c = self.readsegment(s)
            else:
                c = self.readsection(s)
            if c:
                if size!=None:
                    if isinstance(c,Elf64_Str): c = c.data
                    data = c[offset:offset+size]
                else:
                    data = c[offset:]
        return data,0,base+offset

    def readsegment(self,S):
        if S:
            if S.p_type==PT_LOAD:
                self.__file.seek(S.p_offset)
                return self.__file.read(S.p_filesz).ljust(S.p_memsz,'\x00')
        return None
    ##
    def loadsegment(self,S,pagesize=None):
        if S:
            if S.p_type==PT_LOAD:
                self.__file.seek( S.p_offset )
                if S.p_offset != (S.p_vaddr%S.p_align):
                    logger.verbose("wrong p_vaddr/p_align [%08x/%0d]"%(S.p_vaddr,S.p_align))
                base = S.p_vaddr
                bytes = self.__file.read( S.p_filesz ).ljust(S.p_memsz,'\x00')
                if pagesize:
                    # note: bytes are not truncated, only extended if needed...
                    bytes = bytes.ljust(pagesize,'\x00')
                return {base:bytes}
        return None
    ##

    def readsection(self,sect):
        S = None
        if type(sect)==str:
            for st in self.Shdr:
                if st.name==sect: S=st; break
        elif type(sect) in [int,long]:
            S = self.Shdr[sect]
        else:
            S = sect
        if S:
            if   S.sh_type==SHT_SYMTAB \
                or S.sh_type==SHT_DYNSYM : return self.__read_symtab(S)
            elif S.sh_type==SHT_STRTAB : return self.__read_strtab(S)
            elif S.sh_type==SHT_REL \
                or S.sh_type==SHT_RELA  : return self.__read_relocs(S)
            elif S.sh_type==SHT_DYNAMIC : return self.__read_dynamic(S)
            elif S.sh_type==SHT_PROGBITS:
                self.__file.seek(S.sh_offset)
                return self.__file.read(S.sh_size)
        return None
    ##

    def __read_symtab(self,section):
        if section.sh_type!=SHT_SYMTAB and section.sh_type!=SHT_DYNSYM :
            logger.warning('not a symbol table section')
            return None
        # read the section:
        self.__file.seek(section.sh_offset)
        data = self.__file.read(section.sh_size)
        # and parse it into Elf64_Sym objects:
        l = section.sh_entsize
        if (section.sh_size%l)!=0:
            raise ElfError('symbol table size mismatch')
        else:
            n = section.sh_size/l
        symtab = []
        for i in range(n):
            symtab.append( Elf64_Sym(data[i*l:]) )
        self.symtab = symtab
        return symtab
    ##

    def __read_strtab(self,section):
        if section.sh_type!=SHT_STRTAB:
            raise ElfError('not a string table section')
        self.__file.seek(section.sh_offset)
        data = self.__file.read(section.sh_size)
        strtab = Elf64_Str(data)
        self.strtab = strtab
        return strtab
    ##

    def __read_relocs(self,section):
        if  section.sh_type!=SHT_REL \
        and section.sh_type!=SHT_RELA :
            logger.warning('not a relocation table section')
            return None
        self.__file.seek(section.sh_offset)
        data = self.__file.read(section.sh_size)
        l = section.sh_entsize
        if (section.sh_size%l)!=0:
            raise ElfError('relocation table size mismatch')
        else:
            n = section.sh_size/l
        reltab = []
        if   section.sh_type==SHT_REL:
            for i in range(n):
                reltab.append( Elf64_Rel(data[i*l:]) )
        elif section.sh_type==SHT_RELA:
            for i in range(n):
                reltab.append( Elf64_Rela(data[i*l:]) )
        self.reltab = reltab
        return reltab

    def __read_dynamic(self,section):
        if section.sh_type!=SHT_DYNAMIC :
            logger.warning('not a dynamic linking section')
            return None
        # read the section:
        self.__file.seek(section.sh_offset)
        data = self.__file.read(section.sh_size)
        # and parse it into Elf32_Dyn objects:
        l = section.sh_entsize
        if (section.sh_size%l)!=0:
            raise ElfError('dynamic linking size mismatch')
        else:
            n = section.sh_size/l
        dyntab = []
        for i in range(n):
            dyntab.append( Elf64_Dyn(data[i*l:]) )
        self.dyntab = dyntab
        return dyntab
    ##

    def __read_note(self,section):
        if section.sh_type!=SHT_NOTE:
            logger.warning('not a note section')
            return None
        self.__file.seek(section.sh_offset)
        data = self.__file.read(section.sh_size)
        note = Elf64_Note(data)
        self.note = note
        return note
    ##

    def __functions(self,fltr=None):
        D = self.__symbols(STT_FUNC)
        # fltr applies to section name only :
        if fltr:
            for k,v in D.iteritems():
                if self.Shdr[v[2]].name != fltr: D.pop(k)
        if self.dynamic:
            D.update(self.__dynamic(STT_FUNC))
        return D

    def __variables(self,fltr=None):
        D = self.__symbols(STT_OBJECT)
        # fltr applies also to section name :
        if fltr:
            for k,v in D.iteritems():
                if self.Shdr[v[2]].name != fltr: D.pop(k)
        return D

    def __symbols(self,type):
        if not self.readsection('.symtab') : return {}
        D = {}
        if self.readsection('.strtab'):
            for sym in self.symtab:
                if sym.ELF64_ST_TYPE()==type and sym.st_value:
                    D[sym.st_value] = (self.strtab[sym.st_name],
                                       sym.st_size,
                                       sym.st_info,
                                       sym.st_shndx)
        else:
            # need to build a fake strtab with our own symbol names:
            pass #TODO
        return D

    def __dynamic(self,type=STT_FUNC):
        if not self.readsection('.dynsym') : return {}
        D = {}
        if self.readsection('.dynstr'):
            for i,s in enumerate(self.Shdr):
                if s.sh_type == SHT_REL \
                or s.sh_type == SHT_RELA :
                    if self.readsection(i):
                        for r in self.reltab:
                            if r.r_offset:
                                sym = self.symtab[ r.ELF64_R_SYM() ]
                                D[r.r_offset] = self.strtab[sym.st_name]
        else:
            # need to build a fake strtab with our own symbol names:
            pass #TODO
        return D

    def __str__(self):
        ss = ['ELF header:']
        tmp = self.Ehdr.pfx
        self.Ehdr.pfx = '\t'
        ss.append(self.Ehdr.__str__())
        self.Ehdr.pfx = tmp
        ss += ['\nSections:']
        for s in self.Shdr:
            tmp = s.pfx
            s.pfx = '\t'
            ss.append(s.__str__()); ss.append('---')
            s.pfx = tmp
        ss += ['\nSegments:']
        for s in self.Phdr:
            tmp = s.pfx
            s.pfx = '\t'
            ss.append(s.__str__()); ss.append('---')
            s.pfx = tmp
        return '\n'.join(ss)

## End of class Elf64


# String Table entry; provided to deal with C strings and char indexed
# string table sections. This is not a standard structure, it is more
# like a C-string Array class for python.
#------------------------------------------------------------------------------
class Elf64_Str:
    def __init__(self,data):
        self.data = data

    def __getitem__(self,i):
        z = self.data[i:].index('\0')
        return self.data[i:i+z]

    def as_dict(self):
        D = {}
        cstrings = self.data.split('\0')
        p=0
        for cs in cstrings:
            D[p] = cs
            p += len(cs)+1
        return D

    def __str__(self):
        return '\n'.join(
             ("0x%016x: %s"%(k,v) for (k,v) in self.as_dict().iteritems()))
## End of class Elf64_Str

