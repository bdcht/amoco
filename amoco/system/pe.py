# -*- coding: utf-8 -*-

# This code is part of Amoco
# based on elf.py, improving pefile to work out corkami's CoST.exe.
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
system/pe.py
============

The system pe module implements the PE class which support both 32 and 64 bits
executable formats.
"""

from amoco.logger import *
logger = Log(__name__)
logger.debug('loading module')

# our exception handler:
class PEError(Exception):
    def __init__(self,message):
        self.message = message
    def __str__(self):
        return str(self.message)

#------------------------------------------------------------------------------
from amoco.system.core import BinFormat,DataIO

class PE(BinFormat):
    is_PE = True
    @property
    def entrypoints(self):
        l = [ self.Opt.AddressOfEntryPoint + self.basemap ]
        if self.tls:
            l.extend(list(set(self.tls.callbacks)))
        return l

    @property
    def filename(self):
        return self.data.name

    def __init__(self,data):
        self.data = data
        # parse DOS header:
        try:
            self.DOS  = DOSHdr(data)
        except:
            raise PEError('not a DOSHdr')
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

    def getfileoffset(self,addr):
        s,offset = self.locate(addr,absolute=True)
        return s.PointerToRawData+offset

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

class PEBuilder(PE):
    def __init__(self):
        self.data = DataIO(b'')

#------------------------------------------------------------------------------
from amoco.system.structs import *

@StructDefine("""
c*2 : e_magic
x*58: unused
I   : e_lfanew
""")
class DOSHdr(StructFormatter):
    def __init__(self,data=None):
        if data:
            self.unpack(data)
        if self.e_magic!=b'MZ':
            raise PEError('no DOS Header found')

IMAGE_NUMBEROF_DIRECTORY_ENTRIES=16
IMAGE_ORDINAL_FLAG=0x80000000
IMAGE_ORDINAL_FLAG64=0x8000000000000000

@StructDefine("""
I : Signature
H : Machine
H : NumberOfSections
I : TimeDateStamp
I : PointerToSymbolTable
I : NumberOfSymbols
H : SizeOfOptionalHeader
H : Characteristics
""")
class COFFHdr(StructFormatter):
    def __init__(self,data=None,offset=0):
        self.name_formatter('Signature','Machine')
        self.flag_formatter('Characteristics')
        self.func_formatter(TimeDateStamp = token_datetime_fmt)
        if data:
            self.unpack(data,offset)
        if self.Signature != IMAGE_NT_SIGNATURE:
            raise PEError('no PE header found')

with Consts('Signature'):
    IMAGE_DOS_SIGNATURE=0x5A4D
    IMAGE_OS2_SIGNATURE=0x454E
    IMAGE_OS2_SIGNATURE_LE=0x454C
    IMAGE_VXD_SIGNATURE=0x454C
    IMAGE_NT_SIGNATURE=0x00004550

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

with Consts('COFFHdr.Characteristics'):
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

@StructDefine("""
H : Magic
B : MajorLinkerVersion
B : MinorLinkerVersion
I : SizeOfCode
I : SizeOfInitializedData
I : SizeOfUninitializedData
I : AddressOfEntryPoint
I : BaseOfCode
I : BaseOfData
I : ImageBase
I : SectionAlignment
I : FileAlignment
H : MajorOperatingSystemVersion
H : MinorOperatingSystemVersion
H : MajorImageVersion
H : MinorImageVersion
H : MajorSubsystemVersion
H : MinorSubsystemVersion
I : Win32VersionValue
I : SizeOfImage
I : SizeOfHeaders
I : CheckSum
H : Subsystem
H : DllCharacteristics
I : SizeOfStackReserve
I : SizeOfStackCommit
I : SizeOfHeapReserve
I : SizeOfHeapCommit
I : LoaderFlags
I : NumberOfRvaAndSizes
""")
class OptionalHdr(StructFormatter):
    def __init__(self,data=None,offset=0):
        self.name_formatter('Magic')
        self.address_formatter('AddressOfEntryPoint','BaseOfCode','BaseOfData','ImageBase')
        self.address_formatter('Checksum')
        self.flag_formatter('DllCharacteristics','LoaderFlags')
        if data:
            self.unpack(data,offset)
    def unpack(self,data,offset=0):
        magic = data[offset:offset+2]
        if magic==b'\x0b\x01':
            logger.verbose('PE32 Magic found')
        elif magic==b'\x0b\x02':
            logger.verbose('PE32+ Magic found')
            f = self.fields
            f.pop(8)
            for x in (8,23,24,25,26):
                f[x].typename = 'Q'
        elif magic==b'\x07\x01':
            logger.info('ROM Magic found (unsupported)')
        else:
            logger.error('unknown Magic')
        # parse structure
        self.DataDirectories = {}
        StructFormatter.unpack(self,data,offset)
        l = offset+len(self)
        dnames = ('ExportTable','ImportTable','ResourceTable','ExceptionTable',
                  'CertificateTable','BaseRelocationTable','Debug','Architecture',
                  'GlobalPtr','TLSTable','LoadConfigTable','BoundImport','IAT',
                  'DelayImportDescriptor','CLRRuntimeHeader','Reserved')
        for dn in range(min(self.NumberOfRvaAndSizes,len(dnames))):
            d = DataDirectory(data,offset=l)
            self.DataDirectories[dnames[dn]] = d
            l += len(d)

    def __len__(self):
        baselen = StructFormatter.__len__(self)
        dirslen = sum(map(len,self.DataDirectories.values()))
        return baselen+dirslen

with Consts('Magic'):
    OPTIONAL_HEADER_MAGIC_PE=0x10b
    OPTIONAL_HEADER_MAGIC_PE_PLUS=0x20b

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

@StructDefine("""
I : RVA
I : Size
""")
class DataDirectory(StructFormatter):
    def __init__(self,data=None,offset=0):
        self.address_formatter('RVA')
        if data:
            self.unpack(data,offset)

#------------------------------------------------------------------------------
# PE Sections

@StructDefine("""
s*8 : Name
I   : VirtualSize
I   : RVA
I   : SizeOfRawData
I   : PointerToRawData
I   : PointerToRelocations
I   : PointerToLineNumbers
H   : NumberOfRelocations
H   : NumberOfLineNumbers
I   : Characteristics
""")
class SectionHdr(StructFormatter):
    def __init__(self,data=None,offset=0):
        self.name_formatter('Name')
        self.address_formatter('RVA')
        self.address_formatter('PointerToRawData')
        self.flag_formatter('Characteristics')
        if data:
            self.unpack(data,offset)
    def group(self):
        return self.Name.partition('$')

with Consts('SectionHdr.Characteristics'):
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

# COFF Relocations
#------------------------------------------------------------------------------
@StructDefine("""
I : RVA
I : SymboleTableIndex
H : Type
""")
class COFFRelocation(StructFormatter):
    def __init__(self,data=None,offset=0):
        self.address_formatter('RVA')
        if data:
            self.unpack(data,offset)

@StructDefine("""
I : Type
H : LineNumber
""")
class COFFLineNumber(StructFormatter):
    def __init__(self,data=None,offset=0):
        if data:
            self.unpack(data,offset)
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

@StructDefine("""
s*8 : _Name
i   : Value
H   : SectionNumber
H   : Type
B   : StorageClass
B   : NumberOfAuxSymbols
""")
class StdSymbolRecord(StructFormatter):
    def __init__(self,data=None,offset=0):
        self.func_formatter(_Name=lambda k,x,cls: highlight([(Token.Name,self.Name)]))
        self.func_formatter(StorageClass=lambda k,x,cls: highlight([(Token.Name,self.classname())]))
        self.AuxSymbols = []
        if data:
            self.unpack(data,offset)
            offset += len(self)
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
                s = auxclass(data,offset)
                self.AuxSymbols.append(s)
                offset += len(s)

    def __len__(self):
        baselen = StructFormatter.__len__(self)
        auxtlen = sum([len(s) for s in self.AuxSymbols],0)
        return baselen + auxtlen

    @property
    def Name(self):
        if self._Name.startswith('\0'*4):
            index = struct.unpack('I',self._Name[4:8])[0]
            return index.strip('\0')
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
             7   : 'UNDEFINED_LABEL',
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

@StructDefine("""
s*18 : data
""")
class AuxSymbolRecord(StructFormatter):
    def __init__(self,data=None,offset=0):
        if data:
            self.unpack(data,offset)

@StructDefine("""
I  : TagIndex
I  : TotalSize
I  : PointerToLineNumber
I  : PointerToNextFunction
x*2: unused
""")
class AuxFunctionDefinition(StructFormatter):
    def __init__(self,data=None,offset=0):
        if data:
            self.unpack(data,offset)

@StructDefine("""
x*4: unused
H*6: LineNumber
x  : unused
I  : PointerToNextFunction
x*2: unused
""")
class Aux_bf_ef(StructFormatter):
    def __init__(self,data=None,offset=0):
        if data:
            self.unpack(data,offset)

@StructDefine("""
I   : TagIndex
I   : Characteristics
x*10: unused
""")
class AuxWeakExternal(StructFormatter):
    def __init__(self,data=None,offset=0):
        if data:
            self.unpack(data,offset)

@StructDefine("""
s*18 : Filename
""")
class AuxFile(StructFormatter):
    def __init__(self,data=None,offset=0):
        if data:
            self.unpack(data,offset)

@StructDefine("""
I   : length
H   : NumberOfRelocations
H   : NumberOfLineNumbers
I   : Checksum
H   : Number
B   : Selection
x*3 : unused
""")
class AuxSectionDefinition(StructFormatter):
    def __init__(self,data=None,offset=0):
        if data:
            self.unpack(data,offset)


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

class AttributeCertificate(StructFormatter):
    pass

#------------------------------------------------------------------------------

class DelayLoadImportTable(object):
    def __init__(self,data):
        raise NotImplementedError

@StructDefine("""
I : Attributes
I : Name
I : ModuleHandle
I : DelayImportAddressTable
I : DelayImportNameTable
I : BoundDelayImportTable
I : UnloadDelayImportTable
I : TimeStamp
""")
class DelayLoadDirectoryTable(StructFormatter):
    def __init__(self,data=None,offset=0):
        self.func_formatter(TimeStamp = token_datetime_fmt)
        if data:
            self.unpack(data,offset)

#------------------------------------------------------------------------------

@StructDefine("""
I : Flags
I : TimeStamp
H : MajorVersion
H : MinorVersion
I : NameRVA
I : OrdinalBase
I : AddressTableEntries
I : NumberOfNamePointers
I : ExportAddressTableRVA
I : NamePointerRVA
I : OrdinalTableRVA
""")
class ExportTable(StructFormatter):
    def __init__(self,data=None,offset=0):
        self.func_formatter(TimeStamp = token_datetime_fmt)
        self.address_formatter('OrdinalBase','NameRVA')
        self.address_formatter('ExportAddressTableRVA','NamePointerRVA')
        self.address_formatter('OrdinalTableRVA')
        if data:
            self.unpack(data,offset)

#------------------------------------------------------------------------------
class ImportTable(object):
    def __init__(self,data,offset=0):
        self.dlls = []
        e = None
        while len(data)>0:
            e = ImportTableEntry(data,offset)
            if e.isNULL(): return
            self.dlls.append(e)
            offset += len(e)
        logger.warning('NULL Import entry not found')

@StructDefine("""
I : ImportLookupTableRVA
I : TimeStamp
I : ForwarderChain
I : NameRVA
I : ImportAddressTableRVA
""")
class ImportTableEntry(StructFormatter):
    def __init__(self,data=None,offset=0):
        self.address_formatter('ImportLookupTableRVA','NameRVA')
        self.address_formatter('ImportAddressTableRVA')
        self.func_formatter(TimeStamp = token_datetime_fmt)
        if data:
            self.unpack(data,offset)
    def isNULL(self):
        res=0
        for k in self.fields:
            res = res | getattr(self,k.name)
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
@StructDefine("""
I : RawDataStartVA
I : RawDataEndVA
I : AddressOfIndex
I : AddressOfCallbacks
I : SizeOfZeroFill
I : Characteristics
""")
class TLSTable(StructFormatter):
    def __init__(self,data,magic):
        self.address_formatter('RawDataStartVA','RawDataEndVA')
        size = {0x20b:64, 0x10b:32}[magic]
        self.elsize = size//8
        if magic==0x20b:
            for f in self.fields: f.typename='Q'
        if data:
            self.unpack(data)

    def readcallbacks(self,data):
        self.callbacks = []
        while len(data)>=self.elsize:
            v = struct.unpack(self.fields[0].typename,data[:self.elsize])[0]
            if v==0: return
            self.callbacks.append(v)
            data = data[self.elsize:]
#------------------------------------------------------------------------------

