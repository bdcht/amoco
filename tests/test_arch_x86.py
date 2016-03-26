import pytest

from amoco.arch.x86 import cpu_x86 as cpu
from amoco.arch.x86.env import *

# enforce Intel syntax and NullFormatter output:
cpu.configure(format='Intel')
from amoco.ui import render
render.configure(formatter='Null')

def test_decoder_000():
  c = '\x90'
  i = cpu.disassemble(c)
  assert i.mnemonic=='NOP'

# mov eax,[eax+0x10]
def test_decoder_001():
  c = '\x8b\x40\x10'
  i = cpu.disassemble(c)
  op1 = i.operands[0]
  assert str(op1)=='eax'
  op2 = i.operands[1]
  assert str(op2)=='M32(eax+16)'
  p1 = i.operands[0]

# callf [ebx+eax*8+0x01eb6788]
def test_decoder_002():
  c = '\xff\x9c\xc3\x88\x67\xeb\x01'
  i = cpu.disassemble(c)
  op1 = i.operands[0]
  assert str(op1)=='M48(((eax*0x8)+ebx)+32204680)'

# jmp 0xc (relative to current eip!)
def test_decoder_003():
  c = '\xeb\x0c'
  i = cpu.disassemble(c)
  op1 = i.operands[0]
  assert op1.value==0xc and op1.size==32

# mov edx,[eax*4+0x0805bd00]
def test_decoder_004():
  c = '\x8b\x14\x85\x00\xbd\x05\x08'
  i = cpu.disassemble(c)
  op2 = i.operands[1]
  assert str(op2)=='M32((eax*0x4)+134593792)'

# les eax,[ebp+edi+0x70a310d3]
def test_decoder_005():
  c = '\xc4\x84\x3d\xd3\x10\xa3\x70'
  i = cpu.disassemble(c)
  op2 = i.operands[1]
  assert str(op2)=='M48es((ebp+edi)+1889734867)'

# and bl,[0x39a3ac3d]
def test_decoder_006():
  c = '\x22\x1d\x2d\xac\xa3\x39'
  i = cpu.disassemble(c)
  op1 = i.operands[0]
  assert op1.x.ref=='ebx'
  assert str(op1)=='bl'
  op2 = i.operands[1]
  assert str(op2)=='M8(0x39a3ac2d)'

# imul ebp,ecx,0xc23d
def test_decoder_007():
  c = '\x69\xe9\x3d\xc2\x00\x00'
  i = cpu.disassemble(c)
  op1,op2,op3 = i.operands
  assert str(op1)=='ebp' and str(op2)=='ecx' and str(op3)=='0xc23d'

# add dh,[ebp+0x240489ca]
def test_decoder_008():
  c = '\x02\xb5\xca\x89\x04\x24'
  i = cpu.disassemble(c)
  op1 = i.operands[0]
  assert str(op1)=='dh'
  op2 = i.operands[1]
  assert str(op2)=='M8(ebp+604277194)'

# add [eax],al
def test_decoder_009():
  c = '\x00\x00'
  i = cpu.disassemble(c)
  op1 = i.operands[0]
  assert str(op1)=='M8(eax)'
  op2 = i.operands[1]
  assert str(op2)=='al'

# add bh,al
def test_decoder_010():
  c = '\x00\xc7'
  i = cpu.disassemble(c)
  op1 = i.operands[0];  op2 = i.operands[1]
  assert str(op1)=='bh' and str(op2)=='al'

# movzx edx,[eax+0x0805b13c]
def test_decoder_011():
  c = '\x0f\xb6\x90\x3c\xb1\x05\x08'
  i = cpu.disassemble(c)
  op1 = i.operands[0];  op2 = i.operands[1]
  assert str(op1)=='edx' and str(op2)=='M8(eax+134590780)'

# ror cs:[edi],0x8f
def test_decoder_012():
  c = '\x2e\xc0\x0f\x8f'
  i = cpu.disassemble(c)
  op1 = i.operands[0]
  assert str(op1)=='M8cs(edi)'
  assert op1.a.seg.ref=='cs'
  assert op1.size==8
  op2 = i.operands[1]
  assert op2.size==8

