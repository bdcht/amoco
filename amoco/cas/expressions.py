# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.logger import Log
logger = Log(__name__)

from amoco.ui import render

# decorators:
#------------

def _checkarg1_exp(f):
    def checkarg1_exp(*args):
        if len(args)>0 and isinstance(args[0],exp):
            return f(*args)
        else:
            logger.error('first arg is not an expression')
            raise TypeError(args)
    return checkarg1_exp

def _checkarg_sizes(f):
    def checkarg_sizes(self,n):
        if self.size<>n.size:
            if self.size>0 and n.size>0:
                logger.error('size mismatch')
                raise ValueError,n
        return f(self,n)
    return checkarg_sizes

def _checkarg_numeric(f):
    def checkarg_numeric(self,n):
        if isinstance(n,(int,long)):
                n = cst(n,self.size)
        elif isinstance(n,(float)):
                n = cfp(n,self.size)
        return f(self,n)
    return checkarg_numeric

def _checkarg_slice(f):
    def checkarg_slice(self,*args):
        i = args[0]
        if isinstance(i,slice):
            if i.step<>None: raise ValueError,i
            if i.start<0 or i.stop>self.size:
                logger.error('size mismatch')
                raise ValueError,i
            if i.stop<=i.start:
                logger.error('invalid slice')
                raise ValueError,i
        else:
            logger.error('argument should be a slice')
            raise TypeError,i
        return f(self,*args)
    return checkarg_slice


# atoms:
# ------

#------------------------------------------------------------------------------
# exp is the core class for all expressions.
# It defines mandatory attributes, shared methods like dumps/loads, etc.
#------------------------------------------------------------------------------
class exp(object):
    __slots__ = ['size','sf']
    _endian   = 1      # defaults to little-endian
    _is_def   = False
    _is_cst   = False
    _is_reg   = False
    _is_cmp   = False
    _is_slc   = False
    _is_mem   = False
    _is_ext   = False
    _is_lab   = False
    _is_ptr   = False
    _is_tst   = False
    _is_eqn   = False
    _is_vec   = False

    def __init__(self,size=0,sf=False):
        self.size = size
        self.sf   = False

    def __len__(self): return self.length

    @classmethod
    def setendian(cls,e):
        assert e in (-1,+1)
        cls._endian = e

    @property
    def length(self): # length value is in bytes
        return self.size/8

    def bytes(self,sta=0,sto=None,endian=0):
        s = slice(sta,sto)
        l = self.length
        sta,sto,stp = s.indices(l)
        endian |= self._endian
        if endian==-1:
            sta,sto = l-sto,l-sta
        return self[sta*8:sto*8]

    @property
    def mask(self):
        return (1<<self.size)-1

    def eval(self,env):
        if self._is_def is 0    : return top(self.size)
        if self._is_def is False: return exp(self.size)
        else: raise NotImplementedError("can't eval %s"%self)

    def simplify(self):
        return self

    def depth(self):
        return 1.

    def addr(self,env):
        raise TypeError('exp has no address')

    def dumps(self):
        from pickle import dumps,HIGHEST_PROTOCOL
        return dumps(self,HIGHEST_PROTOCOL)
    def loads(self,s):
        from pickle import loads
        self = loads(s)
        return self

    def __str__(self):
        if self._is_def is 0: return 'T%d'%self.size
        if self._is_def is False: return '⊥%d'%self.size
        raise ValueError("void expression")

    def toks(self,**kargs):
        return [(render.Token.Literal,str(self))]

    def pp(self,**kargs):
        return render.highlight(self.toks(**kargs))

    def bit(self,i):
        i = i%self.size
        return self[i:i+1]

    # get item allows to extract the expression of a slice of the exp
    @_checkarg_slice
    def __getitem__(self,i)  :
        return slicer(self,i.start,i.stop-i.start)

    # set item allows to insert the expression of a slice in the exp
    @_checkarg_slice
    def __setitem__(self,i,e)  :
        res = comp(self.size)
        res[0:res.size] = self
        res[i.start:i.stop] = e
        return res.simplify()

    def extend(self,sign,size):
        xt = size-self.size
        if xt<=0: return self
        sb = self[self.size-1:self.size]
        if sign is True:
            xx = tst(sb,cst(-1,xt),cst(0,xt))
            xx.sf = True
        else:
            xx = cst(0,xt)
            xx.sf = False
        return composer([self,xx])

    def signextend(self,size):
        return self.extend(True,size)

    def zeroextend(self,size):
        return self.extend(False,size)

    # arithmetic / logic methods : These methods are shared by all nodes.
    # unary operators:
    def __invert__(self): return oper('~',self)
    def __neg__(self): return oper('-',self)
    def __pos__(self): return self
    # binary operators:
    @_checkarg_numeric
    def __add__(self,n): return oper('+',self,n)
    @_checkarg_numeric
    def __sub__(self,n): return oper('-',self,n)
    @_checkarg_numeric
    def __mul__(self,n): return oper('*',self,n)
    @_checkarg_numeric
    def __pow__(self,n): return oper('**',self,n)
    @_checkarg_numeric
    def __div__(self,n): return oper('/',self,n)
    @_checkarg_numeric
    def __mod__(self,n): return oper('%',self,n)
    @_checkarg_numeric
    def __floordiv__(self,n): return oper('//',self,n)
    @_checkarg_numeric
    def __and__(self,n): return oper('&',self,n)
    @_checkarg_numeric
    def __or__(self,n): return oper('|',self,n)
    @_checkarg_numeric
    def __xor__(self,n): return oper('^',self,n)
    # reflected operand cases:
    @_checkarg_numeric
    def __radd__(self,n): return oper('+',n,self)
    @_checkarg_numeric
    def __rsub__(self,n): return oper('-',n,self)
    @_checkarg_numeric
    def __rmul__(self,n): return oper('*',n,self)
    @_checkarg_numeric
    def __rpow__(self,n): return oper('**',n,self)
    @_checkarg_numeric
    def __rand__(self,n): return oper('&',n,self)
    @_checkarg_numeric
    def __ror__(self,n): return oper('|',n,self)
    @_checkarg_numeric
    def __rxor__(self,n): return oper('^',n,self)
    # shifts:
    @_checkarg_numeric
    def __lshift__(self,n): return oper('<<',self,n)
    @_checkarg_numeric
    def __rshift__(self,n): return oper('>>',self,n)

    # WARNING: comparison operators cmp returns a python bool
    # but any other operators always return an expression !
    def __hash__(self): return hash(str(self))+self.size
    @_checkarg_numeric
    def __cmp__(self,n): return cmp(hash(self),hash(n))

    # An expression defaults to False, and only bit1 will return True.
    def __nonzero__(self): return False

    @_checkarg_numeric
    def __eq__(self,n):
        if exp.__cmp__(self,n)==0: return bit1
        return oper('==',self,n)
    @_checkarg_numeric
    def __ne__(self,n):
        if exp.__cmp__(self,n)==0: return bit0
        return oper('!=',self,n)
    @_checkarg_numeric
    def __lt__(self,n):
        if exp.__cmp__(self,n)==0: return bit0
        return oper('<',self,n)
    @_checkarg_numeric
    def __le__(self,n):
        if exp.__cmp__(self,n)==0: return bit1
        return oper('<=',self,n)
    @_checkarg_numeric
    def __ge__(self,n):
        if exp.__cmp__(self,n)==0: return bit1
        return oper('>=',self,n)
    @_checkarg_numeric
    def __gt__(self,n):
        if exp.__cmp__(self,n)==0: return bit0
        return oper('>',self,n)

    def to_smtlib(self,solver=None):
        logger.warning('no SMT solver defined')
        raise NotImplementedError
