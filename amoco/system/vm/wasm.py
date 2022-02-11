# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2021 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
system/wasm.py
==============

The system wasm module implements both the Wasm class binary format
and a Wasm virtual machine.
"""
from amoco.system.structs import Consts, StructDefine
from amoco.system.structs import StructFormatter, StructCore
from amoco.system.structs import Field, VarField, RawField, Leb128Field
from amoco.system.utils import read_leb128, write_uleb128

from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")

class WasmError(Exception):
    """
    WasmError is raised whenever Wasm object instance fails
    to decode required structures.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return str(self.message)


# ------------------------------------------------------------------------------


class Wasm(object):
    """
    This class takes a DataIO object (ie an opened file of BytesIO instance)
    and decodes all Wasm structures found in it.
    """
    def __init__(self,f):
        from amoco.arch.wasm import cpu
        self.__file = f
        self.cpu = cpu

    @property
    def filename(self):
        return self.__file.name

    @property
    def dataio(self):
        return self.__file

    def __init__(self, f):
        self.__file = f
        self.module = Module(f)


# ------------------------------------------------------------------------------


class VectorField(Field):

    def __init__(self, fmt):
        f0 = StructDefine(fmt,packed=True).fields[0]
        self.__type = f0.type or f0
        self.typename = f0.typename
        self.count = 0
        self.order = f0.order
        self._align_value = f0.align_value
        self.comment = f0.comment
        self.name = f0.name
        self._sz = 0
        self.instance = None

    @property
    def type(self):
        return self.__type

    def size(self, psize=0):
        return self._sz

    @property
    def source(self):
        cnt = self.count if self.count>0 else '#'
        return "vector(%s)[%s]: %s; %s"%(self.typename,cnt,self.name,self.comment)

    def unpack(self, data, offset=0, psize=0):
        "returns a vector of count element(s) of its self.type"
        n,sz = read_leb128(data,1,offset)
        offset += sz
        vec = []
        for _ in range(n):
            e = self.type()
            blob = e.unpack(data, offset)
            vec.append(blob)
            if isinstance(blob,StructCore):
                l = len(blob)
            else:
                l = e.size()
            sz += l
            offset += l
        self.count = n
        self._sz = sz
        return vec

    def get(self, data, offset=0):
        return (self.name, self.unpack(data, offset))

    def pack(self, value):
        assert self.count == len(value)
        vec = b"".join([self.type().pack(v) for v in value])
        res = write_uleb128(self.count)+vec
        assert self._sz == len(res)
        return res


# ------------------------------------------------------------------------------


@StructDefine(
"""
c*4  : magic
I    : version
""", packed=True,
)
class Module(StructFormatter):
    def __init__(self, data=None, offset=0):
        if data:
            self.unpack(data,offset)

    def unpack(self, data, offset=0, psize=0):
        super().unpack(data, offset)
        if self.magic != b"\0asm":
            raise WasmError("Wrong magic number, not a binary Wasm file ?")
        self.sections = []
        offset += len(self)
        end = data.size()
        while offset<(end-1):
            _id = ord(data[offset:offset+1])
            try:
                s = SectionID[_id](data,offset)
                offset += len(s)
                self.sections.append(s)
            except KeyError:
                logger.warning("Wrong section id, aborting...")
                break
            except WasmError:
                logger.warning("malformed section with id %d"%_id)
                break
        return self

    def size(self):
        l = super().size()
        for s in self.sections:
            l += len(s)
        return l

    def __str__(self):
        ss = []
        ss.append(super().__str__())
        ss += ["\nSections:"]
        for s in self.sections:
            tmp = s.pfx
            s.pfx = "\t"
            ss.append(s.__str__())
            ss.append("---")
            s.pfx = tmp
        return "\n".join(ss)

# ------------------------------------------------------------------------------

with Consts('Section.id'):
    Custom = 0
    Type = 1
    Function = 2
    Table = 3
    Memory = 4
    Global = 5
    Export = 6
    Start = 7
    Element = 8
    Code = 9
    Data = 10
    DataCount = 11


# ------------------------------------------------------------------------------


