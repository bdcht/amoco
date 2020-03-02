from amoco.logger import Log
logger = Log(__name__)
logger.debug('loading module')
import weakref
import inspect
import functools
import types

class weakmethod(object):
    __slots__ = ['func','weak']
    def __init__(self,func,weak):
        self.func = func
        self.weak = weak
    def __call__(self,*args,**kargs):
        return self.func(self.weak(),*args,**kargs)
    def __repr__(self):
        return "<weakmethod %s of weakref %s>"%(self.func,self.weak)



#------------------------------------------------------------------------------

REF_FUNC_REGULAR  = 1
REF_FUNC_UNBOUND  = 2
REF_METH_UNBOUND2 = 3
REF_METH_BOUND    = 4
REF_OBJ_CALLABLE  = 5

class reference(object):
    """ A reference to all kinds of python2/3 function or method.
    Handles reference to a regular function, a bound method, a callable object,
    a python3 unbound (or static) method, or a python2 staticmethod.

    Arguments:
        obj: function/method/callable to be referenced

    Attributes:
        ctx: "context" in which the referenced function/method is defined. 
             This is the module for a regular function, the class for an unbound method,
             or the object instance for a bound method or callable.
        type (int): the type of object referenced.
        ref: the python function or method object that is actually referenced.
             This is the function object for regular functions and python3 unbound methods.
        is_static: a flag to indicate if the referenced method is a staticmethod.
    """
    def __init__(self,obj):
        ctx = inspect.getmodule(obj)
        self.is_static = False
        if inspect.isfunction(obj):
            name = obj.__name__
            if name in ctx.__dict__:
                self.type = 1  # regular function accessed from a module
                self.ctx  = ctx
                self.ref  = obj
                logger.debug('ref to regular function %s'%name)
            elif hasattr(obj,'__qualname__'):
                qn = obj.__qualname__.split('.')
                assert qn[-1]==name
                qn.pop()
                while len(qn)>0:
                    ctx = getattr(ctx,qn.pop(0))
                assert inspect.isclass(ctx)
                self.type = 2  # python3 "unbound" (or static) method
                self.ctx  = ctx
                self.ref  = ctx.__dict__[name]
                if isinstance(self.ref,staticmethod):
                    self.is_static = True
                    self.ref = self.ref.__func__
                x = 'static' if self.is_static else 'unbound'
                logger.debug('ref to %s function %s'%(x,self.ref))
            else:
                # a staticmethod, but ctx is still unknown and we have
                # no qualname...so we need to find for the right class in the module.
                # since we known only the staticmethod's name, we need to look for this
                # name in all classes defined in the module:
                found = None
                for x in iter(ctx.__dict__.values()):
                    if not inspect.isclass(x): continue
                    if name in x.__dict__ and getattr(x,name) is obj:
                        found = x
                        break
                if not found:
                    logger.warning("context of staticmethod %s not found"%name)
                    raise ValueError
                self.type = 2
                self.is_static = True
                self.ctx  = found
                self.ref  = self.ctx.__dict__[name].__func__
                logger.debug('ref to staticmethod %s'%self.ref)
        elif inspect.ismethod(obj):
            if obj.__self__ is None:
                #f is a python2.x "unbound" method
                #typically, obj is a (regular) method referenced by a Class
                #rather than by a class instance. Example: MyClass.mymethod
                self.type = 3
                self.ctx  = obj.im_class
                self.ref  = obj.__func__
                logger.debug('ref to python2 unbound method %s'%self.ref)
            else: #f is a (py2/py3) "bound" method
                self.type = 4
                self.ctx  = weakref.ref(obj.__self__)
                self.ref  = obj.__func__
                logger.debug('ref to bound method %s'%self.ref)
        elif callable(obj):
            self.type = 5
            self.ctx  = weakref.ref(obj)
            self.ref  = obj.__call__.__func__
            logger.debug('ref to callable object %s'%obj)

    def reset(self):
        return self.setfunc(self.getfunc())

    def getfunc(self):
        return self.ref

    def setfunc(self,hookfunc):
        name = self.ref.__name__
        if self.type == 1:
            setattr(self.ctx,name,hookfunc)
            return hookfunc
        if self.type == 2:
            if self.is_static:
                newfunc = staticmethod(hookfunc)
            else:
                newfunc = hookfunc
            setattr(self.ctx,name,newfunc)
            return newfunc
        if self.type == 3:
            newmethod = types.UnboundMethodType(hookfunc,None,self.ctx)
            setattr(self.ctx,name,newmethod)
            return newmethod
        obj = self.ctx()
        newmethod = weakmethod(hookfunc,self.ctx)
        setattr(obj,name,newmethod)
        return newmethod

    def __call__(self,*args,**kargs):
        return self.ref(*args,**kargs)

    def __hash__(self):
        return self.ref.__hash__()

    def __eq__(self,other):
        return (self.ref is other.ref)

    def __repr__(self):
        category = {
                1: 'function',
                2: 'wrapped function',
                3: 'unbound method',
                4: 'bound method',
                5: 'callable'}[self.type]
        return '<%s for %s %s in context %s>'%(self.__class__.__name__,
                                                     category,
                                                     self.ref.__name__,
                                                     self.ctx)

