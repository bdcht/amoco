#!/usr/bin/env python

"""
arch/core.py
============

The architecture's core module implements essential classes
for the definition of new cpu architectures:

- the :class:`instruction` class models cpu instructions decoded by the disassembler.
- the :class:`disassembler` class implements the instruction decoding logic based \
        on provided specifications.
- the :class:`ispec` class is a function decorator that allows to define the \
        specification of an instruction.
- the :class:`Formatter` class is used for instruction pretty printing

"""

# This code is part of Amoco
# Copyright (C) 2006-2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

import inspect
import importlib
import codecs
from types import FunctionType
from collections import defaultdict
from functools import reduce
import pyparsing as pp

from crysp.bits import Bits, pack, unpack

from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")

from amoco.ui.render import Token, highlight

type_unpredictable = -1
type_undefined = 0
type_data_processing = 1
type_control_flow = 2
type_cpu_state = 3
type_system = 4
type_other = 5

INSTRUCTION_TYPES = {
    type_unpredictable: "unpredictable",
    type_undefined: "undefined",
    type_data_processing: "data_processing",
    type_control_flow: "control_flow",
    type_cpu_state: "cpu_state",
    type_system: "system",
    type_other: "other",
}


class icore(object):
    """This is the core class for the generic parent instruction class below.
       It defines the mandatory API for all instructions.

       Attributes:
         bytes (bytes)  : instruction's bytes
         type  (int)    : one of (type_data_processing, type_control_flow,
                          type_cpu_state, type_system, type_other) or
                          type_undefined (default) or type_unpredictable.
         spec  (ispec)  : the specification that was decoded by the disassembler
                          to instanciate this instruction.
         mnemonic (str) : the mnemonic string as defined by the specification.
         operands (list): the list of operands' expressions.
         misc (dict)    : a defaultdict for passing various arch-dependent infos
                          (which returns None for undefined keys.)
    """
    def __init__(self, istr=b""):
        self.bytes = bytes(istr)
        self.type = type_undefined
        self.spec = None
        self.mnemonic = None
        self.operands = []
        # we add a misc defaultdict container.
        # see x86 specs for example of misc usage.
        self.misc = defaultdict(_core_misc_default)

    @classmethod
    def set_uarch(cls, uarch):
        "class method to define the instructions' semantics uarch dict"
        cls._uarch = uarch

    def typename(self):
        "returns the instruction's type as a string"
        return INSTRUCTION_TYPES[self.type]

    def __call__(self, fmap):
        """calls the uarch[mnemonic] semantics function for this instruction
           or warns if no semantics is found.
        """
        if self.type in (type_undefined, type_unpredictable):
            logger.error("%s instruction" % self.typename())
        try:
            i_xxx = self._uarch["i_%s" % self.mnemonic]
        except AttributeError:
            logger.warning("no uarch defined (%s)" % self.mnemonic)
        except KeyError:
            logger.warning("instruction %s not implemented" % self.mnemonic)
        else:
            i_xxx(self, fmap)

    @property
    def length(self):
        "length of the instruction in bytes"
        return len(self.bytes)



# instruction class
# -----------------


class instruction(icore):
    """The generic instruction class allows to define instruction for any cpu
    instructions set and provides a common API for all arch-independent methods.
    It extends the :class:`icore` with an :attr:`address` attribute and formatter
    methods.

    Attributes:
        address (cst): the memory address where this instruction as been disassembled.
    """

    def __init__(self, istr):
        icore.__init__(self, istr)
        self.address = None

    def __repr__(self):
        s = self.__class__.__name__
        if self.address is not None:
            s += " [%s] " % self.address
        s += " %s ( " % self.mnemonic
        for k, v in inspect.getmembers(self):
            if k in (
                "address",
                "mnemonic",
                "bytes",
                "spec",
                "operands",
                "misc",
                "formatter",
            ):
                continue
            if k.startswith("_") or inspect.ismethod(v):
                continue
            s += "%s=%s " % (k, v)
        return "<%s)>" % s

    @classmethod
    def set_formatter(cls, f):
        "classmethod that defines the formatter for all instances"
        cls.formatter = f

    @staticmethod
    def formatter(i, toks=False):
        """default formatter if no formatter has been set, will return
           the highlighted list from tokens for raw mnemonic,
           and comma-separated operands expressions.
        """
        t = [(Token.Mnemonic, i.mnemonic)]
        t += [(Token.Literal, op) for op in map(str, i.operands[0:1])]
        t += [(Token.Literal, ", " + op) for op in map(str, i.operands[1:])]
        return t if toks else highlight(t)

    def __str__(self):
        return self.formatter(i=self)

    def toks(self):
        "returns the (unjoined) list of formatted tokens."
        return self.formatter(i=self, toks=True)