@StructDefine(
"""
B         : id
I*%leb128 : size
s*.size   : content
""", packed=True,
)
class CustomSection(StructFormatter):
    alt = "Section"

    def __init__(self, data=None, offset=0):
        self.name_formatter("id")
        if data:
            self.unpack(data,offset)


# ------------------------------------------------------------------------------


@StructDefine(
"""
B         : id
I*%leb128 : size
s*.size   : content
""", packed=True,
)
class TypeSection(StructFormatter):
    alt = "Section"

    def __init__(self, data=None, offset=0):
        self.name_formatter("id")
        if data:
            self.unpack(data,offset)

    def unpack(self,data,offset=0,psize=0):
        super().unpack(data,offset)
        ft = VectorField("FunctionType : ft")
        self.update(ft.get(self.content))
        return self

@StructDefine(
"""
B         : d
I*%leb128 : n1
B*.n1     : rt1
I*%leb128 : n2
B*.n2     : rt2
""", packed=True,
)
class FunctionType(StructFormatter):
    alt = "Section"

    @staticmethod
    def wat_formatter(k, x, cls=None, fmt=None):
        L = [(Token.Literal,'(')]
        for v in x:
            if v in valtype:
                L.append((Token.Register, str(cpu.valtype[v])))
            else:
                L.append((Token.Constant, hex(x)))
            L.append((Token.Literal,', '))
        L.pop()
        L.append((Token.Literal,')'))
        return highlight(L,fmt)

    def __init__(self, data=None, offset=0):
        self.func_formatter(rt1=self.wat_formatter,
                            rt2=self.wat_formatter,)
        if data:
            self.unpack(data,offset)


# ------------------------------------------------------------------------------


@StructDefine(
"""
B         : id
I*%leb128 : size
s*.size   : content
""", packed=True,
)
class ImportSection(StructFormatter):
    alt = "Section"

    def __init__(self, data=None,offset=0):
        self.name_formatter("id")
        if data:
            self.unpack(data,offset)

    def unpack(self,data,offset=0,psize=0):
        super().unpack(data,offset)
        im = VectorField("Import : im")
        self.update(im.get(self.content))
        return self


with Consts("Import.d"):
    typeidx = 0
    tabletype = 1
    memtype = 2
    globaltype = 3

@StructDefine(
"""
I*%leb128 : n1
s*.n1     : mod
I*%leb128 : n2
s*.n2     : nm
B         : d
""", packed=True,
)
class Import(StructFormatter):
    def __init__(self, data=None,offset=0):
        self.name_formatter("d")
        if data:
            self.unpack(data,offset)

    def unpack(self,data,offset=0,psize=0):
        from codecs import decode
        super().unpack(data,offset)
        self.mod = decode(self.mod,"UTF-8")
        self.nm = decode(self.nm,"UTF-8")
        offset += len(self)
        if self.d==0x00:
            f = Leb128Field("I",fname="x")
            f.instance = self
            self.fields.append(f)
            self.update(f.get(data,offset))
        if self.d==0x01:
            f = Field(TableType,fname="tt")
            f.instance = self
            self.fields.append(f)
            self.update(f.get(data,offset))
        if self.d==0x02:
            f = Field(MemType,fname="mt")
            f.instance = self
            self.fields.append(f)
            self.update(f.get(data,offset))
        if self.d==0x03:
            f = Field(GlobalType,fname="gt")
            f.instance = self
            self.fields.append(f)
            self.update(f.get(data,offset))
        return self

# ------------------------------------------------------------------------------


@StructDefine(
"""
B         : id
I*%leb128 : size
s*.size   : content
""", packed=True,
)
class FunctionSection(StructFormatter):
    alt = "Section"

    def __init__(self, data=None, offset=0):
        self.name_formatter("id")
        if data:
            self.unpack(data,offset)

    def unpack(self,data,offset=0,psize=0):
        super().unpack(data,offset)
        x = VectorField("I*%leb128 : x")
        self.update(x.get(self.content))
        return self


# ------------------------------------------------------------------------------


