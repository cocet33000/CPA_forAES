#!/bin/env python
# -*- coding: shift_jis -*-
#
# Written by Takeshi Sugawara

def uint32listToUint16list(data):
    buf = []
    for i in data:
        buf.append( int(i/(2**16) ))
        buf.append( int(i%(2**16) ))
    return buf

def uint16listToUint32list(data):
    if (len(data) % 2) != 0:
        raise Exception("hogehoge")
    buf = []
    for i in range(len(data)/2):
        buf.append( int( ((data[2*i] << 16) & 0xffff0000) |
                         (data[2*i+1]       & 0x0000ffff) ) )
    return buf

def uint16listToUint(aList):
    tmp = aList[:]
    tmp.reverse()
    buf = 0
    for i in range(len(tmp)):
        buf += tmp[i] * (2**(16*i))
    return buf

def uintToUint16list(uint):
    result = [None for i in range(8)]
    for i in range(8):
        result[i] = uint % (2**16)
        uint /= (2**16)
    result.reverse()
    return result

def hammingWeight(data):
    counter = 0
    while data != 0:
        counter += data % 2
        data /= 2
    return counter

def uint16Print(array):
    buf = ["%.4x" % i for i in array]
    print ", ".join(buf)

def uint32Print(array):
    buf = ["%.8x" % i for i in array]
    print ", ".join(buf)
