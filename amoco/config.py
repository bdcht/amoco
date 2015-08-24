# -*- coding: utf-8 -*-

import ConfigParser as cp
from collections import defaultdict

conf = cp.SafeConfigParser()

# define default config:
#-----------------------

# basic block section
conf.add_section('block')
conf.set('block', 'header'   , 'True')
conf.set('block', 'bytecode' , 'True')
conf.set('block', 'padding'  , '4'   )

# log section
conf.add_section('log')
conf.set('log', 'level', 'ERROR')
#conf.set('log', 'file', '/tmp/amoco.log')

# ui section
conf.add_section('ui')
conf.set('ui', 'formatter', 'Null')

# overwrite with config file:
import os
conf.read([os.path.expanduser('~/.amocorc')])

#-----------------------
def get_module_conf(module_name):
    D = defaultdict(lambda:None)
    if conf.has_section(module_name):
        for k,v in conf.items(module_name):
            k = k.lower()
            v = v.lower()
            if  k == 'true': D[k]=True
            elif k == 'false': D[k]=False
            else:
                try:
                    v = int(v,0)
                except ValueError: pass
            D[k] = v
    return D
