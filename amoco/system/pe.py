# -*- coding: utf-8 -*-

# This code is part of Amoco
# based on elf.py, improving pefile to work out corkami's CoST.exe.
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

import struct
from datetime import datetime
from amoco.system.core import DataIO
from amoco.logger import *
logger = Log(__name__)

from collections import defaultdict
from amoco.ui.render import Token,highlight


# our exception handler:
class PEError(Exception):
    def __init__(self,message):
        self.message = message
    def __str__(self):
        return str(self.message)
##

#------------------------------------------------------------------------------
# formatting facilities:

# init of reverse dict to get constant name from value.
# This dict is updated by using 'with' statement of Consts.
PE_CONSTS = defaultdict(dict)

class Consts(object):
    def __init__(self,name):
        self.name = name
    def __enter__(self):
        PE_CONSTS[self.name] = {}
        self.globnames = set(globals().keys())
    def __exit__(self,exc_type,exc_value,traceback):
        G = globals()
        for k in set(G.keys())-self.globnames:
            PE_CONSTS[self.name][G[k]] = k

def default_formatter():
    return token_default_fmt

def token_default_fmt(k,x,cls=None):
    if 'RVA'  in k: return token_address_fmt(k,x)
    if 'flags' in k: return token_flag_fmt(k,x)
    return highlight([(Token.Literal,str(x))])

def token_address_fmt(k,x,cls=None):
    return highlight([(Token.Address,hex(x))])

def token_constant_fmt(k,x,cls=None):
    return highlight([(Token.Constant,str(x))])

def token_name_fmt(k,x,cls=None):
    try:
        return highlight([(Token.Name,PE_CONSTS[k][x])])
    except KeyError:
        return token_constant_fmt(k,x)

def token_flag_fmt(k,x,cls):
    s = []
    for v,name in PE_CONSTS["%s%s"%(cls,k)].items():
        if (x&v): s.append(highlight([(Token.Name,name)]))
    return ','.join(s)


#------------------------------------------------------------------------------
class PEcore(object):
    order = '<' #le
    pfx = ''
    ksz = 20
    fkeys = defaultdict(default_formatter)
    def __init__(self,data,offset=0):
        self.set(data[offset:offset+len(self)])
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
        return fmt%(self.pfx,k,self.fkeys[k](k,getattr(self,k),cls=cname))
    def __str__(self):
        cname = self.__class__.__name__
        s = u'\n'.join(self.strkey(k,cname) for k in self.keys)
        return u"[%s]\n%s"%(cname,s)
    def __len__(self):
        return struct.calcsize(self.fmt)


# The PE file header(s).
#------------------------------------------------------------------------------

with Consts('Signature'):
    IMAGE_DOS_SIGNATURE=0x5A4D
    IMAGE_OS2_SIGNATURE=0x454E
    IMAGE_OS2_SIGNATURE_LE=0x454C
    IMAGE_VXD_SIGNATURE=0x454C
    IMAGE_NT_SIGNATURE=0x00004550

class DOSHdr(PEcore):
    fmt = 'H58xI'
    keys = ('e_magic', 'e_lfanew')
    def __init__(self,data,offset=0):
        if data[offset:offset+2]!=b'MZ': raise PEError('no DOS Header found')
        PEcore.__init__(self,data,offset)

IMAGE_NUMBEROF_DIRECTORY_ENTRIES=16
IMAGE_ORDINAL_FLAG=0x80000000
IMAGE_ORDINAL_FLAG64=0x8000000000000000

with Consts('Magic'):
    OPTIONAL_HEADER_MAGIC_PE=0x10b
    OPTIONAL_HEADER_MAGIC_PE_PLUS=0x20b

