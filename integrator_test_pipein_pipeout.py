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
import wx
import wx.lib.plot as plot
import thread, time
from struct import pack, unpack
from scipy.io import savemat, loadmat
##from wx.lib.pubsub import Publisher as pub
import opalkelly_4_0_3.ok as ok
from generate_sin import gen

# The recommended way to use wx with mpl is with the WXAgg backend.
#
## import matplotlib
## matplotlib.use('WXAgg')
## from matplotlib.figure import Figure
## from matplotlib.backends.backend_wxagg import \
##     FigureCanvasWxAgg as FigCanvas, \
##     NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np

VIEWER_REFRESH_RATE = 20 # in ms, This the T for calculating digital freq
NUM_CHANNEL = 2 # Number of channels
X_ADDR = 0x20 
INT_X_ADDR = 0x22 
PIPE_OUT_ADDR = 0xA0
PIPE_IN_ADDR = 0x80
## II1_ADDR = 0x22 
## VAR2_ADDR = 0x24 
## VAR3_ADDR = 0x26 
## VAR4_ADDR = 0x28 
## VAR5_ADDR = 0x2A 
## VAR6_ADDR = 0x30 
## VAR7_ADDR = 0x32 

DATA_EVT_CLKRATE = 7
##DISPLAY_SCALING = [0.1, 500, 500, 10, 10, 10, 5, 5]
DISPLAY_SCALING = [10, 125.7] 
DATA_OUT_ADDR = [X_ADDR, INT_X_ADDR]
ZERO_DATA = [0.0 for ix in xrange(NUM_CHANNEL)]
BIT_FILE = "../clean_nerf/projects/pipe_in_wave_2048/pipe_in_wave_2048_xem3010.bit"

class Model:
    """ Once each data point is refreshed, it publishes a message called "WANT MONEY"
    """
    def __init__(self):
        self.myMoney = 0
        self.ConfigureXEM()

    def ConfigureXEM(self):
        ## dlg = wx.FileDialog( self, message="Open the Counters bitfile (counters.bit)",
        ##         defaultDir="", defaultFile=BIT_FILE, wildcard="*.bit",
        ##         style=wx.OPEN | wx.CHANGE_DIR )
        
        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        ## if (dlg.ShowModal() == wx.ID_OK):
        ##     bitfile = dlg.GetPath()
        ## defaultDir="../local/projects/fp_spindle_test/"
        ## defaultFile="fp_spindle_test.bit"
        ## defaultFile="counters_fp_muscle.bit"

        bitfile = BIT_FILE
        assert os.path.exists(bitfile.encode('utf-8')), ".bit file NOT found!"
            
        self.xem = ok.FrontPanel()
        self.xem.OpenBySerial("")
        assert self.xem.IsOpen(), "OpalKelly board NOT found!"

        self.xem.LoadDefaultPLLConfiguration()

        self.pll = ok.PLL22393()
        self.pll.SetReference(48.0)        #base clock frequency
        outputRate = 48 # in MHz
        self.pll.SetPLLParameters(0, outputRate, 48,  True)            #multiply up to 400mhz
        self.pll.SetOutputSource(0, ok.PLL22393.ClkSrc_PLL0_0)  #clk1
        finalRate = 1
        self.pll.SetOutputDivider(0, outputRate / finalRate) 
        self.pll.SetOutputEnable(0, True)
        self.xem.SetPLL22393Configuration(self.pll)
        ## self.xem.SetEepromPLL22393Configuration(self.pll)
        self.xem.ConfigureFPGA(bitfile.encode('utf-8'))
        print(bitfile.encode('utf-8'))

    def ReadFPGA(self, buf_len):
        """ Read byte stream with length buf_len
        """

        buf = "\x00" * buf_len # how many bytes
        self.xem.ReadFromBlockPipeOut(PIPE_OUT_ADDR, 4, buf)
        #self.xem.ReadFromPipeOut(PIPE_OUT_ADDR, buf)
        stream = unpack("%d" % (len(buf) / 4) + "I", buf) # from byte stream to 32-bit float stream
        print "len_stream = %d" % len(stream)
        outVal = []
        for i in xrange(len(stream)):
            pre_x = stream[i] & 0xFFFFFFFF
            real_x = ConvertType(pre_x, 'I', 'f')
            print "%.4f" % real_x
            outVal.append(real_x)

        return outVal

    def SendReset(self, resetValue):
        if (resetValue) :
            self.xem.SetWireInValue(0x00, 0x01, 0xff)
            print resetValue,
        else :
            self.xem.SetWireInValue(0x00, 0x00, 0xff)
        self.xem.UpdateWireIns()

    def SendPipe(self, pipeInData):
        """ Send byte stream to OpalKelly board
        """
        # print pipeInData

        buf = "" 
        for x in pipeInData:
            ##print x
            buf += pack('<f', x) # convert float_x to a byte string, '<' = little endian

        if self.xem.WriteToBlockPipeIn(PIPE_IN_ADDR, 4, buf) == len(buf):
            print "%d bytes sent via PipeIn!" % len(buf)
        else:
            print "SendPipe failed!"

    def SendPara(self, trigEvent, newVal, newVal2 = None):
        if trigEvent == DATA_EVT_CLKRATE:
            ## self.pll.SetOutputDivider(0, int(newVal))        #div4 = 100 mhz
            ## self.pll.SetOutputDivider(1, int(newVal))        #div4 = 100 mhz
            ## self.xem.SetPLL22393Configuration(self.pll)
            ## self.xem.SetEepromPLL22393Configuration(self.pll)
            self.xem.SetWireInValue(0x01, int(newVal), 0xffff)
            self.xem.UpdateWireIns();
            self.xem.ActivateTriggerIn(0x50, 7)

