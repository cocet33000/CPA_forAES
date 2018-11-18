#!/bin/env python
# -*- coding: shift_jis -*-
#
# Written by Takeshi Sugawara
# 2010/July/02

"""
選択関数を計算する.
AESの最終ラウンドでの予測電力値を計算する。 
その他のアルゴリズム・ラウンドには未対応なのに注意。
"""

import myAES
import utility

def _hw(interMediateData, cipherText):
    return interMediateData
def _hd(interMediateData, cipherText):
    return [interMediateData[i] ^ cipherText[i] for i in range(4)]
def _rising(interMediateData, cipherText):
    return [~interMediateData[i] & (interMediateData[i] ^ cipherText[i]) for i in range(4)]
def _falling(interMediateData, cipherText):
    return [interMediateData[i] & (interMediateData[i] ^ cipherText[i]) for i in range(4)]

def _uint32listToBytelist(data):
    buf = []
    for i in data:
        buf.append( int( (i >> 24) & 0x000000ff ) )
        buf.append( int( (i >> 16) & 0x000000ff ) )
        buf.append( int( (i >>  8) & 0x000000ff ) )
        buf.append( int( (i      ) & 0x000000ff ) )
    return buf


class AESDPA(object):
    # Dispatch table
    # 引数に応じて、電力モデルをスイッチする
    typeList = {
        "HW": _hw,
        "HD": _hd,
        "Rising": _rising,
        "Falling": _falling}

    def getByteSelectionFunction(self, cipherText, type="HD"):
        ct = utility.uint16listToUint32list( cipherText )
        data = [0, 0, 0, 0]

        # すべての鍵候補を探索する。
        # myAES が uint32 ベースで実装されているので、
        # それに合わせて並列で探索を行う。
        result = [None for i in range(256*16)]
        for candidate in range(256):
            parallelCandidate = (candidate << 24) | (candidate << 16) \
                              | (candidate << 8) | candidate
            for i in range(4):
                data[i] = ct[i] ^ parallelCandidate
            data = map(myAES.invSubWord, data)
            data = myAES.invShiftRow128(data)
            tmp = self.typeList[type](data, ct)
            byte_list = _uint32listToBytelist(tmp)
            for sbox in range(16):
                result[256*sbox + candidate] = utility.hammingWeight( byte_list[sbox] )
        return result
    
def generateSelectionFunction(key, pt_list, ct_list=None):
    """
    平文もしくは暗号文のリストから、選択関数を生成する関数。
    基本的には、この関数のみをインタフェースとして用いるのが望ましい．
    """
    if ct_list is None:
        aes_obj = myAES.AES()
        aes_obj.keyExpansion(key)
        ct_list = []
        for pt in pt_list:
            ct_list += [aes_obj.encrypt(pt)]

    dpa_obj = AESDPA()
    result = []
    for ct in ct_list:
        result += [ dpa_obj.getByteSelectionFunction(ct) ]
    return result

if __name__ == "__main__":
    def test3(N=10):
        import random

        x = AESDPA()
        print "Test for %d different (key, plaintext)" % N
        for i in range(N):
            key = [random.randrange(0, 2**16) for i in range(8)]
            pt  = [random.randrange(0, 2**16) for i in range(8)]
            print x.getByteSelectionFunction(pt)
        print "Test finished"

    def test4(N=10):
        import random
        key = [random.randrange(0, 2**16) for i in range(8)]
        pt_list = [ [random.randrange(0, 2**16) for i in range(8)] for j in range(N) ]

        a = generateSelectionFunction(key, pt_list)
        print a
        
    #test3()
    test4()


#class AESDPA(myAES.AES):
#    """ 選択関数を計算するためのクラス """    
#
#    # Dispatch table
#    # 引数に応じて、電力モデルをスイッチする
#    typeList = {
#        "HW": _hw,
#        "HD": _hd,
#        "Rising": _rising,
#        "Falling": _falling}
#    
#    def getByteSelectionFunction(self, cipherText, type="HD"):
#        ct = utility.uint16listToUint32list( cipherText )
#
#        # すべての鍵候補を探索する。
#        # myAES が uint32 ベースで実装されているので、
#        # それに合わせて並列で探索を行う。
#        result = [None for i in range(256*16)]
#        for candidate in range(256):
#            parallelCandidate = (candidate << 24) | (candidate << 16) \
#                              | (candidate << 8) | candidate
#            for i in range(4):
#                self.data[i] = ct[i] ^ parallelCandidate
#            self.invSubBytes()
#            self.invShiftRows()
#            tmp = self.typeList[type](self.data, ct)
#            byte_list = _uint32listToBytelist(tmp)
#            for sbox in range(16):
#                result[256*sbox + candidate] = utility.hammingWeight( byte_list[sbox] )
#        return result

#def generateSelectionFunction(key, pt_list, ct_list=None):
#    """
#    平文もしくは暗号文のリストから、選択関数を生成する関数。
#    基本的には、この関数のみをインタフェースとして用いるのが望ましい．
#    """
#    x = AESDPA()
#    x.keyExpansion(key)
#    if ct_list is None:
#        ct_list = []
#        for pt in pt_list:
#            ct_list += [x.encrypt(pt)]
#    
#    result = []
#    for ct in ct_list:
#        result += [ x.getByteSelectionFunction(ct) ]
#    return result
