#!/bin/env python
# -*- coding: shift_jis -*-
#
# Written by Takeshi Sugawara
# 2010/July/02


# Converting a list of bytes into a string
def bytelistToStr(byteList):
    tmp = map(chr, byteList)
    return "".join(tmp)

def strTobyteList(str):
    return [ord(i) for i in list(str)]

def strToUint16List(str):
    tmp = strTobyteList(str)
    buf = []
    for i in range(len(tmp)/2):
        buf.append( tmp[2*i] * 256 + tmp[2*i+1] )
    return buf

    
def uint16_to_binstr(uint16_num):
    """
    Convert uint16 value to the corresponding binary string.
    Example:
    IN: uint16_to_binstr(0xfcff)
    OUT: '\xfc\xff'
    """
    return chr(uint16_num / 256) + chr(uint16_num % 256)

def binstr_to_uint16(binstr):
    """
    Convert binary string to the corresponding uint16 value.
    Example:
    IN: print '%x' % binstr_to_uint('\xfc\xff')
    OUT: fcff
    """    
    tmp = map(ord, list(binstr))
    return (tmp[0] << 8) + tmp[1]

def hex_str(uint16List):
    tmp = ["%.4x" % i for i in uint16List]
    return "_".join(tmp)
    

#Added by Sho Endo
#June 10, 2010

def intToUint16List(x):
    import copy
    a = copy.copy(x)
    list = []
    for i in range(32):
        list.append(a % 65536)
        a = a >> 16
    list.reverse()
    return list

def Uint16toint(uint_list):
    tmp = 0
    for i in range(32):
        tmp += uint_list[i] << ((31 - i) * 16)
    return tmp

#Added by Sho Endo
#July 13, 2010

def intToUint16List_nbytes(x, bytes):
    """
    Convert multi-byte integer to list of 16-bit integer
    list = intToUint16List_nbyte(x, bytes)
    """
    import copy
    a = copy.copy(x)
    list = []
    for i in range(bytes / 2):
        list.append(a % 65536)
        a = a >> 16
    list.reverse()
    return list

#Added by Sho Endo
#May, 2018
def hex_str2(uint16List):
    tmp = ["%.4x" % i for i in uint16List]
    tmp2 = [i[j:j+2] for i in tmp for j in range(0,4,2)]
    return "_".join(tmp2)