@StructDefine(
"""
B         : id
I*%leb128 : size
s*.size   : content
""", packed=True,
)
class TableSection(StructFormatter):
    alt = "Section"

    def __init__(self, data=None, offset=0):
        self.name_formatter("id")
        if data:
            self.unpack(data,offset)

    def unpack(self,data,offset=0,psize=0):
        super().unpack(data,offset)
        tt = VectorField("TableType : tt")
        self.update(tt.get(self.content))
        return self


@StructDefine(
"""
B         : et
B         : flags
I*%leb128 : n
""", packed=True,
)
class TableType(StructFormatter):
    def __init__(self, data=None, offset=0):
        self.flag_formatter("flags")
        if data:
            self.unpack(data,offset)

    def unpack(self,data,offset=0,psize=0):
        if len(self.fields)==4:
            self.fields.pop()
        super().unpack(data,offset)
        offset += len(self)
        if self.flags&1:
            self.has_max = True
            f = Leb128Field("I",fname="m")
            f.instance = self
            self.fields.append(f)
            self.update(f.get(data,offset))
        if self.flags&2:
            self.is_shared = True
        else:
            self.is_shared = False
        if self.flags&4:
            self.is_64 = True
        else:
            self.is_64 = False
        return self

# ------------------------------------------------------------------------------


@StructDefine(
"""
B         : id
I*%leb128 : size
s*.size   : content
""", packed=True,
)
class MemorySection(StructFormatter):
    alt = "Section"

    def __init__(self, data=None, offset=0):
        self.name_formatter("id")
        if data:
            self.unpack(data,offset)

    def unpack(self,data,offset=0,psize=0):
        super().unpack(data,offset)
        mem = VectorField("MemType : mem")
        self.update(mem.get(self.content))
        return self

with Consts("flags"):
    has_max = 0x01
    is_shared = 0x02
    is_64 = 0x04

@StructDefine(
"""
B         : flags
I*%leb128 : n
""", packed=True,
)
class MemType(StructFormatter):
    def __init__(self, data=None, offset=0):
        self.flag_formatter("flags")
        if data:
            self.unpack(data,offset)

    def unpack(self,data,offset=0,psize=0):
        if len(self.fields)==3:
            self.fields.pop()
        super().unpack(data,offset)
        offset += len(self)
        if self.flags&1:
            self.has_max = True
            f = Leb128Field("I",fname="m")
            f.instance = self
            self.fields.append(f)
            self.update(f.get(data,offset))
        if self.flags&2:
            self.is_shared = True
        else:
            self.is_shared = False
        if self.flags&4:
            self.is_64 = True
        else:
            self.is_64 = False
        return self


# ------------------------------------------------------------------------------


@StructDefine(
"""
B         : id
I*%leb128 : size
s*.size   : content
""", packed=True,
)
class GlobalSection(StructFormatter):
    alt = "Section"

    def __init__(self, data=None, offset=0):
        self.name_formatter("id")
        if data:
            self.unpack(data, offset)

    def unpack(self,data,offset=0,psize=0):
        super().unpack(data,offset)
        glob = VectorField("GlobalType : glob")
        self.update(glob.get(self.content))
        return self


with Consts("GlobalType.mut"):
    const = 0
    var = 1

@StructDefine(
"""
B : t
B : mut
""", packed=True,
)
class GlobalType(StructFormatter):
    def __init__(self, data=None, offset=0):
        self.name_formatter("mut")
        if data:
            self.unpack(data, offset)


# ------------------------------------------------------------------------------


@StructDefine(
"""
B         : id
I*%leb128 : size
s*.size   : content
""", packed=True,
)
class ExportSection(StructFormatter):
    alt = "Section"

    def __init__(self, data=None, offset=0):
        self.name_formatter("id")
        if data:
            self.unpack(data, offset)

    def unpack(self,data,offset=0,psize=0):
        super().unpack(data,offset)
        ex = VectorField("Export : ex")
        self.update(ex.get(self.content))
        return self

with Consts("Export.desc"):
    func = 0x00
    table = 0x01
    mem = 0x02
    glob = 0x03