##

class top(exp):
    _is_def   = 0

    def depth(self):
        return float('inf')

#-----------------------------------
# cst holds numeric immediate values
#-----------------------------------
class cst(exp):
    __slots__ = ['v']
    _is_def   = True
    _is_cst   = True

    def __init__(self,v,size=32):
        if isinstance(v,bool): #only True/False forces size=1 (not 0/1 !)
            v = 1 if v else 0
            size=1
        self.sf = False if v>=0 else True
        self.size = size
        self.v  = v&self.mask
    ##

    @property
    def value(self):
        if self.sf and (self.v>>(self.size-1)==1):
            return -(self.v^self.mask)-1
        else:
            return self.v

    # for slicing purpose:
    def __index__(self):
        return self.value
    # coercion to Python int:
    def __int__(self):
        return self.value

    # defaults to signed hex base
    def __str__(self):
        return '{:#x}'.format(self.value)

    def toks(self,**kargs):
        return [(render.Token.Constant,str(self))]

    def to_sym(self,ref):
        return sym(ref,self.v,self.size)

    # eval of cst is always itself: (sf flag conserved)
    def eval(self,env): return cst(self.value,self.size)

    def zeroextend(self,size):
        return cst(self.v,max(size,self.size))

    def signextend(self,size):
        sf = self.sf
        self.sf = True
        v = self.value
        self.sf = sf
        return cst(v,max(size,self.size))

    # bit-slice (returns cst) :
    @_checkarg_slice
    def __getitem__(self,i):
        start = i.start or 0
        stop  = i.stop or self.size
        return cst(self.v>>start,stop-start)

    def __invert__(self):
        #note: masking is needed because python uses unlimited ints
        # so ~0x80 means not(...0000080) = ...fffffef
        return cst((~(self.v))&self.mask,self.size)
    def __neg__(self):
        return cst(-(self.value),self.size)

    @_checkarg_numeric
    @_checkarg_sizes
    def __add__(self,n):
        if n._is_cst: return cst(self.value+n.value,self.size)
        else : return exp.__add__(self,n)
    @_checkarg_numeric
    @_checkarg_sizes
    def __sub__(self,n):
        if n._is_cst: return cst(self.value-n.value,self.size)
        else : return exp.__sub__(self,n)
    @_checkarg_numeric
    @_checkarg_sizes
    def __mul__(self,n):
        if n._is_cst: return cst(self.value*n.value,self.size)
        else : return exp.__mul__(self,n)
    @_checkarg_numeric
    @_checkarg_sizes
    def __pow__(self,n):
        if n._is_cst: return cst(self.value*n.value,2*self.size)
        else : return exp.__pow__(self,n)
    @_checkarg_numeric
    def __div__(self,n):
        if n._is_cst: return cst(int(float(self.value)/n.value),self.size)
        else : return exp.__div__(self,n)
    @_checkarg_numeric
    def __mod__(self,n):
        if n._is_cst: return cst(self.value%n.value,self.size)
        else : return exp.__mod__(self,n)
    @_checkarg_numeric
    @_checkarg_sizes
    def __and__(self,n):
        if n._is_cst: return cst(self.v&n.v,self.size)
        else : return exp.__and__(self,n)
    @_checkarg_numeric
    @_checkarg_sizes
    def __or__(self,n):
        if n._is_cst: return cst(self.v|n.v,self.size)
        else : return exp.__or__(self,n)
    @_checkarg_numeric
    @_checkarg_sizes
    def __xor__(self,n):
        if n._is_cst: return cst(self.v^n.v,self.size)
        else : return exp.__xor__(self,n)
    @_checkarg_numeric
    def __lshift__(self,n):
        if n._is_cst: return cst(self.value<<n.value,self.size)
        else : return exp.__lshift__(self,n)
    @_checkarg_numeric
    def __rshift__(self,n):
        self.sf = False # rshift implements logical right shift
        if n._is_cst: return cst(self.value>>n.value,self.size)
        else : return exp.__rshift__(self,n)
    @_checkarg_numeric
    def __floordiv__(self,n):
        self.sf = True # floordiv implements arithmetic right shift
        if n._is_cst: return cst(self.value>>n.value,self.size)
        else : return exp.__floordiv__(self,n)

    @_checkarg_numeric
    def __radd__(self,n): return n+self
    @_checkarg_numeric
    def __rsub__(self,n): return n-self
    @_checkarg_numeric
    def __rmul__(self,n): return n*self
    @_checkarg_numeric
    def __rpow__(self,n): return n**self
    @_checkarg_numeric
    def __rdiv__(self,n): return n/self
    @_checkarg_numeric
    def __rand__(self,n): return n&self
    @_checkarg_numeric
    def __ror__(self,n): return n|self
    @_checkarg_numeric
    def __rxor__(self,n): return n^self

    # the only atom that is considered True is the cst(1,1) (ie bit1 below)
    def __nonzero__(self):
        if self.size==1 and self.v==1: return True
        else: return False

    @_checkarg_numeric
    @_checkarg_sizes
    def __eq__(self,n):
        if n._is_cst: return cst(self.v==n.v)
        else : return exp.__eq__(self,n)
    @_checkarg_numeric
    @_checkarg_sizes
    def __ne__(self,n):
        if n._is_cst: return cst(self.v!=n.v)
        else : return exp.__ne__(self,n)

    @_checkarg_numeric
    @_checkarg_sizes
    def __lt__(self,n):
        if n._is_cst: return cst(self.value<n.value)
        else : return exp.__lt__(self,n)
    @_checkarg_numeric
    @_checkarg_sizes
    def __le__(self,n):
        if n._is_cst: return cst(self.value<=n.value)
        else : return exp.__le__(self,n)
    @_checkarg_numeric
    @_checkarg_sizes
    def __ge__(self,n):
        if n._is_cst: return cst(self.value>=n.value)
        else : return exp.__ge__(self,n)
    @_checkarg_numeric
    @_checkarg_sizes
    def __gt__(self,n):
        if n._is_cst: return cst(self.value>n.value)
        else : return exp.__gt__(self,n)
