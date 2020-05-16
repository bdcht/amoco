# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2019-2020 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

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
    """Amoco console for interactive mode.
    The console is based on IPython if found, or uses CPython otherwise.
    """
    c = amoco.conf
    cvars = dict(globals(), **locals())
    cvars.update(ctx.obj)
    cvars['term'] = Terminal()
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
        except ImportError:
            click.echo("readline not found")
        ic = InteractiveConsole(cvars)
        ic.push("print(amoco.conf.BANNER)")
        if exec_lines:
            for l in exec_lines: ic.push(l)
        ic.interact()


def spawn_emul(ctx,fallback=True):
    from amoco.ui.srv import srv
    q = ctx.obj['q']
    if hasattr(q,'view'):
        print(q.view)
    s = srv(obj=q)
    s.start(daemon=False)
    if fallback:
        spawn_console(ctx,["q"])


def spawn_gui(ctx):
    raise NotImplementedError


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
@click.argument("filename", nargs=1, type=click.Path(exists=True, dir_okay=False))
@click.option("-x", "--gui", is_flag=True, default=False, help="load with GUI")
@click.pass_context
def load_program(ctx, filename, gui):
    p = amoco.load_program(filename)
    ctx.obj["p"] = p
    if gui:
        spawn_gui(ctx)
    else:
        spawn_console(ctx)

@cli.command("bin_info")
@click.argument("filename", nargs=1, type=click.Path(exists=True, dir_okay=False))
@click.option("--header", is_flag=True, default=False, help="show ELF/PE/Mach-O header")
@click.pass_context
def bin_info(ctx, filename, header):
    p = amoco.load_program(filename)
    ctx.obj["p"] = p
    click.secho("file: ",fg='blue')
    click.secho(str(p.view.title))
    click.secho("checksec: ",fg='blue')
    click.echo(str(p.view.checksec))
    if header:
        click.secho("header:",fg='blue')
        click.echo(str(p.view.header))
    spawn_console(ctx)

@cli.command("emul_program")
@click.argument("filename", nargs=1, type=click.Path(exists=True, dir_okay=False))
@click.option("--gui", is_flag=True, default=False, help="load with GUI")
@click.option("--fallback", is_flag=True, default=False, help="fallback to console")
@click.pass_context
def emul_program(ctx, filename, gui, fallback):
    p = amoco.load_program(filename)
    q = amoco.emul(p)
    ctx.obj["p"] = p
    ctx.obj["q"] = q
    if gui:
        spawn_gui(ctx)
    else:
        spawn_emul(ctx,fallback)
