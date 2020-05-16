# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2007-2019 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
system/core.py
==============

This module defines all task/process core classes related to binary format and
execution inherited by all system specific execution classes of
the :mod:`amoco.system` package.

"""

from amoco.arch.core import Bits
from amoco.ui.views import execView
from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")

# ------------------------------------------------------------------------------


class CoreExec(object):
    """
    This class implements the base class for Task(s).
    CoreExec or Tasks are used to represent a memory mapped binary
    executable program, providing the generic instruction or data fetchers and
    the mandatory API for :mod:`amoco.emu` or :mod:`amoco.sa` analysis classes.
    Most of the :mod:`amoco.system` modules use this base class to implement
    a OS-specific Task class (see Linux/x86, Win32/x86, etc).

    Attributes:
        bin: the program executable format object. Currently supported formats
             are provided in :mod:`system.elf` (Elf32/64), :mod:`system.pe` (PE)
             and :mod:`system.utils` (HEX/SREC).

        cpu: reference to the architecture cpu module, which provides a generic
             access to the PC() program counter and
             obviously the CPU registers and disassembler.

        OS:  optional reference to the OS associated to the child Task.

        state: the :class:`mapper` instance that represents the current state
             of the executable program, including mapping of registers as well
             as the :class:`MemoryMap` instance that represents the virtual
             memory of the program.
    """

    __slots__ = ["bin", "cpu", "OS", "state", "view"]

    def __init__(self, p, cpu=None):
        self.bin = p
        self.cpu = cpu
        self.OS = None
        self.state = self.initstate()
        self.view = execView(of=self)

    def __repr__(self):
        c = self.__class__.__name__
        o = self.OS.__module__ if self.OS else "-"
        n = self.bin.filename
        return "<%s %s '%s'>" % (c, o, n)

    def __str__(self):
        return str(self.view)

    def initstate(self):
        from amoco.cas.mapper import mapper

        m = mapper()
        return m

    def read_data(self, vaddr, size):
        """
        fetch size data bytes at virtual address vaddr, returned
        as a list of items being either raw bytes or symbolic expressions.
        """
        return self.state.mmap.read(vaddr, size)

    def read_instruction(self, vaddr, **kargs):
        """
        fetch instruction at virtual address vaddr, returned as an
        cpu.instruction instance or cpu.ext in case an external expression
        is found at vaddr or vaddr is an external symbol.

        Raises MemoryError in case vaddr is not mapped,
        and returns None if disassembler fails to decode bytes at vaddr.

        Note:
        Returning a cpu.ext expression means that this instruction starts
        an external stub function.
        It is the responsibility of the fetcher (emulator or analyzer)
        to eventually call the stub to modify the state mapper.
        """
        if self.cpu is None:
            logger.error("no cpu imported")
            raise ValueError
        maxlen = self.cpu.disassemble.maxlen
        if isinstance(vaddr, int):
            addr = self.cpu.cst(vaddr, self.cpu.PC().size)
        elif vaddr._is_ext:
            vaddr.address = vaddr
            return vaddr
        else:
            addr = vaddr
        try:
            istr = self.state.mmap.read(vaddr, maxlen)
        except MemoryError as e:
            logger.verbose("vaddr %s is not mapped" % addr)
            raise MemoryError(e)
        else:
            if len(istr) <= 0:
                logger.verbose("failed to read instruction at %s" % addr)
                raise MemoryError(addr)
            elif not isinstance(istr[0], bytes):
                if istr[0]._is_ext:
                    istr[0].address = addr
                    return istr[0]
                else:
                    return None
        i = self.cpu.disassemble(istr[0], **kargs)
        if i is None:
            logger.warning("disassemble failed at vaddr %s" % addr)
            return None
        else:
            if i.address is None:
                i.address = addr
            xsz = i.misc["xsz"] or 0
            if xsz > 0:
                xdata = self.state.mmap.read(vaddr + i.length, xsz)
                i.xdata(i, xdata)
            return i

    def symbol_for(self,address):
        info = None
        if address in self.bin.variables:
            info = self.bin.variables[address]
            if isinstance(info,tuple):
                info = info[0]
            info = "$%s"%info
        elif address in self.bin.functions:
            info = self.bin.functions[address]
            if isinstance(info,tuple):
                info = info[0]
            info = "<%s>"%info
        elif self.OS and (address in self.OS.symbols):
            info = self.OS.symbols[address]
            info = "#%s"%info
        return info or ""

    def segment_for(self,address,stype=None):
        s = self.bin.getinfo(address)[0]
        return s.name if hasattr(s,'name') else ""

    def getx(self, loc, size=8, sign=False):
        """
        high level method to get the expressions value associated
        to left-value loc (register or address). The returned value
        is an integer if the expression is constant or a symbolic
        expression instance.
        The input loc is either a register string, an integer address,
        or associated expressions' instances.
        Optionally, the returned expression sign flag can be adjusted
        by the sign argument.
        """
        if isinstance(loc, str):
            x = getattr(self.cpu, loc)
        elif isinstance(loc, int):
            endian = self.cpu.get_data_endian()
            psz = self.cpu.PC().size
            addr = self.cpu.cst(loc, psz)
            x = self.cpu.mem(addr, size, endian=endian)
        else:
            x = loc
        r = self.state(x)
        r.sf = sign
        return r.value if r._is_cst else r

    def setx(self, loc, val, size=0):
        """
        high level method to set the expressions value associated
        to left-value loc (register or address). The value
        is possibly an integer or a symbolic expression instance.
        The input loc is either a register string, an integer address,
        or associated expressions' instances.
        Optionally, the size of the loc expression can be adjusted
        by the size argument.
        """
        if isinstance(loc, str):
            x = getattr(self.cpu, loc)
            size = x.size
        elif isinstance(loc, int):
            endian = self.cpu.get_data_endian()
            psz = self.cpu.PC().size
            x = self.cpu.mem(self.cpu.cst(addr, psz), size, endian=endian)
        else:
            x = loc
            size = x.size
        if isinstance(val, bytes):
            if x._is_mem:
                x.size = len(val) if size == 0 else size
                self.state._Mem_write(x.a, val)
            else:
                endian = self.cpu.get_data_endian()
                v = self.cpu.cst(
                    Bits(val[0 : x.size : endian], bitorder=1).int(), x.size * 8
                )
                self.state[x] = v
        elif isinstance(val, int):
            self.state[x] = self.cpu.cst(val, size)
        else:
            self.state[x] = val

    def get_int64(self, loc):
        "get 64-bit int expression of current state(loc)"
        return self.getx(loc, size=64, sign=True)

    def get_uint64(self, loc):
        "get 64-bit unsigned int expression of current state(loc)"
        return self.getx(loc, size=64)

    def get_int32(self, loc):
        "get 32-bit int expression of current state(loc)"
        return self.getx(loc, size=32, sign=True)

    def get_uint32(self, loc):
        "get 32-bit unsigned int expression of current state(loc)"
        return self.getx(loc, size=32)

    def get_int16(self, loc):
        "get 16-bit int expression of current state(loc)"
        return self.getx(loc, size=16, sign=True)

    def get_uint16(self, loc):
        "get 16-bit unsigned int expression of current state(loc)"
        return self.getx(loc, size=16)

    def get_int8(self, loc):
        "get 8-bit int expression of current state(loc)"
        return self.getx(loc, sign=True)

    def get_uint8(self, loc):
        "get 8-bit unsigned int expression of current state(loc)"
        return self.getx(loc)


# ------------------------------------------------------------------------------

class DefineStub(object):
    """
    decorator to define a stub for the given 'refname' library function.
    """
    def __init__(self, obj, refname, default=False):
        self.obj = obj
        self.ref = refname
        self.default = default

    def __call__(self, f):
        if self.default:
            self.obj.stub_default = f
        else:
            self.obj.stubs[self.ref] = f
        return f


# ------------------------------------------------------------------------------

class BinFormat(object):
    """
    Base class for binary format API, just to define default attributes
    and recommended properties. See elf.py, pe.py and macho.py for example of
    child classes.
    """
    is_ELF = False
    is_PE = False
    is_MachO = False
    basemap = None
    symtab = None
    strtab = None
    reltab = None
    functions = {}
    variables = {}

    @property
    def entrypoints(self):
        raise NotImplementedError

    @property
    def filename(self):
        raise NotImplementedError

    def loadsegment(self, S, pagesize=None, raw=None):
        raise NotImplementedError

    def getinfo(self, target):
        return (None, 0, 0)


class DataIO(BinFormat):
    """
    This class simply wraps a binary file or a bytes string and implements
    both the file and bytes interface. It allows an input to be provided as
    files of bytes and manipulated as either a file or a bytes object.
    """

    def __init__(self, f):
        if isinstance(f, bytes):
            from io import BytesIO

            self.f = BytesIO(f)
        else:
            self.f = f

    def __getitem__(self, i):
        stay = self.f.tell()
        sta = i.start or stay
        self.f.seek(sta, 0)
        if i.stop is None:
            data = self.f.read()
        else:
            data = self.f.read(i.stop - sta)
        self.f.seek(stay, 0)
        return data

    def read(self, size=-1):
        return self.f.read(size)

    def readline(self, size=-1):
        return self.f.readline(size)

    def readlines(self, size=-1):
        return self.f.readlines(size)

    def xreadlines(self, size=-1):
        return self.f.xreadlines(size)

    def write(self, s):
        return self.f.write(s)

    def writelines(self, l):
        return self.f.writelines(l)

    def seek(self, offset, whence=0):
        return self.f.seek(offset, whence)

    def tell(self):
        return self.f.tell()

    def flush(self):
        return self.f.flush()

    def fileno(self):
        return self.f.fileno()

    def isatty(self):
        return self.f.isatty()

    def next(self):
        return self.f.next()

    def truncate(self, size=0):
        return self.f.truncate(size)

    def close(self):
        return self.f.close()

    @property
    def closed(self):
        return self.f.closed

    @property
    def encoding(self):
        return self.f.encoding

    @property
    def errors(self):
        return self.f.errors

    @property
    def mode(self):
        return self.f.mode

    @property
    def name(self):
        try:
            return self.f.name
        except AttributeError:
            s = bytes(self.f.getvalue())
            return "(sc-%s...)" % ("".join(["%02x" % x for x in s])[:8])

    filename = name

    @property
    def newlines(self):
        return self.f.newlines

    @property
    def softspace(self):
        return self.f.softspace


# ------------------------------------------------------------------------------
def read_program(filename):
    """
    Identifies the program header and returns an ELF, PE, Mach-O or DataIO.

    Args:
        filename (str): the program to read.

    Returns:
        an instance of currently supported program format
        (ELF, PE, Mach-O, HEX, SREC)
    """

    try:
        data = open(filename, "rb")
    except (ValueError, TypeError, IOError):
        data = bytes(filename)

    f = DataIO(data)

    try:
        from amoco.system import elf

        # open file as a ELF object:
        p = elf.Elf(f)
        logger.info("ELF format detected")
        return p
    except elf.ElfError:
        f.seek(0)
        logger.debug("ElfError raised for %s" % f.name)

    try:
        from amoco.system import pe

        # open file as a PE object:
        p = pe.PE(f)
        logger.info("PE format detected")
        return p
    except pe.PEError:
        f.seek(0)
        logger.debug("PEError raised for %s" % f.name)

    try:
        from amoco.system import macho

        # open file as a Mach-O object:
        p = macho.MachO(f)
        logger.info("Mach-O format detected")
        return p
    except macho.MachOError:
        f.seek(0)
        logger.debug("MachOError raised for %s" % f.name)

    try:
        from amoco.system import utils

        # open file as a HEX object:
        p = utils.HEX(f)
        logger.info("HEX format detected")
        return p
    except utils.FormatError:
        f.seek(0)
        logger.debug(" HEX FormatError raised for %s" % f.name)

    try:
        # open file as a SREC object:
        p = utils.SREC(f)
        logger.info("SREC format detected")
        return p
    except utils.FormatError:
        f.seek(0)
        logger.debug(" SREC FormatError raised for %s" % f.name)

    logger.warning("unknown format")
    return f


# ------------------------------------------------------------------------------
# decorator that allows to "register" all loaders on-the-fly:


class DefineLoader(object):
    """
    A decorator that allows to register a system-specific loader
    while it is implemented. All loaders are stored in the class global
    LOADERS dict.

    Example:

           @DefineLoader('elf',elf.EM_386)
           def loader_x86(p):
             ...

    Here, a reference to function loader_x86 is stored in
    LOADERS['elf'][elf.EM_386].
    """
    LOADERS = {}

    def __init__(self, fmt, name=""):
        self.fmt = fmt
        self.name = name
        if not self.fmt in self.LOADERS:
            self.LOADERS[self.fmt] = {}
        if self.name in self.LOADERS[self.fmt]:
            logger.warning(
                "DefineLoader %s is already defined by %s"
                % (self.name, self.LOADERS[self.fmt][self.name].__name__)
            )

    def __call__(self, loader):
        logger.verbose(
            "DefineLoader %s[%s]: %s" % (self.fmt, self.name, loader.__name__)
        )
        if self.name:
            self.LOADERS[self.fmt][self.name] = loader
        else:
            self.LOADERS[self.fmt] = loader
        return loader


def load_program(f, cpu=None):
    """
    Detects program format header (ELF/PE/Mach-O/HEX/SREC),
    and *maps* the program in abstract memory,
    loading the associated "system" (linux/win) and "arch" (x86/arm),
    based header informations.

    Arguments:
        f (str): the program filename or string of bytes.

    Returns:
        a Task, ELF/PE (old CoreExec interfaces) or RawExec instance.
    """

    logger.verbose("--- define loaders ---")

    from . import raw
    from . import linux32
    from . import linux64
    from . import win32
    from . import win64
    from . import osx
    from . import baremetal

    logger.verbose("--- detect binary format ---")

    p = read_program(f)

    logger.verbose("--- create task ---")

    Loaders = DefineLoader.LOADERS
    if p.is_ELF:
        try:
            x = Loaders["elf"][p.Ehdr.e_machine](p)
        except KeyError:
            logger.error("ELF machine type not supported:\n%s" % p.Ehdr)
            x = None
    elif p.is_PE:
        try:
            x = Loaders["pe"][p.NT.Machine](p)
        except KeyError:
            logger.error("PE machine type not supported:\n%s" % p.NT)
            x = None
    elif p.is_MachO:
        try:
            x = Loaders["macho"][p.header.cputype](p)
        except KeyError:
            logger.error("Mach-O machine type not supported:\n%s" % p.header.cputype)
            x = None
    else:
        x = Loaders["raw"](p, cpu)
    return x