class View(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="Main View", size = (900, 500))
        self.paused = False
        self.data = ZERO_DATA
        self.xPos = 0
        self.dispRect = self.GetClientRect()

        self.CreateViewMenu()
        self.CreateViewStatusBar()
        self.CreateViewPanel()

        self.redrawTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnRedrawTimer, self.redrawTimer)        
        self.redrawTimer.Start(VIEWER_REFRESH_RATE)

    def OnRedrawTimer(self, event):
        # if paused do not add data, but still redraw the plot
        # (to respond to scale modifications, grid change, etc.)
        #
        ## pub.sendMessage("WANT MONEY", 0.0)
        pass 
        

    def CreateViewMenu(self):
        self.menubar = wx.MenuBar()
        
        menuFile = wx.Menu()
        m_expt = menuFile.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
        ## self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menuFile.AppendSeparator()
        m_exit = menuFile.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.OnExit, m_exit)
                
        self.menubar.Append(menuFile, "&File")
        self.SetMenuBar(self.menubar)

    def CreateViewPanel(self):
        self.panel = wx.Panel(self)
        ## self.panel.Bind(wx.EVT_PAINT, self.OnPaint)
        ## self.pause_button = wx.Button(self.panel, -1, "Pause")
        ## self.Bind(wx.EVT_BUTTON, self.OnPauseButton, self.pause_button)
        ## self.Bind(wx.EVT_UPDATE_UI, self.OnUpdatePauseButton, self.pause_button)
        
    
    def CreateViewStatusBar(self):
        self.statusbar = self.CreateStatusBar()

    def OnExit(self, event):
        self.Destroy()


    ## def DrawPlot(self, newVal):
    ##     """ Redraws the plot
    ##     """
    ##     ##dc = wx.PaintDC(self.panel)
    ##     self.dispRect = self.GetClientRect()
    ##     winScale = self.dispRect.GetHeight() * 4 / 5
    ##     if self.xPos == 0:
    ##         self.dc.Clear()
    ##     self.dc.SetPen(wx.Pen('blue', 1))

    ##     for ix in xrange(NUM_CHANNEL):
    ##         self.dc.DrawLine(self.xPos + 60, winScale / 8 *(1 + ix) -
    ##                     self.data[ix] * DISPLAY_SCALING[ix],\
    ##                     self.xPos + 61, winScale / 8 *(1 + ix) -
    ##                     newVal[ix] * DISPLAY_SCALING[ix])
    ##     self.data = newVal
    ##     self.xPos += 1
    ##     if self.xPos > 300:
    ##         self.xPos = 0


