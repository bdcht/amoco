import os
import click
from amoco import *

@click.command()
def cli():
    try:
        from IPython.terminal.prompts import Prompts, Token
        from IPython.terminal.embed import InteractiveShellEmbed
        from traitlets.config.loader import Config
        class CustomPrompt(Prompts):
            def in_prompt_tokens(self, cli=None):
               return [
                    (Token.Prompt, 'amoco>'),
                    ]
            def out_prompt_tokens(self):
               return [
                    (Token.OutPrompt, ''),
                ]
        cfg = Config()
        cfg.TerminalInteractiveShell.prompts_class=CustomPrompt
        ipshell = InteractiveShellEmbed(config=cfg)
        ipshell()

    except ImportError:
        from code import interact
        interact(local=dict(globals(), **locals()))

