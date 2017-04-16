# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
logger.py
=========

This module defines amoco logging facilities. The ``Log`` class inherits from a standard :py:class:`logging.Logger`,
with minor additional features like a ``'VERBOSE'`` level introduced between ``'INFO'`` and ``'DEBUG'``
levels, and a progress method that can be useful for time consuming activities. See below for details.

Most amoco modules start by creating their local ``logger`` object used to provide various feedback.
Users can thus focus on messages from selected amoco modules by adjusting their level independently,
or use the ``set_quiet()``, ``set_debug()`` or ``set_log_all(level)`` functions to adjust all loggers
at once.

Examples:
    Setting the mapper module to ``'VERBOSE'`` level::

        In [1]: import amoco
        In [2]: amoco.cas.mapper.logger.setlevel('VERBOSE')


    Setting all modules loggers to ``'ERROR'`` level::

        In [2]: amoco.set_quiet()

Note that amoco loggers are configured to log both to *stderr* with selected level
and to a temporary file with ``'DEBUG'`` level.

"""

import logging


VERBOSE = 15
logging.addLevelName(VERBOSE,u'VERBOSE')
#logging.captureWarnings(True)

default_format = logging.Formatter(u"%(name)s: %(levelname)s: %(message)s")

try:
    from amoco import conf
    def get_log_level():
        try:
            level = conf.getint('log','level')
            if level is None: level = 0
        except ValueError:
            level = logging.__dict__.get(conf.get('log','level'),0)
        return level
    default_level = get_log_level()
    if conf.has_option('log','file'):
        logfilename  = conf.get('log','file')
    elif conf.getboolean('log','tempfile'):
        import tempfile
        logfilename  = tempfile.mkstemp('.log',prefix="amoco-")[1]
    else:
        logfilename  = None
except ImportError:
    default_level  = logging.ERROR
    logfilename = None

if logfilename:
    logfile = logging.FileHandler(logfilename,mode='w')
    logfile.setFormatter(default_format)
    logfile.setLevel(logging.DEBUG)
    conf.set('log','file',logfilename)
else:
    logfile = None

class Log(logging.Logger):
    """This class is intended to allow amoco activities to be logged
    simultaneously to the *stderr* output with an adjusted level and to
    a temporary file with full verbosity.

    All instanciated Log objects are tracked by the Log class attribute ``Log.loggers``
    which maps their names with associated instances.

    The recommended way to create a Log object is to add, near the begining
    of amoco modules::

        from amoco.logger import Log
        logger = Log(__name__)

    """
    def __init__(self,name,handler=logging.StreamHandler()):
        logging.Logger.__init__(self,name)
        handler.setFormatter(default_format)
        self.addHandler(handler)
        self.setLevel(default_level)
        if logfile: self.addHandler(logfile)
        self.register(name,self)

    def verbose(self,msg,*args,**kargs):
        return self.log(VERBOSE,msg,*args,**kargs)

    def progress(self,count,total=0,pfx=''):
        if self.level<VERBOSE: return
        term = self.handlers[0].stream
        if not term.isatty(): return
        if total>0:
            barlen = 40
            fillr = min((count+1.)/total,1.)
            done = int(round(barlen*fillr))
            ratio = round(100. * fillr, 1)
            s = (u'='*done).ljust(barlen,u'-')
            term.write(u'%s[%s] %s%%\r'%(pfx,s,ratio))
        else:
            s = (u"%s[%d]"%(pfx,count)).ljust(80,u' ')
            term.write(u"%s\r"%s)

    def setLevel(self,lvl):
        self.handlers[0].setLevel(lvl)

    @classmethod
    def register(cls,name,self):
        if name in self.loggers:
            raise KeyError
        else:
            cls.loggers[name] = self


def set_quiet():
    """set all loggers to ``'ERROR'`` level
    """
    set_log_all(logging.ERROR)

def set_debug():
    """set all loggers to ``'DEBUG'`` level
    """
    set_log_all(logging.DEBUG)

def set_log_all(level):
    """set all loggers to specified level

    Args:
        level (int): level value as an integer.
    """
    default_level = level
    for l in Log.loggers.itervalues():
        l.setLevel(level)

def set_log_file(filename):
    """set log file for all loggers

    Args:
        filename (str): filename for the FileHandler added
                         to all amoco loggers
    """
    if logfile is not None:
        logfile.close()
    logfile = logging.FileHandler(logfilename,mode='w')
    logfile.setFormatter(default_format)
    logfile.setLevel(logging.DEBUG)
    for l in Log.loggers.itervalues():
        l.addHandler(logfile)

Log.loggers = {}
