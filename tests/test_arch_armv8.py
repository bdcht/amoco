import pytest

from amoco.arch.arm import cpu_armv8 as cpu
from amoco.arch.arm.v8.env64 import *

from amoco.ui import render
render.conf.UI.formatter = 'Null'

def test_decoder_000():
  c = b'\x67\x0a\x00\xd0'
  i = cpu.disassemble(c)
  assert i.mnemonic=='ADRP'
  assert i.operands[0] == r7
  assert i.operands[1] == 0x14e000

def test_decoder_001():
  c = b'\xe1\x17\x9f\x1a'
  i = cpu.disassemble(c)
  assert i.mnemonic=='CSINC'
  assert i.operands[0] == w1
  assert CONDITION[i.cond^1][0] == 'eq'

def test_decoder_003():
  c = b'\xe5\x54\x42\xb8'
  i = cpu.disassemble(c)
  assert i.mnemonic=='LDR'
  assert i.operands[0] == w5
  assert i.operands[1] == r7
  assert i.operands[2] == 0x25

# SIMD:

def test_decoder_00x():
  c = b'\xe5\x54\x42\xfd'
  i = cpu.disassemble(c)

def test_decoder_00x():
  c = b'\xe5\x54\x42\xbd'
  i = cpu.disassemble(c)

#------------------------------------------------------------------------------

def test_asm_000(map):
  c = b'\x67\x0a\x00\xd0'
  i = cpu.disassemble(c)
  # fake eip cst:
  map[pc] = cst(0x400924,64)
  i(map)
  assert map(r7)==0x54e000

