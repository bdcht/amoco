# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

# import expressions:
from amoco.cas.expressions import *

# reference documentation:
# PIC18(L)F2X/4XK22 Data Sheet, Microchip Technology Inc.

internals = {
    "version": "F46K22",  # PIC variant
    "xinst": 0,  # Extended Instruction flag
}

tos_ = reg("tos_", 24)
tosl = slc(tos_, 0, 8, "tosl")
tosh = slc(tos_, 8, 8, "tosh")
tosu = slc(tos_, 16, 5, "tosu")
tos = slc(tos_, 0, 21, "tosu")

stkptr = reg("stkptr", 8)
stkunf = slc(stkptr, 6, 1, "stkunf")
stkful = slc(stkptr, 7, 1, "stkful")

pc_ = reg("pc_", 24)
pcl = slc(pc_, 0, 8, "pcl")
pclath = slc(pc_, 8, 8, "pclath")
pclatu = slc(pc_, 16, 8, "pclatu")
pc = slc(pc_, 0, 21, "pc")

tblptr_ = reg("tblptr_", 24)
tblptrl = slc(tblptr_, 0, 8, "tblptrl")
tblptrh = slc(tblptr_, 8, 8, "tblptrh")
tblptru = slc(tblptr_, 16, 8, "tblptru")
tblptr = slc(tblptr_, 0, 21, "tblptr")

tablat = reg("tablat", 8)

prod = reg("prod", 16)
prodh = slc(prod, 8, 8, "prodh")
prodl = slc(prod, 0, 8, "prodl")

intcon = reg("intcon", 8)
intcon2 = reg("intcon2", 8)
intcon3 = reg("intcon3", 8)

indf0 = reg("indf0", 8)
postinc0 = reg("postinc0", 8)
postdec0 = reg("postdec0", 8)
preinc0 = reg("preinc0", 8)
plusw0 = reg("plusw0", 8)

fsr0 = reg("fsr0", 16)
fsr0h = slc(fsr0, 8, 8, "fsr0h")
fsr0l = slc(fsr0, 0, 8, "fsr0l")

wreg = reg("w", 8)
wregs = reg("ws", 8)

indf1 = reg("indf1", 8)
postinc1 = reg("postinc1", 8)
postdec1 = reg("postdec1", 8)
preinc1 = reg("preinc1", 8)
plusw1 = reg("plusw1", 8)

fsr1 = reg("fsr1", 16)
fsr1h = slc(fsr1, 8, 8, "fsr1h")
fsr1l = slc(fsr1, 0, 8, "fsr1l")

bsr = reg("bsr", 8)
bsrs = reg("bsrs", 8)

indf2 = reg("indf2", 8)
postinc2 = reg("postinc2", 8)
postdec2 = reg("postdec2", 8)
preinc2 = reg("preinc2", 8)
plusw2 = reg("plusw2", 8)

fsr2 = reg("fsr2", 16)
fsr2h = slc(fsr2, 8, 8, "fsr2h")
fsr2l = slc(fsr2, 0, 8, "fsr2l")

status = reg("status", 8)
statuss = reg("statuss", 8)
nf = slc(status, 4, 1, "nf")
ovf = slc(status, 3, 1, "ovf")
zf = slc(status, 2, 1, "zf")
dcf = slc(status, 1, 1, "dcf")
cf = slc(status, 0, 1, "cf")

tmr0 = reg("tmr0", 16)
tmr0h = slc(tmr0, 8, 8, "tmr0h")
tmr0l = slc(tmr0, 0, 8, "tmr0l")

t0con = reg("t0con", 8)

osccon = reg("osccon", 8)
osccon2 = reg("osccon2", 8)

wdtcon = reg("wdtcon", 8)
rcon = reg("rcon", 8)

tmr1 = reg("tmr1", 16)
tmr1h = slc(tmr1, 8, 8, "tmr1h")
tmr1l = slc(tmr1, 0, 8, "tmr1l")

t1con = reg("t1con", 8)
t1gcon = reg("t1gcon", 8)

ssp1con3 = reg("ssp1con3", 8)
ssp1msk = reg("ssp1msk", 8)
ssp1buf = reg("ssp1buf", 8)
ssp1add = reg("ssp1add", 8)
ssp1stat = reg("ssp1stat", 8)
ssp1con1 = reg("ssp1con1", 8)
ssp1con2 = reg("ssp1con2", 8)

