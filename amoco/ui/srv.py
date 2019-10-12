# -*- coding: utf-8 -*-

import multiprocessing as mp

from amoco.config import conf
from amoco.logger import Log
logger = Log(__name__)
logger.debug('loading module')

class srv(object):
    def __init__(self):
        self.cmds = mp.Queue()
        self.outs = mp.Queue()
