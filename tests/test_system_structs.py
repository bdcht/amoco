import pytest
from amoco.system.structs import *

def test_rawfield():
    f = RawField('I',fcount=2,fname='v',falign=4)
    assert f.format()=='2I'
    assert f.size()==8
    assert f.unpack(b'\0\x01\x02\x03AAAA') == (0x03020100,0x41414141)
    assert f.align_value()==4

def test_rawfieldPtr():
    f = RawField('P',fname='ptr')
    assert f.format()=='P'
    assert f.size(psize=32)==4
    assert f.size(psize=4)==4
    assert f.size(psize=64)==8
    assert f.size(psize=8)==8
    assert f.unpack(b'\0\x01\x02\x03',psize=32) == 0x03020100

def test_varfield():
    f = VarField('s',fname='string')
    assert f.format()=='#s'
    assert f.size()==float('Infinity')
    assert f.unpack(b'abcdef\0dzdfoihzdofh') == b'abcdef\x00'
    # once unpacked, a variable-length field instance
    # updates its size and format
    assert f.size()==7
    assert f.format()=='7s'

def test_cntfield():
    f = CntField('s','~b',fname='bstr')
    assert f.format()=='#s'
    assert f.size()==float('Infinity')
    assert f.unpack(b'\x04abcdefgh') == b'abcd'
    # once unpacked, a variable-length field instance
    # updates its size and format
    assert f.size()==5
    assert f.format()=='b4s'

def test_StructDefine():
    S = StructDefine("B : v")(type('S',(StructCore,),{}))
    a = S()
    b = S()
    # make sure fields lists are NOT the same object:
    assert not (a.fields is b.fields)
    # but have "identical" content:
    assert a.fields==b.fields
    # make sure that a struct instance can be mutated without
    # impact on the class (or other instance of this class...)
    a.packed = True
    assert S.packed == False
    assert b.packed == False
    assert a.packed == True
    a.unpack(b'\x01')
    b.unpack(b'\x02')
    assert a.v == 1
    assert b.v == 2

def test_embed_varfield():
    inf = float('Infinity')
    S1 = StructDefine("B*~ : v1")(type('S1',(StructCore,),{}))
    assert S1.size() == inf
    S2 = StructDefine("S1 : v2")(type('S2',(StructCore,),{}))
    assert S2.fields[0].type is S1
    assert S2.size() == inf
    a = S2()
    assert S2.size() == a.size() == inf
    assert len(a) == 0
    a.unpack(b"aoijzfoijzdf\0zofijzdfoij")
    assert bytes(a.v2.v1) == b"aoijzfoijzdf\0"
    assert a.size() == inf
    assert len(a) == len(a.v2.v1)


def test_UnionDefine():
    U = UnionDefine("B : v\nI : w")(type('U',(StructCore,),{}))
    u = U()
    assert u.size()==4
    u.unpack(b'\x01\0\0\x01')
    assert u.v == 1
    assert u.w == 0x01000001

def test_TypeDefine():
    @StructDefine("myinteger*1 : z")
    class S1(StructFormatter):
        pass

    myint = TypeDefine('myinteger', 'xxx', 2)
    xxx = TypeDefine('xxx', 'h')
    s = S1()
    assert xxx is Alltypes['xxx']
    assert myint is Alltypes['myinteger']
    assert xxx().unpack(b'\x01\x00') == 1
    assert myint.size() == 2*xxx.size() == 4
    assert myint().unpack(b'\x01\x00\x02\x00') == [1,2]
    assert s.unpack(b'\x03\x00\x04\x00\x05\x00\x06\x00')
    assert s.z == [[3,4]]

def test_Field_aliasing():
    S1 = StructFactory("S1","I : i")
    @StructDefine("S1 : x")
    class S2(StructFormatter): pass
    @StructDefine("S1 : y")
    class S3(StructFormatter): pass
    s = S2()
    # s uses type S1 to decode its field 'x',
    # which by default is little-endian:
    s.unpack(b'\x00\x00\x00\x01')
    assert s.align_value()==4
    assert s.x.i == 0x01000000
    # an S3 instance q, would do the same but
    # if we modify the S1 type to change its
    # field into big-endian for example, then
    # any further decoding that uses this type
    # will indeed use the current definition:
    q = S3()
    S1.fields[0].order = '>'
    q.unpack(b'\x01\x00\x00\x00')
    assert q.y.i == 0x01000000
    assert s.x.i == 0x01000000

def test_Struct_slop():
    S1 = StructFactory("S1","c: a\nI : b")
    # padding occurs between a and b due to field alignement rules:
    assert S1.size()==8
    # padding occurs at end of structure due to structure alignment rules:
    S2 = StructFactory("S2","I: a\nc : b")
    assert S2.size()==8
    # if "packed", no padding should be present:
    S3 = StructFactory("S3","c: a\nI : b",packed=True)
    assert S3.size()==5
    s1 = S1().unpack(b'\x41\xff\xff\xff\xef\xcd\xab\x89')
    assert s1.a == b'A'
    assert s1.b == 0x89abcdef
    s2 = S2().unpack(b'\x01\x02\x03\x04\x42')
    assert s2.a == 0x04030201
    assert s2.b == b'B'
    assert s2.pack() == b'\x01\x02\x03\x04\x42\0\0\0'
    s3 = S3().unpack(b'\x43\x01\x00\x00\x00')
    assert s3.a == b'C'
    assert s3.b == 1
    assert s3.pack() == b'\x43\x01\x00\x00\x00'

