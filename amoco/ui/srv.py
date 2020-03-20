# -*- coding: utf-8 -*-
import ctypes
import multiprocessing as mp
import queue
from amoco.config import conf
from amoco.ui.render import Token, highlight
from amoco.ui.cli import cmdcli_builder

from amoco.logger import Log
logger = Log(__name__)
logger.debug("loading module")


STOPPED = 0
IDLE = 1
WAITING = 2
STALLED = 3

commands = {}


class DefineSrvCommand(object):
    """decorator that allows to "register" commands on-the-fly
    """

    def __init__(self, name):
        global commands
        self.name = name
        if not self.name in commands:
            commands[self.name] = None

    def __call__(self, cls):
        global commands
        logger.verbose("DefineCommand %s:%s" % (self.name, cls))
        commands[self.name] = cls
        return cls


class srv(object):
    def __init__(self, scope=None, obj=""):
        if scope is None:
            scope = globals()
        self.scope = scope
        self.obj = obj
        self.cmds = commands

    def start(self, timeout=conf.Server.timeout):
        def do_cmd(i, cmdline):
            args = cmdline.split()
            cmd = args.pop(0)
            if cmd in self.cmds:
                # logger.debug('Out[%d]: %s'%(i,cmdline))
                res = self.cmds[cmd].run(self, args)
            else:
                logger.debug("command not found: %s" % cmd)
                res = 0
            return res

        def mainloop(msgs, outs):
            i = 0
            while True:
                try:
                    cmdline = msgs.get()
                except queue.Empty:
                    break
                else:
                    if cmdline.endswith("&"):
                        cmdline = cmdline.replace("&", "")
                        p = mp.Process(target=do_cmd, args=(i, cmdline))
                        p.start()
                        p.join(timeout)
                        if p.is_alive():
                            p.terminate()
                        outs.put(p.exitcode)
                    else:
                        res = do_cmd(i, cmdline)
                        outs.put(res)
                    i += 1
            logger.verbose("server stopped (queue is empty.)")
            return i

        self.shar = mp.Array(ctypes.c_ubyte, [0] * conf.Server.wbsz)
        self.msgs = mp.Queue()
        self.outs = mp.Queue()
        self._srv = mp.Process(target=mainloop, args=(self.msgs, self.outs))
        self._srv.start()
        cmd_hello.run(self, [])
        self.interact()
        if self._srv.is_alive():
            self._srv.terminate()
            logger.verbose("server process terminated.")
            self._srv = None

    def interact(self):
        if conf.UI.cli == "cmdcli":
            cmdcli_builder(srv=self).cmdloop()


@DefineSrvCommand("hello")
class cmd_hello(object):
    @staticmethod
    def run(srv, args):
        s = "server process is running"
        if srv._srv.pid:
            s += " (pid:%d)" % srv._srv.pid
        L = ["%s." % s]
        if srv.obj:
            L.append("%s is loaded" % srv.obj)
        print("\n".join(L))
        return 0


@DefineSrvCommand("load")
class cmd_scope(object):
    @staticmethod
    def run(srv, args):
        if len(args) == 1:
            filename = args[0]
            if not srv.obj:
                from amoco.system import load_program

                srv.obj = load_program(filename)
                if srv.obj:
                    print(srv.obj)
        return 0
