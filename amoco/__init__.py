# -*- coding: utf-8 -*-

from .config import conf

# We don't import everything from .main by default. Especially we don't want
# to always import grandalf, because it imports numpy, which leaks memory
# (the garbage collector is not efficient enough)
# You can put [import_all] in your ~/.amocorc
if 'import_all' in conf.sections():
    from .main import *

