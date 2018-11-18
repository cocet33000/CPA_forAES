#!/bin/env python
# -*- coding: shift_jis -*-
#
# Written by Takeshi Sugawara
# 2010/July/01

import myAES, utility
import functools

def ECB_encrypt(cipherObj, key, ptList):
    result = []
    cipherObj.keyExpansion(key)
    for pt in ptList:
        result += [cipherObj.encrypt(pt)]
    return result

def ECB_decrypt(cipherObj, key, ctList):
    result = []
    cipherObj.keyExpansion(key)
    for ct in ctList:
        result += [cipherObj.decrypt(ct)]
    return result

def CBC_encrypt(cipherObj, key, ptList, iv):
    cipherObj.keyExpansion(key)
    result = []
    xorInput = iv
    for pt in ptList:
        aesInput = [x^y for (x, y) in zip(pt, xorInput)]
        #print "aesInput", map((lambda x: "%04x" % x), aesInput)
        xorInput = cipherObj.encrypt(aesInput)
        result += [xorInput]
    return result

def CBC_decrypt(cipherObj, key, ctList, iv):
    cipherObj.keyExpansion(key)
    result = []
    xorInput = iv
    for ct in ctList:
        aesOutput = cipherObj.decrypt(ct)
        result += [[x^y for (x, y) in zip(aesOutput, xorInput)]]
        xorInput = ct
    return result

def CTR_encrypt(cipherObj, key, ptList, iv):
    counter = utility.uint16listToUint(iv)
    cipherObj.keyExpansion(key)
    result = []
    for pt in ptList:
        aesInput = utility.uintToUint16list(counter)
        aesOutput = cipherObj.encrypt(aesInput)
        result += [[x^y for (x, y) in zip(aesOutput, pt)]]
        counter += 1
    return result
        
def AES_ECB_encrypt(key, ptList):
    return ECB_encrypt(myAES.AES(), key, ptList)
def AES_ECB_decrypt(key, ctList):
    return ECB_decrypt(myAES.AES(), key, ctList)

def AES_CBC_encrypt(key, ptList, iv):
    return CBC_encrypt(myAES.AES(), key, ptList, iv)
def AES_CBC_decrypt(key, ctList, iv):
    return CBC_decrypt(myAES.AES(), key, ctList, iv)

def AES_CTR_encrypt(key, ptList, iv):
    return CTR_encrypt(myAES.AES(), key, ptList, iv)
def AES_CTR_decrypt(key, ctList, iv):
    return AES_CTR_encrypt(key, ctList, iv)

def testCTR():
    key = [0x2b7e, 0x1516, 0x28ae, 0xd2a6, 0xabf7, 0x1588, 0x09cf, 0x4f3c]
    iv =  [0xf0f1, 0xf2f3, 0xf4f5, 0xf6f7, 0xf8f9, 0xfafb, 0xfcfd, 0xfeff]
    ptList = [
        [0x6bc1, 0xbee2, 0x2e40, 0x9f96, 0xe93d, 0x7e11, 0x7393, 0x172a],
        [0xae2d, 0x8a57, 0x1e03, 0xac9c, 0x9eb7, 0x6fac, 0x45af, 0x8e51],
        [0x30c8, 0x1c46, 0xa35c, 0xe411, 0xe5fb, 0xc119, 0x1a0a, 0x52ef],
        [0xf69f, 0x2445, 0xdf4f, 0x9b17, 0xad2b, 0x417b, 0xe66c, 0x3710]
        ]
    ctList = [
        [0x874d, 0x6191, 0xb620, 0xe326, 0x1bef, 0x6864, 0x990d, 0xb6ce], 
        [0x9806, 0xf66b, 0x7970, 0xfdff, 0x8617, 0x187b, 0xb9ff, 0xfdff], 
        [0x5ae4, 0xdf3e, 0xdbd5, 0xd35e, 0x5b4f, 0x0902, 0x0db0, 0x3eab], 
        [0x1e03, 0x1dda, 0x2fbe, 0x03d1, 0x7921, 0x70a0, 0xf300, 0x9cee]
        ]

    print "Starting CTR test"
    encResultList = AES_CTR_encrypt(key, ptList, iv)
    for x, y in zip(encResultList, ctList):
        if x != y: raise Exception("Error in CTR encryption")

    decResultList = AES_CTR_decrypt(key, ctList, iv)
    for x, y in zip(decResultList, ptList):
        if x != y: raise Exception("Error in CTR decryption")
    
    print "CBC test finished"

