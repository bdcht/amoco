# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

from amoco.logger import Log
logger = Log(__name__)

# decorators:
#------------

def _checkarg1_exp(f):
    def checkarg1_exp(*args):
        if len(args)>0 and isinstance(args[0],exp):
            return f(*args)
        else:
            raise TypeError('arg is not an expression')
    return checkarg1_exp

def _checkarg_sizes(f):
    def checkarg_sizes(self,n):
        if self.size<>n.size:
            if self.size>0 and n.size>0: raise ValueError,'size mismatch'
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
                    raise ValueError,i
            if i.stop<=i.start: raise ValueError,i
        else:
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
    _is_def   = False
    _is_cst   = False
    _is_reg   = False
    _is_cmp   = False
    _is_slc   = False
    _is_mem   = False
    _is_ext   = False
    _is_ptr   = False
    _is_tst   = False
    _is_eqn   = False

    def __init__(self,size=0,sf=False):
        self.size = size
        self.sf   = False

    def __len__(self): return self.length

    @property
    def length(self): # length value is in bytes
        return self.size/8

    @property
    def mask(self):
        return (1<<self.size)-1

    def eval(self,env):
        if not self._is_def: return exp(self.size)
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

    def __str__(self):
        if self._is_def is 0: return 'T'
        if self._is_def is False: return '_'
        raise ValueError("void expression")

    def bit(self,i):
        i = i%self.size
        return self[i:i+1]

    # get item allows to extract the expression of a slice of the exp
    def __getitem__(self,i)  :
        if isinstance(i,slice):
            return slicer(self,i.start,i.stop-i.start)
        else:
            raise TypeError,i

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
    def __invert__(self): return oper('~',self)
    def __neg__(self): return oper('*',self,cst(-1,self.size))

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
# flt holds float immediate values
#---------------------------------
class flt(exp):
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
    __slots__ = ['ref','_subrefs']
    _is_def   = True
    _is_reg   = True

    def __init__(self,refname,size=32):
        self.size = size
        self.sf  = False
        self.ref = refname
        self._subrefs = {}

    @_checkarg_slice
    def __getitem__(self,i):
        if i.start==0 and i.stop==self.size: return self
        else: return slicer(self,i.start,i.stop-i.start)

    def __str__(self):
        return self.ref

    def eval(self,env):
        return env[self]

    def addr(self,env):
        return self
##

#------------------------------------------------------------------------------
# ext holds external symbols used by the dynamic linker.
#------------------------------------------------------------------------------
class ext(reg):
    _is_ext = True

    def __str__(self):
        return '@%s'%self.ref

    @classmethod
    def stub(cls,ref):
        try:
            return cls.stubs[ref]
        except KeyError:
            logger.info('no stub defined for %s'%ref)
            return (lambda env:None)

    def call(self,env):
        logger.info('stub %s called'%self.ref)
        res = self.stub(self.ref)(env)
        if res is None:
            return top(self.size)
        else:
            return res[0:self.size]
##

# complex expressions are build with atoms attributes:
# ----------------------------------------------------

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
        for nk,nv in self.parts.iteritems():
            s += ' %s->%s |'%('[%d:%d]'%nk,str(nv))
        return s+' }'

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
    ##
##

#------------------------------------------------------------------------------
# mem holds memory fetches, ie a read operation of length size, in segment seg,
# at given address expression.
#------------------------------------------------------------------------------
class mem(exp):
    __slots__ = ['a']
    _is_def   = True
    _is_mem   = True

    def __init__(self,a,size=32,seg='',disp=0):
        self.size  = size
        self.sf    = False
        self.a  = a if isinstance(a,ptr) else ptr(a,seg,disp)

    def __str__(self):
        return 'M%d%s'%(self.size,self.a)

    def eval(self,env):
        a = self.a.eval(env)
        return env[mem(a,self.size)]

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
        assert base._is_def
        self.base = base
        self.disp = disp
        self.seg  = seg
        self.size = base.size
        self.sf   = False

    def __str__(self):
        d = '%+d'%self.disp if self.disp else ''
        return '%s(%s%s)'%(self.seg,self.base,d)

    def simplify(self):
        self.base = self.base.simplify()
        if isinstance(self.seg,exp):
            self.seg = self.seg.simplify()
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
    if pos==0 and size==x.size:
        return x
    else:
        if x._is_mem:
            a = ptr(x.a.base,x.a.seg,x.a.disp+pos)
            return mem(a,size)
        return slc(x,pos,size)

