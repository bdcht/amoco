import pytest

from amoco.cas.expressions import *

def test_cst():
    c = cst(253,8)
    assert c == 0xfd
    assert c.sf == False
    assert c == cst(-3,8)
    c.sf = True
    assert c.value == -3
    assert c.v == 253
    c2 = c.zeroextend(16)
    assert c2.bytes(1,2)==0
    assert c2.sf == False
    e = c2+c.signextend(16)+5
    assert e==0xff
    c3 = e[0:8]
    c3.sf = True
    assert c3==-1
    c = cst(0x1000,32)
    assert c == 0x1000
    assert (0x1000-c)==0
    assert -c==-4096
    assert (-c).sf == True
    assert c.bytes(1,2,endian=1)==0x10
    assert c.bytes(2,4,endian=-1)==0x1000
    assert c.bytes(1,3,endian=-1)==0x0010

def test_reg(r):
    assert +r == -(-r)
    assert -r == 0-r
    with pytest.raises(AttributeError) as x:
        r.size += 1
    assert str(x.value)=='protected attribute'

def test_comp():
    c = composer([cst(1,8),cst(2,8),cst(3,8)])
    assert c == 0x030201
    assert c._endian==1
    assert c.bytes(0,2)==0x0201
    c = comp(24)
    c[0:24] = cst(0xf30201,24)
    c[4:20] = reg('r',16)
    assert c[0:16]._is_cmp
    assert c[16:24][4:8] == c[20:24]
    assert c[0:4] == 1

def test_slc():
    a = reg('%a',32)
    ah = slc(a,24,8,'%ah')
    assert ah.x == a
    assert ah.pos == 24
    assert str(ah)=='%ah'
    ax = a[16:32]
    assert str(ax)=='%a[16:32]'
    assert ax[8:16] == ah

def test_op(a,b):
    assert a+0==a
    assert a*1==a
    assert a^a==0
    assert a*0==0
    assert a&0==0
    assert a|0==a
    assert b-a == (-a)+b
    assert -(a+b) == (-a)-b
    assert -(a-b) == b-a
    assert -(b-a) == (a-b)*1
    assert -(1-a) == a-1
    assert (-a+(b-1)) == b-a-1
    e = -((b-1)-a)
    assert e == 1+(a-b)
    base,offset = extract_offset(e)
    assert base == a-b
    assert offset == 1
    e = -((b+1)-a)
    assert e == (a-b)-1
    base,offset = extract_offset(e)
    assert base == (a-b)
    assert offset == -1
    e = -1+(-b+a)
    base,offset = extract_offset(e)
    assert offset == -1
    assert e.r._is_cst
    assert e.r.v == 0xffffffffL
    assert e.r.sf == True

def test_op_slc(a,b):
    e = a^b
    assert e[8:16] == a[8:16]^b[8:16]
    e = composer([a[0:8],b[0:8]])
    x = (e&a[0:16])[0:8]
    assert x._is_slc
    x = x.simplify()
    assert x._is_reg and x==a[0:8]

def test_ptr(a):
    p = ptr(a)
    q = ptr(a,disp=17)
    assert p+17 == q
    assert p+2  == q-15
    assert (p+3).base == (q-5).base

def test_mem(a):
    p = ptr(a)
    q = ptr(a,disp=17)
    assert p+2  == q-15
    x = mem(p+2,64)
    y = mem(q-5,48,disp=-10)
    assert x.bytes(4,6) == y[32:48]

def test_vec(a):
    p = ptr(a)
    x = mem(p+2,32)
    c = cst(0x10,32)
    v = vec([a,p,x,c])
    assert v.size == 32
    z = v+3
    assert z._is_vec
    assert z.l[1]._is_ptr
    assert z.l[1].disp==3
    assert z.l[2]._is_eqn
    assert z.l[3]==0x13
    assert (~v).l[3]==0xffffffef

def test_vecw():
    x = [cst(n) for n in range(5)]
    v1 = vec(x)
    v2 = vec(x[0:3])
    v3 = vec([v1,v2]).simplify()
    assert len(v3.l)==5
    assert v3==v1
    v4 = vec([v1,v2]).simplify(widening=True)
    assert not v4._is_def
    assert len(v4.l)==5
    assert v4+1 == v4
    assert v4.depth()==float('inf')
    assert v3[8:16].l == v4[8:16].l

def test_top(r):
    t = top(8)
    assert t+3 == t
    assert t^r[0:8] == t
    assert (t==3) == top(1)
