# -*- coding: utf-8 -*-
import ctypes
import multiprocessing as mp
import queue

from amoco.config import conf
from amoco.logger import Log, flush_all
from amoco.ui.cli import cmdcli_builder
logger = Log(__name__)
logger.debug('loading module')

from amoco.ui.cli import cmdcli_builder

STOPPED = 0
IDLE    = 1
WAITING = 2
STALLED = 3

commands = {}

class DefineSrvCommand(object):
    """decorator that allows to "register" commands on-the-fly
    """
    def __init__(self,name):
        global commands
        self.name = name
        if not self.name in commands:
            commands[self.name] = None
    def __call__(self,cls):
        global commands
        logger.verbose('DefineCommand %s:%s'%(self.name,cls))
        commands[self.name] = cls
        return cls

class srv(object):
    def __init__(self,scope=None,obj=''):
        if scope is None:
            scope = globals()
        self.scope = scope
        self.obj = obj
        self.cmds = commands

    def start(self,timeout=conf.Server.timeout):
        def do_cmd(i,cmdline):
            args = cmdline.split()
            cmd = args.pop(0)
            if cmd in self.cmds:
                logger.debug('Out[%d]: %s'%(i,cmdline))
                res = self.cmds[cmd].run(self,args)
            else:
                logger.debug('command not found: %s'%cmd)
                res = -1
            return res
        def mainloop(msgs,outs):
            i=0
            while True:
                try:
                    cmdline = msgs.get()
                except queue.Empty:
                    break
                else:
                    p = mp.Process(target=do_cmd,args=(i,cmdline))
                    p.start()
                    p.join(timeout)
                    if p.is_alive():
                        p.terminate()
                    outs.put(p.exitcode)
                    i += 1
            logger.verbose('server stopped (queue is empty.)')
            return i
        self.shar = mp.Array(ctypes.c_ubyte,[0]*conf.Server.wbsz)
        self.msgs = mp.Queue()
        self.outs = mp.Queue()
        self._srv = mp.Process(target=mainloop,args=(self.msgs,self.outs))
        self._srv.start()
        logger.verbose('server process is running.')
        self.interact()
        if self._srv.is_alive():
            self._srv.terminate()
            logger.verbose('server process is terminated.')
            self._srv = None

    def interact(self):
        if conf.UI.cli == 'cmdcli':
            cmdcli_builder(srv=self).cmdloop()



@DefineSrvCommand('hello')
class cmd_hello(object):
    @staticmethod
    def run(srv,args):
        print('Hello World!')
        print(args)

@DefineSrvCommand('scope')
class cmd_scope(object):
    @staticmethod
    def run(srv,args):
        print(srv.scope)
