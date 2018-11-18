#!/bin/env python
# -*- coding: shift_jis -*-
#
# Written by Takeshi Sugawara
# 2010/July/02

"""
Simulated Power Consumption を計算する.
AESの最終ラウンドでの Hamming Distance (128 bits)
を計算する。その他のアルゴリズム・ラウンドには未対応なのに注意。
"""

import myAES
import utility

class AESSim(myAES.AES):
    """ Simulated Power Consumption を計算するためのクラス """    
    def _forward(self, plainText):
        """
        Plaintext から、最終ラウンドの Hamming Distance (128ビット)
        を生成する関数
        """
        if len(plainText) !=8:
            raise Exception("Invalid length of the input array")
        self.data = utility.uint16listToUint32list(plainText)
        for i in range(4):
            self.data[i] ^= self.subkey[i]
        for i in range(1, 10):
            self.ShiftRows()
            self.SBMX()
            for j in range(4):
                self.data[j] ^= self.subkey[i*4+j]
        tmp1 = self.data[:]
        # Final round
        self.ShiftRows()
        self.subBytes()
        for i in range(4):
            self.data[i] ^= self.subkey[40+i]
        tmp2 = self.data[:]

        # Calculate Hamming distance
        result = 0 
        for i in range(4):
            result += utility.hammingWeight( tmp1[i] ^ tmp2[i] )
        return int(result)

    def _backward(self, cipherText):
        """
        Ciphertext から、最終ラウンドの Hamming Distance (128ビット)
        を生成する関数
        """
        if len(cipherText) !=8:
            raise Exception("Invalid length of the input array")
        self.data = utility.uint16listToUint32list(cipherText)
        tmp2 = self.data[:]
        for i in range(4):
            self.data[i] ^= self.subkey[40+i]
        self.invSubBytes()
        self.invShiftRows()
        tmp1 = self.data[:]

        # Calculate Hamming distance
        result = 0 
        for i in range(4):
            result += utility.hammingWeight( tmp1[i] ^ tmp2[i] )
        return int(result)

    def gen(self, plainText, cipherText=None):
        """ Simulated Power Consumption を生成 """
        if cipherText is not None:
           return self._backward(cipherText)
        else:
           return self._forward(plainText)


def generateSimulatedPower(key, pt_list, ct_list=None):
    """
    平文もしくは暗号文のリストから、Simulated Power Consumption
    を生成する関数。基本的には、この関数のみをインタフェースとして
    用いるのが望ましい．
    """
    x = AESSim()
    x.keyExpansion(key)
    result = []
    if ct_list is not None:
        for (pt, ct) in zip(pt_list, ct_list):
            result.append( x.gen(pt, ct) )
    else:
        for pt in pt_list:
            result.append( x.gen(pt) )
    return result


if __name__ == "__main__":
    def test2(N=10):
        import random

        x = AESSim()
        print "Test for %d different (key, plaintext)" % N
        for i in range(N):
            key = [random.randrange(0, 2**16) for i in range(8)]
            pt  = [random.randrange(0, 2**16) for i in range(8)]
            x.keyExpansion(key)
            x.gen(pt)
        print "Test finished"

    test2()

    
