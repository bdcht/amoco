import pytest

from amoco.arch.x64 import cpu_x64 as cpu
from amoco.arch.x64.env import *

# enforce Intel syntax and NullFormatter output:
cpu.configure(format='Intel')
from amoco.ui import render
render.configure(formatter='Null')

def test_decoder_000():
  c = '\x90'
  i = cpu.disassemble(c)
  assert i.mnemonic=='NOP'

def test_decoder_001():
  c = 'f\x0fo\x04%\xbc\x00`\x00'
  i = cpu.disassemble(c)
  assert i.mnemonic=='MOVDQA'
  assert i.operands[0].ref == 'xmm0'
  assert i.operands[1].a.base == 0x6000bc

# movsx rax, al
def test_decoder_002():
  c = '\x48\x0f\xbe\xc0'
  i = cpu.disassemble(c)
  assert i.mnemonic=='MOVSX'
  assert i.operands[0].ref == 'rax'
  assert i.operands[1].ref == 'al'

def test_decoder_003():
  c = '\x48\x8b\x04\xc5\0\0\0\0'
  i = cpu.disassemble(c)
  assert i.operands[1].a.base==(rax*8)

def test_decoder_004():
  c = '\x64\x48\x8b\x04\x25\x28\0\0\0'
  i = cpu.disassemble(c)
  assert i.operands[1].a.base==40

def test_decoder_005():
  c = '\x8b\x2c\x25\x00\x00\x00\x00'
  i = cpu.disassemble(c)
  assert i.operands[1].a.base==0

def test_decoder_006():
  c = '\x80\xcc\x0c'
  i = cpu.disassemble(c)
  assert i.operands[0].ref == 'ah'

def test_decoder_007():
  c = '\x40\x80\xcc\x0c'
  i = cpu.disassemble(c)
  assert i.operands[0].ref == 'spl'

def test_decoder_008():
  c = '48B88877665544332211'.decode('hex')
  i = cpu.disassemble(c)
  assert i.operands[1]==0x1122334455667788

def test_decoder_009():
  c = '\xf3\x0f\x2a\xc0'
  i = cpu.disassemble(c)
  assert i.mnemonic=='CVTSI2SS'
  assert i.operands[1].ref == 'eax'

def test_decoder_010():
  c = '488d0c59'.decode('hex')
  i = cpu.disassemble(c)
  assert i.operands[1].a.base==((rbx*0x2)+rcx)

def test_decoder_011():
  c = '41ffd7'.decode('hex')
  i = cpu.disassemble(c)
  assert i.mnemonic=='CALL'
  assert i.operands[0].ref == 'r15'

def test_decoder_012():
  c = '488b0d19000000'.decode('hex')
  i = cpu.disassemble(c)
  assert i.mnemonic=='MOV'
  assert i.operands[0].ref == 'rcx'
  assert i.operands[1].a.base == rip
  assert i.operands[1].a.disp == 0x19

# mov ebx, dword ptr [rsp+0xc]
def test_decoder_013():
  c = '8b5c240c'.decode('hex')
  i = cpu.disassemble(c)
  assert i.mnemonic=='MOV'
  assert i.operands[0].ref == 'ebx'
  assert i.operands[1].size == 32
  assert i.operands[1].a.base == rsp
  assert i.operands[1].a.disp == 0xc

def test_decoder_014():
  c = '\x48\xa5'
  i = cpu.disassemble(c)
  assert i.mnemonic=='MOVSQ'

def test_decoder_015():
  c = '\x48\x63\xd2'
  i = cpu.disassemble(c)
  assert i.mnemonic=='MOVSXD'

def test_decoder_016():
  c = '\x86\xf1'
  i = cpu.disassemble(c)
  assert i.mnemonic=='XCHG'
  assert i.operands[0].ref=='dh'
  assert i.operands[1].ref=='cl'

def test_decoder_017():
  c = '\x2a\xf1'
  i = cpu.disassemble(c)
  assert i.mnemonic=='SUB'
  assert i.operands[0].ref=='dh'
  assert i.operands[1].ref=='cl'

def test_decoder_018():
  c = '\xff\x35\x00\x00\x00\x00'
  i = cpu.disassemble(c)
  assert i.mnemonic=='PUSH'
  assert i.operands[0].a.base == rip
  assert i.operands[0].a.disp == 0

def test_decoder_019():
  c = '\xff\x35\x00\x00\x00\x00'
  i = cpu.disassemble(c)
  assert i.mnemonic=='PUSH'
  assert i.operands[0].size == 64
  assert i.operands[0].a.base == rip
  assert i.operands[0].a.disp == 0

def test_decoder_020():
  c = '\x68\x01\x02\x03\xff'
  i = cpu.disassemble(c)
  assert i.mnemonic=='PUSH'
  assert i.operands[0].size == 32
  assert i.operands[0] == 0xff030201
  c = '\x48\x68\x01\x02\x03\xff'
  i = cpu.disassemble(c)
  assert i.mnemonic=='PUSH'
  assert i.operands[0].size == 64
  assert i.operands[0] == 0xffffffffff030201

def test_decoder_021():
  c = '\x66\x68\x03\xff'
  i = cpu.disassemble(c)
  assert i.mnemonic=='PUSH'
  assert i.operands[0].size == 16
  assert i.operands[0] == 0xff03

def test_decoder_022():
  c = '\x66\x48\x51'
  i = cpu.disassemble(c)
  assert i.mnemonic=='PUSH'
  assert i.operands[0].ref == 'rcx'

def test_decoder_023():
  c = '\x45\x51'
  i = cpu.disassemble(c)
  assert i.mnemonic=='PUSH'
  assert i.operands[0].ref == 'r9'

def test_decoder_024():
  c = '\x66\x51'
  i = cpu.disassemble(c)
  assert i.mnemonic=='PUSH'
  assert i.operands[0].ref == 'cx'

def test_decoder_025():
  c = '4c69f1020000f0'.decode('hex')
  i = cpu.disassemble(c)
  assert i.mnemonic=='IMUL'
  assert i.operands[0].ref == 'r14'
  assert i.operands[1].ref == 'rcx'
  assert i.operands[2].size == 64
  assert i.operands[2] == cpu.cst(0xf0000002,32).signextend(64)

def test_decoder_026():
  c = '\x66\x41\xc7\x84\x55\x11\x11\x11\x11\x22\x22'
  i = cpu.disassemble(c)
  assert i.mnemonic=='MOV'
  assert i.operands[0]._is_mem
  assert i.operands[0].size == 16
  assert i.operands[0].a.base == cpu.r13 + (cpu.rdx*2)
  assert i.operands[0].a.disp == 0x11111111
  assert i.operands[1] == cpu.cst(0x2222,16)
