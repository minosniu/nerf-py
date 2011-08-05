#!/usr/bin/env python

"""
Test the fp_spindle_bag1.v, wrapper fp_spindle_test.
sin(omega * T * n) = sin(w * n)
omega * T = w
omega: analog freq
w: digital freq, 1kHz in all test cases
T: digital interval, depends on the wxPython clock, NOT the XEM pll clock!


Vary Pos_flex to see changes in Ia_pps 

C. Minos Niu (minos.niu AT sangerlab.net)
License: this code is in the public domain
Last modified: 10.18.2010
"""
import os
import random
import sys
import time
from struct import pack, unpack
from scipy.io import savemat, loadmat
import opalkelly_4_0_3.ok as ok

import numpy as np
from pylab import * 

VIEWER_REFRESH_RATE = 20 # in ms, This the T for calculating digital freq
NUM_CHANNEL = 2 # Number of channels
X_ADDR = 0x20 
INT_X_ADDR = 0x22 

DATA_EVT_CLKRATE = 7
##DISPLAY_SCALING = [0.1, 500, 500, 10, 10, 10, 5, 5]
DISPLAY_SCALING = [10, 125.7] 
DATA_OUT_ADDR = [X_ADDR, INT_X_ADDR]
ZERO_DATA = [0.0 for ix in xrange(NUM_CHANNEL)]
BIT_FILE = "/home/minos001/nerf_project/clean_nerf/projects/autotester/pipetester_xem3010.bit"

def ConvertType(val, fromType, toType):
    return unpack(toType, pack(fromType, val))[0]

if __name__ == "__main__":
    ## app = wx.App(False)
    ## controller = Controller(app)
    ## app.MainLoop()

    xem = ok.FrontPanel()
    xem.OpenBySerial("")
    bitfile = BIT_FILE
    assert os.path.exists(bitfile.encode('utf-8')), ".bit file NOT found!"

    if (xem.IsOpen()):
        xem.LoadDefaultPLLConfiguration()
        pll = ok.PLL22393()
        pll.SetReference(48.0)        #base clock frequency
        outputRate = 48
        pll.SetPLLParameters(0, outputRate, 48,  True)            #multiply up to 400mhz
        pll.SetOutputSource(0, ok.PLL22393.ClkSrc_PLL0_0)  #clk1
        finalRate = 1
        pll.SetOutputDivider(0, outputRate / finalRate)        #div4 = 100mhz; div128 = 4mhz
        pll.SetOutputEnable(0, True)
        xem.ConfigureFPGA(bitfile.encode('utf-8'))

    time.sleep(0.1)

    buf = "\x00" * 2048
    xem.ReadFromBlockPipeOut(0xA0, 4, buf)
    stream = unpack("%d" % (len(buf) / 4) + "I", buf)
    print "len_stream = %d" % len(stream)
    int_x = []
    for i in xrange(len(stream)):
        pre_x = stream[i] & 0xFFFFFFFF
        ## print "%0x" % pre_x
        real_x = ConvertType(pre_x, 'I', 'f')
        print "%.4f" % real_x
        int_x.append(real_x)

    
    plot(int_x)
    show()


