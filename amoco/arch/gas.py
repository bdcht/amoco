# This code is part of Amoco
# Copyright (C) 2013 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

try:
    import ply.lex as lex
    import ply.yacc as yacc
    _has_ply = True
except ImportError:
    _has_ply = False

from amoco.logger import Log
logger = Log(__name__)
#logger.level = 10

from collections import OrderedDict

import amoco.cas.expressions as expr

deprecated = ('.abort', '.line')

directives = (
  '.ABORT',
  '.align',
  '.altmacro',
  '.ascii',
  '.asciz',
  '.balign', '.balignw', '.balignl',
  '.bundle_align_mode', '.bundle_lock', '.bundle_unlock',
  '.byte',
  '.cfi_sections',
  '.cfi_startproc', '.cfi_endproc',
  '.cfi_personality',
  '.cfi_lsda',
  '.cfi_def_cfa', '.cfi_def_cfa_register', '.cfi_def_cfa_offset',
  '.cfi_adjust_cfa_offset', '.cfi_offset', '.cfi_rel_offset',
  '.cfi_register', '.cfi_restore', '.cfi_undefined',
  '.cfi_same_value', '.cfi_remember_state', '.cfi_return_column',
  '.cfi_signal_frame', '.cfi_window_save', '.cfi_escape',
  '.cfi_val_encoded_addr',
  '.comm', '.common', '.common.s',
  '.data',
  '.def',
  '.desc',
  '.dim',
  '.double',
  '.eject',
  '.else',
  '.elseif',
  '.end',
  '.endef',
  '.endfunc',
  '.endif',
  '.equ',
  '.equiv',
  '.eqv',
  '.err',
  '.error',
  '.exitm',
  '.extern',
  '.fail',
  '.file',
  '.fill',
  '.float',
  '.func',
  '.global', '.globl',
  '.gnu_attribute',
  '.hidden',
  '.hword',
  '.ident',
  '.if',
  '.incbin',
  '.include',
  '.int',
  '.internal',
  '.irp',
  '.irpc',
  '.lcomm',
  '.lflags',
  '.linkonce',
  '.list',
  '.ln',
  '.loc', '.loc_mark_blocks', '.loc_mark_labels',
  '.local',
  '.long',
  '.macro',
  '.mri',
  '.noaltmacro',
  '.nolist',
  '.octa',
  '.offset',
  '.org',
  '.p2align',
  '.popsection',
  '.previous',
  '.print',
  '.protected',
  '.psize',
  '.purgem',
  '.pushsection',
  '.quad',
  '.reloc',
  '.rept',
  '.sbttl',
  '.scl',
  '.section',
  '.set',
  '.short',
  '.single',
  '.size',
  '.skip',
  '.sleb128',
  '.space',
  '.stabd', '.stabn', '.stabs',
  '.string', '.string8', '.string16',
  '.struct',
  '.subsection',
  '.symver',
  '.tag',
  '.text',
  '.title',
  '.type',
  '.uleb128',
  '.val',
  '.version',
  '.vtable_entry', '.vtable_inherit',
  '.warning',
  '.weak',
  '.weakref',
  '.word'
)+deprecated

def setnumber(t,base,idx):
    t.lexer.pop_state()
    t.type = 'integer'
    try:
        x = int(t.value[idx:],base)
    except ValueError:
        print "Illegal Integer Constant '%s'" % t.value
        t.lexer.skip(1)
    else:
        t.value = x
        return t