adres = reg("adres", 16)
adresh = slc(adres, 8, 8, "adresh")
adresl = slc(adres, 0, 8, "adresl")

adcon0 = reg("adcon0", 8)
adcon1 = reg("adcon1", 8)
adcon2 = reg("adcon2", 8)

ccpr1 = reg("ccpr1", 16)
ccpr1h = slc(ccpr1, 8, 8, "ccpr1h")
ccpr1l = slc(ccpr1, 0, 8, "ccpr1l")

ccp1con = reg("ccp1con", 8)

tmr2 = reg("tmr2", 8)

pr2 = reg("pr2", 8)

t2con = reg("t2con", 8)

pstr1con = reg("pstr1con", 8)
baudcon1 = reg("baudcon1", 8)
pwm1con = reg("pwm1con", 8)
eccp1as = reg("eccp1as", 8)

t3gcon = reg("t3gcon", 8)

tmr3 = reg("tmr3", 16)
tmr3h = slc(tmr3, 8, 8, "tmr3h")
tmr3l = slc(tmr3, 0, 8, "tmr3l")

t3con = reg("t3con", 8)

spbrgh1 = reg("spbrgh1", 8)
spbrg1 = reg("spbrg1", 8)
rcreg1 = reg("rcreg1", 8)
txreg1 = reg("txreg1", 8)

txsta1 = reg("txsta1", 8)
rcsta1 = reg("rcsta1", 8)

eeadrh = reg("eeadrh", 8)
eeadr = reg("eeadr", 8)
eedata = reg("eedata", 8)

eecon2 = reg("eecon2", 8)
eecon1 = reg("eecon1", 8)

ipr3 = reg("ipr3", 8)
pir3 = reg("pir3", 8)
pie3 = reg("pie3", 8)
ipr2 = reg("ipr2", 8)
pir2 = reg("pir2", 8)
pie2 = reg("pie2", 8)
ipr1 = reg("ipr1", 8)
pir1 = reg("pir1", 8)
pie1 = reg("pie1", 8)

hlvdcon = reg("hlvdcon", 8)
osctune = reg("osctune", 8)
trise = reg("trise", 8)
trisd = reg("trisd", 8)
trisc = reg("trisc", 8)
trisb = reg("trisb", 8)
trisa = reg("trisa", 8)
late = reg("late", 8)
latd = reg("latd", 8)
latc = reg("latc", 8)
latb = reg("latb", 8)
lata = reg("lata", 8)
porte = reg("porte", 8)
portd = reg("portd", 8)
portc = reg("portc", 8)
portb = reg("portb", 8)
porta = reg("porta", 8)
ipr5 = reg("ipr5", 8)
pir5 = reg("pir5", 8)
pie5 = reg("pie5", 8)
ipr4 = reg("ipr4", 8)
pir4 = reg("pir4", 8)
pie4 = reg("pie4", 8)

cm1con0 = reg("cm1con0", 8)
cm2con0 = reg("cm2con0", 8)
cm2con1 = reg("cm2con1", 8)

spbrgh2 = reg("spbrgh2", 8)
spbrg2 = reg("spbrg2", 8)
rcreg2 = reg("rcreg2", 8)
txreg2 = reg("txreg2", 8)

txsta2 = reg("txsta2", 8)
rcsta2 = reg("rcsta2", 8)

baudcon2 = reg("baudcon2", 8)

ssp2buf = reg("ssp2buf", 8)
ssp2add = reg("ssp2add", 8)
ssp2stat = reg("ssp2stat", 8)
ssp2con1 = reg("ssp2con1", 8)
ssp2con2 = reg("ssp2con2", 8)
ssp2msk = reg("ssp2msk", 8)
ssp2con3 = reg("ssp2con3", 8)

ccpr2 = reg("ccpr2", 26)
ccpr2h = slc(ccpr2, 8, 8, "ccpr2h")
ccpr2l = slc(ccpr2, 0, 8, "ccpr2l")

ccp2con = reg("ccp2con", 8)
pwm2con = reg("pwm2con", 8)
eccp2as = reg("eccp2as", 8)
pstr2con = reg("pstr2con", 8)
iocb = reg("iocb", 8)
wpub = reg("wpub", 8)
slrcon = reg("slrcon", 8)

