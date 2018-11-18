#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyAES.myAES import AES_unroll
from Control.utility import *
import numpy as np
import pickle

aobj = AES_unroll()
hamming_distance = {}
intermediate_values = {}
num = 0


def cal_hamming(A):
    hamming = []
    a = []
    nine = A.data[9]
    ten = A.data[10]
    for i in range(len(nine)):
        a.append(format(nine[i] ^ ten[i], '08x'))
    for data in a:
        hamming.extend([str(bin(int('0x' + (i+j), 0))).count('1')
                        for (i, j) in zip(data[::2], data[1::2])])
    return(hamming)


# load cipher text
with open('./pkl/cipher.pkl', 'rb') as f:
    cipher = pickle.load(f)

# cipher text loop
for ct in cipher:
    # guess_key loop (256)
    for partial_key in range(256):
        key = [partial_key*2**8 + partial_key for l in range(8)]
        aobj.keyExpansion(key)
        # change key of 10R
        aobj.subkey[40:44] = [
            int('0x' + format(partial_key, '02x')*4, 0) for loop in range(4)]
        aobj.decrypt(ct)        # decrypt
        if(partial_key == 0):
            cpa_tmp = np.array([cal_hamming(aobj)])
        else:
            cpa_tmp = np.append(cpa_tmp, [cal_hamming(aobj)], axis=0)
    if num == 0:
        cpa = np.array([cpa_tmp])
    else:
        cpa = np.append(cpa, np.array([cpa_tmp]), axis=0)
    num += 1
    print(num)

# list for shft rows
lis = [0, 5, 10, 15, 4, 9, 14, 3,  8, 13, 2, 7, 12, 1, 6, 11]

# write file
for num in range(16):
    with open('./pkl/b' + str(num) + '.pkl', mode='wb') as f:
        data = cpa[:, :, lis[num]]
        print(data.shape)
        pickle.dump(data, f)