##

bit0 = cst(0,1)
bit1 = cst(1,1)

class sym(cst):
    __slots__ = ['ref']

    def __init__(self,ref,v,size=32):
        self.ref = ref
        cst.__init__(self,v,size)

    def __str__(self):
        return "#%s"%self.ref

#---------------------------------
# cfp holds float immediate values
#---------------------------------
class cfp(exp):
    __slots__ = ['v']
    _is_def   = True
    _is_cst   = True

    def __init__(self,v,size=32):
        self.size = size
        self.v  = float(v)
    ##

    @property
    def value(self):
        return self.v

    # coercion to integer:
    def __int__(self):
        return NotImplementedError

    def __str__(self):
        return '{:f}'.format(self.value)

    def toks(self,**kargs):
        return [(render.Token.Constant,str(self))]

    def eval(self,env): return cfp(self.value,self.size)

    def __neg__(self):
        return cfp(-(self.value),self.size)

    @_checkarg_numeric
    @_checkarg_sizes
    def __add__(self,n):
        if n._is_cst: return cfp(self.v+n.value,self.size)
        else : return exp.__add__(self,n)
    @_checkarg_numeric
    @_checkarg_sizes
    def __sub__(self,n):
        if n._is_cst: return cfp(self.v-n.value,self.size)
        else : return exp.__sub__(self,n)
    @_checkarg_numeric
    @_checkarg_sizes
    def __mul__(self,n):
        if n._is_cst: return cfp(self.v*n.value,self.size)
        else : return exp.__mul__(self,n)
    @_checkarg_numeric
    @_checkarg_sizes
    def __pow__(self,n):
        if n._is_cst: return cfp(self.v**n.value,self.size)
        else : return exp.__pow__(self,n)
    @_checkarg_numeric
    def __div__(self,n):
        if n._is_cst: return cfp(self.v/n.value,self.size)
        else : return exp.__div__(self,n)

    @_checkarg_numeric
    def __radd__(self,n): return n+self
    @_checkarg_numeric
    def __rsub__(self,n): return n-self
    @_checkarg_numeric
    def __rmul__(self,n): return n*self
    @_checkarg_numeric
    def __rpow__(self,n): return n**self
    @_checkarg_numeric
    def __rdiv__(self,n): return n/self

    @_checkarg_numeric
    @_checkarg_sizes
    def __eq__(self,n):
        if n._is_cst: return cst(self.value==n.value)
        else : return exp.__eq__(self,n)
    @_checkarg_numeric
    @_checkarg_sizes
    def __ne__(self,n):
        if n._is_cst: return cst(self.value!=n.value)
        else : return exp.__ne__(self,n)

    @_checkarg_numeric
    @_checkarg_sizes
    def __lt__(self,n):
        if n._is_cst: return cst(self.value<n.value)
        else : return exp.__lt__(self,n)
    @_checkarg_numeric
    @_checkarg_sizes
    def __le__(self,n):
        if n._is_cst: return cst(self.value<=n.value)
        else : return exp.__le__(self,n)
    @_checkarg_numeric
    @_checkarg_sizes
    def __ge__(self,n):
        if n._is_cst: return cst(self.value>=n.value)
        else : return exp.__ge__(self,n)
    @_checkarg_numeric
    @_checkarg_sizes
    def __gt__(self,n):
        if n._is_cst: return cst(self.value>n.value)
        else : return exp.__gt__(self,n)
##

#------------------------------------------------------------------------------
# reg holds 32-bit register reference (refname).
#------------------------------------------------------------------------------
class reg(exp):
    __slots__ = ['ref','type','_subrefs', '__protect']
    _is_def   = True
    _is_reg   = True

    def __init__(self,refname,size=32):
        self.__protect = False
        self.size = size
        self.__protect = True
        self.sf  = False
        self.ref = refname
        self._subrefs = {}
        self.type = regtype.STD

    def __str__(self):
        return self.ref

    def toks(self,**kargs):
        return [(render.Token.Register,str(self))]

    def eval(self,env):
        return env[self]

    def addr(self,env):
        return self

    def __setattr__(self,a,v):
        if a is 'size' and self.__protect is True:
            raise AttributeError,'protected attribute'
        exp.__setattr__(self,a,v)

    #howto pickle/unpickle reg objects:
    def __setstate__(self,state):
        v = state[1]
        self.__protect = False
        self.size = v['size']
        self.sf = v['sf']
        self.ref = v['ref']
        self.type = v['type']
        self._subrefs = v['_subrefs']
        self.__protect = v['_reg__protect']
##

class regtype(object):
    STD   = 0b0000
    PC    = 0b0001
    FLAGS = 0b0010
    STACK = 0b0100
    OTHER = 0b1000
    cur   = None

    def __init__(self,t):
        self.t = t

    def __call__(self,r):
        if not r._is_reg:
            logger.error('pc decorator ignored (not a register)')
        r.type = self.t
        return r

    def __enter__(self):
        regtype.cur = self.t

    def __exit__(self,exc_type,exc_value,traceback):
        regtype.cur = None

is_reg_pc    = regtype(regtype.PC)
is_reg_flags = regtype(regtype.FLAGS)
is_reg_stack = regtype(regtype.STACK)
is_reg_other = regtype(regtype.OTHER)

