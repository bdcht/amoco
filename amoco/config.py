# -*- coding: utf-8 -*-
"""
config.py
=========

This module defines the default amoco configuration
and loads any user-defined configuration file.

Attributes:
    conf (Config): holds in a Config object based on Configurable traitlets,
        various parameters mostly related to how outputs should be formatted.

        The defined configurable sections are:

        - 'block' which deals with how basic blocks are printed, with options:

            - 'header' will show a dashed header line including the address of the block if True (default)
            - 'footer' will show a dashed footer line if True
            - 'bytecode' will show the hex encoded bytecode string of every instruction if True (default)
            - 'padding' will add the specified amount of blank chars to between address/bytecode/instruction (default 4).

        - 'cas' which deals with parameters of the algebra system:

            - 'complexity' threshold for expressions (default 100). See `cas.expressions` for details.
            - 'unicode' will use math unicode symbols for expressions operators if True (default False).

        - 'db' which deals with database backend options:

            - 'url' allows to define the dialect and/or location of the database (default to sqlite)
            - 'log' indicates that database logging should be redirected to the amoco logging handlers

        - 'logger' which deals with logging options:

            - 'level' one of 'ERROR' (default), 'VERBOSE', 'INFO', 'WARNING' or 'DEBUG' from less to more verbose,
            - 'tempfile' to also save DEBUG logs in a temporary file if True (default),
            - 'filename' to also save DEBUG logs using this filename.

        - 'ui' which deals with some user-interface pretty-printing options:

            - 'formatter' one of 'Null' (default), 'Terminal', "Terminal256', 'TerminalDark', 'TerminalLight', 'Html'
            - 'graphics' one of 'term' (default), 'qt' or 'gtk'
            - 'console' one of 'python' (default), or 'ipython'

"""


from traitlets.config import Configurable
from traitlets import Integer, Unicode, Bool, observe

try:
    unicode('a')
except NameError:
    unicode = str

#-----------------------


class DB(Configurable):
    "configurable parameters related to the database"
    url    = Unicode('sqlite://',config=True)
    log    = Bool(False,config=True)

class Code(Configurable):
    "configurable parameters related to assembly blocks"
    helper = Bool(True,config=True)
    header   = Bool(True,config=True)
    footer   = Bool(True,config=True)
    bytecode = Bool(True,config=True)
    padding  = Integer(4,config=True)

class Cas(Configurable):
    "configurable parameters related to the Computer Algebra System (expressions)"
    complexity = Integer(10000,config=True)
    unicode    = Bool(False,config=True)
    noaliasing = Bool(True,config=True)

class Log(Configurable):
    "configurable parameters related to logging"
    level = Unicode('WARNING',config=True)
    filename = Unicode('',config=True)
    tempfile = Bool(False,config=True)

class UI(Configurable):
    "configurable parameters related to User Interface(s)"
    formatter = Unicode('Null',config=True)
    graphics  = Unicode('term',config=True)
    console   = Unicode('python',config=True)

class Arch(Configurable):
    assemble = Bool(False,config=True)
    format_x86 = Unicode('Intel',config=True)
    @observe('format_x86')
    def _format_x86_changed(self,change):
        from amoco.arch.x86.cpu_x86 import configure
        configure(format=change.new)
    format_x64 = Unicode('Intel',config=True)
    @observe('format_x64')
    def _format_x64_changed(self,change):
        from amoco.arch.x64.cpu_x64 import configure
        configure(format=change.new)

class System(Configurable):
    pagesize  = Integer(4096,config=True)
    aslr = Bool(False,config=True)
    nx = Bool(False,config=True)

class Config(object):
    _locations = ['.amoco/config', '.amocorc']
    BANNER = "amoco (version 3.0)"

    def __init__(self,f=None):
        if f is None:
            from os import getenv
            from traitlets.config import PyFileConfigLoader
            for f in self._locations:
                cl = PyFileConfigLoader(filename=f,path=('.',getenv('HOME')))
                try:
                    c = cl.load_config()
                except:
                    c = None
                    self.f = None
                else:
                    self.f = f
                    break
        self.UI = UI(config=c)
        self.DB = DB(config=c)
        self.Code = Code(config=c)
        self.Arch = Arch(config=c)
        self.Log = Log(config=c)
        self.Cas = Cas(config=c)
        self.System = System(config=c)
        self.src = c

    def __str__(self):
        s = []
        mlen = 0
        for c in filter(lambda x: isinstance(getattr(self,x),Configurable),
                       dir(self)):
            pfx = "c.%s"%c
            c = getattr(self,c)
            for t in c.trait_names():
                if t in ('config','parent'): continue
                v = getattr(c,t)
                t = '{}.{}'.format(pfx,t)
                mlen = max(mlen,len(t))
                if isinstance(v,unicode): v="'%s'"%v
                s.append((t,v))
        return u'\n'.join(('{:{mlen}} = {}'.format(t,v,mlen=mlen) for (t,v) in s))


# define default config:
#-----------------------

conf = Config()

