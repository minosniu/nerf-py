import time
import wx
import OpalKelly as ok
import math
from struct import pack, unpack
DEFAULT_FILE = "../local/projects/rsqrt_test/rsqrt_tester.bit"
DATA_EVT_X = 0
NUM_CHANNEL = 1 # Number of channels
DISPLAY_SCALING = [1.0]
CSS_ADDR = 0x20 
DATA_OUT_ADDR = [CSS_ADDR]
t0 = time.clock()

def loop_test(self):
    cnt = 0
    bitfile = DEFAULT_FILE
    xem = ok.FrontPanel()
    xem.OpenBySerial("")
    if (xem.IsOpen()):
        xem.LoadDefaultPLLConfiguration()
        pll = ok.PLL22393()
        pll.SetReference(48.0)        #base clock frequency
        baseRate = 100
        pll.SetPLLParameters(0, baseRate, 48,  True)            #multiply up to 400mhz
        pll.SetOutputSource(0, ok.PLL22393.ClkSrc_PLL0_0)  #clk1 
        clkRate = 100                                #mhz; 200 is fastest
        pll.SetOutputDivider(0, baseRate / clkRate)        #div4 = 100mhz; div128 = 4mhz
        pll.SetOutputEnable(0, True)
        pll.SetOutputSource(1, ok.PLL22393.ClkSrc_PLL0_0)  #clk2
        pll.SetOutputDivider(1, baseRate / clkRate)        #div4 = 100 mhz
        pll.SetOutputEnable(1, True)
        xem.SetPLL22393Configuration(pll)
        xem.SetEepromPLL22393Configuration(pll)
        xem.ConfigureFPGA(bitfile.encode('utf-8'))
    else:
        print "OpalKelly board NOT found!"
        return 0


    ix = ConvertType(0.00001234, 'f', 'I')
    while ix < (ConvertType(12.34, 'f', 'I') + 0x0020ffff):
        real_x = ConvertType(ix, 'I', 'f')
        ## Send ix to FPGA
        bitVal = ix 
        bitValLo = bitVal & 0xffff
        bitValHi = (bitVal >> 16) & 0xffff
        xem.SetWireInValue(0x00, bitValLo, 0xffff)
        xem.SetWireInValue(0x01, bitValHi, 0xffff)
        xem.UpdateWireIns()

        newVal = [0.0 for xx in range(NUM_CHANNEL)]
        for i in xrange(NUM_CHANNEL):
            xem.UpdateWireOuts()
            ## Read 1 byte output from FPGA
            outValLo = xem.GetWireOutValue(DATA_OUT_ADDR[i]) & 0xffff # length = 16-bit
            outValHi = xem.GetWireOutValue(DATA_OUT_ADDR[i]+ 0x01) & 0xffff
            outVal = ((outValHi << 16) + outValLo) & 0xFFFFFFFF
            outVal = ConvertType(outVal, 'i', 'f')
            newVal[i] = outVal

            if real_x < 0.0:
                print "x = %.4f" % real_x
                continue
            real_fx = 1 / math.sqrt(real_x)
            err = abs((newVal[i] - real_fx) / real_fx)
            if err > 0.0001:
                print "x = %.4f" % ConvertType(ix, 'i', 'f'),
                print "rsqrt = %.4f" % newVal[i],
                print "pyrsq = %.4f" % (1 / math.sqrt(real_x)),
                print "diff = %.4f" % (newVal[i] - 1 / math.sqrt(real_x)),
                print "err_ratio = %.4f" % err 
        ix += 0x10000
        cnt += 1
    print "Time = %.4f" % (time.clock() - t0)
    print "Cases tested = %d" % cnt


def ConvertType(val, fromType, toType):
    return unpack(toType, pack(fromType, val))[0]

def SendPara(newVal, trigEvent):
    if trigEvent == DATA_EVT_X:
        bitVal = newVal
        bitValLo = bitVal & 0xffff
        bitValHi = (bitVal >> 16) & 0xffff
        self.xem.SetWireInValue(0x00, bitValLo, 0xffff)
        self.xem.SetWireInValue(0x01, bitValHi, 0xffff)
        self.xem.UpdateWireIns()
        ##self.xem.ActivateTriggerIn(0x50, DATA_EVT_X)
    elif trigEvent == DATA_EVT_CLKRATE:
        self.pll.SetOutputDivider(0, newVal)        #div4 = 100 mhz
        self.pll.SetOutputDivider(1, newVal)        #div4 = 100 mhz
        self.xem.SetPLL22393Configuration(self.pll)
        self.xem.SetEepromPLL22393Configuration(self.pll)


if __name__ == "__main__":
    app = wx.App(False)
    loop_test(app)

