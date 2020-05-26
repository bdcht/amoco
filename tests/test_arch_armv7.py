import pytest
import struct
from amoco.arch.arm import cpu_armv7 as cpu
from amoco.arch.arm.v7.env import *

from amoco.ui import render
render.conf.UI.formatter = 'Null'

def test_decoder_STR():
  #        cond 010 P U 0 W 0 Rn   Rt   imm12          => STR
  v = int('0000 010 1 1 0 1 0 0001 0010 1000 1001 1010'.replace(' ',''),2)
  c = struct.pack('<I',v)
  i = cpu.disassemble(c)
  assert i.mnemonic == "STR"
  assert str(i) == "str.eq      r2, [r1, #+2202]!"

  #        cond 010 P U 0 W 0 Rn   Rt   imm12          => STR
  v = int('0000 010 0 1 0 0 0 0001 0010 1000 1001 1010'.replace(' ',''),2)
  c = struct.pack('<I',v)
  i = cpu.disassemble(c)
  assert i.mnemonic == "STR"
  assert str(i) == "str.eq      r2, [r1], #+2202"

def test_decoder_STRT():
  #        cond 010 P U 0 W 0 Rn   Rt   imm12          => STRT
  v = int('0000 010 0 1 0 1 0 0001 0010 1000 1001 1010'.replace(' ',''),2)
  c = struct.pack('<I',v)
  i = cpu.disassemble(c)
  assert i.mnemonic == "STRT"
  assert str(i) == "strt.eq     r2, [r1], #+2202"

def test_decoder_ROR_RRX():
  v = int('1110 00 0 1101 1 0000 0001 10000 110 0010'.replace(' ',''),2)
  c = struct.pack('<I',v)
  i = cpu.disassemble(c)
  assert i.mnemonic == "ROR"
  assert i.operands[-1] == 16
  v = int('1110 00 0 1101 1 0000 0001 00000 110 0010'.replace(' ',''),2)
  c = struct.pack('<I',v)
  i = cpu.disassemble(c)
  assert i.mnemonic == "RRX"
  assert len(i.operands)==2

def test_decoder_BFI_BFC():
  #        cond         msb   Rd   lsb       Rn
  v = int('1110 0111110 00001 0001 00001 001 0010'.replace(' ',''),2)
  c = struct.pack('<I',v)
  i = cpu.disassemble(c)
  assert i.mnemonic == "BFI"
  assert len(i.operands)==4
  #        cond         msb   Rd   lsb       Rn
  v = int('1110 0111110 00001 0001 00001 001 1111'.replace(' ',''),2)
  c = struct.pack('<I',v)
  i = cpu.disassemble(c)
  assert i.mnemonic == "BFC"
  assert len(i.operands)==3


#------------------------------------------------------------------------------

