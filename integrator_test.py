#!/usr/bin/env python

"""
Test the fp_spindle_bag1.v, wrapper fp_spindle_test.
Gamma_dyn > 0
Gamma_sta > 0
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
from wx.lib.pubsub import Publisher as pub
import opalkelly_4_0_3.ok as ok

# The recommended way to use wx with mpl is with the WXAgg backend.
#
## import matplotlib
## matplotlib.use('WXAgg')
## from matplotlib.figure import Figure
## from matplotlib.backends.backend_wxagg import \
##     FigureCanvasWxAgg as FigCanvas, \
##     NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np

VIEWER_REFRESH_RATE = 40 # in ms
NUM_CHANNEL = 2 # Number of channels
IA1_ADDR = 0x20 
II1_ADDR = 0x22 
VAR2_ADDR = 0x24 
VAR3_ADDR = 0x26 
VAR4_ADDR = 0x28 
VAR5_ADDR = 0x2A 
VAR6_ADDR = 0x30 
VAR7_ADDR = 0x32 

DATA_EVT_IA = 0
DATA_EVT_M1 = 1
DATA_EVT_POS_FLEX = 3
DATA_EVT_VEL_FLEX = 4
DATA_EVT_GAMMA_STA = 5
DATA_EVT_GAMMA_DYN = 6
DATA_EVT_CLKRATE = 7
DATA_EVT_TRQ = 10
##DISPLAY_SCALING = [0.1, 500, 500, 10, 10, 10, 5, 5]
DISPLAY_SCALING = [0.001, 0.00001, 10, 0.0000, 0.0001, 0, 0.000, 0.001]
##DISPLAY_SCALING = [0, 0.01, 0, 5, 5, 3, 3, 0.5]
## DATA_OUT_ADDR = [EMG2_ADDR, TRQ1_ADDR, TRQ2_ADDR, \
##                  POS1_ADDR, POS2_ADDR, VEL1_ADDR, VEL2_ADDR, ACC_ADDR]
DATA_OUT_ADDR = [IA1_ADDR, II1_ADDR, VAR2_ADDR, VAR3_ADDR, \
                 VAR4_ADDR, VAR5_ADDR, VAR6_ADDR, VAR7_ADDR]
ZERO_DATA = [0.0 for ix in xrange(NUM_CHANNEL)]

class Model:
    """ Once each data point is refreshed, it publishes a message called "WANT MONEY"
    """
    def __init__(self):
        self.myMoney = 0
        self.ConfigureXEM()

    def ConfigureXEM(self):
        ## dlg = wx.FileDialog( self, message="Open the Counters
        ##         bitfile (counters.bit)",
        ##         defaultDir="/home/minosniu/Downloads/counter2/counter2",
        ##         defaultFile="counters.bit", wildcard="*.bit",
        ##         style=wx.OPEN | wx.CHANGE_DIR )
        
        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        ## if (dlg.ShowModal() == wx.ID_OK):
        ##     bitfile = dlg.GetPath()
        defaultDir="../local/projects/fp_spindle_test/"
        defaultFile="fp_spindle_test.bit"
        ## defaultFile="counters_fp_muscle.bit"

        bitfile = defaultDir + defaultFile
        assert os.path.exists(bitfile.encode('utf-8')), ".bit file NOT found!"
            
        self.xem = ok.FrontPanel()
        self.xem.OpenBySerial("")
        assert self.xem.IsOpen(), "OpalKelly board NOT found!"

        self.xem.LoadDefaultPLLConfiguration()

        self.pll = ok.PLL22393()
        self.pll.SetReference(48.0)        #base clock frequency
        self.baseRate = 100
        self.pll.SetPLLParameters(0, self.baseRate, 48,  True)            #multiply up to 400mhz
        self.pll.SetOutputSource(0, ok.PLL22393.ClkSrc_PLL0_0)  #clk1 
        self.clkRate = 20                                #mhz; 200 is fastest
        self.pll.SetOutputDivider(0, self.baseRate / self.clkRate)        #div4 = 100mhz; div128 = 4mhz
        self.pll.SetOutputEnable(0, True)
        self.pll.SetOutputSource(1, ok.PLL22393.ClkSrc_PLL0_0)  #clk2
        self.pll.SetOutputDivider(1, self.baseRate / self.clkRate)        #div4 = 100 mhz
        self.pll.SetOutputEnable(1, True)
        self.xem.SetPLL22393Configuration(self.pll)
        self.xem.SetEepromPLL22393Configuration(self.pll)
        self.xem.ConfigureFPGA(bitfile.encode('utf-8'))
        print(bitfile.encode('utf-8'))

        ## delta_t is the real time percounter sample.
        self.updateRate = self.clkRate / 4
        self.delayCount = 128
        self.delta_t = (0.001 * self.updateRate) / (self.delayCount)
        self.xem.SetWireInValue(0x01, 1, 0xffff)
        self.xem.UpdateWireIns()
        self.xem.ActivateTriggerIn(0x50, 7)

        ## set the learning rate for stdp (????)
        self.gamma_plus = 7
        self.gamma_minus = 7
        self.xem.SetWireInValue(0x01, self.gamma_plus, 0xffff)  ## set the software delay
        self.xem.SetWireInValue(0x02, self.gamma_minus, 0xffff)  ## set the software delay
        self.xem.UpdateWireIns()
        self.xem.ActivateTriggerIn(0x50, 9)  ## tell the chip there is new data

    def ReadFPGA(self, getAddr):

        """ getAddr = 0x20 -- 0x3F (maximal in OkHost)
        """
        self.xem.UpdateWireOuts()
        ## Read 1 byte output from FPGA
        outValLo = self.xem.GetWireOutValue(getAddr) & 0xffff # length = 16-bit
        outValHi = self.xem.GetWireOutValue(getAddr + 0x01) & 0xffff
        outVal = ((outValHi << 16) + outValLo) & 0xFFFFFFFF
        outVal = ConvertType(outVal, 'I', 'f')
        ## if getAddr == DATA_OUT_ADDR[0]:
        ##     print "%2.4f" % outVal, 
        ##     ##print "%d" % (outValLo), 
        
        ## Python default int is unsigned, use pack/unpack to
        ## convert into signed
##        outVal = ConvertType(outVal, fromType = 'I', toType = 'i')
        ## if (outVal & 0x80):
        ##     outVal = -0x80 + outVal
            ## outVal = -(~(outVal - 0x1) & 0xFF)
        return outVal

    def SendReset(self, resetValue):
        if (resetValue) :
            self.xem.SetWireInValue(0x00, 0x01, 0xff)
            print resetValue,
        else :
            self.xem.SetWireInValue(0x00, 0x00, 0xff)
        self.xem.UpdateWireIns()

    def SendPara(self, newVal, trigEvent):
        if trigEvent == DATA_EVT_IA:
            bitVal = ConvertType(newVal, fromType = 'f', toType = 'i')
            bitVal = bitVal << 2
            self.xem.SetWireInValue(0x01, bitVal >> 0, 0xffff)
            self.xem.SetWireInValue(0x02, bitVal >> 16, 0xffff)
            self.xem.SetWireInValue(0x03, bitVal >> 0, 0xffff)
            self.xem.SetWireInValue(0x04, bitVal >> 16, 0xffff)
            self.xem.UpdateWireIns()
            self.xem.ActivateTriggerIn(0x50, DATA_EVT_IA)
        elif trigEvent == DATA_EVT_M1:
            ##bitVal = newVal << 2
            bitVal = newVal
            self.xem.SetWireInValue(0x01, 0 >> 0, 0xffff)
            self.xem.SetWireInValue(0x02, 0 >> 16, 0xffff)
            self.xem.SetWireInValue(0x03, bitVal >> 0, 0xffff)
            self.xem.SetWireInValue(0x04, bitVal >> 16, 0xffff)
            self.xem.UpdateWireIns()
            self.xem.ActivateTriggerIn(0x50, DATA_EVT_M1)
        elif trigEvent == DATA_EVT_POS_FLEX:
            bitVal = ConvertType(newVal, fromType = 'f', toType = 'I')
            bitValLo = bitVal & 0xffff
            bitValHi = (bitVal >> 16) & 0xffff
            self.xem.SetWireInValue(0x01, bitValLo, 0xffff)
            self.xem.SetWireInValue(0x02, bitValHi, 0xffff)
            self.xem.SetWireInValue(0x03, bitValLo, 0xffff)
            self.xem.SetWireInValue(0x04, bitValHi, 0xffff)
            self.xem.UpdateWireIns()
            self.xem.ActivateTriggerIn(0x50, DATA_EVT_POS_FLEX)
        elif trigEvent == DATA_EVT_VEL_FLEX:
            bitVal = ConvertType(newVal, fromType = 'f', toType = 'I')
            bitValLo = bitVal & 0xffff
            bitValHi = (bitVal >> 16) & 0xffff
            self.xem.SetWireInValue(0x01, bitValLo, 0xffff)
            self.xem.SetWireInValue(0x02, bitValHi, 0xffff)
            self.xem.SetWireInValue(0x03, bitValLo, 0xffff)
            self.xem.SetWireInValue(0x04, bitValHi, 0xffff)
            self.xem.UpdateWireIns()
            self.xem.ActivateTriggerIn(0x50, DATA_EVT_VEL_FLEX)
        elif trigEvent == DATA_EVT_GAMMA_STA:
            bitVal = ConvertType(newVal, fromType = 'f', toType = 'I')
            bitValLo = bitVal & 0xffff
            bitValHi = (bitVal >> 16) & 0xffff
            self.xem.SetWireInValue(0x01, bitValLo, 0xffff)
            self.xem.SetWireInValue(0x02, bitValHi, 0xffff)
            self.xem.UpdateWireIns()
            self.xem.ActivateTriggerIn(0x50, DATA_EVT_GAMMA_STA)
        elif trigEvent == DATA_EVT_GAMMA_DYN:
            bitVal = ConvertType(newVal, fromType = 'f', toType = 'I')
            bitValLo = bitVal & 0xffff
            bitValHi = (bitVal >> 16) & 0xffff
            self.xem.SetWireInValue(0x01, bitValLo, 0xffff)
            self.xem.SetWireInValue(0x02, bitValHi, 0xffff)
            self.xem.UpdateWireIns()
            self.xem.ActivateTriggerIn(0x50, DATA_EVT_GAMMA_DYN)
        elif trigEvent == DATA_EVT_CLKRATE:
            self.pll.SetOutputDivider(0, newVal)        #div4 = 100 mhz
            self.pll.SetOutputDivider(1, newVal)        #div4 = 100 mhz
            self.xem.SetPLL22393Configuration(self.pll)
            self.xem.SetEepromPLL22393Configuration(self.pll)
            ## self.xem.SetWireInValue(0x01, newVal, 0xffff)
            ## self.xem.UpdateWireIns();
            ## self.xem.ActivateTriggerIn(0x50, 7)
        elif trigEvent == 8:
            pass
        elif trigEvent == 9:
            pass
        elif trigEvent == DATA_EVT_TRQ:
            ## NOTE: here newVal should be a floating point number
            bitVal = ConvertType(newVal, fromType = 'f', toType = 'I')
            bitValLo = bitVal & 0xffff
            bitValHi = (bitVal >> 16) & 0xffff
            self.xem.SetWireInValue(0x01, bitValLo, 0xffff)
            self.xem.SetWireInValue(0x02, bitValHi, 0xffff)
            self.xem.UpdateWireIns()
            self.xem.ActivateTriggerIn(0x50, DATA_EVT_TRQ)

class View(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="Main View",\
                          size = (900, 500))
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
        pub.sendMessage("WANT MONEY", 0.0)
        

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
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)
        ## self.pause_button = wx.Button(self.panel, -1, "Pause")
        ## self.Bind(wx.EVT_BUTTON, self.OnPauseButton, self.pause_button)
        ## self.Bind(wx.EVT_UPDATE_UI, self.OnUpdatePauseButton, self.pause_button)
        
    
    def CreateViewStatusBar(self):
        self.statusbar = self.CreateStatusBar()

    def OnExit(self, event):
        self.Destroy()

    def OnPauseButton(self, event):
        ## self.xem.ActivateTriggerIn(0x50, 15)
        self.paused = not self.paused
        
    def OnUpdatePauseButton(self, event):
        label = "Resume" if self.paused else "Pause"
        self.pause_button.SetLabel(label)

    def OnPaint(self, event = None, newVal = ZERO_DATA):

        """ aksjdf
        """
        if ~hasattr(self, 'dc'):
            self.dc = wx.PaintDC(self.panel)

        self.dispRect = self.GetClientRect()
        winScale = self.dispRect.GetHeight() * 4 / 5
        self.dc.DrawText("Pos", 1, winScale / 5)
        self.dc.DrawText("Vel", 0, winScale / 5)
        self.dc.DrawText("Flex", 0, 2*winScale / 5)
        self.dc.DrawText("Ext", 0, 3*winScale / 5)

        self.dc.DrawText("S1.f", 0, winScale - 126)
        self.dc.DrawText("M1.f", 0, winScale - 94)
        self.dc.DrawText("alpha.f", 0, winScale - 62)
        self.dc.DrawText("Ia.f", 0, winScale - 30)

        self.dc.DrawText("S1.e", 0, winScale + 2)
        self.dc.DrawText("M1.e", 0, winScale + 34)
        self.dc.DrawText("alpha.e", 0, winScale + 66)
        self.dc.DrawText("Ia.e", 0, winScale + 98)

        self.dispRect = self.GetClientRect()
        winScale = self.dispRect.GetHeight() * 4 / 5
        if self.xPos == 0:
            self.dc.Clear()
        self.dc.SetPen(wx.Pen('blue', 1))

        for ix in xrange(NUM_CHANNEL):
            self.dc.DrawLine(self.xPos + 60, winScale / 8 *(1 + ix) -
                        self.data[ix] * DISPLAY_SCALING[ix],\
                        self.xPos + 61, winScale / 8 *(1 + ix) -
                        newVal[ix] * DISPLAY_SCALING[ix])
        self.data = newVal
        self.xPos += 1
        if self.xPos > 300:
            self.xPos = 0


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


class BoundControlBox(wx.Panel):
    """ A static box with a couple of radio buttons and a text
        box. Allows to switch between an automatic mode and a 
        manual mode with an associated value.
    """
    def __init__(self, parent, ID, label, initval):
        wx.Panel.__init__(self, parent, ID)
        
        self.value = initval
        
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        
        self.radio_auto = wx.RadioButton(self, -1, 
            label="Auto", style=wx.RB_GROUP)
        self.radio_manual = wx.RadioButton(self, -1,
            label="Manual")
        self.manual_text = wx.TextCtrl(self, -1, 
            size=(35,-1),
            value=str(initval),
            style=wx.TE_PROCESS_ENTER)
        
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)
        
        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)
        
        sizer.Add(self.radio_auto, 0, wx.ALL, 10)
        sizer.Add(manual_box, 0, wx.ALL, 10)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
    
    def on_update_manual_text(self, event):
        self.manual_text.Enable(self.radio_manual.GetValue())
    
    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()
    
    def is_auto(self):
        return self.radio_auto.GetValue()
        
    def manual_value(self):
        return self.value


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

        self.slider1 = wx.Slider(self.panel, -1, 0, 0, 100, (10, 10), (250, 50),
                                  wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.slider2 = wx.Slider(self.panel, -1, 50, 0, 100, (10, 10), (250, 50),
                                  wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.slider3 = wx.Slider(self.panel, -1, 0, 0, 100, (10, 10), (250, 50),
                                  wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.slider4 = wx.Slider(self.panel, -1, 50, 0, 100, (10, 10), (250, 50),
                                  wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.slider5 = wx.Slider(self.panel, -1, 0, 0, 100, (10, 10), (250, 50),
                                  wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.slider6 = wx.Slider(self.panel, -1, 0, 0, 100, (10, 10), (250, 50),
                                  wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.slider7 = wx.Slider(self.panel, -1, 0, 0, 100, (10, 10), (250, 50),
                                  wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.slider8 = wx.Slider(self.panel, -1, 50, 0, 100, (10, 10), (250, 50),
                                  wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.tglReset = wx.ToggleButton(self.panel, -1, "Reset", wx.Point(20,25), wx.Size(60,20))

        self.label1 = wx.StaticText(self.panel, -1, "Ia_bias")
        self.label2 = wx.StaticText(self.panel, -1, "M1")
        self.label3 = wx.StaticText(self.panel, -1, "Pos")
        self.label4 = wx.StaticText(self.panel, -1, "Vel")
        self.label5 = wx.StaticText(self.panel, -1, "GammaStatic")
        self.label6 = wx.StaticText(self.panel, -1, "GammaDynamic")
        self.label7 = wx.StaticText(self.panel, -1, "ClockRate")
        self.label8 = wx.StaticText(self.panel, -1, "ExtTrq")
#        self.label1.SetBackgroundColour((self.Red1, self.Green1, self.Blue1))

        self.hbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox.Add(self.slider1, border=5, flag=wx.ALL|wx.EXPAND)
        self.hbox.Add(self.label1,flag=wx.ALIGN_CENTER, border=5)
        self.hbox.Add(self.slider2, border=5, flag=wx.ALL|wx.EXPAND)
        self.hbox.Add(self.label2,flag=wx.ALIGN_CENTER, border=5)
        self.hbox.Add(self.slider3, border=5, flag=wx.ALL|wx.EXPAND)
        self.hbox.Add(self.label3,flag=wx.ALIGN_CENTER, border=5)
        self.hbox.Add(self.slider4, border=5, flag=wx.ALL|wx.EXPAND)
        self.hbox.Add(self.label4,flag=wx.ALIGN_CENTER, border=5)
        self.hbox.Add(self.slider5, border=5, flag=wx.ALL|wx.EXPAND)
        self.hbox.Add(self.label5,flag=wx.ALIGN_CENTER, border=5)
        self.hbox.Add(self.slider6, border=5, flag=wx.ALL|wx.EXPAND)
        self.hbox.Add(self.label6,flag=wx.ALIGN_CENTER, border=5)
        self.hbox.Add(self.slider7, border=5, flag=wx.ALL|wx.EXPAND)
        self.hbox.Add(self.label7,flag=wx.ALIGN_CENTER, border=5)
        self.hbox.Add(self.slider8, border=5, flag=wx.ALL|wx.EXPAND)
        self.hbox.Add(self.label8,flag=wx.ALIGN_CENTER, border=5)

        self.hbox.Add(self.tglReset, border=5, flag=wx.ALL|wx.EXPAND)
        self.hbox.Add(self.tglReset,flag=wx.ALIGN_CENTER, border=5)

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
        self.ctrlView.slider2.Bind(wx.EVT_SLIDER, self.SendMI)
        self.ctrlView.slider3.Bind(wx.EVT_SLIDER, self.SendPosFlex)
        self.ctrlView.slider4.Bind(wx.EVT_SLIDER, self.SendVelFlex)
        self.ctrlView.slider5.Bind(wx.EVT_SLIDER, self.SendGammaSta)
        self.ctrlView.slider6.Bind(wx.EVT_SLIDER, self.SendGammaDyn)
        self.ctrlView.slider7.Bind(wx.EVT_SLIDER, self.SendClkRate)
        self.ctrlView.slider8.Bind(wx.EVT_SLIDER, self.SendExtTrq)
       ## self.ctrlView.tglReset.Bind(wx.EVT_TOGGLEBUTTON, self.OnReset)
        self.ctrlView.Bind(wx.EVT_TOGGLEBUTTON, self.OnReset, self.ctrlView.tglReset)

        pub.subscribe(self.WantMoney, "WANT MONEY")

        self.dispView.Show()
        self.ctrlView.Show()

    ## def UpdateIa(self, event):
    ##     newIa = 2048 * self.ctrlView.slider1.GetValue() / 100
    ##     self.fpgaData.xem.SetWireInValue(0x01, self.Ia_bias, 0xffff)
    ##     self.fpgaData.xem.SetWireInValue(0x02, self.Ia_bias, 0xffff)
    ##     self.fpgaData.xem.UpdateWireIns()
    ##     self.fpgaData.xem.ActivateTriggerIn(0x50, 0)

    def SendMI(self, event):
        newMI = 2048 * self.ctrlView.slider2.GetValue() / 100
        self.nerfModel.SendPara(newMI, DATA_EVT_M1)

    def SendPosFlex(self, event):
        ## newExtTrq = (self.ctrlView.slider8.GetValue() - 50)
        newPosFlex = 1.0 + (self.ctrlView.slider3.GetValue() - 50) / 10.0 
        self.nerfModel.SendPara(newPosFlex, DATA_EVT_POS_FLEX)

    def SendVelFlex(self, event):
        ## newExtTrq = (self.ctrlView.slider8.GetValue() - 50)
        newVelFlex = (self.ctrlView.slider4.GetValue() - 50) / 10.0 
        self.nerfModel.SendPara(newVelFlex, DATA_EVT_VEL_FLEX)

    def SendGammaSta(self, event):
        ## newExtTrq = (self.ctrlView.slider8.GetValue() - 50)
        newGammaSta = self.ctrlView.slider5.GetValue() 
        self.nerfModel.SendPara(newGammaSta, DATA_EVT_GAMMA_STA)

    def SendGammaDyn(self, event):
        ## newExtTrq = (self.ctrlView.slider8.GetValue() - 50)
        newGammaDyn = self.ctrlView.slider6.GetValue() * 5 
        self.nerfModel.SendPara(newGammaDyn, DATA_EVT_GAMMA_DYN)

    def SendClkRate(self, event):
        newClkRate = self.ctrlView.slider7.GetValue() / 5 + 1
        self.nerfModel.SendPara(newClkRate, DATA_EVT_CLKRATE)

    def SendExtTrq(self, event):
        ## newExtTrq = (self.ctrlView.slider8.GetValue() - 50)
        newExtTrq = (self.ctrlView.slider8.GetValue() - 50) * 0.1 
        self.nerfModel.SendPara(newExtTrq, DATA_EVT_TRQ)

    def OnReset(self, evt):
        newReset = self.ctrlView.tglReset.GetValue()
        self.nerfModel.SendReset(newReset)


    def WantMoney(self, message):
        """
        This method is the handler for "WANT MONEY" messages,
        which pubsub will call as messages are sent from the model.

        We already know the topic is "WANT MONEY", but if we
        didn't, message.topic would tell us.
        """
        ## self.dispView.SetMoney(message.data)
        newVal = [0.0 for ix in range(NUM_CHANNEL)]
        for i in xrange(NUM_CHANNEL):
            newVal[i] = self.nerfModel.ReadFPGA(DATA_OUT_ADDR[i])
##            newVal[i] = self.nerfModel.ReadFPGA16Bit(0x23)
#            hi = ConvertType(hi, 'i', 'h')
        self.dispView.OnPaint(newVal = newVal)

def ConvertType(val, fromType, toType):
    return unpack(toType, pack(fromType, val))[0]

if __name__ == "__main__":
    app = wx.App(False)
    controller = Controller(app)
    app.MainLoop()

