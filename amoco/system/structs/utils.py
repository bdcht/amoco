# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2014 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

def read_leb128(data, sign=1, offset=0):
    result = 0
    shift = 0
    count = 0
    for b in data[offset:]:
        if isinstance(b, bytes):
            b = ord(b)
        count += 1
        result |= (b & 0x7F) << shift
        shift += 7
        if b & 0x80 == 0:
            break
    if sign < 0 and (b & 0x40):
        result |= ~0 << shift
    return result, count


def read_uleb128(data):
    return read_leb128(data)


def read_sleb128(data):
    return read_leb128(data, -1)

def write_uleb128(val):
    if val==0:
        return b'\0'
    res = []
    while val!=0:
        x = val&0x7f
        val = val>>7
        if val!=0:
            x = 0x80|x
        res.append(x)
    return bytes(res)

def write_sleb128(val):
    more=True
    neg=(val<0)
    res = []
    while more:
         x = val&0x7f
         val = val>>7
         if ((val==0) and (x&0x40==0)) or ((val==-1) and (x&0x40)):
             more=False
         else:
             x = 0x80|x
         res.append(x)
    return bytes(res)