# mov cs,[edi-0x6d1b46d2]
def test_decoder_013():
  c = '\x8e\x8f\x2e\xb9\xe4\x92'
  i = cpu.disassemble(c)
  op1 = i.operands[0];  op2 = i.operands[1]
  assert str(op1)=='cs' and op2.size==16

# fsub st,st(5)
def test_decoder_014():
  c = '\xd8\xe5'
  i = cpu.disassemble(c)
  #op1 = i.operands[0];  op2 = i.operands[1]
  #assert str(op1)=='st0' and str(op2)=='st5' and op1.size==80 and op2.size==80

# dec [edx+0x6153e80e]
def test_decoder_015():
  c = '\xfe\x8a\x0e\xe8\x53\x61'
  i = cpu.disassemble(c)
  op1 = i.operands[0]
  assert str(op1)=='M8(edx+1632888846)'

# fistp word [ebx+edi*8]
def test_decoder_016():
  c = '\xdf\x1c\xfb'
  i = cpu.disassemble(c)
  #op1 = i.operands[0]
  #assert str(op1)=='M16((ebx + (edi * 0x8)))'

# imul ecx,fs:[edx-0x2893a953],0x82da771e
def test_decoder_017():
  c = '\x64\x69\x8a\xad\x56\x6c\xd7\x1e\x77\xda\x82'
  i = cpu.disassemble(c)
  op1,op2,op3 = i.operands
  assert str(op2)=='M32fs(edx-680765779)' and str(op3)=='0x82da771e'

# fsubrl [ecx]
def test_decoder_018():
  c = '\xdc\x29'
  i = cpu.disassemble(c)
  op1 = i.operands[0]
  assert str(op1)=='M64(ecx)'

# cmpxchg8b qword ptr [ecx]
def test_decoder_019():
  c = '\x0f\xc7\x09'
  i = cpu.disassemble(c)
  assert str(i.operands[0])=='M64(ecx)'

# movzx eax, byte ptr [eax+0x806fb088]
def test_decoder_020():
  c = '\x0f\xb6\x80\x88\xb0\x6f\x80'
  i = cpu.disassemble(c)
  assert str(i.operands[1])=='M8(eax-2140163960)'
  assert i.toks()[-1][1] == 'byte ptr [eax+0x806fb088]'

# mov eax, [esp-300]
def test_decoder_021():
  c = '\x8b\x84\x24\xd4\xfe\xff\xff'
  i = cpu.disassemble(c)
  assert str(i.operands[1])=='M32(esp-300)'
  assert i.toks()[-1][1] == '[esp-300]'

# cvtss2sd [ebp-16], xmm0
def test_decoder_022():
  c = '\xf3\x0f\x5a\x45\xf0'
  i = cpu.disassemble(c)
  assert i.mnemonic == 'CVTSS2SD'
  op1 = i.operands[0]
  assert op1._is_reg and op1.size==128
  assert str(op1)=='xmm0'

# cvttss2si eax, [ebp-16]
def test_decoder_023():
  c = '\xf3\x0f\x2c\x45\xf0'
  i = cpu.disassemble(c)
  assert i.mnemonic == 'CVTTSS2SI'
  assert i.toks()[1][1] == 'eax'

# cvtss2si eax, [ebp-16]
def test_decoder_024():
  c = '\xf3\x0f\x2d\x45\xf0'
  i = cpu.disassemble(c)
  assert i.mnemonic == 'CVTSS2SI'
  assert i.toks()[1][1] == 'eax'

# push -1
def test_decoder_025():
  c = '\x6a\xff'
  i = cpu.disassemble(c)
  assert i.mnemonic == 'PUSH'
  op1 = i.operands[0]
  assert op1.sf == True
  assert op1.value == -1
  assert op1.size == 8

# movq qword ptr [ebp-16], xmm1
def test_decoder_026():
  c = '\x66\x0f\xd6\x4d\xf0'
  i = cpu.disassemble(c)
  assert i.mnemonic == 'MOVQ'
  assert i.toks()[1][1] == 'qword ptr [ebp-16]'

# movq xmm2, qword ptr [ebp-16]
def test_decoder_027():
  c = '\xf3\x0f\x7e\x55\xf0'
  i = cpu.disassemble(c)
  assert i.mnemonic == 'MOVQ'
  assert i.toks()[1][1] == 'xmm2'
  assert i.toks()[3][1] == 'qword ptr [ebp-16]'