class InstructionError(Exception):
    def __init__(self, i):
        self.ins = i

    def __str__(self):
        return repr(self.ins)


class DecodeError(Exception):
    pass


def _core_misc_default():
    return None


# disassembler core  class
# ------------------------


class disassembler(object):
    """The generic disassembler class will decode a byte string based on provided
    sets of instructions specifications and various parameters like endianess and
    ways to select the appropriate instruction set.

    Arguments:

      specmodules: list of python modules containing ispec decorated funcs
      iclass: the specific instruction class based on :class:`instruction`
      iset: lambda used to select module (ispec list)
      endian: instruction fetch endianess (1: little, -1: big)

    Attributes:

      maxlen: the length of the longest instruction found in provided specmodules.
      iset: the lambda used to select the right specifications for decoding
      endian: the lambda used to define endianess.
      specs: the *tree* of :class:`ispec` objects that defines the cpu architecture.
    """

    def __init__(
        self,
        specmodules,
        iclass=instruction,
        iset=(lambda *args, **kargs: 0),
        endian=(lambda *args, **kargs: 1),
    ):
        self.iclass = iclass
        self.maxlen = max(
            (s.mask.size // 8 for s in sum((m.ISPECS for m in specmodules), []))
        )
        self.iset = iset
        self.endian = endian
        # build ispecs tree for each set:
        logger.debug("building specs tree for modules %s", [m.__name__ for m in specmodules])
        # self.indent = 0
        self.specs = [self.setup(m.ISPECS) for m in specmodules]
        # del self.indent
        # some arch like x86 require a stateful decoding due to optional prefixes,
        # so we keep an __i instruction for decoding until a non prefix ispec is used.
        self.__i = None

    def setup(self, ispecs):
        """setup will (recursively) organize the provided ispecs list into an optimal tree so that
        __call__ can efficiently find the matching ispec format for a given bytestring
        (we don't want to search all specs until a match, so we need to separate formats as much
        as possible). The output tree is (f,l) where f is the submask to check at this level
        and l is a defaultdict such that l[x] is the subtree of formats for which submask is x.
        """
        # self.indent += 2
        # ind = ' '*self.indent
        # sort ispecs from high constrained to low constrained:
        # logger.debug('%scurrent subset count: %d',ind,len(ispecs))
        ispecs.sort(key=(lambda x: x.mask.hw()), reverse=True)
        if len(ispecs) < 5:
            # logger.debug('%stoo small to divide',ind)
            # self.indent -= 2
            return (0, ispecs)
        # find separating mask:
        if self.endian() == -1:
            # in bigendian cases where not all instructions have the same length (like ARM),
            # then the MSB byte needs to be maxlen-justified. Hence, if a spec is shorter
            # than maxlen*8 bits, its mask and fix values need to be shifted up to a
            # maxlen bitsize.
            maxsize = self.maxlen * 8
            adjust = lambda x: x.ival << (maxsize - x.size)
        else:
            adjust = lambda x: x.ival
        localmask = reduce(lambda x, y: x & y, [adjust(s.mask) for s in ispecs])
        if localmask == 0:
            # logger.debug('%sno local mask',ind)
            # self.indent -= 2
            return (0, ispecs)
        # subsetup:
        f = localmask
        # logger.debug('%slocal mask is %X',ind,f)
        l = defaultdict(lambda: list())
        for s in ispecs:
            l[adjust(s.fix) & f].append(s)
        if len(l) == 1:  # if subtree has only 1 spec, we're done here
            # logger.debug('%sfound 1 branch: done',ind)
            # self.indent -=2
            return (0, list(l.values())[0])
        # logger.debug('%sfound %d branches',ind,len(l))
        for x, S in l.items():
            l[x] = self.setup(S)
        # self.indent -=2
        return (f, l)

    def __call__(self, bytestring, **kargs):
        e = self.endian(**kargs)
        adjust = lambda x: x.ival
        bs = bytestring[0:self.maxlen]
        if e == -1:
            maxsize = self.maxlen * 8
            adjust = lambda x: x.ival << (maxsize - x.size)
            bs = bytestring[self.maxlen-1::-1]
        b = adjust(Bits(bs, bitorder=1))
        # get organized/optimized tree of specs:
        fl = self.specs[self.iset(**kargs)]
        while True:
            f, l = fl
            if f == 0:  # we are on a leaf...
                for s in l:  # lets search linearly over this branch
                    try:
                        i = s.decode(bytestring, e, i=self.__i, iclass=self.iclass)
                    except (DecodeError, InstructionError):
                        # logger.debug(u'exception raised by disassembler:'
                        #             u'decoding %s with spec %s'%(codecs.encode(bytestring,'hex'),s.format))
                        continue
                    # we found the instruction (or prefix)
                    if i.spec.pfx is True:
                        if self.__i is None:
                            self.__i = i
                        return self(bytestring[s.mask.size // 8 :], **kargs)
                    elif i.spec.pfx == "xdata":
                        i.xdata(i,**kargs)
                    self.__i = None
                    if "address" in kargs:
                        i.address = kargs["address"]
                    return i
                logger.debug(
                    "no instruction spec matching %s"
                    % (codecs.encode(bytestring, "hex"))
                )
                break
            else:  # go deeper in the tree according to submask value of b
                fl = l.get(b & f, None)
                if fl is None:
                    break
        self.__i = None
        return None


# -----------------------------------------


class ispec(object):
    """ispec (customizable) decorator

    @ispec allows to easily define instruction decoders based on architecture specifications.

    Arguments:

        spec (str):
            a human-friendly *format* string that describes how the ispec object will
            (on request) decode a given bytestring and how it will expose various
            decoded entities to the decorated "hook" function to define an instruction.
        **kargs:
            additional arguments to ispec decorator **must** be provided with ``name=value``
            form and are declared as attributes/values within the instruction instance *before*
            calling the hook function. If the provided value is a FunctionType, it is 
            called with the bytestring passed as a Bits instance argument to produce the final
            value associated with name. See below for conventions about names.

    Attributes:

        format (str): the spec format passed as argument (see Note below).
        hook (callable): the decorated python function to be called during decoding. The hook
                         function name is relevant only for instructions' formatter.
                         See :class:`arch.core.Formatter`.
        iattr (dict): the dictionary of instruction attributes to add before decoding.
                      Attributes and their values are passed from the spec's kargs when the
                      name does not start with an underscore.
        fargs (dict): the dictionary of keywords arguments to pass to the hook.
                      These keywords are decoded from the format or given by the spec's kargs
                      when name starts with an underscore.
        precond (func): If the spec's kargs contains a name '__obj=func', then the func is
                        used as a pre-condition function that takes the instruction object
                        and returns a boolean to indicate wether the hook can be called or not.
                        (This allows to avoid decoding when a prefix is missing for example.)
        size (int): the bit length of the format (``LEN`` value)
        fix (Bits): the values of fixed bits within the format
        mask (Bits): the mask of fixed bits within the format

    Examples:

        This statement creates an ispec object with hook ``f``, and registers this object
        automatically in a SPECS list object within the module where the statement is found::

            @ispec("32[ .cond(4) 101 1 imm24(24) ]", mnemonic="BL", _flag=True)
            def f(obj,imm24,_flag):
                [...]

        When provided with a bytestring, the :meth:`decode` method of this ispec object will:

         - proceed with decoding ONLY if bits 27,26,25,24 are 1,0,1,1 or raise an exception
         - instanciate an instruction object (obj)
         - decode 4 bits at position [28,29,30,31] and provide this value as an integer \
              in 'obj.cond' instruction instance attribute.
         - decode 24 bits at positions 23..0 and provide this value as an integer as \
              argument 'imm24' of the decorated function f.
         - set obj.mnemonic to 'BL' and pass argument _flag=True to f.
         - call f(obj,...)
         - return obj

    Note:

        The ``spec`` string format is  ``LEN ('<' or '>') '[' FORMAT ']' ('+' or '&')``

          - ``LEN`` is either an integer that represents the bit length of the instruction or '*'.
              Length must be a multiple of 8, '*' is used for a variable length
              instruction.
          - ``FORMAT`` is a series of *directives* (see below.)
             Each directive represents a sequence of bits ordered according to the spec
             direction : '<' (default) means that directives are ordered from MSB (bit index LEN-1)
             to LSB (bit index 0) whereas '>' means LSB to MSB.

        The spec string is optionally terminated with '+' to indicate that it
        represents an instruction *prefix*, or by '&' to indicate that the instruction
        has a *suffix* of some more bytes to decode and that the disassembler needs to call its
        'xdata' method while passing all its kargs to this method.
        In the *prefix* case, the bytestring matching the ispec format is stacked temporarily
        until the rest of the bytestring matches a non prefix ispec.
        In the *suffix* case, only the spec bytestring is used to define the instruction
        but the :meth:`read_instruction` fetcher will provide additional arguments to the
        :meth:`xdata` method of the instruction in order to finish its decoding.
        (See wasm architecture for example.)

        The directives defining the ``FORMAT`` string are used to associate symbols to bits
        located at dedicated offsets within the bitstring to be decoded. A directive has the
        following syntax:

        * ``-`` (indicates that current bit position is not decoded)
        * ``0`` (indicates that current bit position must be 0)
        * ``1`` (indicates that current bit position must be 1)

        or

        * ``type SYMBOL location`` where:

           * ``type`` is an *optional* modifier char with possible values:

             * ``.`` indicates that the ``SYMBOL`` will be an *attribute* of the :class:`instruction`.
             * ``~`` indicates that the decoded value will be returned as a Bits instance.
             * ``#`` indicates that the decoded value will be returned as a string of [01] chars.
             * ``=`` indicates that decoding should *end* at current position (overlapping)

             if not present, the ``SYMBOL`` will be passed as a keyword argument to the function with
             value decoded as an integer.
           * ``SYMBOL``: is a mandatory string matching regex ``[A-Za-z_][0-9A-Za-z_]*``
           * ``location``: is an optional string matching the following expressions:

             * ``( len )``    : indicates that the value is decoded from the next len bits starting
                                from the current position of the directive within the ``FORMAT`` string.
             * ``(*)``        : indicates a *variable length directive* for which the value is decoded
                                from the current position with all remaining bits in the ``FORMAT``.\
                                If the ``LEN`` is also variable then all remaining bits from the instruction
                                buffer input string are used.

             default location value is ``(1)``.

        The special directive ``{byte}`` is a shortcut for 8 fixed bits. For example
        ``8>[{2f}]`` is equivalent to ``8>[ 1111 0100 ]``, or ``8<[ 0010 1111 ]``.
    """

    __slots__ = [
        "format",
        "iattr",
        "fargs",
        "precond",
        "ast",
        "fix",
        "mask",
        "pfx",
        "size",
        "hook",
    ]

    def __init__(self, format, **kargs):
        self.format = format
        self.setup(kargs)
        # when ispec is used as a function decorator, hook holds the decorated function
        self.hook = None

    def __getstate__(self):
        D = {}
        D["format"] = self.format
        D["module"] = self.hook.__module__
        return D

    def __setstate__(self, state):
        self.format = state["format"]
        modname = state["module"]
        m = importlib.import_module(modname)
        self.hook = None
        for h in m.ISPECS:
            if h.format == self.format:
                self.hook = h.hook
                break

    def setup(self, kargs):
        self.iattr = {}
        self.fargs = {}
        self.precond = None
        for k, v in iter(kargs.items()):
            if k.startswith("_"):
                if k=="__obj":
                    self.precond = v
                else:
                    self.fargs[k] = v
            else:
                self.iattr[k] = v
        self.ast = self.buildspec()

    def fixed(self):
        s = list(str(self.fix))
        for i, x in enumerate(self.mask):
            if x == 0:
                s[i] = "-"
        if self.ast[0][1] == "<":
            s.reverse()
        return "".join(s)

    def buildspec(self):
        ast = specdecode.parseString(self.format, True)
        size, direction = ast[0]
        self.size = size
        fmt = ast[1]
        self.pfx = ast[2]
        xsz = ast[3]
        if xsz:
            self.pfx = xsz
        go = +1
        chklen = True
        if direction == "<":  # format goes from high bits to low bits
            fmt = list(reversed(fmt))
            go = -1
        if size == "*":
            self.size = 0
            chklen = False
            size = 0
            for d in fmt:
                if d in ("-", "0", "1"):
                    size += 1
                elif isinstance(d, Bits):
                    size += d.size
                else:
                    loc = d[2]
                    if loc == "*":
                        break
                    if d[0]!='=':
                        size += loc
        if size % 8 != 0:
            logger.error("ispec length %d not a multiple of 8 %s" % (size,self.format))
        self.fix = Bits(0, size)  # values of fixed bits
        self.mask = Bits(0, size)  # location of fixed bits
        i = 0
        count = 0
        for d in fmt:
            if chklen and not i < size:
                logger.error("ispec format too wide %s" % self.format)
            # unknown bit (skipped)
            if d == "-":
                i += 1
                count += 1
                continue
            # fixed bit:
            if d in ("0", "1"):
                self.fix[i] = int(d)
                self.mask[i] = 1
                i += 1
                count += 1
                continue
            # fixed byte:
            if isinstance(d, Bits):
                self.fix[i : i + d.size] = d
                self.mask[i : i + d.size] = d.mask
                i += d.size
                count += d.size
                continue
            # directive:
            opt, symbol, loc = d
            if loc != "*":
                if opt == "=" and go > 0:
                    i = i - loc
                sta = i
                sto = i + loc
                if sta < 0 or sto > size:
                    logger.error("ispec directive out of bound in %s" % self.format)
                if opt != "=":
                    count += loc
                i = sto
                if opt == "=" and go < 0:
                    i = i - loc
            else:
                if opt == "=":
                    logger.error("ispec directive invalid length in %s" % self.format)
                sta = i
                sto = None
                i = size
                if count < size:
                    count = size
                chklen = True
            # now set D (fargs or iattr) to corresponding extractor lambdas which
            # will be called when decode is called by the disassembler:
            D = self.fargs
            if "." in opt:
                D = self.iattr
            if symbol in D:
                raise logger.error("ispec symbol %s redefined" % symbol)
            if "~" in opt:
                f = lambda b, p=sta, q=sto: b[p:q]
            elif "#" in opt:
                f = lambda b, p=sta, q=sto, x=go: str(b[p:q])[::x]
            else:
                f = lambda b, p=sta, q=sto: b[p:q].ival
            D[symbol] = f
        if count != size:
            logger.error("ispec size mismatch (%s)" % self.format)
        return ast

    # decode always receive input bytes in ascending memory order
    def decode(self, istr, endian=1, i=None, iclass=instruction):
        # check spec :
        blen = self.fix.size // 8
        if len(istr) < blen:
            raise DecodeError
        bs = istr[0:blen]
        # Bits object created with LSB to MSB byte string:
        ival = bs[::endian]
        b = Bits(ival, self.fix.size, bitorder=1)
        if b & self.mask != self.fix:
            raise DecodeError
        if self.size == 0:  # variable length spec:
            if endian != 1:
                logger.error("invalid endianess")
            b = b // Bits(istr[blen:], bitorder=1)
        # create & update instruction object:
        if i is None:
            i = iclass(bs)
        else:
            i.bytes += bs
        saved_bytes = i.bytes[:-len(bs)]
        i.spec = self
        # set instruction attributes from directives, and then
        # call hook function with instruction as first parameter
        # and fargs (note that hook can thus overwrite previous attributes)
        for k, v in iter(self.iattr.items()):
            if isinstance(v, FunctionType):
                v = v(b)
            setattr(i, k, v)
        kargs = {}
        for k, v in iter(self.fargs.items()):
            if isinstance(v, FunctionType):
                v = v(b)
            kargs[k] = v
        # and finally call the hook:
        try:
            # check any precondition on i:
            if self.precond and (not self.precond(i)):
                raise InstructionError(i)
            # ok, lets call the spec hook...
            self.hook(obj=i, **kargs)
        except InstructionError:
            # clean up:
            i.bytes = saved_bytes
            for k in iter(self.iattr.keys()):
                delattr(i, k)
            raise InstructionError(i)
        return i

    def encode(self, i):
        raise NotImplementedError

    # decorate:
    def __call__(self, handler):
        m = inspect.getmodule(handler)
        ispec_register(self, m)
        varnames = handler.__code__.co_varnames
        fname = handler.__name__
        for k in iter(self.fargs.keys()):
            if k not in varnames:
                logger.error("ispec symbol not found in decorated function %s" % fname)
        self.hook = handler
        return handler


# -------------------------------------------------


class Formatter(object):
    """Formatter is used for instruction pretty printing

    Basically, a ``Formatter`` object is created from a dict associating a key with a list
    of functions or format string. The key is either one of the mnemonics or possibly
    the name of a @ispec-decorated function (this allows to group formatting styles rather
    than having to declare formats for every possible mnemonic.)
    When the instruction is printed, the formatting list elements are "called" and
    concatenated to produce the output string.
    """

    def __init__(self, formats):
        self.formats = formats
        self.default = ("{i.mnemonic:<20}", lambda i: ", ".join(map(str, i.operands)))

    def getkey(self, i):
        if i.mnemonic in self.formats:
            return i.mnemonic
        fname = i.spec.hook.__name__
        if fname in self.formats:
            return fname
        return None

    def getparts(self, i):
        try:
            fmts = self.formats[i.mnemonic]
        except KeyError:
            fname = i.spec.hook.__name__
            fmts = self.formats.get(fname, self.default)
        return fmts

    def __call__(self, i, toks=False):
        s = []
        for f in self.getparts(i):
            if hasattr(f, "format"):
                t = f.format(i=i)
            else:
                t = f(i)
            if isinstance(t, str):
                t = [(Token.Literal, t)]
            s.extend(t)
        return s if toks else highlight(s)


# ispec format parser:
# ---------------------

integer = pp.Regex(r"[1-9][0-9]*")
indxdir = pp.oneOf(["<", ">"])
fixbit = pp.oneOf(["0", "1"])
number = integer | fixbit
number.setParseAction(lambda r: int(r[0]))
unklen = pp.Literal("*")
length = number | unklen
unkbit = pp.oneOf(["-"])
fixbyte = pp.Regex(r"{[0-9a-fA-F][0-9a-fA-F]}").setParseAction(
    lambda r: Bits(int(r[0][1:3], 16), 8)
)
fixed = fixbyte | fixbit | unkbit
option = pp.oneOf([".", "~", "#", "="])
symbol = pp.Regex(r"[A-Za-z_][A-Za-z0-9_]*")
location = pp.Suppress("(") + length + pp.Suppress(")")
directive = pp.Group(
    pp.Optional(option, default="") + symbol + pp.Optional(location, default=1)
)
speclen = pp.Group(length + pp.Optional(indxdir, default="<"))
specformat = pp.Group(
    pp.Suppress("[") + pp.OneOrMore(directive | fixed) + pp.Suppress("]")
)
specoption = pp.Optional(pp.Literal("+").setParseAction(lambda r: True), default=False)
specmore = pp.Optional(pp.Literal("&").setParseAction(lambda r: "xdata"), default=False)
specdecode = speclen + specformat + specoption + specmore


def ispec_register(x, module):
    F = []
    try:
        S = module.ISPECS
    except AttributeError:
        logger.error("spec modules must declare ISPECS=[] before @ispec decorators")
        raise AttributeError
    f = x.fixed()
    if f in F:
        logger.error(
            "ispec conflict for %s (vs. %s)" % (x.format, S[F.index(f)].format)
        )
    else:
        if x.mask != 0:
            S.append(x)
            F.append(f)


def test_parser():
    while 1:
        try:
            res = raw_input("ispec>")
            s = ispec(res, mnemonic="TEST")
            print(s.ast)
            return s
        except EOFError:
            return


if __name__ == "__main__":
    test_parser()