#------------------------------------------------------------------------------
# slc holds bit-slice of a non-cst (and non-slc) expressions 
#------------------------------------------------------------------------------
class slc(exp):
    __slots__ = ['x','pos','ref']
    _is_def   = True
    _is_slc   = True

    def __init__(self,x,pos,size,ref=None):
        if not isinstance(pos,(int,long)): raise TypeError,pos
        if isinstance(x,slc):
            res = x[pos:pos+size]
            x,pos = res.x,res.pos
        self.x = x
        self.size = size
        self.sf   = False
        self.pos  = pos
        self.setref(ref)

    def setref(self,ref):
        if self.x._is_reg:
            if ref is None:
                ref = self.x._subrefs.get((self.pos,self.size),None)
            else:
                self.x._subrefs[(self.pos,self.size)] = ref
        self.ref = ref

    def raw(self):
        return "%s[%d:%d]"%(str(self.x),self.pos,self.pos+self.size)

    def __str__(self):
        return self.ref or self.raw()
    ##
    def __hash__(self): return hash(self.raw())

    def eval(self,env):
        n = self.x.eval(env)
        return n[self.pos:self.pos+self.size]

    def simplify(self):
        self.x = self.x.simplify()
        if self.x._is_mem:
            a = ptr(self.x.a.base,self.x.a.seg,self.x.a.disp+self.pos)
            return mem(a,self.size)
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
##

#------------------------------------------------------------------------------
# tst holds a conditional expression: l if test==1 else r
#------------------------------------------------------------------------------
class tst(exp):
    __slots__ = ['tst','l','r']
    _is_def   = True
    _is_tst   = True

    def __new__(cls,t,l,r):
        if t is True or t==1: return l
        if t is False or t==0: return r
        obj=super(exp,cls).__new__(cls)
        tst.__init__(obj,t,l,r)
        return obj

    def __init__(self,t,l,r):
        if t in [True,False]: t=cst(t)
        self.tst = t   # the expression to test, probably a 'op' expressions.
        if l.size<>r.size: raise ValueError,(l,r)
        self.l  = l    # true (tst evals to val)
        self.r  = r    # false
        self.size = self.l.size
        self.sf   = False
    ##
    def __str__(self):
        return '(%s ? %s : %s)'%(str(self.tst),str(self.l),str(self.r))

    def eval(self,env):
        flag = self.tst.eval(env)
        l = self.l.eval(env)
        r = self.r.eval(env)
        if not flag._is_cst:
            return tst(flag,l,r)
        if flag.v == 1: return l
        else          : return r

    def simplify(self):
        self.tst = self.tst.simplify()
        self.l   = self.l.simplify()
        self.r   = self.r.simplify()
        if   self.tst==bit1: return self.l
        elif self.tst==bit0: return self.r
        return self


#------------------------------------------------------------------------------
# oper returns a possibly simplified op() object (see below)
#------------------------------------------------------------------------------
def oper(opsym,l,r=None):
    return op(opsym,l,r).simplify()

#------------------------------------------------------------------------------
# op holds binary operations, integer arithmetic and bitwise logic
# internal representation is either in tree form or flat form (std=True).
#------------------------------------------------------------------------------
class op(exp):
    __slots__ = ['op','l','r','prop']
    _is_def   = True
    _is_eqn   = True

    def __init__(self,op,l,r=None):
        self.op = _operator(op)
        self.prop = self.op.type
        if r is not None and self.prop<4 and l.size <> r.size:
            raise ValueError,"size mismatch"
        self.l  = l
        self.r  = r
        self.size = self.l.size
        if self.prop==4:
            self.size=1
        elif self.op.symbol in ['**']: self.size *= 2
        self.sf = l.sf
        if self.l._is_eqn: self.prop |= self.l.prop
        if self.r is not None:
            if self.prop==1: self.sf |= r.sf
            if self.r._is_eqn : self.prop |= self.r.prop

    @classmethod
    def limit(cls,v):
        cls.threshold = v

    def eval(self,env):
        # single-operand :
        l = self.l.eval(env)
        r = None
        if self.r is not None:
            r = self.r.eval(env)
        res = self.op(l,r)
        res.sf = self.sf
        return res
    ##

    def __str__(self):
        if self.r is None:
            return '(%s%s)'%(self.op.symbol,str(self.l))
        else:
            return '(%s%s%s)'%(str(self.l),self.op.symbol,str(self.r))

    def simplify(self):
        self.l = self.l.simplify()
        if self.r is not None:
            self.r = self.r.simplify()
            return eqn_helpers(self)
        return self

    def depth(self):
        if self.r is not None: d = self.r.depth()
        else: d = 0.
        return self.l.depth()+d

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
   def __init__(self,op):
       self.symbol = op
       if   op in OP_ARITH:
           self.type = 1
           self.impl = OP_ARITH[op]
       elif op in OP_LOGIC:
           self.type = 2
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
           impl = {'+': operator.pos, '-': operator.neg}.get(self.symbol,self.impl)
           return impl(l)
       return self.impl(l,r)

   def __mul__(self,op):
       ss = self.symbol+op.symbol
       if ss in ('++','--'): return '+'
       if ss in ('+-','-+'): return '-'
       return None

# basic simplifier:
#------------------

op.limit(30)