#------------------------------------------------------------------------------
# ext holds external symbols used by the dynamic linker.
#------------------------------------------------------------------------------
class ext(reg):
    _is_ext = True

    def __init__(self,refname,**kargs):
        self.ref = refname
        self._subrefs = kargs
        self.size = kargs.get('size',None)
        self.sf = False
        self._reg__protect = False
        self.type = regtype.OTHER

    def __str__(self):
        return '@%s'%self.ref

    def toks(self,**kargs):
        tk = render.Token.Tainted if '!' in self.ref else render.Token.Name
        return [(tk,str(self))]

    def __setattr__(self,a,v):
        exp.__setattr__(self,a,v)

    @classmethod
    def stub(cls,ref):
        try:
            return cls.stubs[ref]
        except AttributeError,KeyError:
            logger.info('no stub defined for %s'%ref)
            return (lambda env,**kargs:None)

    def call(self,env,**kargs):
        logger.info('stub %s called'%self.ref)
        if not 'size' in kargs: kargs.update(size=self.size)
        res = self.stub(self.ref)(env,**kargs)
        if res is None: return top(self.size)
        return res[0:self.size]

    # used when the expression is a target used to build a block
    def __call__(self,env):
        logger.info('stub %s called'%self.ref)
        self.stub(self.ref)(env,**self._subrefs)
##

#------------------------------------------------------------------------------
# lab holds labels/symbols, e.g. from relocations
#------------------------------------------------------------------------------
class lab(ext):
    _is_lab = True

#------------------------------------------------------------------------------
# composer returns a comp object (see below) constructed with parts from low
# significant bits parts to most significant bits parts. The last part sf flag
# propagates to the resulting comp.
#------------------------------------------------------------------------------
def composer(parts):
    assert len(parts)>0
    if len(parts)==1: return parts[0]
    s = sum([x.size for x in parts])
    c = comp(s)
    c.sf = parts[-1].sf
    pos = 0
    for x in parts:
        c[pos:pos+x.size] = x
        pos += x.size
    return c.simplify()

#------------------------------------------------------------------------------
# comp is used to represent expressions that are made of many parts (slices).
# each part is accessed by 'slicing' the comp to obtain another comp or atom.
# comp is the only expression that can be built adaptively.
#------------------------------------------------------------------------------
class comp(exp):
    __slots__ = ['smask','parts']
    _is_def   = True
    _is_cmp   = True

    def __init__(self,s):
        self.size = s
        self.sf   = False
        self.smask = [None]*self.size
        self.parts = {}
        # the symp is only obtained after a restruct !

    def __str__(self):
        s = '{ |'
        cur = 0
        for nv in self:
            nk = cur,cur+nv.size
            s += ' %s->%s |'%('[%d:%d]'%nk,str(nv))
            cur += nv.size
        return s+' }'

    def toks(self,**kargs):
        if 'indent' in kargs:
            p = kargs.get('indent',0)
            pad = '\n'.ljust(p+1)
            kargs['indent'] = p+4
        else:
            pad = ''
        tl = (render.Token.Literal,', ')
        s  = [(render.Token.Literal,'{')]
        cur=0
        for nv in self:
            loc = "%s[%2d:%2d] -> "%(pad,cur,cur+nv.size)
            cur += nv.size
            s.append((render.Token.Literal,loc))
            t = nv.toks(**kargs)
            s.extend(t)
            s.append(tl)
        if len(s)>1: s.pop()
        s.append((render.Token.Literal,'%s}'%pad))
        return s

    def eval(self,env):
        res = comp(self.size)
        res.smask = self.smask[:]
        for nk,nv in self.parts.iteritems(): res.parts[nk] = nv.eval(env)
        # now there may be raw numeric value in enode dict, so tiddy up:
        res.restruct()
        # once simplified, it may be reduced to 1 part, so:
        if res.parts.has_key((0,res.size)):
            res = res.parts[(0,res.size)]
        return res

    def copy(self):
        res = comp(self.size)
        res.smask = self.smask[:]
        for nk,nv in self.parts.iteritems(): res.parts[nk] = nv
        res.sf = self.sf
        return res

    def simplify(self):
        for nk,nv in self.parts.iteritems():
            self.parts[nk] = nv.simplify()
        self.restruct()
        if self.parts.has_key((0,self.size)):
            return self.parts[(0,self.size)]
        else:
            return self

    @_checkarg_slice
    def __getitem__(self,i):
        start = i.start or 0
        stop  = i.stop or self.size
        # see if the slice is exactly in the compound set:
        if self.parts.has_key((start,stop)): return self.parts[(start,stop)]
        if start==0 and stop==self.size: return self.copy()
        l = stop-start
        res = comp(l)
        b   = 0
        while b < l:
            # select symbol index and object:
            idx = self.smask[start]
            if idx is None:
                b += 1
                start += 1
                continue
            else: # idx is a slice keyed in enode dict
                s = self.parts[idx]
                # get slice for this symbol:
                deb = start-idx[0]
                fin = min(idx[1],stop)-idx[0]
                d = fin-deb
                res[b:b+d] = s[deb:fin]
                b += d
                start += d
        res.restruct()
        if len(res.parts.keys())==0: return slicer(self,start,stop-start)
        if len(res.parts.keys())==1: return res.parts.values()[0]
        return res
    ##

    @_checkarg_slice
    def __setitem__(self,i,v):
        sta = i.start or 0
        sto = i.stop or self.size
        l = sto-sta
        if v.size <> l : raise ValueError,'size mismatch'
        # make cmp always flat:
        if v._is_cmp:
            for vp,vv in v.parts.items():
                vsta,vsto = vp
                self[sta+vsta:sta+vsto] = vv
        else:
            # see if the slice is exactly in the compound set:
            if self.parts.has_key((sta,sto)):
                self.parts[(sta,sto)] = v
            else:
                self.parts[(sta,sto)] = v
                self.cut(sta,sto)

    # cut will scan the parts dict to find slices spanning over (start,stop)
    # then it will split them (inner parts are removed)
    def cut(self,start,stop):
        # update parts covered by (start,stop)
        maskset = []
        for nk in filter(None,self.smask[start:stop]):
            if not nk in maskset: maskset.append(nk)
        for nk in maskset:
            nv= self.parts.pop(nk)
            if nk[0] < start:
                self.parts[(nk[0],start)] = nv[0:start-nk[0]]
                self.smask[nk[0]:start] = [(nk[0],start)]*(start-nk[0])
            if nk[1] > stop :
                self.parts[(stop,nk[1])]  = nv[stop-nk[0]:nk[1]-nk[0]]
                self.smask[stop:nk[1]] = [(stop,nk[1])]*(nk[1]-stop)
            ##
        self.smask[start:stop] = [(start,stop)]*(stop-start)
    ##

    def __iter__(self):
        # gather cst as possible:
        rcmp = lambda x,y: cmp(x[0],y[0])
        part = self.parts.keys()
        part.sort(rcmp)
        cur = 0
        for p in part:
            assert p[0]==cur
            yield self.parts[p]
            cur = p[1]

    # restruct will concatenate cst expressions when possible
    # to minimize the number of parts.
    def restruct(self):
        # gather cst as possible:
        rcmp = lambda x,y: cmp(x[0],y[0])
        part = self.parts.keys()
        part.sort(rcmp)
        for i in range(len(part)-1):
            ra = part[i]
            rb = part[i+1]
            if ra[1]==rb[0]:
                na = self.parts[ra]
                nb = self.parts[rb]
                if na._is_cst and nb._is_cst:
                    v = (nb.v<<ra[1])|(na.v)
                    self.parts[(ra[0],rb[1])] = cst(v,rb[1]-ra[0])
                    self.parts.pop(ra)
                    self.parts.pop(rb)
                    self.smask[ra[0]:rb[1]] = [(ra[0],rb[1])]*(rb[1]-ra[0])
                    self.restruct()
                    break
                elif not (na._is_def or nb._is_def):
                    self.parts[(ra[0],rb[1])] = top(rb[1]-ra[0])
                    self.parts.pop(ra)
                    self.parts.pop(rb)
                    self.smask[ra[0]:rb[1]] = [(ra[0],rb[1])]*(rb[1]-ra[0])
                    self.restruct()
                    break
    ##

    def depth(self):
        return sum((p.depth() for p in self))
    ##

