#!/bin/env python
# -*- coding: shift_jis -*-
#
# Written by Sho Endo
# June 8, 2010

import copy
import CipherModule
import time
from utility import *

rev2_addr_list = { "ADDR_CONT"     : 0x0002,
                   "ADDR_IPSEL0"   : 0x0004,
                   "ADDR_IPSEL1"   : 0x0006,
                   "ADDR_OUTSEL0"  : 0x0008,
                   "ADDR_OUTSEL1"  : 0x000A,
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
                   "ADDR_VERSION"  : 0xFFFC }

rev2_cipher_list_ipsel0 = { "AES_Comp"     : 0x0001,
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
                     "AES_RSL2"     : 0x2000, 
                     "RSA"          : 0x0000  }

rev2_cipher_list_ipsel1 = { "RSA" : 0x0080 }

params_addr_list = {"ADDR_WIDTH"     : 0x0000,
		    "ADDR_PERIOD"    : 0x0001,
		    "ADDR_POS"       : 0x0002,
		    "ADDR_POS_FINE"  : 0x0003,
		    "ADDR_GLITCH_EN" : 0x0004 }


class CipherModuleRSA(CipherModule.CipherModule):
    def __init__(self, interface="USB"):
        super(CipherModuleRSA, self).__init__(interface)
        #Dictionary of addresses
        self.cipher_list_ipsel0 = rev2_cipher_list_ipsel0
        self.cipher_list_ipsel1 = rev2_cipher_list_ipsel1
        self.addr_list = rev2_addr_list
        self.select("RSA")  # Set IP
        self.reset_lsi()    # Reset RSA IP
    
    def set_key(self, exp_list, mod_list):
        """ 指数eおよび法nの格納 """
        #Set exponent
        self.write_burst(self.addr_list["ADDR_EXP00"], exp_list)
        #Set modulus
        self.write_burst(self.addr_list["ADDR_MOD00"], mod_list)
        #Set KSET
        self.write(self.addr_list["ADDR_CONT"], 0x0002)
        #Wait until KSET is cleared
        while (self.read(self.addr_list["ADDR_CONT"]) == 0x0010):
            a = 1 #do nothing

    def set_precomputed_value(self, pre_list):
        """前処理結果の入力"""
        print "pre_list = ", hex_str(pre_list)
        self.write_burst(self.addr_list["ADDR_PREDAT00"], pre_list)

    def reset_lsi(self):
        """LSIのリセット"""
        self.write(self.addr_list["ADDR_CONT"], 0x0004)
        self.write(self.addr_list["ADDR_CONT"], 0x0000)

    def start_encdec(self, dat):
        """暗号化または復号処理の開始"""
        self.write_burst(self.addr_list["ADDR_IDATA00"], dat)
        self.write(self.addr_list["ADDR_CONT"], 0x0001) # kick the cipher
        #time.sleep(0.5)
        #Wait until RUN is cleared
        while ((self.read(self.addr_list["ADDR_CONT"]) & 0x0001) == 1):
            1 #do nothing
        #print self.read(self.addr_list["ADDR_CONT"]) & 0x0001
        return self.read_burst(self.addr_list["ADDR_ODATA00"], 64)

    def set_rsa_mode(self, rsa_mode):
        """
        Setting the mode of RSA core.
        set_rsa_mode(rsa_mode) 
        rsa_mode: 0: Left binary method
                  1: Right binary method
                  2: Left binary method with countermeasures
                  3: Left binary method with countermeasures
                  4: Montgomery Powering Ladder
                  5: Right binary method by M. Joye
        """
        reg = self.read(self.addr_list["ADDR_MODE"])
        reg = (reg & 0xffc7) | (rsa_mode << 3)
        self.write(self.addr_list["ADDR_MODE"], reg)
        print "Set RSA core to mode ", rsa_mode

    def set_rsa_crt(self, crt):
        """
        Turn on or off CRT mode. 
        set_rsa_crt(crt) crt: 1 enable/ 0 disable
        """
        reg = self.read(self.addr_list["ADDR_MODE"])
        reg = (reg & 0xffbf) | (crt << 6)
        self.write(self.addr_list["ADDR_MODE"], reg)
        print "CRT mode was set to ", crt
    
    def select(self, cipher):
        """ 暗号コアの選択 """
        self.write(self.addr_list["ADDR_IPSEL0"], self.cipher_list_ipsel0[cipher])
        self.write(self.addr_list["ADDR_IPSEL1"], self.cipher_list_ipsel1[cipher])
        self.write(self.addr_list["ADDR_OUTSEL0"], self.cipher_list_ipsel0[cipher])
        self.write(self.addr_list["ADDR_OUTSEL1"], self.cipher_list_ipsel1[cipher])

    def encrypt(self, plaintext, exp, mod):
        """Encrypt or decrypt given plaintext"""
        # Convert multi-byte integer to list
        pt = intToUint16List(plaintext)
        e = intToUint16List(exp)
        n = intToUint16List(mod)
        # Set keys
        self.set_key(e, n)
        return self.start_encdec(pt) # Start encrytption and return the result

    def read_param(self, addr):
        buf = []
        buf.append(0x02) # Magic number for reading
        buf.append(addr / 256)
        buf.append(addr % 256)
        self.ctrlif.write(bytelistToStr(buf))
        
        tmp = self.ctrlif.read(2)
        #print "%.4x" % binstr_to_uint16(tmp)
        return binstr_to_uint16(tmp)

    def write_param(self, addr, dat):
        """Write parameters to the FPGA
        """
        buf = []
        buf.append(0x03) # Magic number of setting parameter
        buf.append( addr / 256)
        buf.append( addr % 256)
        buf.append( dat / 256)
        buf.append( dat % 256)
        self.ctrlif.write(bytelistToStr(buf))

if __name__ == '__main__':
    #Test code
    import sys
    from utility import *
    p = 0x8a1f8f59c0f652f2bed5498caed013ba45a5f75e653d8146331d5b37d032bff9L
    q = 0xcd2cf753681b4c649db4d3242f25418ca48b7cc014a837119a60d75bd5d7fee9L
    mod_int = p * q
    mod = intToUint16List(mod_int)

    pt = 0x19c8826e116109f90ce5bd560c1aa529c94462c3865fcee1567501afc94ffb9817d5696ad0e3921d53b199f1d914ba38a2d312a1a02ee75b913458d9191f2932L
    e = 65537
    d = 130998322792435220395308624386101773160162987917373681661950767902801767667663054016021266559449606905313108783547020205125622601925280660381647356566673

    cm = CipherModuleRSA(interface="COM1")
    
    ct = 0x64901bff353e701126673e643de1a1d76eb7b1a0cf567f715b903d21b896f812201209f72cc6bfa53d6f64758e9524d9f2bae6a100e5513697eeb2c90b6d3b20L
    ciphertext = intToUint16List(ct)
    
    cm.set_key(intToUint16List(d), mod)
    print hex_str(cm.start_encdec(ciphertext))
    del cm