def symbols_of(e):
   if e is None: return []
   if e._is_cst: return []
   if e._is_reg: return [e]
   if e._is_mem: return symbols_of(e.a.base)
   if e._is_eqn: return symbols_of(e.l)+symbols_of(e.r)
   # tst/slc/comp cases:
   if isinstance(e,tst): return sum(map(symbols_of,(e.tst,e.l,e.r)),[])
   if isinstance(e,slc): return symbols_of(e.x)
   return sum(map(symbols_of,e.parts.itervalues()),[])

def complexity(e):
   return e.depth()+len(symbols_of(e))

def eqn_helpers(e):
    if e.r is None: return e
    if hasattr(e,'threshold'):
        if e.l.depth()>e.threshold: e.l = top(e.l.size)
        if e.r.depth()>e.threshold: e.r = top(e.r.size)
    if False in (e.l._is_def, e.r._is_def): return top(e.size)
    if e.l._is_cst and e.r._is_cst:
        return e.op(e.l,e.r)
    if e.l is e.r:
        if e.op.symbol in ('!=','<', '>' ): return bit0
        if e.op.symbol in ('==','<=','>='): return bit1
        if e.op.symbol is '-' : return cst(0,e.size)
        if e.op.symbol is '^' : return cst(0,e.size)
        if e.op.symbol is '&' : return e.l
        if e.op.symbol is '|' : return e.l
    if e.l._is_cst:
        if e.l.value==0:
            if e.op.symbol in ('*','&','>>','<<','>>>','<<<'):
                return cst(0,e.size)
            if e.op.symbol in ('|','^','+'):
                return e.r
        elif e.l.value==1 and e.op.symbol=='*':
            return e.r
        elif e.r._is_eqn:
            xop = e.op*e.r.op
            if xop:
                if e.r.l._is_cst:
                    cc = e.op(e.l,e.r.l)
                    return op(xop, cc, e.r.r)
                elif e.r.r._is_cst:
                    cc = OP_ARITH[xop](e.l, e.r.r)
                    e.l = cc
                    e.r = e.r.l
            return e
    if e.r._is_cst:
        if e.r.value==0:
            if e.op.symbol in ('|','^','+','-','>>','<<','>>>','<<<'):
                return e.l
            if e.op.symbol in ('&','*'):
                return cst(0,e.size)
        elif e.r.value==1 and e.op.symbol in ('*','/'):
            return e.l
        elif e.l._is_eqn:
            xop = e.op*e.l.op
            if xop:
                if e.l.l._is_cst:
                    cc = e.op(e.l.l,e.r)
                    e.r = e.l.r
                    e.op = e.l.op
                    e.l = cc
                elif e.l.r._is_cst:
                    cc = OP_ARITH[xop](e.l.r,e.r)
                    e.op = e.l.op
                    e.l = e.l.l
                    e.r = cc
    return e

# expression parser:
#-------------------

import pyparsing as pp

#terminals:
p_bottop  = pp.oneOf('_ T')
p_symbol  = pp.Word(pp.alphas)
p_extern  = pp.Suppress('@')+p_symbol
p_cst     = pp.Suppress('0x')+pp.Combine(pp.Optional('-')+pp.Regex('[0-9a-f]+'))
p_int     = pp.Word(pp.nums).setParseAction(lambda r:int(r[0]))
p_slc     = '['+p_int.setResultsName('start')+':'+p_int.setResultsName('stop')+']'
p_op1     = pp.oneOf('~ -')
p_op2     = pp.oneOf('+ - / // * & | ^ << >> < > == <= >= != ? :')
p_term    = p_bottop|p_symbol|p_extern|p_cst

#nested expressions:
p_expr    = pp.Forward()

p_csl     = pp.Suppress('|')+p_slc+pp.Suppress('->')
p_comp    = pp.Group(pp.Suppress('{')+pp.ZeroOrMore(p_expr)+pp.Suppress('| }'))
p_mem     = 'M'+p_int+pp.Optional(p_symbol)

operators = [(p_op1,1,pp.opAssoc.RIGHT),
             (p_mem,1,pp.opAssoc.RIGHT),
             (p_slc,1,pp.opAssoc.LEFT),
             (p_op2,2,pp.opAssoc.LEFT),
             (p_csl,1,pp.opAssoc.RIGHT),
            ]

p_expr   << pp.operatorPrecedence(p_term|p_comp,operators)

p_bottop.setParseAction(lambda r: bot if r[0]=='_' else top)
p_symbol.setParseAction(lambda r: reg(r[0]))
p_extern.setParseAction(lambda r: ext(r[0]))
p_cst.setParseAction(lambda r: int(r[0],16))
p_slc.setParseAction(lambda r: slice(r['start'],r['stop']))


def parse(s):
    p_expr.parseString(s,True)

def test_parser():
    while 1:
        try:
            res = raw_input('amoco[test_parser]>')
            E = p_expr.parseString(res,True)
            print E
        except EOFError:
            return