@StructDefine(
"""
I*%leb128 : n
s*.n      : name
B         : desc
I*%leb128 : x
""", packed=True,
)
class Export(StructFormatter):
    alt = "Section"

    def __init__(self, data=None, offset=0):
        self.name_formatter("desc")
        if data:
            self.unpack(data, offset)

    def unpack(self,data,offset=0,psize=0):
        from codecs import decode
        super().unpack(data,offset)
        self.name = decode(self.name,"UTF-8")
        return self


# ------------------------------------------------------------------------------


@StructDefine(
"""
B         : id
I*%leb128 : size
s*.size   : content
""", packed=True,
)
class StartSection(StructFormatter):
    alt = "Section"

    def __init__(self, data=None, offset=0):
        self.name_formatter("id")
        if data:
            self.unpack(data, offset)

    def unpack(self,data,offset=0,psize=0):
        super().unpack(data,offset)
        n,sz = read_uleb128(self.content)
        self.x = n
        return self


# ------------------------------------------------------------------------------


@StructDefine(
"""
B         : id
I*%leb128 : size
s*.size   : content
""", packed=True,
)
class ElementSection(StructFormatter):
    alt = "Section"

    def __init__(self, data=None, offset=0):
        self.name_formatter("id")
        if data:
            self.unpack(data, offset)

    def unpack(self,data,offset=0,psize=0):
        super().unpack(data,offset)
        seg = VectorField("Elem : seg")
        self.update(seg.get(self.content))
        return self


@StructDefine(
"""
B         : d
""", packed=True,
)
class Elem(StructFormatter):
    alt = "Section"

    def __init__(self, data=None, offset=0):
        if data:
            self.unpack(data, offset)

    def reset(self):
        self.fields = self.fields[0:1]
        t = type("container", (object,), {})
        self._v = t()

    def add_expr(self,data,offset):
        expr = VarField("B","~","e")
        expr.set_terminate(lambda b,f: b==0x0B)
        self.fields.append(expr)
        expr.instance = self
        self.update(expr.get(data,offset))
        return expr

    def add_et(self,data,offset):
        et = RawField("B",0,"et")
        self.fields.append(et)
        et.instance = self
        self.update(et.get(data,offset))
        return et

    def add_vec(self,fmt,data,offset):
        v = VectorField(fmt)
        self.fields.append(v)
        v.instance = self
        self.update(v.get(data,offset))
        return v

    def unpack(self,data,offset=0,psize=0):
        self.reset()
        super().unpack(data,offset)
        offset += 1
        if self.d==0x00:
            f = self.add_expr(data,offset)
            offset += f.size()
            self.add_vec("I*%leb128 : y", data, offset)
        elif self.d in (0x01,0x03):
            f = self.add_et(data,offset)
            offset += f.size()
            self.add_vec("I*%leb128 : y", data, offset)
        elif self.d == 0x02:
            f = Leb128Field("I",fname="x")
            self.fields.append(f)
            self.update(f.get(data,offset))
            offset += f.size()
            f = self.add_expr(data,offset)
            offset += f.size()
            f = self.add_et(data,offset)
            offset += f.size()
            self.add_vec("I*%leb128 : y", data, offset)
        elif self.d == 0x04:
            f = self.add_expr(data,offset)
            offset += f.size()
            f = VectorField("B~ : el")
            f.type.set_terminate(lambda b,f: b==0x0B)
            self.fields.append(f)
            self.update(f.get(data,offset))
        elif self.d in (0x05,0x07):
            f = self.add_et(data,offset)
            offset += f.size()
            f = VectorField("B~ : el")
            self.fields.append(f)
            f.type.set_terminate(lambda b,f: b==0x0B)
            self.update(f.get(data,offset))
        elif self.d == 0x06:
            f = Leb128Field("I",fname="x")
            self.fields.append(f)
            self.update(f.get(data,offset))
            offset += f.size()
            f = self.add_expr(data,offset)
            offset += f.size()
            f = self.add_et(data,offset)
            offset += f.size()
            f = VectorField("B~ : el")
            f.type.set_terminate(lambda b,f: b==0x0B)
            self.fields.append(f)
            self.update(f.get(data,offset))
        return self


# ------------------------------------------------------------------------------


