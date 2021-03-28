# -*- coding: utf-8 -*-
"""
config.py
=========

This module defines the default amoco configuration
and loads any user-defined configuration file. It is based on the traitlets package.

Attributes:
    conf (Config): holds in a Config object based on Configurable traitlets,
        various parameters mostly related to how outputs should be formatted.

        The defined configurable sections are:

        - 'Code' which deals with how basic blocks are printed, with options:

            - 'helper' will use codeblock helper functions to pretty print code if True (default)
            - 'header' will show a dashed header line including the address of the block if True (default)
            - 'footer' will show a dashed footer line if True
            - 'segment' will show memory section/segment name in codeblock view if True (default)
            - 'bytecode' will show the hex encoded bytecode string of every instruction if True (default)
            - 'padding' will add the specified amount of blank chars to between address/bytecode/instruction (default 4).
            - 'hist' number of instruction's history shown in emulator view (default 3).

        - 'Cas' which deals with parameters of the algebra system:

            - 'noaliasing' will assume that mapper's memory pointers are not aliased if True (default)
            - 'complexity' threshold for expressions (default 100). See `cas.expressions` for details.
            - 'memtrace' store memory writes as mapper items if True (default).
            - 'unicode' will use math unicode symbols for expressions operators if True (default False).

        - 'DB' which deals with database backend options:

            - 'url' allows to define the dialect and/or location of the database (default to sqlite)
            - 'log' indicates that database logging should be redirected to the amoco logging handlers

        - 'Log' which deals with logging options:

            - 'level' one of 'ERROR' (default), 'VERBOSE', 'INFO', 'WARNING' or 'DEBUG' from less to more verbose,
            - 'tempfile' to also save DEBUG logs in a temporary file if True (default is False),
            - 'filename' to also save DEBUG logs using this filename.

        - 'UI' which deals with some user-interface pretty-printing options:

            - 'formatter' one of 'Null' (default), 'Terminal', "Terminal256', 'TerminalDark', 'TerminalLight', 'Html'
            - 'graphics' one of 'term' (default), 'qt' or 'gtk'
            - 'console' one of 'python' (default), or 'ipython'
            - 'unicode' will use unicode symbols for drawing lines and icons if True

        - 'Server' which deals with amoco's server parameters:

            - 'wbsz' sets the size of the server's internal shared memory buffer with spawned commands
            - 'timeout' sets the servers's internal timeout for the connection with spawned commands

        - 'Emu' which deals with amoco's emulator parameters:

            - 'hist' defines the size of the emulator's instructions' history list (defaults to 100.)
            - 'stacksize' defines the size in bytes of the emulator's frame view that displays the stack.

        - 'Arch' which allows to configure assembly format parameters:

            - 'assemble' (unused)
            - 'format_x86' one of 'Intel' (default), 'ATT'
            - 'format_x64' one of 'Intel' (default), 'ATT'
"""


import os
from traitlets.config import Configurable,PyFileConfigLoader
from traitlets import Integer, Unicode, Bool, observe

# -----------------------


class DB(Configurable):
    """
    Configurable parameters related to the database.

    Attributes:
        url (str): defaults to sqlite:// (in-memory database).
        log (Bool): If True, merges database's logs into amoco loggers.
    """
    url = Unicode("sqlite://", config=True)
    log = Bool(False, config=True)


class Code(Configurable):
    """
    Configurable parameters related to assembly blocks (code.block).

    Attributes:
        helper (Bool): use block helpers if True.
        header (Bool): display block header dash-line with its name if True.
        footer (Bool): display block footer dash-line if True.
        segment (Bool): display memory section/segment name if True.
        bytecode (Bool): display instructions' bytes.
        padding (int): add space-padding bytes to bytecode (default=4).
        hist (int): number of history instructions to show in
                    emulator's code frame view.
    """
    helper = Bool(True, config=True)
    header = Bool(True, config=True)
    footer = Bool(True, config=True)
    bytecode = Bool(True, config=True)
    segment = Bool(True, config=True)
    padding = Integer(4, config=True)
    hist = Integer(3, config=True)


class Cas(Configurable):
    """
    Configurable parameters related to the Computer Algebra System (expressions).

    Attributes:
        complexity (int): limit expressions complexity to given value. Defaults
                          to 10000, a relatively high value that keeps precision
                          but can lead to very large expressions.
        unicode (Bool): use unicode character for expressions' operators if True.
        noaliasing (Bool): If True (default), then assume that symbolic memory
                           expressions (pointers) are **never** aliased.
        memtrace (Bool): keep memory writes in mapper in addition to MemoryMap (default).
    """
    complexity = Integer(10000, config=True)
    unicode = Bool(False, config=True)
    noaliasing = Bool(True, config=True)
    memtrace = Bool(True, config=True)


class Log(Configurable):
    """
    Configurable parameters related to logging.

    Attributes:
        level (str): terminal logging level (defaults to 'INFO'.)
        filename (str): if not "" (default), a filename receiving VERBOSE logs.
        tempfile (Bool): log at VERBOSE level to a temporary tmp/ file if True.

    Note:
        observers for Log traits are defined in the amoco.logger module
        (to avoid module cyclic imports.)
    """
    level = Unicode("INFO", config=True)
    filename = Unicode("", config=True)
    tempfile = Bool(False, config=True)