#------------------------------------------------------------------------------
# mem holds memory fetches, ie a read operation of length size, in segment seg,
# at given address expression.
# The mods list allows to handle aliasing issues detected at fetching time
# and adjust the eval result accordingly.
#------------------------------------------------------------------------------
class mem(exp):
    __slots__ = ['a', 'mods']
    _is_def   = True
    _is_mem   = True

    def __init__(self,a,size=32,seg='',disp=0,mods=None):
        self.size  = size
        self.sf    = False
        self.a  = ptr(a,seg,disp)
        self.mods = mods or []

    def __str__(self):
        n = len(self.mods)
        n = '$%d'%n if n>0 else ''
        return 'M%d%s%s'%(self.size,n,self.a)

    def toks(self,**kargs):
        return [(render.Token.Memory,str(self))]

    def eval(self,env):
        a = self.a.eval(env)
        m = env.use()
        for loc,v in self.mods:
            if loc._is_ptr: loc = env(loc)
            m[loc] = env(v)
        return m[mem(a,self.size)]

    def simplify(self):
        self.a.simplify()
        return self

    def addr(self,env):
        return self.a.eval(env)


#------------------------------------------------------------------------------
# ptr holds memory addresses with segment, base expressions and
# displacement integer (offset relative to base).
#------------------------------------------------------------------------------
class ptr(exp):
    __slots__ = ['base','disp','seg']
    _is_def   = True
    _is_ptr   = True

    def __init__(self,base,seg='',disp=0):
        if base._is_ptr:
            if seg is '': seg=base.seg
            disp = base.disp+disp
            base = base.base
        self.base,offset = extract_offset(base)
        self.disp = disp+offset
        self.seg  = seg
        self.size = base.size
        self.sf   = False

    def __str__(self):
        d = self.disp_tostring()
        return '%s(%s%s)'%(self.seg,self.base,d)

    def disp_tostring(self,base10=True):
        if self.disp==0: return ''
        if base10: return '%+d'%self.disp
        c = cst(self.disp,self.size)
        c.sf=False
        return '+%s'%str(c)

    def toks(self,**kargs):
        return [(render.Token.Address,str(self))]

    def simplify(self):
        self.base,offset = extract_offset(self.base)
        self.disp += offset
        if isinstance(self.seg,exp):
            self.seg = self.seg.simplify()
        if not self.base._is_def: self.disp=0
        return self

    # default segment handler does not care about seg value:
    @staticmethod
    def segment_handler(env,s,bd):
        base,disp = bd
        return ptr(base,s,disp)

    def eval(self,env):
        a = self.base.eval(env)
        s = self.seg
        if isinstance(s,exp):
            s = s.eval(env)
        return self.segment_handler(env,s,(a,self.disp))

#------------------------------------------------------------------------------
# slicer is slc class wrapper that deals with slicing the entire expression
#------------------------------------------------------------------------------
def slicer(x,pos,size):
    if not isinstance(x,exp): raise TypeError,x
    if not x._is_def: return top(size)
    if pos==0 and size==x.size:
        return x
    else:
        if x._is_mem and size%8==0:
            off,rst = divmod(pos,8)
            if rst==0:
                a = ptr(x.a.base,x.a.seg,x.a.disp+off)
                return mem(a,size)
        elif x._is_cmp:
            return x[pos:pos+size]
        return slc(x,pos,size)

