import CipherModule
from utility import *

rev2_addr_list = { "ADDR_CONT"     : 0x0002,
                   "ADDR_IPSEL"    : 0x0004,
                   "ADDR_OUTSEL"   : 0x0008,
                   "ADDR_MODE"     : 0x000C,
                   "ADDR_ENCDEC"   : 0x000C,
                   "ADDR_RSEL"     : 0x000E,
                   "ADDR_KEY0"     : 0x0100,
                   "ADDR_IV0"      : 0x0110,
                   "ADDR_ITEXT0"   : 0x0120,
                   "ADDR_RAND0"    : 0x0160,
                   "ADDR_OTEXT0"   : 0x0180,
                   "ADDR_RDATA0"   : 0x01C0,
                   "ADDR_RKEY0"    : 0x01D0,
                   "ADDR_EXP00"    : 0x0200,
                   "ADDR_MOD00"    : 0x0300,
                   "ADDR_PREDAT00" : 0x0340,
                   "ADDR_IDATA00"  : 0x0400,
                   "ADDR_ODATA00"  : 0x0500,
                   "ADDR_VERSION" : 0xFFFC}

# Note that IPSEL1 is not supported for now
rev2_cipher_list = { "AES_Comp"     : 0x0001,
                     "AES_TBL"      : 0x0002,
                     "AES_PPRM1"    : 0x0004,
                     "AES_PPRM3"    : 0x0008,
                     "AES_Comp_ENC" : 0x0010,
                     "AES_CTR_Pipe" : 0x0020,
                     "AES_FA"       : 0x0040,
                     "AES_PKG"      : 0x0080,
                     "AES_MAO"      : 0x0100,
                     "AES_MDPL"     : 0x0200,   
                     "AES_TI"       : 0x0400,
                     "AES_WDDL"     : 0x0800,
                     "AES_RSL"      : 0x1000,
                     "AES_RSL2"     : 0x2000 }

class CipherModule_mash(CipherModule.CipherModule):
    def __init__(self, interface="USB"):
        super(CipherModule_mash, self).__init__(interface)
        #CipherModule.CipherModule.__init__(self)
        self.cipher_list = rev2_cipher_list
        self.addr_list   = rev2_addr_list
        
    def select(self, cipher):
        # version = self.read(self.addr_list["ADDR_VERSION"])
        # print version
        # self.write(self.addr_list["ADDR_IPSEL"], self.cipher_list[cipher])
        # self.write(self.addr_list["ADDR_CONT"], 0x0004)
        # self.write(self.addr_list["ADDR_CONT"], 0x0000)
        # self.write(self.addr_list["ADDR_OUTSEL"], self.cipher_list[cipher])
        CipherModule.CipherModule.select(self, cipher)
        
        # Special reset for RSL module
        self.write(0x0012, 0x0001)
        self.write(0x0012, 0x0000)        
      
if __name__ == '__main__':
    import sys
    # Note that key-length is limited to 56 bits in MASH / CHAR
    key = [0x0001, 0x0203, 0x0405, 0x0607, 0x0809, 0x0a0b, 0x0c0d, 0x0e0f]
    pt  = [0x3243, 0xf6a8, 0x885a, 0x308d, 0x3131, 0x98a2, 0xe037, 0x0734]
    cm = CipherModule_mash(interface="COM3")
    
    print "key", hex_str(key)
    print "pt", hex_str(pt)
    
    cm.select("AES_Comp")
    cm.encdec(0x0000)

    cm.set_key(key)
    print hex_str(cm.encrypt(pt))
    print hex_str(cm.encrypt(key))
    del cm
    
    #aobj = myAES.AES()
    #aobj.keyExpansion(key)
    #recalc = aobj.encrypt(pt)
    #print hex_str(recalc)
    #aobj = AES_wrapper()
    #print "Recalc:", hex_str(aobj.encrypt(pt, key, AES_wrapper.keySize["SIZE_128"]))
    
