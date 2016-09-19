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

            - 'complexity' threshold for expressions (default 100). See expressions_ for details.

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

import ConfigParser as cp
from collections import defaultdict

conf = cp.SafeConfigParser()

# define default config:
#-----------------------

# basic block section
conf.add_section('block')
conf.set('block', 'header'   , 'True')
conf.set('block', 'footer'   , 'False')
conf.set('block', 'bytecode' , 'True')
conf.set('block', 'padding'  , '4'   )

conf.add_section('cas')
conf.set('cas', 'complexity' , '100'  )

# db section
conf.add_section('db')
conf.set('db', 'url', 'sqlite:///')
conf.set('db', 'log', 'False')

# log section
conf.add_section('log')
conf.set('log', 'level', 'ERROR')
conf.set('log', 'tempfile', 'True')

# ui section
conf.add_section('ui')
conf.set('ui', 'formatter', 'Null')
conf.set('ui', 'graphics', 'term')

# overwrite with config file:
import os
conf.read([os.path.expanduser('~/.amocorc')])

#-----------------------


def get_module_conf(module_name):
    """utility function that will return the dict of options related to a section name.

    Args:
        module_name (str): a section of the conf object, usually the name of the module (__name__).

    Returns:
        dict: The options associated to the section module_name, with values casted to their
        natural python types (lowercase strings, booleans, or integers).

    """
    D = defaultdict(lambda:None)
    if conf.has_section(module_name):
        for k,v in conf.items(module_name):
            if  v.lower() == 'true':
                D[k]=True
            if  v.lower() == 'false':
                D[k]=False
            else:
                try:
                    v = int(v,0)
                except ValueError: pass
            D[k] = v
    return D