def testCBC():
    # NIST 800-38A test vectors
    key = [0x2b7e, 0x1516, 0x28ae, 0xd2a6, 0xabf7, 0x1588, 0x09cf, 0x4f3c]
    iv = [0x0001, 0x0203, 0x0405, 0x0607, 0x0809, 0x0a0b, 0x0c0d, 0x0e0f]
    ptList = [
        [0x6bc1, 0xbee2, 0x2e40, 0x9f96, 0xe93d, 0x7e11, 0x7393, 0x172a],
        [0xae2d, 0x8a57, 0x1e03, 0xac9c, 0x9eb7, 0x6fac, 0x45af, 0x8e51],
        [0x30c8, 0x1c46, 0xa35c, 0xe411, 0xe5fb, 0xc119, 0x1a0a, 0x52ef],
        [0xf69f, 0x2445, 0xdf4f, 0x9b17, 0xad2b, 0x417b, 0xe66c, 0x3710]
        ]
    ctList = [
        [0x7649, 0xabac, 0x8119, 0xb246, 0xcee9, 0x8e9b, 0x12e9, 0x197d], 
        [0x5086, 0xcb9b, 0x5072, 0x19ee, 0x95db, 0x113a, 0x9176, 0x78b2], 
        [0x73be, 0xd6b8, 0xe3c1, 0x743b, 0x7116, 0xe69e, 0x2222, 0x9516], 
        [0x3ff1, 0xcaa1, 0x681f, 0xac09, 0x120e, 0xca30, 0x7586, 0xe1a7]
        ]

    print "Starting CBC test"
    encResultList = AES_CBC_encrypt(key, ptList, iv)
    for x, y in zip(encResultList, ctList):
        if x != y: raise Exception("Error in CBC encryption")

    decResultList = AES_CBC_decrypt(key, ctList, iv)
    for x, y in zip(decResultList, ptList):
        if x != y: raise Exception("Error in CBC decryption")
    print "CBC test finished"

def testECB():
    # NIST 800-38A test vectors
    key = [0x2b7e, 0x1516, 0x28ae, 0xd2a6, 0xabf7, 0x1588, 0x09cf, 0x4f3c]
    ptList = [
        [0x6bc1, 0xbee2, 0x2e40, 0x9f96, 0xe93d, 0x7e11, 0x7393, 0x172a],
        [0xae2d, 0x8a57, 0x1e03, 0xac9c, 0x9eb7, 0x6fac, 0x45af, 0x8e51],
        [0x30c8, 0x1c46, 0xa35c, 0xe411, 0xe5fb, 0xc119, 0x1a0a, 0x52ef],
        [0xf69f, 0x2445, 0xdf4f, 0x9b17, 0xad2b, 0x417b, 0xe66c, 0x3710]
        ]
    ctList = [
        [0x3ad7, 0x7bb4, 0x0d7a, 0x3660, 0xa89e, 0xcaf3, 0x2466, 0xef97],
        [0xf5d3, 0xd585, 0x03b9, 0x699d, 0xe785, 0x895a, 0x96fd, 0xbaaf],
        [0x43b1, 0xcd7f, 0x598e, 0xce23, 0x881b, 0x00e3, 0xed03, 0x0688],
        [0x7b0c, 0x785e, 0x27e8, 0xad3f, 0x8223, 0x2071, 0x0472, 0x5dd4], 
        ]

    print "Starting ECB test."

    # Encryption test
    encResultList = AES_ECB_encrypt(key, ptList)
    for x, y in zip(encResultList, ctList):
        if x != y:
            raise Exception("")

    # Decryption test
    decResultList = AES_ECB_decrypt(key, ctList)
    for x, y in zip(decResultList, ptList):
        if x != y:
            raise Exception("")
    print "ECB test finished."
    
if __name__ == "__main__":
    testECB()
    testCBC()
    testCTR()
    #counter = 100
    #tmp = utility.uintToUint16list(counter)
    #print tmp
    #print utility.uint16listToUint(tmp)

    key = [0x2b7e, 0x1516, 0x28ae, 0xd2a6, 0xabf7, 0x1588, 0x09cf, 0x4f3c]
    iv =  [0 for i in range(8)]
    ptList = [
        [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000],        
        [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0001],
        [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0002],
        [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0003],
        [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0004],
        [0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0005]]
    #ctList = [
    #    [0x874d, 0x6191, 0xb620, 0xe326, 0x1bef, 0x6864, 0x990d, 0xb6ce], 
    #    [0x9806, 0xf66b, 0x7970, 0xfdff, 0x8617, 0x187b, 0xb9ff, 0xfdff], 
    #    [0x5ae4, 0xdf3e, 0xdbd5, 0xd35e, 0x5b4f, 0x0902, 0x0db0, 0x3eab], 
    #    [0x1e03, 0x1dda, 0x2fbe, 0x03d1, 0x7921, 0x70a0, 0xf300, 0x9cee]
    #    ]

    encResultList = AES_CBC_encrypt(key, ptList, iv)
    for i in encResultList:
        print map((lambda x: "%04x" % x), i)
    print "CBC test finished"
