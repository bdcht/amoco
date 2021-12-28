import pytest

from amoco.config import conf
conf.UI.formatter = 'Null'
conf.Cas.unicode = False
conf.UI.unicode = False

from amoco.arch.wasm import cpu

def test_decoder_000():
  c = b'\x00'
  i = cpu.disassemble(c)
  assert i.mnemonic=='unreachable'

def test_refnull():
  c = b'\xd0\x70'
  i = cpu.disassemble(c)
  op1 = i.operands[0]
  assert str(op1)=='#funcref'
  c = b'\xd0\x6f'
  i = cpu.disassemble(c)
  op1 = i.operands[0]
  assert str(op1)=='#externref'

def test_ref_func():
  c = b'\xd2\x81\x02'
  i = cpu.disassemble(c)
  assert i.mnemonic=="ref" and i.action=="func"
  op1 = i.operands[0]
  assert i.bytes==c
  assert op1==0x0101

def test_xdata_select():
  c = b'\x1c\x03\x41\xe5\x8e\x26\x81\x02'
  i = cpu.disassemble(c,address=0,code=c)
  assert i.mnemonic=="select"
  op1 = i.operands[0]
  assert i.bytes==c
  assert len(op1)==i.x==3
  assert op1[0] == 0x41
  assert op1[1] == 624485
  assert op1[2] == 0x0101
