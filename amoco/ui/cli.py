# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2018-2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
cli.py
======

This module...
"""

import cmd
import time
from amoco.config import conf
from amoco.ui.render import Token, highlight
from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")


def cmdcli_builder(srv):
    cmdcli = type("cmdcli", (cmdcli_core,), {})
    func = cmdcli.default
    for cname,cdef in srv.cmds.items():
        setattr(cmdcli, "do_%s" % cname, func)
        setattr(cmdcli, "help_%s" % cname,
                   lambda x,m=cdef.__doc__: print(m))
    s = cmdcli(srv)
    return s


class cmdcli_core(cmd.Cmd):
    intro = conf.BANNER

    def __init__(self, srv):
        cmd.Cmd.__init__(self, completekey=conf.UI.completekey)
        self.srv = srv
        prompt = [(Token.Mnemonic, "amoco"), (Token.Literal, "> ")]
        self.prompt = highlight(prompt)

    def precmd(self, line):
        if (self.srv._srv is None) or self.srv._srv.is_alive():
            return line
        else:
            return "EOF"

    def onecmd(self, line):
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if line == "EOF":
            self.lastcmd = ""
            print()
            return True
        elif cmd == "help":
            self.lastcmd = cmd
            return self.do_help(arg)
        return self.default(line)

    def default(self, line):
        "default command handler will pass line to the server"
        # check if the server is running in its own thread (daemon):
        if self.srv._srv is not None:
            # if it is, just end it the line...
            self.srv.ctrl.put(line)
        else:
            # otherwise, the server is just an object in the current
            # thread, so we call the command directly and put the
            # return code in outs queue:
            res = self.srv._do_cmd(0,line)
            time.sleep(0.1)
            self.srv.outs.put(res)
        # when outs queue receives server's response, it means
        # that the command has finished executing:
        while self.srv.outs.empty():
            try:
                print(self.srv.msgs.get_nowait())
            except Exception:
                pass
        # get the return code
        res = self.srv.outs.get()
        # print received messages from server command execution:
        while not self.srv.msgs.empty():
            print(self.srv.msgs.get())
        return res