with Consts('Machine'):
    IMAGE_FILE_MACHINE_UNKNOWN=0
    IMAGE_FILE_MACHINE_AM33=0x1d3
    IMAGE_FILE_MACHINE_AMD64=0x8664
    IMAGE_FILE_MACHINE_ARM=0x1c0
    IMAGE_FILE_MACHINE_EBC=0xebc
    IMAGE_FILE_MACHINE_I386=0x14c
    IMAGE_FILE_MACHINE_IA64=0x200
    IMAGE_FILE_MACHINE_MR32=0x9041
    IMAGE_FILE_MACHINE_MIPS16=0x266
    IMAGE_FILE_MACHINE_MIPSFPU=0x366
    IMAGE_FILE_MACHINE_MIPSFPU16=0x466
    IMAGE_FILE_MACHINE_POWERPC=0x1f0
    IMAGE_FILE_MACHINE_POWERPCFP=0x1f1
    IMAGE_FILE_MACHINE_R4000=0x166
    IMAGE_FILE_MACHINE_SH3=0x1a2
    IMAGE_FILE_MACHINE_SH3DSP=0x1a3
    IMAGE_FILE_MACHINE_SH4=0x1a6
    IMAGE_FILE_MACHINE_SH5=0x1a8
    IMAGE_FILE_MACHINE_THUMB=0x1c2
    IMAGE_FILE_MACHINE_WCEMIPSV2=0x169

with Consts('COFFHdrCharacteristics'):
    IMAGE_FILE_RELOCS_STRIPPED=0x0001
    IMAGE_FILE_EXECUTABLE_IMAGE=0x0002
    IMAGE_FILE_LINE_NUMS_STRIPPED=0x0004
    IMAGE_FILE_LOCAL_SYMS_STRIPPED=0x0008
    IMAGE_FILE_AGGRESIVE_WS_TRIM=0x0010
    IMAGE_FILE_LARGE_ADDRESS_AWARE=0x0020
    IMAGE_FILE_16BIT_MACHINE=0x0040
    IMAGE_FILE_BYTES_REVERSED_LO=0x0080
    IMAGE_FILE_32BIT_MACHINE=0x0100
    IMAGE_FILE_DEBUG_STRIPPED=0x0200
    IMAGE_FILE_REMOVABLE_RUN_FROM_SWAP=0x0400
    IMAGE_FILE_NET_RUN_FROM_SWAP=0x0800
    IMAGE_FILE_SYSTEM=0x1000
    IMAGE_FILE_DLL=0x2000
    IMAGE_FILE_UP_SYSTEM_ONLY=0x4000
    IMAGE_FILE_BYTES_REVERSED_HI=0x8000

class COFFHdr(PEcore):
    fmt = 'IHHIIIHH'
    keys = (
        'Signature',
        'Machine',
        'NumberOfSections',
        'TimeDateStamp',
        'PointerToSymbolTable',
        'NumberOfSymbols',
        'SizeOfOptionalHeader',
        'Characteristics')
    def __init__(self,data,offset=0):
        if data[offset:offset+2]!=b'PE': raise PEError('no PE Header found')
        PEcore.__init__(self,data,offset)
        self.name_formatter('Signature','Machine')
        self.flag_formatter('Characteristics')
        self.func_formatter(TimeDateStamp = (lambda k,x,cls: str(datetime.utcfromtimestamp(x))))

class OptionalHdr(PEcore):
    fmt = 'HBBIIIIII'+'IIIHHHHHHIIIIHH'+'IIII'+'II'
    keys = (
        'Magic',
        'MajorLinkerVersion',
        'MinorLinkerVersion',
        'SizeOfCode',
        'SizeOfInitializedData',
        'SizeOfUninitializedData',
        'AddressOfEntryPoint',
        'BaseOfCode',
        'BaseOfData',
        'ImageBase',
        'SectionAlignment',
        'FileAlignment',
        'MajorOperatingSystemVersion',
        'MinorOperatingSystemVersion',
        'MajorImageVersion',
        'MinorImageVersion',
        'MajorSubsystemVersion',
        'MinorSubsystemVersion',
        'Win32VersionValue',
        'SizeOfImage',
        'SizeOfHeaders',
        'CheckSum',
        'Subsystem',
        'DllCharacteristics',
        'SizeOfStackReserve',
        'SizeOfStackCommit',
        'SizeOfHeapReserve',
        'SizeOfHeapCommit',
        'LoaderFlags',
        'NumberOfRvaAndSizes',
        )
    def __init__(self,data,offset=0):
        magic = data[offset:offset+2]
        if magic==b'\x0b\x01':
            logger.verbose('PE32 Magic found')
        elif magic==b'\x0b\x02':
            logger.verbose('PE32+ Magic found')
            l = list(self.fmt)
            l.pop(8)
            for x in (8,23,24,25,26):
                l[x] = 'Q'
            self.fmt = ''.join(l)
            k = list(self.keys)
            k.pop(8)
            self.keys = tuple(k)
        elif magic==b'\x07\x01':
            logger.info('ROM Magic found (unsupported)')
        else:
            logger.error('unknown Magic')
        self.name_formatter('Magic')
        self.address_formatter('AddressOfEntryPoint','BaseOfCode','BaseOfData','ImageBase')
        self.address_formatter('Checksum')
        self.flag_formatter('DllCharacteristics','LoaderFlags')
        # parse structure
        self.DataDirectories = {}
        PEcore.__init__(self,data,offset)
        l = offset+len(self)
        dnames = ('ExportTable','ImportTable','ResourceTable','ExceptionTable',
                  'CertificateTable','BaseRelocationTable','Debug','Architecture',
                  'GlobalPtr','TLSTable','LoadConfigTable','BoundImport','IAT',
                  'DelayImportDescriptor','CLRRuntimeHeader','Reserved')
        for dn in range(min(self.NumberOfRvaAndSizes,len(dnames))):
            d = DataDirectory(data,l)
            self.DataDirectories[dnames[dn]] = d
            l += len(d)

    def __len__(self):
        dirslen = sum(map(len,self.DataDirectories.values()))
        return struct.calcsize(self.fmt)+dirslen
