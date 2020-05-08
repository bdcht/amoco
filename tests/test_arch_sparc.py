import pytest
import codecs
from amoco.arch.sparc import cpu_v8 as cpu
from amoco.arch.sparc.env import *

# enforce synthetic syntax and NullFormatter output:
cpu.instruction_sparc.set_formatter(cpu.SPARC_V8_synthetic)
from amoco.ui import render
render.conf.UI.formatter = 'Null'

def test_decoder_000():
  c = b'\x9d\xe3\xbf\x98'
  i = cpu.disassemble(c)
  assert i.mnemonic == 'save'
  assert i.operands[0].ref == 'sp'
  assert i.operands[1] == -104
  assert i.operands[2].ref == 'sp'
  assert str(i) == 'save  %sp, -104, %sp'

def test_decoder_001():
  c = b'\xc0\x27\xbf\xfc'
  i = cpu.disassemble(c)
  assert i.mnemonic == 'st'
  assert i.operands[0].ref == 'g0'
  assert i.operands[1].size == 32
  assert i.operands[1].base.ref == 'fp'
  assert i.operands[1].disp == -4
  assert str(i) == 'clr  [%fp+-4]'

def test_decoder_002():
  c = b'\xc2\x07\xbf\xfc'
  i = cpu.disassemble(c)
  assert i.mnemonic == 'ld'
  assert i.operands[0].size == 32
  assert i.operands[0].base.ref == 'fp'
  assert i.operands[0].disp == -4
  assert i.operands[1].ref == 'g1'
  assert str(i) == 'ld  [%fp+-4], %g1'

def test_decoder_003():
  c = b'\x82\x00\x60\x42'
  i = cpu.disassemble(c)
  assert i.mnemonic == 'add'
  assert i.operands[0].ref == 'g1'
  assert i.operands[1] == 0x42
  assert i.operands[2].ref == 'g1'
  assert str(i) == 'inc  0x42, %g1'

def test_decoder_004():
  c = b'\xc2\x27\xbf\xfc'
  i = cpu.disassemble(c)
  assert i.mnemonic == 'st'
  assert i.operands[0].ref == 'g1'
  assert i.operands[1].size == 32
  assert i.operands[1].base.ref == 'fp'
  assert i.operands[1].disp == -4
  assert str(i) == 'st  %g1, [%fp+-4]'

def test_decoder_005():
  c = b'\xb0\x10\x00\x01'
  i = cpu.disassemble(c)
  assert i.mnemonic == 'or'
  assert i.operands[0].ref == 'g0'
  assert i.operands[1].ref == 'g1'
  assert i.operands[2].ref == 'i0'
  assert str(i) == 'mov  %g1, %i0'

def test_decoder_006():
  c = b'\x81\xe8\x00\x00'
  i = cpu.disassemble(c)
  assert i.mnemonic == 'restore'
  assert str(i) == 'restore'

def test_decoder_007():
  c = b'\x81\xc3\xe0\x08'
  i = cpu.disassemble(c)
  assert i.mnemonic == 'jmpl'
  assert str(i.operands[0]) == '(o7+0x8)'
  assert i.operands[1].ref == 'g0'
  assert str(i) == 'retl'

def test_decoder_008():
  c = b'\x01\x00\x00\x00'
  i = cpu.disassemble(c)
  assert i.mnemonic == 'nop'
  assert str(i) == 'nop  '
