from amoco.signals import *

sig1 = Signal("#1")
sig2 = Signal("#2")
sig3 = Signal("#3")

class SigRaised(Exception):
    pass

def MyFunction1(x,y,z=0):
    def MyFunction2(x,y,z):
        return x+y+z
    return MyFunction2(x,y,z)

def Myaction1(sig,ref,args):
    assert isinstance(sig,Signal)
    raise SigRaised

def Myaction2(sig,ref,args):
    pass
    #pdb.set_trace()

def Myaction3(sig,ref,args):
    sig3.emit()

def Myaction4(sig,ref,args):
    print(sig)
    print(ref)
    print(args)

class MyClassA(object):
    @staticmethod
    def smeth(x,y,z=1):
        return x+y+z
    @classmethod
    def cmeth(cls,x,y,z=2):
        return x+y+z
    def meth(self,x,y,z=3,q=4):
        return x+y+z+q
    def __call__(self,x,y,z=4,q=5):
        return x+y+z+q
    @property
    def x(self):
        return self._x
    @x.setter
    def x(self,v):
        self._x = v

class MyClassB(MyClassA):
    @staticmethod
    def smethb(x,y,z=1):
        return x+y+z
    @classmethod
    def cmethb(cls,x,y,z=2):
        return x+y+z
    def methb(self,x,y,z=3,q=4):
        return x+y+z+q
    def __call__(self,x,y,z=4,q=5):
        return x+y+z+q

def test_references():
    a = MyClassA()
    b = MyClassB()
    r = reference(a.meth)
    rf = reference(MyFunction1)
    rA = reference(MyClassA.meth)
    rsA = reference(a.smeth)
    rsB = reference(b.smeth)
    rcA = reference(a.cmeth)
    rcB = reference(MyClassB.cmeth)
    roa = reference(a)
    rob = reference(b)
    assert r.type==REF_METH_BOUND
    assert rf.type==REF_FUNC_REGULAR
    assert rsA.type == REF_FUNC_UNBOUND and rsA.is_static
    assert rsB.type == REF_FUNC_UNBOUND and rsB.is_static
    assert rsB.ctx is rsA.ctx
    assert rsB.ref is rsA.ref
    assert rsB == rsA
    assert rcA.type == REF_METH_BOUND
    assert rcB.type == REF_METH_BOUND
    assert roa.type == REF_OBJ_CALLABLE
    assert rob.type == REF_OBJ_CALLABLE
    del a
    assert r.ctx() is None

def test_signal_0():
    assert Signal('#1')==sig1
    assert Signal('#1') is sig1

def test_signal_1():
    a = MyClassA()
    r = reference(a.meth)
    sig1.receiver(Myaction1)
    sig1.patch(r)
    assert MyClassA().meth(1,2) == 10
    try:
        assert a.meth(1,2) == 10
    except SigRaised:
        sig1.unpatch(a.meth)
    else:
        assert False
    assert a.meth(1,2) == 10
    sig1.recv.remove(Myaction1)

def test_signal_2():
    sig1.sender(MyClassB.methb)
    sig1.receiver(Myaction1)
    b = MyClassB()
    try:
        assert MyClassB().methb(1,2) == 10
    except SigRaised:
        pass
    else:
        assert False
    try:
        assert b.methb(1,2) == 10
    except SigRaised:
        pass
    else:
        assert False
    sig1.unpatch(MyClassB.methb)
    sig1.recv.remove(Myaction1)
    assert b.methb(1,2) == 10

def test_signal_3():
    b = MyClassB()
    sig1.sender(MyClassA.smeth)
    sig1.sender(b.meth)
    sig1.receiver(Myaction3)
    sig3.receiver(Myaction1)
    try:
        assert MyClassA().smeth(1,1)==3
    except SigRaised:
        pass
    else:
        assert False
    try:
        assert b.meth(1,2)==10
    except SigRaised:
        pass
    else:
        assert False
    sig1.unpatch(MyClassA.smeth)
    sig1.recv.remove(Myaction3)
    sig3.recv.remove(Myaction1)
    assert MyClassA().smeth(1,1)==3

def test_signal_4():
    b = MyClassB()
    sig1.sender(MyClassA.cmeth)
    sig1.sender(b.meth)
    sig1.receiver(Myaction3)
    sig3.receiver(Myaction1)
    try:
        assert MyClassA().cmeth(1,1)==4
    except SigRaised:
        pass
    else:
        assert False
    try:
        assert b.meth(1,2)==10
    except SigRaised:
        pass
    else:
        assert False
    sig1.unpatch(MyClassA.cmeth)
    sig1.recv.remove(Myaction3)
    sig3.recv.remove(Myaction1)
    assert MyClassA().cmeth(1,1)==4

def test_signal_5():
    sig2.receiver(Myaction2)
    sig2.emit()
    sig2.recv.remove(Myaction2)
