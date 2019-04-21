import pytest
from amoco.system.structs import *

def test_varfield():
    f = VarField('s',fname='string')
    assert f.size()==float('Infinity')
    assert f.unpack(b'abcdef\0dzdfoihzdofh') == b'abcdef\x00'
    assert f.size()==7

def test_StructDefine():
    S = StructDefine("B : v")(type('S',(StructCore,),{}))
    a = S()
    b = S()
    assert not (a.fields is b.fields)
    a.packed = True
    assert S.packed == False
    assert b.packed == False
    assert a.packed == True
    a.unpack(b'\x01')
    b.unpack(b'\x02')
    assert a.v == 1
    assert b.v == 2

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
    s = S2()
    s.unpack(b'\x00\x00\x00\x01')
    assert s.x.i == 0x01000000
    q = S3()
    S1.fields[0].order = '>'
    q.unpack(b'\x01\x00\x00\x00')
    assert q.y.i == 0x01000000
    assert s.x.i == 0x01000000

def test_Struct_slop():
    S1 = StructFactory("S1","c: a\nI : b")
    assert S1.size()==8
    S2 = StructFactory("S2","I: a\nc : b")
    assert S2.size()==8
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
