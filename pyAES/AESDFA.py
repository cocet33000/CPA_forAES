#!/bin/env python
# -*- coding: shift_jis -*-
#
# Written by Takeshi Sugawara
# 2010/July/05

from myAES import mixColumn32
from myAES import invSbox

# For compatibility
try: set
except NameError:
    import sets
    set = sets.Set

def _byteArray2word(byteArray):    # 4 つの uint8 を，uint32 に変換する
    return byteArray[0] | byteArray[1] | byteArray[2] | byteArray[3]


#_indexTable = ( ( 1, 14, 11,  8),
#                ( 5,  2, 15, 12),
#                ( 9,  6,  3, 16),
#                (13, 10,  7,  4) );
_indexTable = ( ( 0, 13, 10,  7),
                ( 4,  1, 14, 11),
                ( 8,  5,  2, 15),
                (12,  9,  6,  3) );

def _printUint16List(uint16List):
    buf = []
    for uint16 in uint16List:
        buf += ["%.4x" % uint16]
    print " ".join(buf)

def _printByteList(byteList):
    buf = []
    for byte in byteList:
        buf += ["%.2x" % byte]
    print " ".join(buf)

def _invSboxUint16(uint16):
    if uint16 >= 2**16 or uint16 < 0:
        raise Exception( "%x"%uint16 )
    #print "%x" % uint16
    upper = uint16 / 256
    lower = uint16 % 256
    return (invSbox[upper] << 8) + invSbox[lower]
    
def _word2byte(word):     # uint32 を 4 つの uint8 に変換する
    a0 = ( word >> 24 ) % 256
    a1 = ( word >> 16 ) % 256
    a2 = ( word >> 8  ) % 256
    a3 = ( word       ) % 256
    return [a0, a1, a2, a3]

#def uint32List2ByteList(uint32List):
#    return map(_word2byte, uint32List)

def uint16List2ByteList(uint16List):
    buf = []
    for uint16 in uint16List:
        buf += [uint16 / 256]
        buf += [uint16 % 256]
    return buf


class AESDFA(object):
    def __init__(self):
        self.table32 = set()
        self.table16Lower = set()
        self.table16Upper = set()
        self.candidate16Upper = [set(range(2**16)) for i in range(4)]
        self.candidate16Lower = [set(range(2**16)) for i in range(4)]
        self.genTable()

    def genTable(self):
        byteArray = [None for i in range(4)]
        for byteIndex in range(4):
            for byteValue in range(256):
                for i in range(4):
                    byteArray[i] = (byteIndex==i) and byteValue or 0
                #MCout = mixColumnWord( _byteArray2word(byteArray) )
                MCout = mixColumn32( _byteArray2word(byteArray) )
                self.table32.add(MCout)
                self.table16Upper.add(MCout / (2**16))
                self.table16Lower.add(MCout % (2**16))

    def search16(self, (correct, faulty), pattern):
        (indU0, indU1, indL0, indL1) = _indexTable[pattern]
        correctList = uint16List2ByteList(correct)
        faultyList  = uint16List2ByteList(faulty)

        correctUpper = (correctList[indU0] << 8) + correctList[indU1]
        correctLower = (correctList[indL0] << 8) + correctList[indL1]
        faultyUpper  = (faultyList[indU0]  << 8) + faultyList[indU1]
        faultyLower  = (faultyList[indL0]  << 8) + faultyList[indL1]

        # Upper search
        for cand in list(self.candidate16Upper[pattern]):
            diff = _invSboxUint16(correctUpper ^ cand) ^ \
                   _invSboxUint16( faultyUpper ^ cand) 
            if diff not in self.table16Upper:
                self.candidate16Upper[pattern].remove(cand)
        # Lower search
        for cand in list(self.candidate16Lower[pattern]):
            diff = _invSboxUint16(correctLower ^ cand) ^ \
                   _invSboxUint16( faultyLower ^ cand)
            if diff not in self.table16Lower:
                self.candidate16Lower[pattern].remove(cand)

    def __str__(self):
        upper = map(len, self.candidate16Upper)
        lower = map(len, self.candidate16Upper)
        return  " ".join(["upper", str(upper), "lower", str(lower)])

    def getResult(self):
        shiftRowsTable = (0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 1, 6, 11)
        tmp = [0 for i in range(16)]
        result = [0 for i in range(16)]
        for i in range(4):
            if len(self.candidate16Upper[i]) == 1:
                res = list(self.candidate16Upper[i])[0]
                tmp[4*i  ] = "%.2x" % (res / 256)
                tmp[4*i+1] = "%.2x" % (res % 256)
            else:
                tmp[4*i  ] = "XX"
                tmp[4*i+1] = "XX"
            if len(self.candidate16Lower[i]) == 1:
                res = list(self.candidate16Lower[i])[0]
                tmp[4*i+2] = "%.2x" % (res / 256)
                tmp[4*i+3] = "%.2x" % (res % 256)
            else:
                tmp[4*i+2] = "XX"
                tmp[4*i+3] = "XX"
        for i in range(16):
            result[i] = tmp[ shiftRowsTable[i] ]
        return " ".join(result)