#------------------------------------------------------------------------------
# slc holds bit-slice of a non-cst (and non-slc) expressions
#------------------------------------------------------------------------------
class slc(exp):
    __slots__ = ['x','pos','ref','__protect','_is_reg']
    _is_def   = True
    _is_slc   = True

    def __init__(self,x,pos,size,ref=None):
        if not isinstance(pos,(int,long)): raise TypeError,pos
        if isinstance(x,slc):
            res = x[pos:pos+size]
            x,pos = res.x,res.pos
        self.x = x
        self.__protect = False
        self.size = size
        self.sf   = False
        self.pos  = pos
        self.setref(ref)

    def setref(self,ref):
        self._is_reg = False
        if self.x._is_reg:
            self._is_reg = True
            if ref is None:
                ref = self.x._subrefs.get((self.pos,self.size),None)
            else:
                self.x._subrefs[(self.pos,self.size)] = ref
            self.__protect = True
        self.ref = ref

    @property
    def type(self):
        if self._is_reg: return self.x.type

    def raw(self):
        return "%s[%d:%d]"%(str(self.x),self.pos,self.pos+self.size)

    def __setattr__(self,a,v):
        if a is 'size' and self.__protect is True:
            raise AttributeError,'protected attribute'
        exp.__setattr__(self,a,v)

    def __str__(self):
        return self.ref or self.raw()

    def toks(self,**kargs):
        if self._is_reg: return [(render.Token.Register,str(self))]
        subpart = [(render.Token.Literal,'[%d:%d]'%(self.pos,self.pos+self.size))]
        return self.x.toks(**kargs)+subpart

    def __hash__(self): return hash(self.raw())

    def depth(self): return 2*self.x.depth()

    def eval(self,env):
        n = self.x.eval(env)
        return n[self.pos:self.pos+self.size]

    # slc of mem objects are simplified by adjusting the disp offset of
    # the sliced mem object.
    def simplify(self):
        self.x = self.x.simplify()
        if not self.x._is_def: return top(self.size)
        if self.x._is_mem and self.size%8==0:
            off,rst = divmod(self.pos,8)
            if rst==0:
                a = ptr(self.x.a.base,self.x.a.seg,self.x.a.disp+off)
                return mem(a,self.size)
        if self.x._is_eqn and self.x.op.type==2:
            r = self.x.r[self.pos:self.pos+self.size]
            if self.x.op.unary:
                return self.x.op(r)
            l = self.x.l[self.pos:self.pos+self.size]
            return self.x.op(l,r)
        else:
            return self

    # slice of a slice:
    @_checkarg_slice
    def __getitem__(self,i):
        if i.start==0 and i.stop==self.size:
            return self
        else:
            start = self.pos+i.start
            return slicer(self.x,start,i.stop-i.start)
    ##
    # simplify: the only simplification would apply on slc'ed expression x
    # but x can't be of type slc...
    def addr(self,env):
        if self.x._is_mem:
            a = self.x.addr(env)
            a.disp = self.pos
            return a
        elif self.x._is_reg:
            return self.x
        else:
            raise TypeError('this expression is not a location')

    def __setstate__(self,state):
        v = state[1]
        self.__protect = False
        self.size = v['size']
        self.sf = v['sf']
        self.x = v['x']
        self.pos = v['pos']
        self.ref = v['ref']
        self._is_reg = v['_is_reg']
        self.__protect = v['_slc__protect']
##

#------------------------------------------------------------------------------
# tst holds a conditional expression: l if test==1 else r
#------------------------------------------------------------------------------
class tst(exp):
    __slots__ = ['tst','l','r']
    _is_def   = True
    _is_tst   = True

    def __init__(self,t,l,r):
        if t is True or t is False: t=cst(t,1)
        self.tst = t   # the expression to test, probably a 'op' expressions.
        if l.size<>r.size: raise ValueError,(l,r)
        self.l  = l    # true (tst evals to val)
        self.r  = r    # false
        self.size = self.l.size
        self.sf   = False
    ##
    def __str__(self):
        return '(%s ? %s : %s)'%(str(self.tst),str(self.l),str(self.r))

    def toks(self,**kargs):
        ttest  = self.tst.toks(**kargs)
        ttest.append((render.Token.Literal,' ? '))
        ttrue  = self.l.toks(**kargs)
        ttrue.append((render.Token.Literal,' : '))
        tfalse = self.r.toks(**kargs)
        return ttest+ttrue+tfalse

    # default verify method if smt module is not loaded.
    # here we check if tst or its negation exist in env.conds but we can
    # only rely on "syntaxic" features unless we have a solver.
    # see smt.py: tst_verify() for a SMT-based implementation.
    def verify(self,env):
        flag = self.tst.eval(env)
        for c in env.conds:
            if c==flag:
                flag=bit1
                break
            if c==(~flag):
                flag=bit0
                break
        return flag

    def eval(self,env):
        cond = self.verify(env)
        l = self.l.eval(env)
        r = self.r.eval(env)
        if not cond._is_cst:
            return tst(cond,l,r)
        if cond.v == 1: return l
        else          : return r

    def simplify(self):
        if self.l == self.r: return self.l
        self.tst = self.tst.simplify()
        self.l   = self.l.simplify()
        self.r   = self.r.simplify()
        if   self.tst==bit1: return self.l
        elif self.tst==bit0: return self.r
        if not self.tst._is_def:
            return vec([self.l,self.r]).simplify()
        return self

    def depth(self):
        return (self.tst.depth()+self.l.depth()+self.r.depth())/3.


#------------------------------------------------------------------------------
# oper returns a possibly simplified op() object (see below)
#------------------------------------------------------------------------------
def oper(opsym,l,r=None):
    if r is None: return uop(opsym,l).simplify()
    return op(opsym,l,r).simplify()

#------------------------------------------------------------------------------
# op holds binary integer arithmetic and bitwise logic expressions
#------------------------------------------------------------------------------
class op(exp):
    __slots__ = ['op','l','r','prop']
    _is_def   = True
    _is_eqn   = True

    def __init__(self,op,l,r):
        self.op = _operator(op)
        self.prop = self.op.type
        if self.prop<4:
            if l.size <> r.size:
                raise ValueError("Size mismatch %d <> %d"%(l.size,r.size))
        self.l  = l
        self.r  = r
        self.size = self.l.size
        if self.prop==4:
            self.size=1
        elif self.op.symbol in ['**']: self.size *= 2
        self.sf = l.sf
        if self.prop==1: self.sf |= r.sf
        if self.l._is_eqn: self.prop |= self.l.prop
        if self.r._is_eqn : self.prop |= self.r.prop

    @classmethod
    def limit(cls,v):
        cls.threshold = v

    def eval(self,env):
        # single-operand :
        l = self.l.eval(env)
        r = self.r.eval(env)
        res = self.op(l,r)
        res.sf = self.sf
        return res
    ##

    def __str__(self):
        return '(%s%s%s)'%(str(self.l),self.op.symbol,str(self.r))

    def toks(self,**kargs):
        l = self.l.toks(**kargs)
        l.insert(0,(render.Token.Literal,'('))
        r = self.r.toks(**kargs)
        r.append((render.Token.Literal,')'))
        return l+[(render.Token.Literal,self.op.symbol)]+r

    def simplify(self):
        l = self.l.simplify()
        r = self.r.simplify()
        minus = (self.op.symbol=='-')
        if self.prop<4:
            if l._is_def==0: return l
            if r._is_def==0: return r
            # arithm/logic normalisation:
            # push cst to the right
            if l._is_cst:
                if r._is_cst: return self.op(l,r)
                if minus:
                    l,r = (-r),l
                    self.op = _operator('+')
                else:
                    l,r = r,l
            # lexical ordering of symbols:
            elif not r._is_cst:
                lh = ''.join(map(str,symbols_of(l)))
                rh = ''.join(map(str,symbols_of(r)))
                if lh>rh:
                    if minus:
                        l,r = (-r),l
                        self.op = _operator('+')
                    else:
                        l,r=r,l
        self.l = l
        self.r = r
        return eqn2_helpers(self)

    def depth(self):
        return self.l.depth()+self.r.depth()

