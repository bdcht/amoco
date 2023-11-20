import pytest

from amoco.config import conf
conf.UI.formatter = 'Null'
conf.Cas.unicode = False
conf.UI.unicode = False

from amoco.arch.ppc32 import cpu

def test_decoder_START():
  c = b'\x91\x00\x00\xf8'
  i = cpu.disassemble(c)
  assert i.mnemonic=='stw'
  assert i.operands[0] is cpu.R[8]
  assert i.operands[1]._is_ptr
  assert str(i.operands[1]) == '(0xf8)'
  c = b'\xd9\xff\x14\x02'
  i = cpu.disassemble(c)
  assert i.mnemonic=="stfd"
  assert i.operands[0] is cpu.FPR[15]
  assert i.operands[1].base == cpu.R[31]
  assert i.operands[1].disp == 20488
  c = b'\x7b\xd0\x38\xf1'
  i = cpu.disassemble(c)
  assert i.mnemonic=="rldcl"
  assert i.operands[0] is cpu.R[16]
  assert i.operands[1] is cpu.R[30]
  assert i.operands[2] is cpu.R[7]
  assert i.operands[3] == 0x23
