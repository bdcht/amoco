# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

import logging


VERBOSE = 15
logging.addLevelName(VERBOSE,'VERBOSE')
#logging.captureWarnings(True)

default_format = logging.Formatter("%(name)s: %(levelname)s: %(message)s")

try:
    from amoco import conf
    try:
        default_level = conf.getint('log','level')
        if default_level is None: default_level = 0
    except ValueError:
        default_level = logging._levelNames.get(conf.get('log','level'),0)
    if conf.has_option('log','file'):
        logfilename  = conf.get('log','file')
    else:
        logfilename  = None
except ImportError:
    default_level  = logging.ERROR
    logfilename = None

if logfilename:
    logfile = logging.FileHandler(logfilename,mode='w')
    logfile.setFormatter(default_format)
    logfile.setLevel(logging.DEBUG)
else:
    logfile = None

class Log(logging.Logger):
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
            s = ('='*done).ljust(barlen,'-')
            term.write('%s[%s] %s%%\r'%(pfx,s,ratio))
        else:
            s = ("%s[%d]"%(pfx,count)).ljust(80,' ')
            term.write("%s\r"%s)

    def setLevel(self,lvl):
        self.handlers[0].setLevel(lvl)

    @classmethod
    def register(cls,name,self):
        if name in self.loggers:
            raise KeyError
        else:
            cls.loggers[name] = self


def set_quiet():
    set_log_all(logging.ERROR)

def set_debug():
    set_log_all(logging.DEBUG)

def set_log_all(level):
    default_level = level
    for l in Log.loggers.itervalues():
        l.setLevel(level)

def set_log_file(filename):
    if logfile is not None:
        logfile.close()
    logfile = logging.FileHandler(logfilename,mode='w')
    logfile.setFormatter(default_format)
    logfile.setLevel(logging.DEBUG)
    for l in Log.loggers.itervalues():
        l.addHandler(logfile)

Log.loggers = {}