##

IMAGE_DIRECTORY_ENTRY_EXPORT=0
IMAGE_DIRECTORY_ENTRY_IMPORT=1
IMAGE_DIRECTORY_ENTRY_RESOURCE=2
IMAGE_DIRECTORY_ENTRY_EXCEPTION=3
IMAGE_DIRECTORY_ENTRY_SECURITY=4
IMAGE_DIRECTORY_ENTRY_BASERELOC=5
IMAGE_DIRECTORY_ENTRY_DEBUG=6
IMAGE_DIRECTORY_ENTRY_COPYRIGHT=7
IMAGE_DIRECTORY_ENTRY_GLOBALPTR=8
IMAGE_DIRECTORY_ENTRY_TLS=9
IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG=10
IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT=11
IMAGE_DIRECTORY_ENTRY_IAT=12
IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT=13
IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR=14
IMAGE_DIRECTORY_ENTRY_RESERVED=15

class DataDirectory(PEcore):
    fmt = 'II'
    keys = ('RVA','Size')

# PE Sections
#------------------------------------------------------------------------------

with Consts('SectionHdrCharacteristics'):
    IMAGE_SCN_CNT_CODE=0x00000020
    IMAGE_SCN_CNT_INITIALIZED_DATA=0x00000040
    IMAGE_SCN_CNT_UNINITIALIZED_DATA=0x00000080
    IMAGE_SCN_LNK_OTHER=0x00000100
    IMAGE_SCN_LNK_INFO=0x00000200
    IMAGE_SCN_LNK_REMOVE=0x00000800
    IMAGE_SCN_LNK_COMDAT=0x00001000
    IMAGE_SCN_MEM_FARDATA=0x00008000
    IMAGE_SCN_MEM_PURGEABLE=0x00020000
    IMAGE_SCN_MEM_16BIT=0x00020000
    IMAGE_SCN_MEM_LOCKED=0x00040000
    IMAGE_SCN_MEM_PRELOAD=0x00080000
    IMAGE_SCN_ALIGN_1BYTES=0x00100000
    IMAGE_SCN_ALIGN_2BYTES=0x00200000
    IMAGE_SCN_ALIGN_4BYTES=0x00300000
    IMAGE_SCN_ALIGN_8BYTES=0x00400000
    IMAGE_SCN_ALIGN_16BYTES=0x00500000
    IMAGE_SCN_ALIGN_32BYTES=0x00600000
    IMAGE_SCN_ALIGN_64BYTES=0x00700000
    IMAGE_SCN_ALIGN_128BYTES=0x00800000
    IMAGE_SCN_ALIGN_256BYTES=0x00900000
    IMAGE_SCN_ALIGN_512BYTES=0x00A00000
    IMAGE_SCN_ALIGN_1024BYTES=0x00B00000
    IMAGE_SCN_ALIGN_2048BYTES=0x00C00000
    IMAGE_SCN_ALIGN_4096BYTES=0x00D00000
    IMAGE_SCN_ALIGN_8192BYTES=0x00E00000
    IMAGE_SCN_ALIGN_MASK=0x00F00000
    IMAGE_SCN_LNK_NRELOC_OVFL=0x01000000
    IMAGE_SCN_MEM_DISCARDABLE=0x02000000
    IMAGE_SCN_MEM_NOT_CACHED=0x04000000
    IMAGE_SCN_MEM_NOT_PAGED=0x08000000
    IMAGE_SCN_MEM_SHARED=0x10000000
    IMAGE_SCN_MEM_EXECUTE=0x20000000
    IMAGE_SCN_MEM_READ=0x40000000
    IMAGE_SCN_MEM_WRITE=0x80000000