def faultAnalysisDemo(key = [0x2b7e, 0x1516, 0x28ae, 0xd2a6, 0xabf7, 0x1588, 0x09cf, 0x4f3c]):
    from myAES import FaultyAES
    from myAES import AES
    import random
    
    correctAES = AES()
    faultyAES = FaultyAES()
    correctAES.keyExpansion(key)
    faultyAES.keyExpansion(key)

    solver = AESDFA()
    toStr = (lambda x: " ".join( map((lambda x: "%.4x" %x), x )))

    print "\n=== Fault Analysis Demo ==="
    for pos in range(4):
        print "Iteration %d" % pos
        pair_list = []
        for i in range(3):
            pt = [random.randrange(0, 2**16) for i in range(8)]
            ct1 = correctAES.encrypt(pt)
            ct2 = faultyAES.encrypt(pt, pos)
            diff = [i^j for (i, j) in zip(ct1, ct2)]
            print "CT1:", toStr(ct1), "CT2:", toStr(ct2), "Diff:", toStr(diff)
            pair_list += [(ct2, ct1)]

        for (ct, faultyCt) in pair_list:
            solver.search16( (ct, faultyCt), pos )
        print "Temporal results are:", solver.getResult()
        print ""
    
if __name__ == "__main__":
    ## # The secret key is [2b 7e 15 16 28 ae d2 a6 ab f7 15 88 09 cf 4f 3c]
    ## # final-roundkey is [D0 14 F9 A8 C9 EE 25 89 E1 3F 0C C8 B6 63 0C A6]
    ## 
    ## pair0 = ([0x91ff, 0xce1b, 0x90e0, 0x246e, 0x4253, 0xea24, 0xbd1e, 0x32a1],
    ##          [0x91d3, 0xce1b, 0x64e0, 0x246e, 0x4253, 0xea26, 0xbd1e, 0xb8a1])
    ## pair1 = ([0x6ddf, 0x88a8, 0x6588, 0xfba6, 0x2125, 0xa13e, 0x8862, 0x8bc7],
    ##          [0x6db3, 0x88a8, 0x1388, 0xfba6, 0x2125, 0xa1f4, 0x8862, 0x00c7])
    ## pair2 = ([0x2d6a, 0xa7b5, 0x6859, 0xfbd1, 0xaf47, 0x5003, 0x27a9, 0x0a97],
    ##          [0x2db3, 0xa7b5, 0x4059, 0xfbd1, 0xaf47, 0x5007, 0x27a9, 0xec97])
    ## pair3 = ([0x5614, 0x2476, 0x976f, 0x8061, 0xa05a, 0xe71d, 0xba4b, 0x6967],
    ##          [0x5624, 0x2476, 0x0f6f, 0x8061, 0xa05a, 0xe7b4, 0xba4b, 0x0c67])
    ## 
    ## aobj = AESDFA()
    ## 
    ## aobj.search16(pair0, 1);  print aobj
    ## aobj.search16(pair1, 1);  print aobj
    ## aobj.search16(pair2, 1);  print aobj
    ## aobj.search16(pair3, 1);  print aobj    
    ## 
    ## print aobj.getResult()

    faultAnalysisDemo()