##

#------------------------------------------------------------------------------
# uop holds unary operations (+x, -x, ~x)
#------------------------------------------------------------------------------
class uop(exp):
    __slots__ = ['op','r','prop']
    _is_def   = True
    _is_eqn   = True

    def __init__(self,op,r):
        self.op = _operator(op,unary=1)
        self.prop = self.op.type
        self.r  = r
        self.size = r.size
        self.sf = r.sf
        if self.r._is_eqn: self.prop |= self.r.prop

    def eval(self,env):
        # single-operand :
        r = self.r.eval(env)
        res = self.op(r)
        res.sf = self.sf
        return res
    ##

    @property
    def l(self): return None

    def __str__(self):
        return '(%s%s)'%(self.op.symbol,str(self.r))

    def toks(self,**kargs):
        r = self.r.toks(**kargs)
        r.append((render.Token.Literal,')'))
        return [(render.Token.Literal,'(%s'%self.op.symbol)]+r

    def simplify(self):
        r = self.r.simplify()
        if r._is_def==0: return r
        self.r = r
        return eqn1_helpers(self)

    def depth(self):
        return self.r.depth()

##
# operators:
#-----------

import operator

def ror(x,n):
    return (x>>n | x<<(x.size-n)) if x._is_cst else op('>>>',x,n)

def rol(x,n):
    return (x<<n | x>>(x.size-n)) if x._is_cst else op('<<<',x,n)

OP_ARITH = {'+'  : operator.add,
            '-'  : operator.sub,
            '*'  : operator.mul,
            '**' : operator.pow,
            '/'  : operator.div,
            '%'  : operator.mod,
           }
OP_LOGIC = {'&'  : operator.and_,
            '|'  : operator.or_,
            '^'  : operator.xor,
            '~'  : operator.invert,
           }
OP_CONDT = {'==' : operator.eq,
            '!=' : operator.ne,
            '<=' : operator.le,
            '>=' : operator.ge,
            '<'  : operator.lt,
            '>'  : operator.gt,
           }
OP_SHIFT = {'>>' : operator.rshift, # logical shift right (see cst.value)
            '<<' : operator.lshift,
            '//' : operator.floordiv, # this is arithmetic shift right
            '>>>': ror,
            '<<<': rol
           }

class _operator(object):
    def __init__(self,op,unary=0):
        self.symbol = op
        self.unary = unary
        if   op in OP_ARITH:
            self.type = 1
            if self.unary:
                self.impl = {'+': operator.pos, '-': operator.neg}[op]
            else:
                self.impl = OP_ARITH[op]
        elif op in OP_LOGIC:
            self.type = 2
            if self.unary: assert op == '~'
            self.impl = OP_LOGIC[op]
        elif op in OP_CONDT:
            self.type = 4
            self.impl = OP_CONDT[op]
        elif op in OP_SHIFT:
            self.type = 8
            self.impl = OP_SHIFT[op]
        else:
            raise NotImplementedError

    def __call__(self,l,r=None):
        if r  is None:
            assert self.unary
            return self.impl(l)
        return self.impl(l,r)

    def __mul__(self,op):
        ss = self.symbol+op.symbol
        if ss in ('++','--'): return '+'
        if ss in ('+-','-+'): return '-'
        return None

# basic simplifier:
#------------------

def configure(**kargs):
    from amoco.config import get_module_conf
    conf = get_module_conf('cas')
    conf.update(kargs)
    if conf['complexity']:
        op.limit(conf['complexity'])

configure()

def symbols_of(e):
    if e is None: return []
    if e._is_cst: return []
    if e._is_reg: return [e]
    if e._is_mem: return symbols_of(e.a.base)
    if e._is_ptr: return symbols_of(e.base)
    if e._is_eqn: return symbols_of(e.l)+symbols_of(e.r)
    if e._is_tst: return sum(map(symbols_of,(e.tst,e.l,e.r)),[])
    if e._is_slc: return symbols_of(e.x)
    if e._is_cmp: return sum(map(symbols_of,e.parts.itervalues()),[])
    if e._is_vec: return sum(map(symbols_of,e.l),[])
    if not e._is_def: return []
    raise ValueError(e)

def locations_of(e):
    if e is None: return []
    if e._is_cst: return []
    if e._is_reg: return [e]
    if e._is_mem: return [e]
    if e._is_ptr: return [e]
    if e._is_eqn: return locations_of(e.l)+locations_of(e.r)
    if e._is_tst: return sum(map(locations_of,(e.tst,e.l,e.r)),[])
    if e._is_slc: return locations_of(e.x)
    if e._is_cmp: return sum(map(locations_of,e.parts.itervalues()),[])
    if e._is_vec: return sum(map(locations_of,e.l),[])
    if not e._is_def: return []
    raise ValueError(e)

def complexity(e):
    factor = e.prop if e._is_eqn else 1
    return (e.depth()+len(locations_of(e)))*factor

# helpers for unary expressions:
def eqn1_helpers(e):
    assert e.op.unary
    if e.r._is_cst:
        return e.op(e.r)
    if e.r._is_vec:
        return vec(map(e.op,e.r.l))
    if e.r._is_eqn:
        if e.r.op.unary:
            ss = e.op*e.r.op
            if   ss == '+': return e.r.r
            elif ss == '-': return -e.r.r
        elif e.op.symbol == '-':
            if e.r.op.symbol in ('-','+'):
                l = -e.r.l
                r = e.r.r
                return OP_ARITH[e.op*e.r.op](l,r)
        elif e.op.symbol == '~' and e.r.op.type==4:
            notop = {'==':'!=', '!=':'==',
                     '<':'>=' , '>' :'<=',
                     '<=':'>' , '>=':'<'}[e.r.op.symbol]
            return OP_CONDT[notop](e.r.l,e.r.r)
    return e