class SectionHdr(PEcore):
    fmt = '8sIIIIIIHHI'
    keys = ('Name',
            'VirtualSize',
            'RVA',
            'SizeOfRawData',
            'PointerToRawData',
            'PointerToRelocations',
            'PointerToLineNumbers',
            'NumberOfRelocations',
            'NumberOfLineNumbers',
            'Characteristics')
    def __init__(self,data,offset=0):
        PEcore.__init__(self,data,offset)
        try:
            self.Name = self.Name.decode('utf-8').strip('\0')
        except UnicodeDecodeError:
            logger.info('SectionHdr: Name string decode error %s'%repr(self.Name))
        self.name_formatter('Name')
        self.address_formatter('RVA')
        self.flag_formatter('Characteristics')

    def group(self):
        return self.Name.partition('$')

# COFF Relocations
#------------------------------------------------------------------------------
class COFFRelocation(PEcore):
    fmt = 'IIH'
    keys = ('RVA',
            'SymbolTableIndex',
            'Type')

class COFFLineNumber(PEcore):
    fmt = 'IH'
    keys = ('Type',
            'LineNumber')

    @property
    def SymbolTableIndex(self):
        if self.LineNumber==0:
            return self.Type
        else:
            logger.warning('invalid COFF Line Number entry')

IMAGE_SYM_UNDEF=0
IMAGE_SYM_ABSOLUTE=-1
IMAGE_SYM_DEBUG=-2

# COFF Symbol table
#------------------------------------------------------------------------------

class COFFSymbolTable(object):
    def __init__(self,data=None):
        self.symbols = []
        if data is None: data=''
        if len(data)>0:
            self.build(data)

    def build(self,data):
        q,r = divmod(len(data),18)
        assert r==0
        while len(data)>0:
            self.symbols.append(StdSymbolRecord(data))
            data = data[len(self.symbols[-1]):]
        assert len(self.symbols)==q

    def __len__(self):
        return sum(map(len,self.symbols))

class StdSymbolRecord(PEcore):
    fmt = '8siHHBB'
    keys = ('_Name',
            'Value',
            'SectionNumber',
            'Type',
            'StorageClass',
            'NumberOfAuxSymbols')
    def __init__(self,data):
        PEcore.__init__(self,data)
        self.func_formatter(_Name=lambda k,x,cls: highlight([(Token.Name,self.Name)]))
        self.func_formatter(StorageClass=lambda k,x,cls: highlight([(Token.Name,self.classname())]))
        self.AuxSymbols = []
        data = data[len(self):]
        if self.Type>>8==0x20 and self.StorageClass==2 and self.SectionNumber>IMAGE_SYM_UNDEF:
            auxclass = AuxFunctionDefinition
        elif self.StorageClass==101 and (self.Name=='.bf' or self.Name=='.ef'):
            auxclass = Aux_bf_ef
        elif self.StorageClass==2 and self.SectionNumber==IMAGE_SYM_UNDEF and Self.Value==0:
            auxclass = AuxWeakExternal
        elif self.StorageClass==103:
            assert self.Name == '.file'
            auxclass = AuxFile
        elif self.StorageClass==3:
            auxclass = AuxSectionDefinition
        else:
            auxclass = AuxSymbolRecord
        for x in range(self.NumberOfAuxSymbols):
            self.AuxSymbols.append(auxclass(data))
            data = data[len(self):]

    def __len__(self):
        return sum(map(len,self.AuxSymbols),struct.calcsize(self.fmt))

    @property
    def Name(self):
        if self._Name.startswith('\0'*4):
            index = struct.unpack('I',self._Name[4:8])[0]
            return index
        else:
            try:
                return self._Name.decode('utf-8').strip('\0')
            except UnicodeDecodeError:
                logger.info('StdSymbolHdr: Name decode error %s'%repr(self._Name))
                return self._Name

    def typename(self):
        try:
            t1 = ['NULL'  , 'VOID' , 'CHAR' , 'SHORT' ,
                  'INT'   , 'LONG' , 'FLOAT', 'DOUBLE',
                  'STRUCT', 'UNION', 'ENUM' , 'MOE'   ,
                  'BYTE'  , 'WORD' , 'UINT' , 'DWORD' ][self.Type&0xff]
            t2 = ['NULL','POINTER','FUNC','ARRAY'][self.Type>>8]
            return (t1,t2)
        except IndexError:
            logger.warning('invalid Type field (was: %d)'%self.Type)

    def classname(self):
        c = {0xff: 'END_OF_FUNCTION',
             0   : 'NULL',
             1   : 'AUTOMATIC',
             2   : 'EXTERNAL',
             3   : 'STATIC',
             4   : 'REGISTER',
             5   : 'EXTERNAL_DEF',
             6   : 'LABEL',
             6   : 'UNDEFINED_LABEL',
             8   : 'MEMBER_OF_STRUCT',
             9   : 'ARGUMENT',
             10  : 'STRUCT_TAG',
             11  : 'MEMBER_OF_UNION',
             12  : 'UNION_TAG',
             13  : 'TYPE_DEF',
             14  : 'UNDEFINED_STATIC',
             15  : 'ENUM_TAG',
             16  : 'MEMBER_OF_ENUM',
             17  : 'REGISTER_PARAM',
             18  : 'BITFIELD',
             100 : 'BLOCK',
             101 : 'FUNCTION',
             102 : 'END_OF_STRUCT',
             103 : 'FILE',
             104 : 'SECTION',
             105 : 'WEAK_EXTERNAL',
             107 : 'CLR_TOKEN' }.get(self.StorageClass,None)
        return c

