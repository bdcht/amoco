# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2012 Axel Tillequin (bdcht3@gmail.com) 
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

#registers :
#-----------

# main reg set:
af    = reg('af',16)     # accumulator / flags
bc    = reg('bc',16)     # 
de    = reg('de',16)     # 
hl    = reg('hl',16)     # 

a = slc(af,8,8,'a')
f = slc(af,0,8,'f')
b = slc(bc,8,8,'b')
c = slc(bc,0,8,'c')
d = slc(de,8,8,'d')
e = slc(de,0,8,'e')
h = slc(hl,8,8,'h')
l = slc(hl,0,8,'l')

# alternate reg set:
af_   = reg("af'",16)    # (alternate bank)
bc_   = reg("bc'",16)    # 
de_   = reg("de'",16)    # 
hl_   = reg("hl'",16)    # 

a_ = slc(af_,8,8,"a'")
f_ = slc(af_,0,8,"f'")
b_ = slc(bc_,8,8,"b'")
c_ = slc(bc_,0,8,"c'")
d_ = slc(de_,8,8,"d'")
e_ = slc(de_,0,8,"e'")
h_ = slc(hl_,8,8,"h'")
l_ = slc(hl_,0,8,"l'")

# other registers:
sp    = reg('sp',16)     # stack pointer
pc    = reg('pc',16)     # program pointer
ix    = reg('ix',16)     # index register x  (indexed addressing mode)
iy    = reg('iy',16)     # index register y  (indexed addressing mode)
ir    = reg('ir',16)     # interrupt vector / memory refresher
i = slc(ir,8,8,'i')
r = slc(ir,0,8,'r')
# extra registers slices from undocumented instructions
ixh   = slc(ix,8,8,'ixh')
ixl   = slc(ix,0,8,'ixl')
iyh   = slc(iy,8,8,'iyh')
iyl   = slc(iy,0,8,'iyl')

#flags:
cf = slc(af,0,1,'cf')  # carry/borrow flag
nf = slc(af,1,1,'nf')  # add/sub flag
pf = slc(af,2,1,'pf')  # parity flag        
xf = slc(af,3,1,'xf')  # copy of bit3 of result
hf = slc(af,4,1,'hf')  # half carry (for BCD)
yf = slc(af,5,1,'yf')  # copy of bit5 of result
zf = slc(af,6,1,'zf')  # zero flag
sf = slc(af,7,1,'sf')  # copy of MSB

# interrupts flipflops
iff1 = reg('iff1',1)
iff2 = reg('iff2',1)

reg8  = [ b, c, d, e, h, l, mem(hl,8), a ]
reg8_ = [ b_, c_, d_, e_, h_, l_, mem(hl_,8), a_ ]

reg16 = [ bc, de, hl, af ]
reg16_= [ bc_, de_, hl_, af_ ]

CONDITION = {
    0b000: ('nz', (zf==0)),
    0b001: ('z' , (zf==1)),
    0b010: ('nc', (cf==0)),
    0b011: ('c' , (cf==1)),
    0b100: ('po', (pf==1)),
    0b101: ('pe', (pf==0)),
    0b110: ('p' , (sf==0)),
    0b111: ('m' , (sf==1)),
}