class ChangerView(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, title="On-chip parameters",\
                          pos = wx.Point(300, 700))
        self.panel = wx.Panel(self)

        ## sizer = wx.BoxSizer(wx.VERTICAL)
        ## self.add = wx.Button(self, label="Add Money")
        ## self.remove = wx.Button(self, label="Remove Money")
        ## sizer.Add(self.add, 0, wx.EXPAND | wx.ALL)
        ## sizer.Add(self.remove, 0, wx.EXPAND | wx.ALL)
        ## self.SetSizer(sizer)

        self.sliderClk = wx.Slider(self.panel, -1, 0, 0, 100, (10, 10), (250, 50),
                                  wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.tglReset = wx.ToggleButton(self.panel, -1, "Reset", wx.Point(20,25), wx.Size(50,30))
        self.feedData = wx.Button(self.panel, -1, "Feed", wx.Point(20,25), wx.Size(50,30))
        self.runTest = wx.Button(self.panel, -1, "Run", wx.Point(20,25), wx.Size(50,30))
        self.plotResult = wx.Button(self.panel, -1, "Plot", wx.Point(20,25), wx.Size(50,30))

#        self.label1.SetBackgroundColour((self.Red1, self.Green1, self.Blue1))

        self.hbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox.Add(self.sliderClk, border=5, flag=wx.ALL|wx.EXPAND)
        self.hbox.Add(self.tglReset, border=5, flag=wx.ALL|wx.EXPAND)
        self.hbox.Add(self.feedData, border=5, flag=wx.ALL|wx.EXPAND)
        self.hbox.Add(self.runTest, border=5, flag=wx.ALL|wx.EXPAND)
        self.hbox.Add(self.plotResult, border=5, flag=wx.ALL|wx.EXPAND)
        #self.hbox.Add(self.tglReset,flag=wx.ALIGN_CENTER, border=5)

        self.hbox.Fit(self)
        self.panel.SetSizer(self.hbox)

class Controller:
    def __init__(self, app):
        self.nerfModel = Model()

        #set up the first frame which displays the current Model value
        self.dispView = View(None)
        ## thread.start_new_thread(self.nerfModel.ReadFPGA, ("Refreshing data", 0.05, 0x20))
        ## self.dispView.SetMoney(self.nerfModel.myMoney)

        #set up the second frame which allows the user to modify the Model's value
        self.ctrlView = ChangerView(self.dispView)
        ## self.ctrlView.add.Bind(wx.EVT_BUTTON, self.AddMoney)
        ## self.ctrlView.remove.Bind(wx.EVT_BUTTON, self.RemoveMoney)

        ## self.ctrlView.slider1.Bind(wx.EVT_SLIDER, self.UpdateIa)
        self.ctrlView.Bind(wx.EVT_SLIDER, self.SendClkRate, self.ctrlView.sliderClk)
        self.ctrlView.Bind(wx.EVT_TOGGLEBUTTON, self.OnReset, self.ctrlView.tglReset)
        self.ctrlView.Bind(wx.EVT_BUTTON, self.OnFeedData, self.ctrlView.feedData)
        self.ctrlView.Bind(wx.EVT_BUTTON, self.OnRunTest, self.ctrlView.runTest)
        self.ctrlView.Bind(wx.EVT_BUTTON, self.OnPlotResult, self.ctrlView.plotResult)

        ##pub.subscribe(self.WantMoney, "WANT MONEY")

        self.dispView.Show()
        self.ctrlView.Show()
        self.data = []

    def SendClkRate(self, evt):
        newClkRate = self.ctrlView.sliderClk.GetValue() / 10
        self.nerfModel.SendPara(newClkRate, DATA_EVT_CLKRATE)

    def OnReset(self, evt):
        newReset = self.ctrlView.tglReset.GetValue()
        self.nerfModel.SendReset(newReset)

    def OnFeedData(self, evt):
        pipeInData = gen()
        self.nerfModel.SendPipe(pipeInData)

    def OnRunTest(self, evt):
        self.data = self.data + self.nerfModel.ReadFPGA(1024 * 4 )

    def OnPlotResult(self, evt):
        import pylab
        pylab.plot(self.data)
        pylab.show()

def ConvertType(val, fromType, toType):
    return unpack(toType, pack(fromType, val))[0]

if __name__ == "__main__":
    app = wx.App(False)
    controller = Controller(app)
    app.MainLoop()