@StructDefine(
"""
B         : id
I*%leb128 : size
s*.size   : content
""", packed=True,
)
class CodeSection(StructFormatter):
    alt = "Section"

    def __init__(self, data=None, offset=0):
        self.name_formatter("id")
        if data:
            self.unpack(data, offset)

    def unpack(self,data,offset=0,psize=0):
        super().unpack(data,offset)
        seg = VectorField("Code : code")
        self.update(seg.get(self.content))
        return self


@StructDefine(
"""
I*%leb128 : sz
""", packed=True,
)
class Code(StructFormatter):
    alt = "Section"

    def __init__(self, data=None, offset=0):
        if data:
            self.unpack(data, offset)

    def reset(self):
        self.fields = self.fields[0:1]
        t = type("container", (object,), {})
        self._v = t()

    def unpack(self,data,offset=0,psize=0):
        self.reset()
        super().unpack(data,offset)
        offset += len(self)
        func = data[offset:offset+self.sz]
        locs = VectorField("Locs : t")
        locs.instance = self
        self.fields.append(locs)
        self.update(locs.get(func))
        offset = locs.size()
        body = func[offset:]
        if body[-1]!=0x0B:
            raise WasmError("func body has no END")
        expr = RawField("s",len(body),"e")
        self.fields.append(expr)
        expr.instance = self
        self.update(expr.get(body))
        return self

@StructDefine(
"""
I*%leb128 : n
i*%leb128 : t
""", packed=True,
)
class Locs(StructFormatter):
    alt = "Section"

    def __init__(self, data=None):
        if data:
            self.unpack(data)


# ------------------------------------------------------------------------------


@StructDefine(
"""
B         : id
I*%leb128 : size
s*.size   : content
""", packed=True,
)
class DataSection(StructFormatter):
    alt = "Section"

    def __init__(self, data=None, offset=0):
        self.name_formatter("id")
        if data:
            self.unpack(data, offset)

    def unpack(self,data,offset=0,psize=0):
        super().unpack(data,offset)
        seg = VectorField("Data : code")
        self.update(seg.get(self.content))
        return self

@StructDefine(
"""
B         : d
""", packed=True,
)
class Data(StructFormatter):
    alt = "Section"

    def __init__(self, data=None, offset=0):
        if data:
            self.unpack(data, offset)

    def reset(self):
        self.fields = self.fields[0:1]
        t = type("container", (object,), {})
        self._v = t()

    def add_initexpr(self,data,offset):
        expr = VarField("B","~","e")
        expr.set_terminate(lambda b,f: b==0x0B)
        expr.instance = self
        self.fields.append(expr)
        try:
            self.update(expr.get(data,offset))
        except StandardError:
            raise WasmError("malformed init expr")
        return expr

    def add_vec(self,fmt,data,offset):
        v = VectorField(fmt)
        self.fields.append(v)
        v.instance = self
        self.update(v.get(data,offset))
        return v


    def unpack(self,data,offset=0,psize=0):
        super().unpack(data,offset)
        offset += 1
        if self.d&0x02:
            f = Leb128Field("I",fname="x")
            self.fields.append(f)
            self.update(f.get(data,offset))
            offset += f.size()
        if self.d&0x01==0:
            f = self.add_initexpr(data,offset)
            offset += f.size()
        self.add_vec("B : b", data, offset)
        return self


# ------------------------------------------------------------------------------


@StructDefine(
"""
B         : id
I*%leb128 : size
s*.size   : content
""", packed=True,
)
class DataCountSection(StructFormatter):
    alt = "Section"

    def __init__(self, data=None, offset=0):
        self.name_formatter("id")
        if data:
            self.unpack(data, offset)

    def unpack(self,data,offset=0,psize=0):
        super().unpack(data,offset)
        n,sz = read_uleb128(self.content)
        self.n = n
        return self


# ------------------------------------------------------------------------------


SectionID = {
        0: CustomSection,
        1: TypeSection,
        2: ImportSection,
        3: FunctionSection,
        4: TableSection,
        5: MemorySection,
        6: GlobalSection,
        7: ExportSection,
        8: StartSection,
        9: ElementSection,
        10: CodeSection,
        11: DataSection,
        12: DataCountSection,
}

# ------------------------------------------------------------------------------


