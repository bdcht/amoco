import cmd
from types import MethodType
from amoco.config import conf
from amoco.ui.render import Token, highlight
from amoco.logger import Log

logger = Log(__name__)
logger.debug("loading module")


def spawn_console():
    """ amoco console for interactive mode.
    The console is based on IPython if found, or uses CPython otherwise.
    """
    c = conf
    cvars = dict(globals(), **locals())
    if c.Terminal.console.lower() == "ipython":
        try:
            from IPython import start_ipython
        except ImportError:
            logger.verbose("ipython not found")
            c.Terminal.console = "python"
        else:
            ic = c.src.__class__()
            ic.TerminalTerminalIPythonApp.display_banner = False
            ic.InteractiveShellApp.exec_lines = ["print(conf.BANNER)"]
            start_ipython(argv=[], config=ic, user_ns=cvars)
    if c.Terminal.console.lower() == "python":
        from code import interact

        try:
            import readline, rlcompleter

            readline.set_completer(rlcompleter.Completer(cvars).complete)
            readline.parse_and_bind("Tab: complete")
            del readline, rlcompleter
        except ImportError:
            logger.verbose("readline not found")
        interact(banner=conf.BANNER + "\n", local=cvars)


def cmdcli_builder(srv):
    cmdcli = type("cmdcli", (cmdcli_core,), {})
    func = cmdcli.default
    for c in srv.cmds.keys():
        setattr(cmdcli, "do_%s" % c, func)
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
        if self.srv._srv.is_alive():
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
            return self.do_EOF(arg)
        return self.default(line)

    def do_EOF(self, args):
        print()
        return True

    def default(self, line):
        self.srv.msgs.put(line)
        res = self.srv.outs.get()
        return res
