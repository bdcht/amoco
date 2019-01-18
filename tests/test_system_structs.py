import pytest
from amoco.system.structs import *

def test_field():
    pass

def test_StructDefine():
    pass

def test_UnionDefine():
    pass

def test_TypeDefine():
    @StructDefine("myinteger*1 : z")
    class S1(StructFormatter): pass
    TypeDefine('myinteger', 'xxx', 2)
    TypeDefine('xxx', 'h')
    s = S1()
    xxx = StructDefine.All['xxx']
    myint = StructDefine.All['myinteger']
    assert xxx.unpack(b'\x01\x00') == 1
    assert xxx == myint.type
    assert myint.unpack(b'\x01\x00\x02\x00') == [1,2]
    assert s.unpack(b'\x03\x00\x04\x00\x05\x00\x06\x00')
    assert s.z == [[3,4]]

def test_Field_aliasing():
    S1 = StructFactory("S1","I : i")
    @StructDefine("S1 : x")
    class S2(StructFormatter): pass
    @StructDefine("S1 : y")
    class S3(StructFormatter): pass
    S3.order = '>'
    assert S2.order == '<'
    s = S2()
    s.unpack(b'\x00\x00\x00\x01')
    assert s.x.i == 0x01000000
    q = S3()
    assert q.order == '>'
    q.unpack(b'\x01\x00\x00\x00')
    assert q.y.i == 0x01000000
    assert s.x.i == 0x01000000
