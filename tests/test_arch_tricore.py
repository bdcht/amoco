import pytest

from amoco.config import conf
conf.UI.formatter = 'Null'
conf.Cas.unicode = False
conf.UI.unicode = False

from amoco.arch.tricore import cpu

def test_decoder_START():
  c = b'\x91\x00\x00\xf8'
  i = cpu.disassemble(c)
  assert i.mnemonic=='MOVH_A'
  assert i.operands[0] is cpu.A[15]
  assert i.operands[1]==0x8000
  c = b'\xd9\xff\x14\x02'
  i = cpu.disassemble(c)
  assert i.mnemonic=="LEA"
  assert i.mode=="Long-offset"
  assert i.operands[2]==0x2014
  c = b'\xdc\x0f'
  i = cpu.disassemble(c)
  assert i.mnemonic=="JI"
  assert i.operands[0]==cpu.A[15]
  c = b'\x00\x90'
  i = cpu.disassemble(c)
  assert i.mnemonic=="RET"
  c = b'\x00\x00'
  i = cpu.disassemble(c)
  assert i.mnemonic=="NOP"

def test_decoder_ldw():
    c = b'\x19\xf0\x10\x16'
    i = cpu.disassemble(c)
    assert str(i)=="ld.w        d0 , a15, 0x6050"

def test_movh():
    c = b'\x7b\xd0\x38\xf1'
    i = cpu.disassemble(c)
