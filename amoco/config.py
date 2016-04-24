# -*- coding: utf-8 -*-

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

# log section
conf.add_section('log')
conf.set('log', 'level', 'ERROR')
#conf.set('log', 'file', '/tmp/amoco.log')

# ui section
conf.add_section('ui')
conf.set('ui', 'formatter', 'Null')
conf.set('ui', 'graphics', 'term')

# overwrite with config file:
import os
conf.read([os.path.expanduser('~/.amocorc')])

#-----------------------
def get_module_conf(module_name):
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
