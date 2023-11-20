# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2019-2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

"""
This is the 'Click' frontend that allows to invoke amoco directly from a shell with
command 'amoco'::

    $ amoco [-c/--config file]
            [-v/--verbose]
            [-g/--debug]
            [-q/--quiet]

This command essentially loads the amoco python package in the ipython interpreter or
the CPython interpreter if IPython is not installed.
The logging level can be adjusted with general options.

Several subcommands are also available::

    $ amoco [general options] bin_info "filename"
                              load_program [-x/--gui] "filename"
                              emul_program [-x/--gui] "filename"
"""

import click
from blessed import Terminal

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


def spawn_console(ctx,exec_lines=None):
    """
    Start the amoco interactive terminal console.
    The console is based on IPython if found, or uses CPython otherwise.
    This can be controlled by configuration (see c.UI.console.)
    """
    c = amoco.conf
    cvars = dict(globals(), **locals())
    cvars.update(ctx.obj)
    cvars['term'] = Terminal()
    if c.UI.console.lower() == "ipython":
        try:
            from IPython import start_ipython
        except (ImportError,ModuleNotFoundError):
            if c.Log.level=="VERBOSE":
                click.echo("ipython not found")
            c.UI.console = "python"
        else:
            ic = c.src.__class__()
            ic.TerminalTerminalIPythonApp.display_banner = False
            ic.InteractiveShellApp.exec_lines = ["print(amoco.conf.BANNER)"]
            ic.InteractiveShellApp.gui = c.UI.graphics
            if c.UI.formatter == 'TerminalLight':
                ic.TerminalInteractiveShell.colors = 'LightBG'
            if exec_lines:
                ic.InteractiveShellApp.exec_lines.extend(exec_lines)
            start_ipython(argv=[], config=ic, user_ns=cvars)
    elif c.UI.console.lower() == "python":
        from code import InteractiveConsole
        try:
            import readline, rlcompleter
            readline.set_completer(rlcompleter.Completer(cvars).complete)
            readline.parse_and_bind("Tab: complete")
            del readline, rlcompleter
        except (ImportError,ModuleNotFoundError):
            click.echo("readline not found")
        ic = InteractiveConsole(cvars)
        ic.push("print(amoco.conf.BANNER)")
        if exec_lines:
            for l in exec_lines: ic.push(l)
        ic.interact()


def spawn_emul(ctx,fallback=True):
    """
    Start the amoco interactive console-based emulator.
    If fallback is True, the amoco console is spawned when
    terminating the emulator.
    """
    from amoco.ui.srv import srv
    p = ctx.obj['p']
    if hasattr(p,'view'):
        print(p.view)
    s = srv(obj=p)
    s.start(daemon=False)
    if fallback:
        spawn_console(ctx,["p"])


def spawn_gui(ctx):
    """
    Let the amoco console show the graphic user interface
    for its current object.
    """
    do = ['from amoco.ui.graphics import load_engine',
          'load_engine()',
          'p.view.obj.show()',
          'p',
         ]
    spawn_console(ctx,do)

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
        amoco.conf.load(configfile)
    c = amoco.conf
    if quiet:
        amoco.logger.set_quiet()
    if verbose:
        amoco.logger.set_log_all("VERBOSE")
    if debug:
        amoco.logger.set_debug()
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
@click.option("-x", "--gui", is_flag=True, default=False, help="load with GUI")
@click.argument("filename", nargs=1, type=click.Path(exists=True, dir_okay=False))
@click.pass_context
def load_program(ctx, filename, gui):
    p = amoco.load_program(filename)
    ctx.obj["p"] = p
    if gui:
        spawn_gui(ctx)
    else:
        spawn_console(ctx,["p"])

@cli.command("bin_info")
@click.argument("filename", nargs=1, type=click.Path(exists=True, dir_okay=False))
@click.option("--header", is_flag=True, default=False, help="show executable format (ELF/PE/Mach-O/...) header")
@click.pass_context
def bin_info(ctx, filename, header):
    p = amoco.load_program(filename)
    ctx.obj["p"] = p
    click.secho("file: ",fg='blue')
    click.secho(str(p.view.title()))
    click.secho("checksec: ",fg='blue')
    click.echo(str(p.view.checksec))
    if header:
        click.secho("header:",fg='blue')
        click.echo(str(p.view.header))
    spawn_console(ctx)

@cli.command("emul_program")
@click.argument("filename", nargs=1, type=click.Path(exists=True, dir_okay=False))
@click.option("-x", "--gui", is_flag=True, default=False, help="load with GUI")
@click.option("-i", "--interact", is_flag=True, default=False,
              help="fallback to python interactive console")
@click.pass_context
def emul_program(ctx, filename, gui, interact):
    p = amoco.load_program(filename)
    p = amoco.emul(p)
    ctx.obj["p"] = p
    if gui:
        spawn_gui(ctx)
    else:
        spawn_emul(ctx,interact)

# ------------------------------------------------------------------------------