class AuxSymbolRecord(PEcore):
    fmt = '18s'
    keys = ('data')
    def __init__(self,data):
        self.set(data[:len(self)])

class AuxFunctionDefinition(AuxSymbolRecord):
    fmt = 'IIII2x'
    keys = ('TagIndex','TotalSize',
            'PointerToLineNumber','PointerToNextFunction')

class Aux_bf_ef(AuxSymbolRecord):
    fmt = '4xH6xI2x'
    keys = ('LineNumber', 'PointerToNextFunction')

class AuxWeakExternal(AuxSymbolRecord):
    fmt = 'II10x'
    keys = ('TagIndex', 'Characteristics')

class AuxFile(AuxSymbolRecord):
    fmt = '18s'
    keys = ('Filename')

class AuxSectionDefinition(AuxSymbolRecord):
    fmt = 'IHHIHB3x'
    keys = ('Length',
            'NumberOfRelocations',
            'NumberOfLineNumbers',
            'CheckSum',
            'Number',
            'Selection')

# COFF String table
#------------------------------------------------------------------------------
class COFFStringTable(object):
    def __init__(self,data=None):
        if data is None: data=struct.pack('I',4)
        self.length = struct.unpack('I',data[:4])
        self.strings = data[4:self.length].split('\0')
        self.strings.pop()

#------------------------------------------------------------------------------
class AttributeCertificateTable(object):
    NotImplementedError

class AttributeCertificate(PEcore):
    fmt = ''
    keys = tuple()

#------------------------------------------------------------------------------
class DelayLoadImportTable(object):
    def __init__(self,data):
        raise NotImplementedError

class DelayLoadDirectoryTable(PEcore):
    fmt = 'IIIIIIII'
    keys = ('Attributes',
            'Name',
            'ModuleHandle',
            'DelayImportAddressTable',
            'DelayImportNameTable',
            'BoundDelayImportTable',
            'UnloadDelayImportTable',
            'TimeStamp')

#------------------------------------------------------------------------------
class ExportTable(PEcore):
    fmt = 'IIHHIIIIIII'
    keys = ('Flags',
            'TimeStamp',
            'MajorVersion',
            'MinorVersion',
            'NameRVA'
            'OrdinalBase',
            'AddressTableEntries',
            'NumberOfNamePointers',
            'ExportAddressTableRVA',
            'NamePointerRVA',
            'OrdinalTableRVA')

#------------------------------------------------------------------------------
class ImportTable(object):
    def __init__(self,data):
        self.dlls = []
        e = None
        while len(data)>0:
            e = ImportTableEntry(data)
            if e.isNULL(): return
            self.dlls.append(e)
            data = data[len(e):]
        logger.warning('NULL Import entry not found')

