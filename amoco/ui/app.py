import click

import amoco

# we want command aliases:


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail("Too many matches: %s" % ", ".join(sorted(matches)))


# ------------------------------------------------------------------------------


def spawn_console(ctx):
    """Amoco console for interactive mode.
    The console is based on IPython if found, or uses CPython otherwise.
    """
    c = amoco.conf
    cvars = dict(globals(), **locals())
    cvars.update(ctx.obj)
    if c.UI.console.lower() == "ipython":
        try:
            from IPython import start_ipython
        except ImportError:
            if conf.VERBOSE:
                click.echo("ipython not found")
            c.UI.console = "python"
        else:
            ic = c.src.__class__()
            ic.TerminalTerminalIPythonApp.display_banner = False
            ic.InteractiveShellApp.exec_lines = ["print(amoco.conf.BANNER)"]
            start_ipython(argv=[], config=ic, user_ns=cvars)
    elif c.UI.console.lower() == "python":
        from code import interact

        try:
            import readline, rlcompleter

            readline.set_completer(rlcompleter.Completer(cvars).complete)
            readline.parse_and_bind("Tab: complete")
            del readline, rlcompleter
        except ImportError:
            click.echo("readline not found")
        interact(banner=amoco.conf.BANNER + "\n", local=cvars)


def spawn_gui(ctx):
    from amoco.ui.srv import srv

    s = srv(obj=ctx.obj["p"])
    s.start()


# ------------------------------------------------------------------------------


@click.group(invoke_without_command=True, cls=AliasedGroup)
@click.option("-v", "--verbose", is_flag=True, default=False)
@click.option("-g", "--debug", is_flag=True, default=False)
@click.option("-q", "--quiet", is_flag=True, default=False)
@click.option(
    "-c",
    "--config",
    "configfile",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.pass_context
def cli(ctx, verbose, debug, quiet, configfile):
    ctx.obj = {}
    if configfile:
        amoco.conf = amoco.conf.__class__(configfile)
    c = amoco.conf
    if quiet:
        amoco.set_quiet()
    if verbose:
        amoco.set_log_all("VERBOSE")
    if debug:
        amoco.set_debug()
    if verbose | debug:
        if c.src:
            click.echo("config file '%s' loaded" % c.f)
        else:
            click.echo("default config loaded (file '%s' not found)" % c.f)
    if ctx.invoked_subcommand is None:
        spawn_console(ctx)
    else:
        if debug:
            click.echo("COMMAND: %s" % ctx.invoked_subcommand)


# ------------------------------------------------------------------------------


@cli.command("load_program")
@click.argument("filename", nargs=1, type=click.Path(exists=True, dir_okay=False))
@click.option("-x", "--gui", is_flag=True, default=False, help="load with GUI")
@click.pass_context
def load_program(ctx, filename, gui):
    p = amoco.system.load_program(filename)
    ctx.obj["p"] = p
    if gui:
        spawn_gui(ctx)
    else:
        spawn_console(ctx)