class UI(Configurable):
    """
    Configurable parameters related to User Interface(s).

    Attributes:
        formatter (str): pygments formatter for pretty printing. Defaults to Null,
                         but recommended to be set to 'Terminal256' if pygments
                         package is installed.
        graphics (str):  rendering backend. Currently only 'term' is supported.
        console (str): default python console, either 'python' (default) or 'ipython'.
        completekey (str): client key for command completion (Tab).
        cli (str): client frontend. Currently only 'cmdcli' is supported.
    """
    formatter = Unicode("Null", config=True)
    graphics = Unicode("term", config=True)
    console = Unicode("python", config=True)
    completekey = Unicode("tab", config=True)
    cli = Unicode("cmdcli", config=True)
    unicode = Bool(False, config=True)


class Server(Configurable):
    """
    Configurable parameters related to the Server mode.

    Attributes:
        wbsz (int): size of the shared buffer between server and its command threads.
        timeout (int): timeout for the servers' command threads.
    """
    wbsz = Integer(0x1000, config=True)
    timeout = Integer(600, config=True)


class Arch(Configurable):
    """
    Configurable parameters related to CPU architectures.

    Attributes:
        assemble (Bool): unused yet.
        format_x86 (str): select disassembly flavor: Intel (default) vs. AT&T (att).
        format_x64 (str): select disassembly flavor: Intel (default) vs. AT&T (att).
    """
    assemble = Bool(False, config=True)
    format_x86 = Unicode("Intel", config=True)

    @observe("format_x86")
    def _format_x86_changed(self, change):
        from amoco.arch.x86.cpu_x86 import configure

        configure(format=change.new)

    format_x64 = Unicode("Intel", config=True)

    @observe("format_x64")
    def _format_x64_changed(self, change):
        from amoco.arch.x64.cpu_x64 import configure

        configure(format=change.new)


class Emu(Configurable):
    """
    Configurable parameters related to the amoco.emu module.

    Attributes:
        hist (int): size of the emulated instruction history list (defaults to 100.)
        stacksize (int): max-size of the stack frame displayed by the emulator (defaults to 256.)
    """
    hist = Integer(100, config=True)
    stacksize = Integer(256, config=True)


class System(Configurable):
    """
    Configurable parameters related to the system sub-package.

    Attributes:
        pagesize (int): provides the default memory page size in bytes.
        aslr (Bool): simulates ASLR if True. (not supported yet.)
        nx (Bool): unused.
    """
    pagesize = Integer(4096, config=True)
    aslr = Bool(False, config=True)
    nx = Bool(False, config=True)


class Config(object):
    """
    A Config instance takes an optional filename argument or
    looks for .amoco/config or .amocorc files to
    load a traitlets.config.PyFileConfigLoader used to adjust
    UI, DB, Code, Arch, Log, Cas, System, and Server parameters.

    Note:
        The Config object supports a print() method to display
        the entire configuration.
    """
    _locations = [".config/amoco/config", ".amoco/config", ".amocorc"]
    BANNER = "amoco (version 3.0)"

    def __init__(self, f=None):

        if f is not None:
            f = os.path.expanduser(f)
            self._locations = [f]
        for f in self._locations:
            cl = PyFileConfigLoader(filename=f, path=(".", os.getenv("HOME")))
            try:
                c = cl.load_config()
            except Exception:
                c = None
                self.f = None
            else:
                self.f = f
                break
        self.setup(c)

    def load(self,f):
        f = os.path.expanduser(f)
        cl = PyFileConfigLoader(filename=f, path=(".", os.getenv("HOME")))
        self.setup(cl.load_config())

    def setup(self,c=None):
        self.UI = UI(config=c)
        self.DB = DB(config=c)
        self.Code = Code(config=c)
        self.Arch = Arch(config=c)
        self.Log = Log(config=c)
        self.Cas = Cas(config=c)
        self.System = System(config=c)
        self.Emu = Emu(config=c)
        self.Server = Server(config=c)
        self.src = c

    def __str__(self):
        s = []
        mlen = 0
        for c in filter(
            lambda x: isinstance(getattr(self, x), Configurable), dir(self)
        ):
            pfx = "c.%s" % c
            c = getattr(self, c)
            for t in c.trait_names():
                if t in ("config", "parent"):
                    continue
                v = getattr(c, t)
                t = "{}.{}".format(pfx, t)
                mlen = max(mlen, len(t))
                if isinstance(v, str):
                    v = "'%s'" % v
                s.append((t, v))
        return "\n".join(("{:{mlen}} = {}".format(t, v, mlen=mlen) for (t, v) in s))


# define default config:
# -----------------------

conf = Config()

from amoco.logger import Log as _LogClass #lgtm [py/unsafe-cyclic-import]

logger = _LogClass(__name__)
logger.debug("loading module")
