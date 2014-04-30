# This code is part of Amoco
# Copyright (C) 2006-2011 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

import logging

VERBOSE = 15
logging.addLevelName(VERBOSE,'VERBOSE')
#logging.captureWarnings(True)

default_format = logging.Formatter("%(name)s: %(levelname)s: %(message)s")

default_level  = logging.INFO

class Log(logging.Logger):
    def __init__(self,name,handler=logging.StreamHandler()):
        logging.Logger.__init__(self,name)
        handler.setFormatter(default_format)
        self.addHandler(handler)
        self.setLevel(default_level)
        self.register(name,self)

    def verbose(self,msg,*args,**kargs):
        return self.log(VERBOSE,msg,*args,**kargs)

    @classmethod
    def register(cls,name,self):
        if name in self.loggers:
            raise KeyError
        else:
            cls.loggers[name] = self


Log.loggers = {}