ccpr3 = reg("ccpr3", 36)
ccpr3h = slc(ccpr3, 8, 8, "ccpr3h")
ccpr3l = slc(ccpr3, 0, 8, "ccpr3l")

ccp3con = reg("ccp3con", 8)
pwm3con = reg("pwm3con", 8)
eccp3as = reg("eccp3as", 8)
pstr3con = reg("pstr3con", 8)

ccpr4 = reg("ccpr4", 46)
ccpr4h = slc(ccpr4, 8, 8, "ccpr4h")
ccpr4l = slc(ccpr4, 0, 8, "ccpr4l")
ccp4con = reg("ccp4con", 8)

ccpr5 = reg("ccpr5", 56)
ccpr5h = slc(ccpr5, 8, 8, "ccpr5h")
ccpr5l = slc(ccpr5, 0, 8, "ccpr5l")
ccp5con = reg("ccp5con", 8)

tmr4 = reg("tmr4", 8)
pr4 = reg("pr4", 8)
t4con = reg("t4con", 8)

tmr5 = reg("tmr5", 16)
tmr5h = slc(tmr5, 8, 8, "tmr5h")
tmr5l = slc(tmr5, 0, 8, "tmr5l")
t5con = reg("t5con", 8)
t5gcon = reg("t5gcon", 8)

tmr6 = reg("tmr6", 8)
pr6 = reg("pr6", 8)
t6con = reg("t6con", 8)

ccptmrs0 = reg("ccptmrs0", 8)
ccptmrs1 = reg("ccptmrs1", 8)

srcon0 = reg("srcon0", 8)
srcon1 = reg("srcon1", 8)

ctmucon = reg("ctmucon", 16)
ctmuconh = slc(ctmucon, 8, 8, "ctmuconh")
ctmuconl = slc(ctmucon, 0, 8, "ctmuconl")
ctmuicon = reg("ctmuicon", 8)
vrefcon0 = reg("vrefcon0", 8)
vrefcon1 = reg("vrefcon1", 8)
vrefcon2 = reg("vrefcon2", 8)
pmd0 = reg("pmd0", 8)
pmd1 = reg("pmd1", 8)
pmd2 = reg("pmd2", 8)
ansele = reg("ansele", 8)
anseld = reg("anseld", 8)
anselc = reg("anselc", 8)
anselb = reg("anselb", 8)
ansela = reg("ansela", 8)


def getreg(a, f):
    x = cst(f, 12)
    if a == 0:  # access Bank
        if f < 0x60:
            if internals["xinst"]:
                x = fsr2 + x
            return mem(x, 8)
        else:
            return SFRs[f]
    else:  # bsr-bank
        return mem(x, 8, seg=bsr)