class ImportTableEntry(PEcore):
    fmt = 'IIIII'
    keys = ('ImportLookupTableRVA',
            'TimeStamp',
            'ForwarderChain',
            'NameRVA',
            'ImportAddressTableRVA')
    def isNULL(self):
        res=0
        for k in self.keys:
            res = res | getattr(self,k)
        return res==0

class ImportLookupTable(object):
    def __init__(self,data,magic):
        size = {0x20b:64, 0x10b:32}[magic]
        self.elsize = size//8
        self.fmt = 'Q' if size==64 else 'I'
        self.readimports(data)

    def readimports(self,data):
        self.imports = []
        fshift = (self.elsize*8)-1
        while len(data)>=self.elsize:
            v = struct.unpack(self.fmt,data[:self.elsize])[0]
            if v==0: return
            flag = v>>fshift
            if   flag==1: self.imports.append([flag,v&0xffff])
            elif flag==0: self.imports.append([flag,v&0x7fffffff])
            data = data[self.elsize:]

class NameTableEntry(object):
    def __init__(self,data):
        hint = struct.unpack('H',data[:2])
        s,_,_ = data[2:].partition(b'\0')
        self.hint = hint
        self.symbol = str(s.decode())

#------------------------------------------------------------------------------
class TLSTable(PEcore):
    fmt = 'IIIIII'
    keys = ('RawDataStartVA',
            'RawDataEndVA',
            'AddressOfIndex',
            'AddressOfCallbacks',
            'SizeOfZeroFill',
            'Characteristics')
    def __init__(self,data,magic):
        size = {0x20b:64, 0x10b:32}[magic]
        self.elsize = size//8
        if magic==0x20b:
            self.fmt='Q'*len(self.keys)
        PEcore.__init__(self,data)

    def readcallbacks(self,data):
        self.callbacks = []
        while len(data)>=self.elsize:
            v = struct.unpack(self.fmt[0],data[:self.elsize])[0]
            if v==0: return
            self.callbacks.append(v)
            data = data[self.elsize:]
#------------------------------------------------------------------------------