# movq xmm0, xmm1
def test_decoder_028():
  c = '\xf3\x0f\x7e\xc1'
  i = cpu.disassemble(c)
  assert i.mnemonic == 'MOVQ'
  op1,op2 = i.operands
  assert op1.size==op2.size==128

#------------------------------------------------------------------------------


def test_asm_000(map):
  c = '\x90'
  i = cpu.disassemble(c,address=0)
  # fake eip cst:
  map[eip] = cst(0,32)
  i(map)
  assert str(map(eip))=='0x1'

# wait
def test_asm_001(map):
  c = '\x9b'
  i = cpu.disassemble(c,address=0)
  i(map)
  assert i.mnemonic=='WAIT'
  assert str(map(eip))=='0x2'

# leave
def test_asm_002(map):
  c = '\xc9'
  i = cpu.disassemble(c,address=0)
  i(map)
  assert str(map)=='''\
eip <- { | [0:32]->0x3 | }
esp <- { | [0:32]->(ebp+0x4) | }
ebp <- { | [0:32]->M32(ebp) | }'''

# ret
def test_asm_003(map):
  c = '\xc3'
  i = cpu.disassemble(c,address=0)
  i(map)
  assert str(map(eip))=='M32(ebp+4)'
  assert str(map(esp))=='(ebp+0x8)'
  assert str(map(ebp))=='M32(ebp)'

# hlt
def test_asm_004(map):
  c = '\xf4'
  i = cpu.disassemble(c,address=0)
  i(map)
  assert i.mnemonic=='HLT'
  assert map(eip)==top(32)

# int3
def test_asm_005(map):
  c = '\xcc'
  i = cpu.disassemble(c,address=0)
  assert i.mnemonic=='INT3'
  i(map)

# push eax
def test_asm_006(map):
  c = '\x50'
  i = cpu.disassemble(c,address=0)
  map.clear()
  map[eip] = cst(0)
  map[esp] = cst(0)
  i(map)
  assert map(mem(esp))==eax
  assert map(esp)==cst(-4)

# pop eax
def test_asm_007(map):
  c = '\x58'
  i = cpu.disassemble(c,address=0)
  i(map)
  assert map(eax)==eax
  assert map(esp)==0

# call edx
def test_asm_008(map):
  c = '\xff\xd2'
  i = cpu.disassemble(c,address=0)
  i(map)
  assert map(eip)==edx
  assert map(mem(esp))==0x4

# call eip+0x00000000 (eip+0)
def test_asm_009(map):
  c = '\xe8\x00\x00\x00\x00'
  i = cpu.disassemble(c,address=0)
  i.address = 0x08040000
  map.clear()
  i(map)
  assert map(mem(esp,32))==map(eip)

# call eip+0xffffff9b (eip-101)
def test_asm_010(map):
  c = '\xe8\x9b\xff\xff\xff'
  i = cpu.disassemble(c,address=0)
  map.clear()
  i.address = 0x08040005
  map[eip] = cst(i.address,32)
  i(map)
  assert str(i)=='call        *0x803ffa5'
  assert map(mem(esp))==i.address+5
  assert map(eip)==(i.address+5-101)

# jmp eip+12
def test_asm_011(map):
  c = '\xeb\x0c'
  i = cpu.disassemble(c,address=0)
  i.address = map(eip).v
  i(map)
  assert map(mem(esp))==i.address+101
  assert map(eip)==i.address+i.length+12

# jmp eip-32
def test_asm_012(map):
  c = '\xe9\xe0\xff\xff\xff'
  i = cpu.disassemble(c,address=0)
  i.address = map(eip).v
  i(map)
  assert map(eip)==i.address+i.length-32

# jmp [0x0805b0e8]
def test_asm_013(map):
  c = '\xff\x25\xe8\xb0\x05\x08'
  i = cpu.disassemble(c,address=0)
  i(map)
  assert map(eip)==mem(cst(0x805b0e8))

# retn 0xc
def test_asm_014(map):
  c = '\xc2\x0c\x00'
  i = cpu.disassemble(c,address=0)
  i(map)
  assert map(eip)==0x804000a
  assert str(map(esp))=='(esp+0xc)'

# int 0x80
def test_asm_015(map):
  c = '\xcd\x80'
  i = cpu.disassemble(c,address=0)
  i(map)