#------------------------------------------------------------------------------

class Signal(object):
    pool = {}

    def __new__(cls,name):
        if name in cls.pool: return cls.pool[name]
        return super(Signal,cls).__new__(cls)

    def __init__(self,name):
        self.name = name
        if name not in self.pool:
            self.recv = []
            self.hook = {}
            self.pool[self.name] = self

    def __repr__(self):
        return "<Signal %s>"%self.name

    def __eq__(self,other):
        return self.name==other.name

    def sender(self,func):
        "add method to senders of the signal"
        r = reference(func)
        assert r.ref not in self.recv
        self.patch(r)

    def receiver(self,func):
        "add func to receivers of the signal"
        self.recv.append(func)

    def patch(self,r):
        def hook(*args,**kargs):
            self.emit(r,(args,kargs))
            return r(*args,**kargs)
        hooked = r.setfunc(hook)
        self.hook[hooked] = r

    def codepatch(self,r):
        from struct import pack
        c = r.ref.__func__.func_code
        patch_ = [('LOAD_GLOBAL',len(c.co_names)),
                 ('LOAD_CONST',len(c.co_consts)),
                 ('CALL_FUNCTION',1),
                 ('LOAD_ATTR',len(c.co_names)+1),
                 ('CALL_FUNCTION',0),
                 ('POP_TOP',None)]
        hook = ''
        for op in patch_:
            opc = chr(inspect.dis.opmap[op[0]])
            if op[1] is not None: opc+=pack('<H',op[1])
            hook += opc
        newc = types.CodeType(
                c.co_argcount,
                c.co_nlocals,
                c.co_stacksize,
                c.co_flags,
                hook + c.co_code,
                c.co_consts+(self.name,),
                c.co_names+('Signal','emit'),
                c.co_varnames,
                c.co_filename,
                c.co_name,
                c.co_firstlineno,
                c.co_lnotab)
        self.hook[r.ref.__func__] = c
        r.ref.__func__.func_code = newc

    def unpatch(self,hooked):
        while hooked in self.hook:
            descr = self.hook[hooked].reset()
            del self.hook[hooked]
            hooked = descr

    def emit(self,ref=None,args=None):
        if ref is None:
            ref=inspect.currentframe().f_back
        for recv in self.recv:
           recv(self,ref,args=args)

#------------------------------------------------------------------------------

SIG_TRGT = Signal("#TRGT")
SIG_NODE = Signal("#NODE")
SIG_EDGE = Signal("#EDGE")
SIG_BLCK = Signal("#BLCK")
SIG_FUNC = Signal("#FUNC")