SFRs = {
    0xFF: tosu,
    0xFE: tosh,
    0xFD: tosl,
    0xFC: stkptr,
    0xFB: pclatu,
    0xFA: pclath,
    0xF9: pcl,
    0xF8: tblptru,
    0xF7: tblptrh,
    0xF6: tblptrl,
    0xF5: tablat,
    0xF4: prodh,
    0xF3: prodl,
    0xF2: intcon,
    0xF1: intcon2,
    0xF0: intcon3,
    0xEF: indf0,
    0xEE: postinc0,
    0xED: postdec0,
    0xEC: preinc0,
    0xEB: plusw0,
    0xEA: fsr0h,
    0xE9: fsr0l,
    0xE8: wreg,
    0xE7: indf1,
    0xE6: postinc1,
    0xE5: postdec1,
    0xE4: preinc1,
    0xE3: plusw1,
    0xE2: fsr1h,
    0xE1: fsr1l,
    0xE0: bsr,
    0xDF: indf2,
    0xDE: postinc2,
    0xDD: postdec2,
    0xDC: preinc2,
    0xDB: plusw2,
    0xDA: fsr2h,
    0xD9: fsr2l,
    0xD8: status,
    0xD7: tmr0h,
    0xD6: tmr0l,
    0xD5: t0con,
    0xD4: None,
    0xD3: osccon,
    0xD2: osccon2,
    0xD1: wdtcon,
    0xD0: rcon,
    0xCF: tmr1h,
    0xCE: tmr1l,
    0xCD: t1con,
    0xCC: t1gcon,
    0xCB: ssp1con3,
    0xCA: ssp1msk,
    0xC9: ssp1buf,
    0xC8: ssp1add,
    0xC7: ssp1stat,
    0xC6: ssp1con1,
    0xC5: ssp1con2,
    0xC4: adresh,
    0xC3: adresl,
    0xC2: adcon0,
    0xC1: adcon1,
    0xC0: adcon2,
    0xBF: ccpr1h,
    0xBE: ccpr1l,
    0xBD: ccp1con,
    0xBC: tmr2,
    0xBB: pr2,
    0xBA: t2con,
    0xB9: pstr1con,
    0xB8: baudcon1,
    0xB7: pwm1con,
    0xB6: eccp1as,
    0xB5: None,
    0xB4: t3gcon,
    0xB3: tmr3h,
    0xB2: tmr3l,
    0xB1: t3con,
    0xB0: spbrgh1,
    0xAF: spbrg1,
    0xAE: rcreg1,
    0xAD: txreg1,
    0xAC: txsta1,
    0xAB: rcsta1,
    0xAA: eeadrh,
    0xA9: eeadr,
    0xA8: eedata,
    0xA7: eecon2,
    0xA6: eecon1,
    0xA5: ipr3,
    0xA4: pir3,
    0xA3: pie3,
    0xA2: ipr2,
    0xA1: ipr2,
    0xA0: pie2,
    0x9F: ipr1,
    0x9E: pir1,
    0x9D: pie1,
    0x9C: hlvdcon,
    0x9B: osctune,
    0x9A: None,
    0x99: None,
    0x98: None,
    0x97: None,
    0x96: trise,
    0x95: trisd,
    0x94: trisc,
    0x93: trisb,
    0x92: trisa,
    0x91: None,
    0x90: None,
    0x8F: None,
    0x8E: None,
    0x8D: late,
    0x8C: latd,
    0x8B: latc,
    0x8A: latb,
    0x89: lata,
    0x88: None,
    0x87: None,
    0x86: None,
    0x85: None,
    0x84: porte,
    0x83: portd,
    0x82: portc,
    0x81: portb,
    0x80: porta,
    0x7F: ipr5,
    0x7E: pir5,
    0x7D: pie5,
    0x7C: ipr4,
    0x7B: pir4,
    0x7A: pie4,
    0x79: cm1con0,
    0x78: cm2con0,
    0x77: cm2con1,
    0x76: spbrgh2,
    0x75: spbrg2,
    0x74: rcreg2,
    0x73: txreg2,
    0x72: txsta2,
    0x71: rcsta2,
    0x70: baudcon2,
    0x6F: ssp2buf,
    0x6E: ssp2add,
    0x6D: ssp2stat,
    0x6C: ssp2con1,
    0x6B: ssp2con2,
    0x6A: ssp2msk,
    0x69: ssp2con3,
    0x68: ccpr2h,
    0x67: ccpr2l,
    0x66: ccp2con,
    0x65: pwm2con,
    0x64: eccp2as,
    0x63: pstr2con,
    0x62: iocb,
    0x61: wpub,
    0x60: slrcon,
    0x5F: ccpr3h,
    0x5E: ccpr3l,
    0x5D: ccp3con,
    0x5C: pwm3con,
    0x5B: eccp3as,
    0x5A: pstr3con,
    0x59: ccpr4h,
    0x58: ccpr4l,
    0x57: ccp4con,
    0x56: ccpr5h,
    0x55: ccpr5l,
    0x54: ccp5con,
    0x53: tmr4,
    0x52: pr4,
    0x51: t4con,
    0x50: tmr5h,
    0x4F: tmr5l,
    0x4E: t5con,
    0x4D: t5gcon,
    0x4C: tmr6,
    0x4B: pr6,
    0x4A: t6con,
    0x49: ccptmrs0,
    0x48: ccptmrs1,
    0x47: srcon0,
    0x46: srcon1,
    0x45: ctmuconh,
    0x44: ctmuconl,
    0x43: ctmuicon,
    0x42: vrefcon0,
    0x41: vrefcon1,
    0x40: vrefcon2,
    0x3F: pmd0,
    0x3E: pmd1,
    0x3D: pmd2,
    0x3C: ansele,
    0x3B: anseld,
    0x3A: anselc,
    0x39: anselb,
    0x38: ansela,
}
