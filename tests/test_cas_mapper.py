import pytest

from amoco.cas.mapper import *

def test_slicing(m,x,y):
    m.clear()
    m[x] = cst(0xabcdef89,32)
    xl = slc(x,0,8,ref='xl')
    xh = slc(x,8,8,ref='xh')
    assert m(xl)==0x89
    assert m(xh)==0xef
    m[xl] = y[8:16]
    assert m(xl)==y[8:16]
    assert m(xh)==0xef
    assert m(x[16:32])==0xabcd
    m[xh] = y[0:8]
    assert m(xl)==y[8:16]
    assert m(xh)==y[0:8]
    assert m(x[16:32])==0xabcd

def test_aliasing1(m,x,y):
    m.clear()
    mx = mem(x,32)
    my = mem(y,32)
    mxx = mem(x+2,32)
    m[mx] = cst(0xdeadbeef,32)
    m[my] = cst(0xbabebabe,32)
    m[mxx] = cst(0x01234567,32)
    assert m(my)._is_mem
    assert m(mxx) == 0x01234567
    rx = m(mx)
    assert str(rx)=='M32$3(x)'
    assert rx.mods[0][1]==0xdeadbeef
    assert rx.mods[1][0]==my.a

def test_aliasing2(m,x,y,z,w,r,a,b):
    m.clear()
    mx = mem(x,32)
    my = mem(y,32)
    m[r] = m(mx)                      # mov  r  , [x]
    m[mx] = cst(0,32)                 # mov [x] , 0
    assert m(r)==mx
    assert m(mx)==0
    m[my] = cst(1,32)                 # mov [y] , 1
    assert m(my)==1
    assert (m(mx)==0) is not True
    assert len(m(mx).mods)==2
    m[z]  = m(r)                      # mov  z  , r
    assert m(z)==mx
    m[w]  = m(my)                     # mov  w  , [y]
    assert m(w)==1
    m[a]  = m(a+mx)                   # add  a  , [x]
    assert m(a).r.mods[1][0]==my.a
    m[mx] = cst(2,32)                 # mov [x] , 2
    m[my] = m(z)                      # mov [y] , z
    m[b]  = m(b+mx)                   # add  b  , [x]
    assert len(m(b).r.mods)==2
    m[mem(a,32)] = cst(0,32)          # mov [a] , 0

def test_aliasing3(m,x,y,a):
    m.clear()
    m[mem(x-4,32)] = cst(0x44434241,32)
    m[mem(x-8,32)] = y
    m[x] = x-8
    res = m(mem(x+2,32))
    assert res._is_cmp
    assert res[16:32] == 0x4241
    assert res[0:16] == y[16:32]
    m[mem(a,8)] = cst(0xCC,8)
    res = m(mem(x+2,32))
    assert res._is_mem and len(res.mods)==3
    mprev = mapper()
    mprev[a] = x-4
    res = mprev(res)
    assert res[16:24] == 0xcc

def test_compose1(m,x,y,z,w):
    mx = mem(x,32)
    my = mem(y,32)
    mxx = mem(x+2,32)
    m[mx] = cst(0xdeadbeef,32)
    m[my] = cst(0xbabebabe,32)
    m[mxx] = cst(0x01234567,32)
    m[z] = m(mem(w,32))
    mprev = mapper()
    mprev[x] = z
    mprev[y] = z
    mprev[w] = z
    cm = m<<mprev
    assert cm(my) == 0x4567babe
    assert cm(z) == 0x4567babe

def test_compose2(m,x,y,z,w):
    mx = mem(x,32)
    my = mem(y,32)
    mxx = mem(x+2,32)
    m[mx] = cst(0xdeadbeef,32)
    m[my] = cst(0xbabebabe,32)
    m[mxx] = cst(0x01234567,32)
    m[z] = m(mem(w,32))
    m[w] = m(my)
    mprev = mapper()
    mprev[x] = z
    mprev[y] = z
    cm = m<<mprev
    assert cm(my) == 0x4567babe
    assert cm(w)==cm(my)

def test_vec(m,x,y,z,w,a,b):
    mx = mem(x,32)
    m[z] = vec([mx,y,w,cst(0x1000,32)])
    m[y] = vec([a,b])
    yy = m(y+y).simplify()
    assert len(yy.l)==3
    assert (b+a) in yy
    m[a] = m(z+y)
    mm = m.use(a=1,b=1)
    assert mm(a) == mm(z+1)

def test_use(m,x,y):
    mx = mem(x+12,32)
    m[y] = mx
    mm = m.use(x=0x1000)
    assert mm[y].a.base == 0x1000
    assert mm[y].a.disp == 12

def test_assume(m,r,w,x,y):
    m[r] = w+3
    mm = m.assume([x==3,w==0,y>0])
    assert mm[r]==3
    assert mm.conds[2]==(y>0)

def test_merge(m,r,w,x,y,a,b):
    m[r] = w+3
    mm = m.assume([x==3,w==0,y>0])
    m2 = mapper()
    m2[r] = a+b
    mm2 = m2.assume([w==1,y<0])
    mm3 = merge(mm,mm2)
    assert mm3(r)._is_vec
    assert mm3(r).l[0] == 0x3
    m3 = mapper()
    m3[r] = x
    m3[w] = cst(0x1000,32)
    mm4 = merge(mm3,m3)
    mm4w = mm4(w)
    assert mm4w._is_vec
    assert w in mm4w
    assert 0x1000 in mm4w
