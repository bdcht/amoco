# -*- coding: utf-8 -*-

from cStringIO import StringIO
from amoco.config import conf
from amoco.logger import Log
logger = Log(__name__)

try:
    from pygments.token import Token
    from pygments.style import Style
    from pygments.lexer import RegexLexer
    from pygments.formatters import *
except ImportError:
    logger.info("pygments package not found, no renderer defined")
    has_pygments = False

    class TokenType(type):
        def __getattr__(cls,key):
            return key
    class Token:
        __metaclass__ = TokenType

    class NullFormatter(object):
        def __init__(self,**options):
            self.options = options
        def format(self,tokensource,outfile):
            for t,v in tokensource:
                outfile.write(v)
else:
    logger.info("pygments package imported")
    has_pygments = True
    class DefaultStyle(Style):
        default_style = ""
        styles = {
          Token.Literal:  '#fff',
          Token.Address:  '#fb0',
          Token.Constant: '#f30',
          Token.Prefix:   '#fff',
          Token.Mnemonic: 'bold #fff',
          Token.Register: '#33f',
          Token.Memory:   '#3ff',
          Token.Comment:  '#8f8',
          Token.Name:     'underline #fff',
          Token.Tainted:  'bold #f00',
        }

    Formats = {
      'Terminal':TerminalFormatter(style=DefaultStyle),
      'Terminal256':Terminal256Formatter(style=DefaultStyle),
    }

default_formatter = NullFormatter()
if has_pygments:
    if conf.has_option("ui","formatter"):
        f = conf.get("ui","formatter")
        default_formatter = Formats.get(f,default_formatter)

def highlight(toks,formatter=None,outfile=None):
    formatter = formatter or default_formatter
    outfile = outfile or StringIO()
    formatter.format(toks,outfile)
    return outfile.getvalue()