def test_Struct_CntFields():
    # we test StructDefine ability to declare CntField:
    @StructDefine("""
    s*16 : uuidDesigner
    I    : cbStructSize
    s*~I : bstrAddinRegKey
    s*~I : bstrAddinName
    s*~I : bstrAddinDescription
    I    : dwLoadBehaviour
    s*~I : bstrSatelliteDll
    s*~I : bstrAdditionalRegKey
    I    : dwCommandLineSafe
    """,packed=True)
    class DesignerInfo(StructFormatter):
        order = '<'
        def __init__(self,data="",offset=0):
            if data:
                self.unpack(data,offset)
    # instance of this class should have infinite length until
    # some unpacking is performed:
    d = DesignerInfo()
    assert d.format() == '16sI#s#s#sI#s#sI'
    assert d.size() == float('Infinity')
    # lets unpack the structure from some bytes...
    d.unpack(b'A'*16+
             b'\x01\0\0\0'+
             b'\x04\0\0\0abcd'+
             b'\x04\0\0\0abcd'+
             b'\x04\0\0\0abcd'+
             b'\x02\0\0\0'+
             b'\x04\0\0\0abcd'+
             b'\x04\0\0\0abcd'+
             b'\x03\0\0\0')
    assert d.uuidDesigner == b'A'*16
    assert d.bstrAddinRegKey == b'abcd'
    assert d.dwCommandLineSafe == 3
    # a StructCore format and size is not updated even
    # when an instance is unpacked:
    assert d.format() == '16sI#s#s#sI#s#sI'
    assert d.size() == float('Infinity')
    # but the actual byte-length of the structure is
    # obtained with len:
    assert len(d)==68
    # and field offsets are known for this instance: 
    assert d.offset_of("dwLoadBehaviour")==44

def test_bitfield1():
    f = BitField('B',fcount=[2,4,1,1],fname=['a','b','c','d'])
    assert f.format()=='B'
    assert f.size()==1
    assert f.name is None
    assert str(f)=="<Field ['a:2', 'b:4', 'c:1', 'd:1']>"
    v = f.unpack(b"\x93")
    # values are splitted from low to high order bits...
    assert v['a'] == 3
    assert v['b'] == 4
    assert v['c'] == 0
    assert v['d'] == 1

def test_bitfield2():
    f = BitField('H',fcount=[2,4,1,1],fname=['a','b','c','d'])
    assert f.format()=='H'
    assert f.size()==2
    assert f.name is None
    assert str(f)=="<Field ['a:2', 'b:4', 'c:1', 'd:1']>"
    v = f.unpack(b"\x40\x93")
    # values are splitted from low to high order bits...
    assert v['a'] == 0
    assert v['b'] == 0
    assert v['c'] == 1
    assert v['d'] == 0
    # if we change to big-endian:
    f.order = '>'
    v = f.unpack(b"\x40\x93")
    assert v['a'] == 3
    assert v['b'] == 4
    assert v['c'] == 0
    assert v['d'] == 1

def test_bitfield3():
    xxx = TypeDefine('int16', 'h')
    f = BitFieldEx('int16',fcount=[2,4,3,1,6],fname=['a','b','c','d','e'])
    assert f.format()=='2s'
    assert f.size()==2
    assert f.type().unpack(b"\x01\x02")==513
    D = f.unpack(b"\x01\x02")
    assert D['a'] == D['d'] == 1
    assert D['b'] == D['c'] == D['e'] == 0
    D = f.unpack(b"\x29\x8a")
    assert D['b'] == 10
    assert D['e'] == 34

def test_bitfield_struct():
    xxx = TypeDefine('int16', 'h')
    @StructDefine("""
    int16 *#2/4/3/1/6 : a/b/c/d/e
    """)
    class stru_bf(StructFormatter):
        order = '<'
        def __init__(self,data="",offset=0):
            if data:
                self.unpack(data,offset)
    s = stru_bf()
    assert s.size()==2
    assert s.offsets() == [(0.0, 0.2), (0.2, 0.4), (0.6, 0.3), (0.9, 0.1), (0.1, 0.6)]

def test_ptr_struct():
    xxx = TypeDefine('int32', 'I')
    @StructDefine("""
    P : ptr
    int32 : val
    l : lval
    """)
    class stru_ptrval(StructFormatter):
        order = '<'
        def __init__(self,data="",offset=0):
            if data:
                self.unpack(data,offset)
    s = stru_ptrval()
    assert s.size(psize=4)==12
    assert s.size(psize=8)==24
    assert s.offsets(psize=4) == [(0, 4), (4, 4), (8, 4)]
    assert s.offsets(psize=8) == [(0, 8), (8, 4), (16, 8)]

def test_bindedfield():
    @StructDefine("""
    I          : counter
    H          : unused
    s*.counter : data
    """)
    class bindit(StructFormatter):
        order = '<'
        def __init__(self,data="",offset=0):
            if data:
                self.unpack(data,offset)
    s = bindit()
    s.unpack(b"\x05\0\0\0\x99\xffabcdef")
    assert s.counter == 5
    assert s.unused == 0xff99
    assert s.fields[2].instance is s
    assert isinstance(s.fields[2],BindedField)
    assert s.data == b"abcde"

def test_wasm_():
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
        def __init__(self, data=None):
            if data:
                self.unpack(data)
        def unpack(self,data,offset=0):
            from codecs import decode
            super().unpack(data,offset)
            self.mod = decode(self.mod,"UTF-8")
            self.nm = decode(self.nm,"UTF-8")
            return self
    i = Import(b"\x05AAAAA\x07BBBBBBBxxx")
    assert i.n1 == 5
    assert i.mod == "AAAAA"
    assert i.n2 == 7
    assert i.nm == "BBBBBBB"

