import opalkelly_4_0_3.ok as ok
import time
import wx
from struct import pack, unpack
DIV1 = 100.0 
DIV2 = 10.0
DIV_ADDR = 0x20 
DEFAULT_FILE = "../local/projects/rsqrt_test/rsqrt_tester.bit"
NONLINEAR_ADDR = 0x22 
INV_ADDR = 0x24 

class CountersFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "FPGA Module Verifier (Python)", wx.DefaultPosition, wx.Size(400,300))

        ID_UPDATE_TIMER = wx.NewId()
        IDC_CNT1_RESET = wx.NewId()
        IDC_CNT1_DISABLE = wx.NewId()
        IDC_CNT2_RESET = wx.NewId()
        IDC_CNT2_UP = wx.NewId()
        IDC_CNT2_DOWN = wx.NewId()
        IDC_CNT2_AUTOCOUNT = wx.NewId()

        panel = wx.Panel(self, -1, wx.Point(0,0), wx.Size(400,170))

        # Setup Counter #1
        wx.StaticBox(panel, -1, "Counter #1 Controls", wx.Point(10,10), wx.Size(250,70))
        self.tglReset1 = wx.ToggleButton(panel, IDC_CNT1_RESET, "Reset", wx.Point(20,25), wx.Size(60,20))
        self.tglDisable1 = wx.ToggleButton(panel, IDC_CNT1_DISABLE, "Disable", wx.Point(90,25), wx.Size(60,20))

        self.txtCounter1 = wx.StaticText(panel, -1, "00", wx.Point(190,22))
        font = self.txtCounter1.GetFont()
        font.SetPointSize(30)
        self.txtCounter1.SetFont(font)
        self.txtLEDs = []
        for i in range(8):
            self.txtLEDs.append(wx.StaticText(panel, -1, "0", wx.Point(17+20*i,50)))
            str = "%d" % (7-i)
            wx.StaticText(panel, -1, str, wx.Point(17+20*i,65))
        

        # Setup Counter #2
        wx.StaticBox(panel, -1, "Counter #2 Controls", wx.Point(10,90), wx.Size(250,70))
        self.btnReset2 = wx.Button(panel, IDC_CNT2_RESET, "- Reset -", wx.Point(20,110), wx.Size(60,20))
        self.btnUp2 = wx.Button(panel, IDC_CNT2_UP, "- Up -", wx.Point(110,110), wx.Size(55,20))
        self.btnDown2 = wx.Button(panel, IDC_CNT2_DOWN, "- Down -", wx.Point(110,130), wx.Size(55,20))
        self.chkAutocount2 = wx.CheckBox(panel, IDC_CNT2_AUTOCOUNT, "Autocount.", wx.Point(20,135))        
        self.txtCounter2 = wx.StaticText(panel, -1, "00", wx.Point(190,102))
        font = self.txtCounter2.GetFont()
        font.SetPointSize(30)
        self.txtCounter2.SetFont(font)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnUpdateTimer)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnReset1, self.tglReset1)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnDisable1, self.tglDisable1)
        self.Bind(wx.EVT_BUTTON, self.OnReset2, self.btnReset2)
        self.Bind(wx.EVT_BUTTON, self.OnUp2, self.btnUp2)
        self.Bind(wx.EVT_BUTTON, self.OnDown2, self.btnDown2)
        self.Bind(wx.EVT_CHECKBOX, self.OnAutocount2, self.chkAutocount2)
        
        self.ConfigureXEM()
        self.timer.Start(50)

    def ConfigureXEM(self):
        dlg = wx.FileDialog(
                self, message="Open the Counters bitfile (counters.bit)", defaultDir="",
                defaultFile=DEFAULT_FILE, wildcard="*.bit", style=wx.OPEN | wx.CHANGE_DIR
                )
        
        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if (dlg.ShowModal() == wx.ID_OK):
            bitfile = dlg.GetPath()
            
            self.xem = ok.FrontPanel()
            self.xem.OpenBySerial("")
            if (self.xem.IsOpen()):
                self.xem.LoadDefaultPLLConfiguration()
                self.xem.ConfigureFPGA(bitfile.encode('utf-8'))
                return

        else:
            self.Close()

    def OnReset1(self, evt):
        if (True == self.tglReset1.GetValue()) :
            self.xem.SetWireInValue(0x00, 0xff, 0x01)
        else :
            self.xem.SetWireInValue(0x00, 0x00, 0x01)
        self.xem.UpdateWireIns()
        
    def OnDisable1(self, evt):
        if (True == self.tglDisable1.GetValue()) :
            self.xem.SetWireInValue(0x00, 0xff, 0x02)
        else :
            self.xem.SetWireInValue(0x00, 0x00, 0x02)
        self.xem.UpdateWireIns()
        
    def OnReset2(self, evt):
        self.xem.ActivateTriggerIn(0x40, 0);
        
    def OnUp2(self, evt):
        self.xem.ActivateTriggerIn(0x40, 1);

    def OnDown2(self, evt):
        self.xem.ActivateTriggerIn(0x40, 2);

    def OnAutocount2(self, evt):
        if (True == self.chkAutocount2.GetValue()) :
            self.xem.SetWireInValue(0x00, 0xff, 0x04)
        else :
            self.xem.SetWireInValue(0x00, 0x00, 0x04)
        self.xem.UpdateWireIns()

    def OnUpdateTimer(self, evt):
        bitVal = ConvertType(DIV1, fromType = 'f', toType = 'i')
        self.xem.SetWireInValue(0x00, bitVal >> 0, 0xffff)
        self.xem.SetWireInValue(0x01, bitVal >> 16, 0xffff)
        bitVal = ConvertType(DIV2, fromType = 'f', toType = 'i')
        self.xem.SetWireInValue(0x02, bitVal >> 0, 0xffff)
        self.xem.SetWireInValue(0x03, bitVal >> 16, 0xffff)
        self.xem.UpdateWireIns()
        ##self.xem.ActivateTriggerIn(0x50, 0)

        self.xem.UpdateWireOuts()
        ##self.xem.UpdateTriggerOuts()

        outValLo = self.xem.GetWireOutValue(DIV_ADDR) & 0xffff # length = 16-bit
        outValHi = self.xem.GetWireOutValue(DIV_ADDR + 0x01) & 0xffff
        outVal = ((outValHi << 16) + outValLo) & 0xFFFFFFFF
        invSqrt = ConvertType(outVal, fromType = 'i', toType = 'f')
##        print invSqrt
        str = "%.4f" % (invSqrt) ## "%02X" = unsigned hex integer, 2 digits
        self.txtCounter1.SetLabel(str)

def ConvertType(val, fromType, toType):
    return unpack(toType, pack(fromType, val))[0]

if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = CountersFrame(None)
    frame.Show(1)
    app.MainLoop()
