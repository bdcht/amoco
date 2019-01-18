# -*- coding: utf-8 -*-
"""
config.py
=========

This module defines the default amoco configuration
and loads any user-defined configuration file.

Attributes:
    conf (SafeConfigParser): holds in a standard ConfigParser object,
        various parameters mostly related to how outputs should be formatted.

        The defined sections are:

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

        - 'log' which deals with logging options:

            - 'level' one of 'ERROR' (default), 'VERBOSE', 'INFO', 'WARNING' or 'DEBUG' from less to more verbose,
            - 'tempfile' to also save DEBUG logs in a temporary file if True (default),
            - 'filename' to also save DEBUG logs using this filename.

        - 'ui' which deals with some user-interface pretty-printing options:

            - 'formatter' one of 'Null' (default), 'Terminal', "Terminal256', 'TerminalDark', 'TerminalLight', 'Html'
            - 'graphics' one of 'term' (default), 'qt' or 'gtk'

"""

from os.path import expanduser
from os import access, F_OK, R_OK
from io import StringIO
from collections import defaultdict

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

#-----------------------

_locations = ['~/.amoco/config', '~/.amocorc']

_default = u"""
[block]
header   = True
footer   = False
bytecode = True
padding  = 4

[cas]
complexity = 10000
unicode    = False
noaliasing = True

[db]
url = sqlite://
log = False

[log]
level    = WARNING
tempfile = True

[ui]
formatter = Null
graphics  = term

[x86]
format = Intel
"""

class confdict(defaultdict):

    def __setitem__(self,key,value):
        super(confdict,self).__setitem__(key,value)

class Conf(object):
    def __init__(self,default):
        self.cp = ConfigParser()
        self.cp.readfp(StringIO(default))
        for f in _locations:
            f = expanduser(f)
            if access(f,F_OK|R_OK):
                self.cp.read([f])
                break
        self.setup()

    def setup(self):
        self.sections = defaultdict(lambda:None)
        for s in self.cp.sections():
            self.sections[s] = defaultdict(lambda:None)
            for (k,v) in self.cp.items(s):
                self.sections[s][k] = self.converter(v)

    def converter(self,value):
        if value in ('True','true'): return True
        if value in ('False','false'): return False
        try:
            return int(value,0)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value

# define default config:
#-----------------------

conf = Conf(_default)

def conf_proxy(module_name):
    return conf.sections[module_name.split('.')[-1]]

