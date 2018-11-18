#!/bin/env python
# -*- coding: shift_jis -*-
#
# Written by Sho Endo
# 2010/Aug/11

"""
Class for operating DPO7254
"""

import visa
import time
class DPO7254:
    def __init__(self, name):
        #'GPIB0::1'
        print visa.get_instruments_list()
        self.mbs = visa.instrument(name)
        self.mbs.timeout = 10
        #self.mbs.chunk_size = 1 * 1024 * 1024
        
    def reset(self):
        self.mbs.write("*IDN?")
        print self.mbs.read()
        self.mbs.write("*RST\n");
        self.mbs.write("*CLS\n");

    def setup(self, configFile=None):
        _defaultConfig = [
            ":ACQuire:SAMPlingmode RT", 
            ":HORizontal:MAIn:UNIts \"s\"",
            ":HORizontal:RECORDlength 5e5",
            ":HORizontal:MAIn:SAMPLERate 10e9", 
            ":HORizontal:SCAle 5e-6",
            ":HORizontal:DELay:MODe 1", 
            ":HORizontal:DELay:POSition 10",
            ":CH1:SCAle 1",
            ":CH1:POSition 1.00",
            ":CH2:SCALE 1.0",
            ":CH3:SCAle 2.0",
            ":CH3:POSition -1.50",
            ":CH4:TERmination 50",
            ":CH4:SCAle 2.0e-3",
            ":CH4:POSition 0",
            ":CH4:BANdwidth 20.0e6",
            ":TRIGger:A:TYPe PULSE",
            ":TRIGger:A:PULse:CLAss TIMEOUT",
            ":TRIGger:A:PULse:SOUrce CH3", 
            ":TRIGger:A:LEVel:CH3 1.6",
            ":TRIGger:A:PULse:TIMEOut:TIMe 23e-9",
            ":TRIGger:A:MODe NORM", 
            ":SELect:CH1 1",
            ":SELect:CH2 0",
            ":SELect:CH3 1",
            ":SELect:CH4 1",
            ":AUXout:SOUrce ATRIGger",
            ":AUXout:EDGE RISing", 
            ":DATa:SOUrce CH4",
            ":DATa:ENCdg RIBinary",
            ":DATa:STARt 1",
            ":DATa:STOP  5e6",
            ":WFMOutpre:BYT_Nr 2",
            ":WFMOutpre:BYT_Or LSB"
            ":RUN"]

        def _parseConfig(fileName):
            buf = []
            with open(fileName, 'r') as fd:
                for line in fd:
                    line = line.strip()
                    if not (line == "" or line[0] == "#"):
                        buf += [line]
            return buf

        if configFile is None:  buf = _defaultConfig
        else:                   buf = _parseConfig(configFile)
        for command in buf:
            self.mbs.write(command+"\n")
        time.sleep(1)
        print 'Setup of the oscilloscope finished.'

    def get_data(self):
        """
        オシロスコープから波形を取り込む
        もし、トリガが来ていない場合、ブロックする.
        """
        #self.mbs.write("WFMOutpre?")
        #time.sleep(2)
        #print self.mbs.read()
        #self.mbs.values_format = single
        self.mbs.write("ACQuire:NUMAcq?")
        #time.sleep(1)
        n_acq = self.mbs.read()
        #print n_acq
        if n_acq != '0':
            self.mbs.write("CURVe?")
            #time.sleep(1)
            print "Reading"
            tmp = self.mbs.read()
            return tmp
        else:
            #If no waveform exists, triggers
            self.mbs.write("TRIGger FORCe")
            return self.get_data()

    def binary_to_ascii(self, data):
        """バイナリデータからASCIIへの変換"""
        import struct
        data_nh = self.remove_header(data)
        l_data = len(data_nh) / 2
        res = l_data * [0]
        #print data
        for i in range(l_data):
            index = i * 2
            tmp = struct.unpack("h", data_nh[index:index+2])
            res[i] = tmp[0]
        return res

    def remove_header(self, data):
        #Omit header bytes
        #Read second byte which describes the number of digits
        n_digit = int(data[1])
        l_data = len(data)
        res = data[n_digit+2:l_data]
        return res

    def wait_ready(self):
        while 1:
            self.mbs.write("TRIGger:STATE?")
            if self.mbs.read() == "READY":
                break

    def clear(self):
        self.mbs.write("ACQuire:MODe?")
        if self.mbs.read() == "AVERAGE":
            self.mbs.write("ACQuire:MODe SAMPLE")
            self.mbs.write("ACQuire:MODe AVERAGE")

if __name__ == '__main__':
    x = DPO7254('GPIB::1')
    x.reset()
    x.setup("DPO7254config.txt")