# helpers for binary expressions:
# reminder: be careful not to modify the internal structure of
# e.l or e.r because these objects might be used also in other
# expressions. See tests/test_cas_exp.py for details.
def eqn2_helpers(e):
    if complexity(e.r)>e.threshold: e.r = top(e.r.size)
    if complexity(e.l)>e.threshold: e.l = top(e.l.size)
    if not (e.r._is_def and e.l._is_def): return top(e.size)
    if e.l._is_eqn and e.l.r._is_cst and e.l.op.unary==0:
        xop = e.op*e.l.op
        if xop:
            e.op,lop = e.l.op,e.op
            lr,e.r   = e.r,e.l.r
            e.l = lop(e.l.l,lr)
    if e.r._is_eqn and e.r.op.unary:
        if e.op.symbol == '+' and e.r.op.symbol == '-':
            e.op = _operator('-')
            e.r  = e.r.r
    if e.r._is_eqn and e.r.r._is_cst:
        xop = e.op*e.r.op
        if xop:
            e.l = e.op(e.l,e.r.l)
            e.r = e.r.r
            e.op = _operator(xop)
    if e.r._is_cst:
        if e.r.value==0:
            if e.op.symbol in ('|','^','+','-','>>','<<','>>>','<<<'):
                return e.l
            if e.op.symbol in ('&','*'):
                return cst(0,e.size)
        elif e.r.value==1 and e.op.symbol in ('*','/'):
            return e.l
        if e.l._is_eqn:
            xop = e.op*e.l.op
            if xop:
                if e.l.r._is_cst:
                    cc = OP_ARITH[xop](e.l.r,e.r)
                    e.op = e.l.op
                    if not e.l.op.unary: e.l = e.l.l
                    e.r = cc
                return e
            elif e.r.size==1:
                if e.op.symbol == '==':
                    return e.l if e.r.value==1 else ~(e.l)
                if e.op.symbol == '!=':
                    return ~(e.l) if e.r.value==1 else ~(e.l)
        elif e.l._is_ptr:
            if e.op.symbol in ('-','+'):
                return ptr(e.l,disp=e.op(0,e.r.value))
        elif e.l._is_cst:
            return e.op(e.l,e.r)
    if e.l._is_vec:
        return vec([e.op(x,e.r) for x in e.l.l]).simplify()
    if e.r._is_vec:
        return vec([e.op(e.l,x) for x in e.r.l]).simplify()
    if str(e.l)==str(e.r):
        if e.op.symbol in ('!=','<', '>' ): return bit0
        if e.op.symbol in ('==','<=','>='): return bit1
        if e.op.symbol is '-' : return cst(0,e.size)
        if e.op.symbol is '^' : return cst(0,e.size)
        if e.op.symbol is '&' : return e.l
        if e.op.symbol is '|' : return e.l
    return e

# separate expression e into (e' + C) with C cst offset.
def extract_offset(e):
    x = e.simplify()
    if x._is_eqn and x.r._is_cst:
        if e.op.symbol == '+':
            return (x.l,x.r.value)
        elif e.op.symbol == '-':
            return (x.l,-x.r.value)
    return (x,0)

# vec holds a list of expressions each being a possible
# representation of the current expression. A vec object
# is obtained by merging several execution paths using
# the merge function in the mapper module.
# The simplify method uses the complexity measure to
# eventually "reduce" the expression to top with a hard-limit
# currently set to op.threshold.
# -----------------------------------------------------
class vec(exp):
    __slots__ = ['l']
    _is_def = True
    _is_vec = True

    def __init__(self,l=None):
        if l is None: l = []
        self.l = l
        size = 0
        for e in self.l:
            if e.size>size: size=e.size
        if any([e.size!=size for e in self.l]):
            raise ValueError,'size mismatch'
        self.size = size
        self.sf = any([e.sf for e in self.l])

    def __str__(self):
        s = ','.join(map(str,self.l))
        return '[%s]'%(s)

    def toks(self,**kargs):
        t = []
        for x in self.l:
            t.extend(x.toks(**kargs))
            t.append((render.Token.Literal,', '))
        if len(t)>0: t.pop()
        t.insert(0,(render.Token.Literal,'['))
        t.append((render.Token.Literal,']'))
        return t

    def simplify(self,widening=False):
        l = []
        for e in self.l:
            ee = e.simplify()
            if ee._is_vec:
                l.extend(ee.l)
                if isinstance(ee,vecw):
                    widening = True
            else: l.append(ee)
        self.l = []
        for e in l:
            if e in self.l: continue
            self.l.append(e)
        if len(self.l)==1:
            return self.l[0]
        if widening:
            return vecw(self)
        cl = map(complexity,self.l)
        if sum(cl,0.)>op.threshold:
            return top(self.size)
        return self

    def eval(self,env):
        l = []
        for e in self.l:
            l.append(e.eval(env))
        return vec(l)

    def depth(self):
        if self.size==0: return 0.
        return max([e.depth() for e in self.l])

    @_checkarg_slice
    def __getitem__(self,i):
        sta,sto,stp = i.indices(self.size)
        l = []
        for e in self.l:
            l.append(e[sta:sto])
        return vec(l)

    def __contains__(self,x):
        return (x in self.l)

    def __nonzero__(self):
        return all([e.__nonzero__() for e in self.l])

class vecw(top):
    __slots__ = ['l']
    _is_def = 0
    _is_vec = True

    def __init__(self,v):
        self.l = v.l
        self.size = v.size
        self.sf = False

    def __str__(self):
        s = ','.join(map(str,self.l))
        return '[%s, ...]'%(s)

    def toks(self,**kargs):
        t = []
        for x in self.l:
            t.extend(x.toks(**kargs))
            t.append((render.Token.Literal,', '))
        if len(t)>0: t.pop()
        t.insert(0,(render.Token.Literal,'['))
        t.append((render.Token.Literal,', ...]'))
        return t

    def eval(self,env):
        v = vec([x.eval(env) for x in self.l])
        return vecw(v)

    @_checkarg_slice
    def __getitem__(self,i):
        sta,sto,stp = i.indices(self.size)
        l = []
        for e in self.l:
            l.append(e[sta:sto])
        return vecw(vec(l))
##