#------------------------------------------------------------------------------
# LALR(1) parser for gas assembler syntax
class Gas:

    class Directive(object):
        def __init__(self,symbol,args=None):
            self.key = symbol
            self.args = args

    _tokens = (
        'comment',
        'eol',
        'directive',
        'symbol',
        'isymbol',
        'string',
        'character',
        'integer',
        'flonum',
        'shl', 'shr',
        'eq', 'neq',
        'leq', 'geq',
        'AND', 'OR'
    )

    _literals = [',',';','=',':','~','+','-','*','/','%','|','&','^','!','@','<','>','(',')']

    class Lexer(object):
        def __init__(self):
            self.states = (('select','exclusive'),
                           ('dstate','exclusive'),
                           ('istate','exclusive'),
                           ('number','exclusive'))
            self.tokens = Gas._tokens
            self.literals = Gas._literals
            self.t_ANY_ignore_whitespace = r'[\t\f\r ]'

        def t_ANY_comment(self,t):
            r'(/\*(.|\n)*\*/)|(\#.*)'
            pass

        def t_eol(self,t):
            r'\n'
            return t

        def t_dstate_istate_eol(self,t):
            r'(\n|;)'
            t.lexer.begin('INITIAL')
            return t

        def t_INITIAL_symbol(self,t):
            r'[A-Za-z_.$][A-Za-z0-9_.$]*'
            if t.value in directives:
                t.type = 'directive'
                t.lexer.begin('dstate')
            else:
                t.lexer.begin('select')
            return t

        def t_select_symbol(self,t):
            r'[^ \t\f\r]|\n'
            if t.value == ':':
                t.lexer.begin('INITIAL')
            elif t.value == '=':
                t.lexer.begin('dstate')
            else:
                t.lexer.begin('istate')
            t.lexer.lexpos -= 1

        def t_dstate_symbol(self,t):
            r'[A-Za-z_.$][A-Za-z0-9_.$]*'
            return t

        def t_istate_isymbol(self,t):
            r'[^;\n]+'
            cstart = t.value.find('/*')
            if cstart!=-1:
                cend   = t.value.find('*/',cstart)
                if cend!=-1:
                    t.value.replace(t.value[cstart,cend+2],'')
                else:
                    t.value = t.value[:cstart]
                    cend = t.lexer.lexdata.find('*/',t.lexer.lexpos)
                    if cend!=-1:
                        t.lexer.lexpos = cend+2
            return t

        def t_dstate_string(self,t):
            r'"(.|(\\\n))*"'
            return t

        def t_dstate_character(self,t):
            "('.)|('\\\\)"
            t.value = ord(t.value[1])
            return t

        def t_dstate_integer(self,t):
            "[1-9][0-9]*"
            t.value = int(t.value,10)
            return t

        def t_dstate_number_flonum(self,t):
            "[1-9][0-9]*\.[0-9]*([eE][+-]?[0-9]+)?"
            t.value = float(t.value)
            return t

        def t_dstate_other(self,t):
            "0"
            t.lexer.push_state('number')

        def t_number_ignore_f(self,t):
            r'[fF]'
            pass

        def t_number_integer_bin(self,t):
            r'[bB]-?[0-1]+'
            base=2
            idx=1
            return setnumber(t,base,idx)

        def t_number_integer_hex(self,t):
            r'[xX]-?[0-9a-fA-F]+'
            base=16
            idx=1
            return setnumber(t,base,idx)

        def t_number_integer_oct(self,t):
            r'[0-9]+' # include 8,9 digit to raise exception (avoids 008 -> 0, 8)
            base=8
            idx=0
            return setnumber(t,base,idx)

        def t_dstate_shl(self,t):
            r'<<'
            return t

        def t_dstate_shr(self,t):
            r'>>'
            return t

        def t_dstate_eq(self,t):
            r'=='
            return t

        def t_dstate_neq(self,t):
            r'<>|!='
            return t

        def t_dstate_leq(self,t):
            r'<='
            return t

        def t_dstate_geq(self,t):
            r'>='
            return t

        def t_dstate_AND(self,t):
            r'&&'
            return t
        def t_dstate_OR(self,t):
            r'\|\|'
            return t

        def t_ANY_error(self,t):
            print "Illegal character '%s'" % t.value[0]
            t.lexer.skip(1)

        def build(self,**kargs):
            if _has_ply:
                self._lexer = lex.lex(module=self, **kargs)

        def test(self,data):
            self._lexer.input(data)
            while 1:
                tok = self._lexer.token()
                if not tok: break
                print tok

    class Parser(object):
        def __init__(self):
            self.tokens = Gas._tokens
            self.precedence = (
                ('left', '+', '-'),
                ('left', 'AND', 'OR'),
                ('left', '*', '/'),
                ('nonassoc', 'shl', 'shr', '%', 'eq', 'neq', 'leq', 'geq'),
                ('right', 'UNARYOP'),
            )
            self.blks = OrderedDict()
            self.cur = None

        def __makelist(self,p):
            N=len(p)
            if N>2:
                L = p[1]
                L.append(p[N-1])
            else:
                L = []
                if N>1:
                    L.append(p[N-1])
            p[0] = L

        def p_statements(self,p):
            r'''statements : statements stmt
                           | stmt'''
            p[0] = self.blks

        def p_endstmt(self,p):
            r'''endstmt : ';' 
                        | eol
                        | comment '''
            pass

        def p_stmt_empty(self,p):
            r'''stmt : endstmt'''
            pass

        def p_stmt_labels(self,p):
            r'''stmt : labels'''
            self.cur = []
            for l in p[1]:
                if l not in self.blks:
                    self.blks[l] = self.cur
                else:
                    logger.warning('label %s redefined (ignored)'%l)

        def p_stmt_key(self,p):
            r'''stmt : key'''
            if self.cur is None:
                assert 0 not in self.blks
                self.blks[0]=self.cur=[]
            self.cur.append(p[1])

        def p_key_directive(self,p):
            r'''key : directive args endstmt'''
            p[0] = Gas.Directive(p[1],p[2])

        def p_key_asign(self,p):
            r'''key : symbol    '=' arg endstmt
                    | directive '=' arg endstmt'''
            p[0] = Gas.Directive('.set',[p[1],p[3]])

        def p_key_instr(self,p):
            r'''key : instruction endstmt'''
            p[0] = p[1]

        def p_instruction(self,p):
            r'''instruction : symbol isymbol
                            | symbol '''
            p[0] = ' '.join(p[1:])

        def p_labels(self,p):
            r'''labels : labels label
                       | label'''
            self.__makelist(p)

        def p_label(self,p):
            r'''label : symbol ':' '''
            p[0] = p[1]

        def p_args(self,p):
            r'''args : args ',' arg
                     | arg
                     | '''
            self.__makelist(p)

        def p_arg_1(self,p):
            r'''arg : string
                    | flonum
                    | expr'''
            p[0] = p[1]

        def p_arg_at(self,p):
            r'''arg : '@' symbol'''
            p[0] = p[1]+p[2]

        def p_expr2(self,p):
            r'''expr : expr op term'''
            a=p[1]
            b=p[3]
            p[0] = eval('a %s b'%p[2])

        def p_expr1(self,p):
            r'''expr : term'''
            p[0] = p[1]

        def p_op_arith(self,p):
            r'''op : '+'
                   | '-'
                   | '*'
                   | '/'
                   | '%'
                   | shl
                   | shr'''
            p[0] = p[1]

        def p_op_bit(self,p):
            r'''op : '^'
                   | '|'
                   | '&'
                   | AND
                   | OR'''
            p[0] = p[1]

        def p_op_comp(self,p):
            r'''op : '<'
                   | '>'
                   | eq
                   | neq
                   | leq
                   | geq'''
            p[0] = p[1]

        def p_term_unary(self,p):
            r'''term : '~' term %prec UNARYOP
                     | '-' term %prec UNARYOP'''
            if p[1]=='~':
                p[0] = ~p[2]
            else:
                p[0] = -p[2]

        def p_term_expr(self,p):
            r'''term : '(' expr ')' '''
            p[0] = p[2]

        def p_term_symbol(self,p):
            r'''term : symbol
                     | directive'''
            p[0] = expr.reg(p[1])

        def p_term_number(self,p):
            r'''term : integer
                     | character'''
            p[0] = expr.cst(p[1])

        def p_error(self,p):
            print 'Syntax Error',p
            self._parser.restart()

        def build(self,**kargs):
            opt=dict(debug=0,write_tables=0)
            opt.update(**kargs)
            if _has_ply:
                self._parser = yacc.yacc(module=self,**opt)

    def __init__(self,**kargs):
        self.lexer  = Gas.Lexer()
        self.parser = Gas.Parser()
        if not _has_ply:
            print 'warning: Gas parser not supported (install python-ply)'

    def parse(self,data):
        try:
            self.parser._parser.restart()
        except AttributeError:
            self.lexer.build(reflags=lex.re.UNICODE)
            self.parser.build()
        except:
            logger.warning('unexpected parser error')
            return None
        try:
            s = data.decode('utf-8')
        except UnicodeDecodeError:
            s = data
        L=self.parser._parser.parse(s, lexer=self.lexer._lexer,debug=logger)
        return L

    def read(self,filename):
        with file(filename,'r') as f:
            return self.parse(f.read())

