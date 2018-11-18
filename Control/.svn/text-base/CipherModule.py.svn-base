#!/bin/env python
# -*- coding: shift_jis -*-
#
# Written by Takeshi Sugawara
# 2010/July/02

"""
SASEBO 制御用のクラス
"""

import time
from utility import *

# ASIC version1 用のアドレスの辞書
rev1_cipher_list = {"AES_Comp"     : 0x0001,
                    "AES_Comp_ENC" : 0x0002,
                    "AES_TBL"      : 0x0004,
                    "AES_PPRM1"    : 0x0008,
                    "AES_PPRM3"    : 0x0010,
                    "DES"          : 0x0020,
                    "MISTY1"       : 0x0040,
                    "Camellia"     : 0x0080,
                    "SEED"         : 0x0100,
                    "CAST128"      : 0x0200,
                    "RSA"          : 0x0400,
                    "AES_SSS1"     : 0x0800,
                    "AES_S"        : 0x1000 }

rev1_addr_list = { "ADDR_CONT"    : 0x0002,
                   "ADDR_IPSEL"   : 0x0004,
                   "ADDR_OUTSEL"  : 0x0008,
                   "ADDR_ENCDEC"  : 0x000C,
                   "ADDR_RSEL"    : 0x000E,
                   "ADDR_KEY0"    : 0x0100,
                   "ADDR_ITEXT0"  : 0x0140,
                   "ADDR_OTEXT0"  : 0x0180,
                   "ADDR_RDATA0"  : 0x01C0,
                   "ADDR_EXP00"   : 0x0200,
                   "ADDR_MOD00"   : 0x0300,
                   "ADDR_IDATA00" : 0x0400,
                   "ADDR_ODATA00" : 0x0500,
                   "ADDR_VERSION" : 0xFFFC }

class LocalBus(object):
    """
    制御FPGA間との通信のためのモジュール
    """
    def __init__(self, interface):
        # Switching between USB and RS232C interfaces
        if interface == "USB":
            import d2xx
            self.ctrlif = d2xx.open(0)
        else:
            # Here, interface is expected to be like "COM1"
            # In this case, port number for pySecial should be 0
            import serial
            portNum = int(interface[3:]) - 1
            try:
                self.ctrlif = serial.Serial(port=portNum, baudrate=19200,timeout=1)
            except serial.serialutil.SerialException:
                import sys
                sys.exit("Cannot open port: " + interface)
        self.cipher_list = rev1_cipher_list
        self.addr_list = rev1_addr_list
    def __del__(self):
        if self.ctrlif:
            self.ctrlif.close()


    def write(self, addr, dat):
        buf = []
        buf.append(0x01) # Magic number of writing
        buf.append( addr / 256)
        buf.append( addr % 256)
        buf.append( dat / 256)
        buf.append( dat % 256)
        self.ctrlif.write(bytelistToStr(buf))

    def write_burst(self, addr, dat):
        buf = []
        counter = 0
        for chunk in dat: # chunk is a 16-bit (positive) integer
            buf.append(0x01) # Magic number of writing
            buf.append( (addr + counter) / 256)
            buf.append( (addr + counter) % 256)
            buf.append( chunk / 256)
            buf.append( chunk % 256)
            counter += 2
        self.ctrlif.write(bytelistToStr(buf))

    def read(self, addr):
        buf = []
        buf.append(0x00) # Magic number for reading
        buf.append(addr / 256)
        buf.append(addr % 256)
        self.ctrlif.write(bytelistToStr(buf))
        
        tmp = self.ctrlif.read(2)
        #print "%.4x" % binstr_to_uint16(tmp)
        return binstr_to_uint16(tmp)

    def read_burst(self, addr, len=2):
        buf = []
        for offset in range(0, len, 2):
            buf.append(0x00)
            buf.append( (addr+offset) / 256 )
            buf.append( (addr+offset) % 256 )
        self.ctrlif.write(bytelistToStr(buf))
        tmp = self.ctrlif.read(len)
        return strToUint16List(tmp)
        

class CipherModule(LocalBus):
    """
    暗号チップの制御用クラス
    """
    def __init__(self, interface):
        super(CipherModule, self).__init__(interface)
        
    def select(self, cipher):
        """ 暗号コアの選択 """
        version = self.read(self.addr_list["ADDR_VERSION"])
        self.write(self.addr_list["ADDR_IPSEL"], self.cipher_list[cipher])
        self.write(self.addr_list["ADDR_CONT"], 0x0004)
        self.write(self.addr_list["ADDR_CONT"], 0x0000)
        self.write(self.addr_list["ADDR_OUTSEL"], self.cipher_list[cipher])

    def encdec(self, dat):
        self.write(self.addr_list["ADDR_ENCDEC"], dat)

    def set_key(self, key_list):
        """ 秘密鍵の格納と鍵スケジュール """
        self.key = key_list # Store the key
        self.write_burst(self.addr_list["ADDR_KEY0"], key_list)
        self.write(self.addr_list["ADDR_CONT"], 0x0002)
        
        for i in range(10):
            if self.read(self.addr_list["ADDR_CONT"]) == 0x0000:
                return
            else:
                print self.read(self.addr_list["ADDR_CONT"])
                time.sleep(0.1) # wait for 0.1 sec
        raise "Error in key scheduling: never return"
    
    def encrypt(self, dat):
        self.write_burst(self.addr_list["ADDR_ITEXT0"], dat)
        self.write(self.addr_list["ADDR_CONT"], 0x0001) # kick the cipher
        return self.read_burst(self.addr_list["ADDR_OTEXT0"], 16)

    def encrypt_again(self):
        """ Encrypt again without feeding a new plaintext (for test) """
        self.write(self.addr_list["ADDR_CONT"], 0x0001) # kick the cipher
        return self.read_burst(self.addr_list["ADDR_OTEXT0"], 16)

    def read_key(self):
        return self.read_burst(self.addr_list["ADDR_KEY0"], 16)

    def read_otext(self):
        return self.read_burst(self.addr_list["ADDR_OTEXT0"], 16)

    def read_rdata(self):
        return self.read_burst(self.addr_list["ADDR_RDATA0"], 16)    

    def set_rsel(self, dat=0x8000):
        self.write(self.addr_list["ADDR_RSEL"],dat)
        #print self.read(self.addr_list["ADDR_RSEL"])

    def read_rsel(self):
        print self.read(self.addr_list["ADDR_RSEL"])

    def set_ipsel(self, dat=0x8000):
        self.write(self.addr_list["ADDR_IPSEL"], dat)
        return self.read(self.addr_list["ADDR_IPSEL"])


if __name__ == '__main__':
    key = [0x2b7e, 0x1516, 0x28ae, 0xd2a6, 0xabf7, 0x1588, 0x09cf, 0x4f3c]
    pt  = [0x3243, 0xf6a8, 0x885a, 0x308d, 0x3131, 0x98a2, 0xe037, 0x0734]
    cm = CipherModule()

    print "key", hex_str(key)
    print "pt", hex_str(pt)
    
    cm.select("AES_TBL")
    cm.encdec(0x0000)

    cm.set_key(key)
    print hex_str(cm.encrypt(pt))
    del cm

    #from aes_v001_wrapper import AES_wrapper
    #aobj = AES_wrapper()
    #print "Recalc:", hex_str(aobj.encrypt(pt, key, AES_wrapper.keySize["SIZE_128"]))


    
