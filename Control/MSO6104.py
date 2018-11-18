#!/bin/env python
# -*- coding: shift_jis -*-
#
# Written by Takeshi Sugawara
# 2010/July/02

"""
オシロスコープ制御用クラス
"""

import visa
import time
class MSO6104:
    def __init__(self, name):
        #'USB0::0x0957::0x1754::MY44002614'
        #'GPIB0::1'
        print visa.get_instruments_list()
        self.mbs = visa.instrument(name)
        self.mbs.timeout = 60
        self.mbs.chunk_size = 10 * 1024 * 1024
        
    def reset(self):
        self.mbs.write("*IDN?")
        print self.mbs.read()
        self.mbs.write("*RST\n");
        self.mbs.write("*CLS\n");

    def setup(self, configFile=None):
        _defaultConfig = [
            ":TIMebase:REFerence center",
            ":TIMebase:SCALe 100e-9",
            ":TIMebase:POSition 300e-9",
            ":CHANnel1:IMPedance FIFTy",
            ":CHANnel1:SCALe 50e-3",
            ":CHANnel1:OFFSet 150e-3",
            ":CHANnel1:BWLimit 0",
            ":CHANnel1:DISPlay ON",
            ":TRIGger:MODE EDGE",
            ":TRIGger:EDGE:SOURce CHANnel2",
            ":TRIGger:EDGE:SLOPe NEGative",
            ":TRIGger:EDGE:LEVel 1.0",
            ":TRIGger:SWEep NORMal",
            ":ACQuire:MODE RTIMe",
            ":ACQuire:TYPE NORMal",
            ":WAVeform:SOURce CHANnel1",
            ":WAVeform:FORMat BYTE",
            ":WAVeform:UNSigned 1",
            ":WAVeform:POINts MAX",
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
            
    def acquire(self):
        """ オシロスコープをトリガ待ち(アーム状態)にする """
        self.mbs.write(":DIGitize CHANnel1\n")
        
    def get_data(self):
        """
        オシロスコープから波形を取り込む
        もし、トリガが来ていない場合、ブロックする.
        """
        self.mbs.write(":WaveForm:DATA?")
        tmp = self.mbs.read()
        return tmp
        
    def get_sampling_freq(self):
        self.mbs.write(":Timebase:scale?")
        tmp = self.mbs.read()
        print tmp
        return float(tmp)

    def get_num_points(self):
        self.mbs.write(":Waveform:points?")
        print self.mbs.read()

    def query(self, str):
        self.mbs.write(str)
        print self.mbs.read()
        

def _ascii_to_float(ascii_list):
    tmp = ascii_list[1:] # Eliminate a header
    return map(float, tmp)

if __name__ == '__main__':
    x = MSO6104()
    x.reset()
    x.setup()
    a = x.get_data()
    b = x.get_sampling_freq()