# inc eax
def test_asm_016(map):
  c = '\x40'
  i = cpu.disassemble(c,address=0)
  i(map)
  assert map(eax)==(eax+1)

# dec esi
def test_asm_017(map):
  c = '\x4e'
  i = cpu.disassemble(c,address=0)
  i(map)
  assert map(esi)==(esi-1)


# mov eax,[eax+0x10]
def test_asm_018(map):
  c = '\x8b\x40\x10'
  i = cpu.disassemble(c,address=0)
  map.clear()
  i(map)
  assert str(map(eax))=='M32(eax+16)'

# movsx edx,al
def test_asm_019(map):
  c = '\x0f\xbe\xd0'
  i = cpu.disassemble(c,address=0)
  i(map)
  assert map(edx)[0:8]==map(al)
  assert str(map(edx)[8:32])=='(M8(eax+16)[7:8] ? -0x1 : 0x0)'

# movzx edx,[eax+0x0805b13c]
def test_asm_020(map):
  c = '\x0f\xb6\x90\x3c\xb1\x05\x08'
  i = cpu.disassemble(c,address=0)
  i(map)
  assert map(edx)[8:32]==0

# add [eax],al
def test_asm_021(map):
  c = '\x00\x00'
  i = cpu.disassemble(c,address=0)
  i(map)
  assert str(map(mem(eax,8)))=='(M8(M32(eax+16))+M8(eax+16))'

# sub [edx+esi-0x43aa74b0], cl
def test_asm_022(map):
  c = '\x28\x8c\x32\x50\x8b\x55\xbc'
  i = cpu.disassemble(c,address=0)
  i(map)
  loc = ptr(map(edx)+esi,disp=-0x43aa74b0)
  assert str(map[mem(loc,8)])=='((-cl)+M8(({ | [0:8]->M8(M32(eax+16)+134590780) | [8:32]->0x0 | }+esi)-1135244464))'

# and ebp,[edi-0x18]
def test_asm_023(map):
  c = '\x23\x6f\xe8'
  i = cpu.disassemble(c,address=0)
  map.clear()
  i(map)
  assert map(ebp)==ebp&mem(edi,32,disp=-0x18)

# and esp,0xfffffff0
def test_asm_024(map):
  c = '\x83\xe4\xf0'
  i = cpu.disassemble(c,address=0)
  map[esp] = cst(0xc0000004)
  i(map)
  assert map[esp]==0xc0000000

# or al,0
def test_asm_025(map):
  c = '\x0c\x00'
  i = cpu.disassemble(c,address=0)
  i(map)
  assert map(al)==al|0
  assert map(ah)==ah

# xor edx,[ebp-0x1c]
def test_asm_026(map):
  c = '\x33\x55\xe4'
  i = cpu.disassemble(c,address=0)
  i(map)
  assert map(edx)==edx^map(mem(ebp,32,disp=-0x1c))

# cmp edx,0
def test_asm_027(map):
  c = '\x83\xfa\x00'
  i = cpu.disassemble(c,address=0)
  map.clear()
  i(map)
  assert str(map(zf))=='(edx==0x0)'

# sal al,2
def test_asm_028(map):
  c = '\xc0\xf0\x02'
  i = cpu.disassemble(c,address=0)
  i(map)

# sal esi,0
def test_asm_029(map):
  c = '\xc1\xf6\x20'
  i = cpu.disassemble(c,address=0)
  i(map)

# mov byte ptr [edx], al
def test_asm_030(map):
  c = '\x88\x02'
  i = cpu.disassemble(c,address=0)
  i(map)

# lea eax, [edx]
def test_asm_031(map):
  c = '\x8d\x02\xc3'
  i = cpu.disassemble(c,address=0)
  i(map)
  assert str(map(eax))=='(edx)'

# pop esp
def test_asm_032(map):
  c = '\x5c'
  i = cpu.disassemble(c,address=0)
  map.clear()
  map[esp] = cst(0x1000,32)
  map[mem(esp,32)] = cst(0x67452301,32)
  i(map)
  assert map(esp)==cst(0x67452301,32)

# push esp
def test_asm_033(map):
  c = '\x54'
  i = cpu.disassemble(c,address=0)
  i(map)
  assert map(esp)==0x67452301-4
  assert map(mem(esp,32))==cst(0x67452301,32)

