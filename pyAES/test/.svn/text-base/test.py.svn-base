import sys
sys.path.append("..")
from myAES import AES

from aes_v001_wrapper import AES_wrapper
import random
import time

if __name__ == "__main__":

   
    aobj = AES()
    bobj = AES_wrapper()

    key = [random.randrange(0, 65535) for i in range(8)]
    aobj.keyExpansion(key)

    N = 100
    pt_array = []
    for i in range(N):
        pt_array.append( [random.randrange(0, 65535) for i in range(8)] )

    aobj_list = []
    bobj_list = []
    
    t1 = time.time()
    for pt in pt_array:
        aobj_list.append( aobj.encrypt(pt) )
    t2 = time.time()

    t3 = time.time()
    for pt in pt_array:
        bobj_list.append( bobj.encrypt(pt, key, bobj.keySize["SIZE_128"]) )
    t4 = time.time()

    print "New", (t2-t1)/N
    print "Old", (t4-t3)/N

    for i in range(N):
        if aobj_list[i] != bobj_list[i]:
            raise Exception("hogehoge")
    print "Finished"