class PE(PEcore):

    basemap   = None
    symtab    = None
    strtab    = None
    reltab    = None
    functions = None
    variables = None

    @property
    def entrypoints(self):
        l = [ self.Opt.AddressOfEntryPoint + self.basemap ]
        if self.tls:
            l.extend(list(set(self.tls.callbacks)))
        return l

    @property
    def filename(self):
        return self.data.name

    def __init__(self,filename):
        try:
            f = open(filename,'rb')
        except (TypeError,IOError):
            f = bytes(filename)
        data = DataIO(f)
        self.data = data
        # parse DOS header:
        self.DOS  = DOSHdr(data)
        # parse PE header:
        self.NT = COFFHdr(data,self.DOS.e_lfanew)
        # parse Optional Header:
        self.Opt  = OptionalHdr(data,self.DOS.e_lfanew+len(self.NT))
        self.basemap = self.Opt.ImageBase
        if self.NT.SizeOfOptionalHeader != len(self.Opt):
            logger.warning('Optional header size mismatch')
        # read Sections:
        self.sections = []
        offset = self.DOS.e_lfanew + len(self.NT) + self.NT.SizeOfOptionalHeader
        for i in range(self.NT.NumberOfSections):
            s = SectionHdr(data,offset)
            self.sections.append(s)
            offset += len(s)
        self.functions = self.__functions()
        self.variables = self.__variables()
        self.tls       = self.__tls()
    ##

    #  allows to retreive section that holds target address (rva or absolute)
    def locate(self,addr,absolute=False):
        if absolute: addr = addr-self.basemap
        # now we have addr so we can see in which section/segment it is...
        # sections are smaller than segments so we try first with Shdr
        # but this may lead to errors because what really matters are segments
        # loaded by the kernel binfmt_elf.c loader.
        for s in self.sections:
            if s.Characteristics==IMAGE_SCN_LNK_REMOVE: continue
            if s.RVA <= addr < s.RVA+s.VirtualSize:
                return s,addr-s.RVA
        if 0<= addr < self.Opt.SizeOfImage:
            return 0,addr
        logger.info('address not found (was %08x)'%addr)
        return None,0

    def getdata(self,addr,absolute=False):
        s,offset = self.locate(addr,absolute)
        if s is None:
            logger.error('address not mapped')
            raise ValueError
        return self.loadsegment(s,raw=True)[offset:]

    def loadsegment(self,S,pagesize=0,raw=False):
        if S and not S.Characteristics==IMAGE_SCN_LNK_REMOVE:
            addr = self.basemap+S.RVA
            if addr%self.Opt.SectionAlignment:
                logger.warning('bad alignment for section %s'%S.Name)
            sta = S.PointerToRawData
            if sta%self.Opt.FileAlignment:
                logger.warning('bad file alignment for section %s'%S.Name)
            sto = sta+S.SizeOfRawData
            bytes = self.data[sta:sto].ljust(S.VirtualSize)
            if pagesize:
                # note: bytes are not truncated, only extended if needed...
                bytes = bytes.ljust(pagesize,b'\x00')
            if raw: return bytes
            else  : return {addr: bytes}
        elif S==0:
            bytes = self.data[0:self.Opt.SizeOfHeaders]
            if raw: return bytes
            else  : return {self.basemap: bytes}
        return None

    def __functions(self):
        D = {}
        imports = self.Opt.DataDirectories.get('ImportTable',None)
        if imports is not None:
            data = b''
            while len(data)<imports.Size:
                try:
                    nextdata = self.getdata(imports.RVA+len(data))
                    if len(nextdata)==0: break
                    data += nextdata
                except ValueError:
                    return D
            if len(data)<imports.Size:
                logger.warning('ImportTable length mismatch')
            data = data[:imports.Size]
            self.ImportTable = ImportTable(data)
            for e in self.ImportTable.dlls:
                try:
                    dllname = self.getdata(e.NameRVA)
                    e.Name = str(dllname.partition(b'\0')[0].decode())
                except:
                    logger.warning('invalid dll name RVA in ImportTable')
                try:
                    if e.ImportLookupTableRVA != 0:
                        data = self.getdata(e.ImportLookupTableRVA)
                    else:
                        data = self.getdata(e.ImportAddressTableRVA)
                except ValueError:
                    logger.warning('invalid ImportLookupTable RVA')
                else:
                    e.ImportLookupTable = ImportLookupTable(data,self.Opt.Magic)
                    e.ImportAddressTable = []
                    vaddr = e.ImportAddressTableRVA + self.basemap
                    for x in e.ImportLookupTable.imports:
                        if x[0]==0:
                            ref = NameTableEntry(self.getdata(x[1]))
                        else:
                            ref = '#%s'%str(x[1]) #ordinal case
                        e.ImportAddressTable.append((vaddr,ref))
                        vaddr += e.ImportLookupTable.elsize
                    D.update(e.ImportAddressTable)
                    for vaddr,ref in e.ImportAddressTable:
                        if isinstance(ref,str): symbol=ref
                        else: symbol = ref.symbol
                        D[vaddr] = "%s::%s"%(e.Name,symbol)
        return D

    def __tls(self):
        tls = self.Opt.DataDirectories.get('TLSTable',None)
        if tls is not None and tls.RVA != 0:
            try:
                data = self.getdata(tls.RVA)
            except ValueError:
                logger.warning('invalid TLS RVA')
            else:
                tls = TLSTable(data,self.Opt.Magic)
                try:
                    cbtable = self.getdata(tls.AddressOfCallbacks,absolute=True)
                except ValueError:
                    tls.callbacks = []
                else:
                    tls.readcallbacks(cbtable)
                return tls
        return None

    def __variables(self):
        D = {}
        return D

    def __str__(self):
        ss = ['DOS header:']
        tmp = self.DOS.pfx
        self.DOS.pfx = '\t'
        ss.append(str(self.DOS))
        self.DOS.pfx = tmp
        ss += ['\nPE header:']
        tmp = self.NT.pfx
        self.NT.pfx = '\t'
        ss.append(str(self.NT))
        self.NT.pfx = tmp
        ss += ['\nOptional header:']
        tmp = self.Opt.pfx
        self.Opt.pfx = '\t'
        ss.append(str(self.Opt))
        self.Opt.pfx = tmp
        ss += ['\nSections:']
        for s in self.sections:
            tmp = s.pfx
            s.pfx = '\t'
            ss.append(str(s)); ss.append('---')
            s.pfx = tmp
        return '\n'.join(ss)
## End of class PE

