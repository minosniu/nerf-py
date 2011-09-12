"""
This demo demonstrates how to draw a dynamic mpl (matplotlib) 
plot in a wxPython application.

It allows "live" plotting as well as manual zooming to specific
regions.

Both X and Y axes allow "auto" or "manual" settings. For Y, auto
mode sets the scaling of the graph to see all the data points.
For X, auto mode makes the graph "follow" the data. Set it X min
to manual 0 to always see the whole data from the beginning.

Note: press Enter in the 'manual' text box to make a new value 
affect the plot.

C. Minos Niu (minos.niu@sangerlab.net)
License: this code is in the public domain
Last modified: 10.18.2010
"""
import os
import pprint
import random
import sys
import wx
import ok

# The recommended way to use wx with mpl is with the WXAgg
# backend. 
#
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab


class DataGen(object):
    """ A silly class that generates pseudo-random data for
        display in the plot.
    """
    def __init__(self, init=50):
        self.data = self.init = init
        
    def next(self):
        self._recalc_data()
        return self.data
    
    def _recalc_data(self):
        self.data = 0xffff


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


class FpNumBox(wx.Panel):
    """ A static box with two text boxes. Allows to switch between an
        automatic mode and a manual mode with an associated value.
    """
    def __init__(self, parent, ID, label, initval):
        wx.Panel.__init__(self, parent, ID)
        
        self.value = initval
        
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        
        self.manual_text = wx.TextCtrl(self, -1, 
            size=(35,-1),
            value=str(initval),
            style=wx.TE_PROCESS_ENTER)
        
        
        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)
        
        sizer.Add(manual_box, 0, wx.ALL, 10)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
    
    
    def manual_value(self):
        return self.value


class GraphFrame(wx.Frame):
    """ The main frame of the application
    """
    title = 'NERF: FPGA motoneuron simulation'
    
    def __init__(self):
        wx.Frame.__init__(self, None, -1, self.title)
        
        self.datagen = DataGen()
        self.data = [self.datagen.next()]
        self.paused = False
        
        self.Ia_bias = 0
        self.M1_bias = 0 
        self.LLR = 0 
        self.pos1 = 0 
        self.vel1 = 0 
        self.gamma = 0 

        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()
        
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)        
        
        self.ConfigureXEM()
        
        self.redraw_timer.Start(50)
        

    def create_menu(self):
        self.menubar = wx.MenuBar()
        
        menu_file = wx.Menu()
        m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
                
        self.menubar.Append(menu_file, "&File")
        self.SetMenuBar(self.menubar)

    def create_main_panel(self):
        self.panel = wx.Panel(self)

        self.init_plot()
        self.canvas = FigCanvas(self.panel, -1, self.fig)

        self.xmin_control = BoundControlBox(self.panel, -1, "X min", 0)
        self.xmax_control = BoundControlBox(self.panel, -1, "X max", 50)
        self.ymin_control = BoundControlBox(self.panel, -1, "Y min", 0)
        self.ymax_control = BoundControlBox(self.panel, -1, "Y max", 100)
        self.a_base_control = FpNumBox(self.panel, -1, "A base", 0)
        self.a_expo_control = FpNumBox(self.panel, -1, "A expo", 50)
        self.b_base_control = FpNumBox(self.panel, -1, "B base", 0)
        self.b_expo_control = FpNumBox(self.panel, -1, "B expo", 100)
        
        self.pause_button = wx.Button(self.panel, -1, "Pause")
        self.Bind(wx.EVT_BUTTON, self.on_pause_button, self.pause_button)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_pause_button, self.pause_button)
        
        self.cb_grid = wx.CheckBox(self.panel, -1, 
            "Show Grid",
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
        self.cb_grid.SetValue(False)
        
        self.cb_xlab = wx.CheckBox(self.panel, -1, 
            "Show X labels",
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)        
        self.cb_xlab.SetValue(False)
        
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.pause_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(20)
        self.hbox1.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.xmin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.xmax_control, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.ymin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.ymax_control, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.a_base_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.a_expo_control, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.b_base_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.b_expo_control, border=5, flag=wx.ALL)
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)        
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)
    
    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def init_plot(self):
        self.dpi = 200
        self.fig = Figure((3.0, 3.0), dpi=self.dpi)

        self.axes = self.fig.add_subplot(311)
        self.axes.set_axis_bgcolor('gray')
        self.axes.set_title('EMG data', size=12)
        
        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)

        # plot the data as a line series, and save the reference 
        # to the plotted line series
        #
        self.plot_data = self.axes.plot(
            self.data, 
            linewidth=0.8,
            color=(1, 1, 0),
            )[0]

    def draw_plot(self):
        """ Redraws the plot
        """
        # when xmin is on auto, it "follows" xmax to produce a 
        # sliding window effect. therefore, xmin is assigned after
        # xmax.
        #
        if self.xmax_control.is_auto():
            xmax = len(self.data) if len(self.data) > 50 else 50
        else:
            xmax = int(self.xmax_control.manual_value())
            
        if self.xmin_control.is_auto():            
            xmin = xmax - 500
        else:
            xmin = int(self.xmin_control.manual_value())

        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        # 
        # note that it's easy to change this scheme to the 
        # minimal/maximal value in the current display, and not
        # the whole data set.
        # 
        if self.ymin_control.is_auto():
            ymin = round(min(self.data), 0) - 10
        else:
            ymin = int(self.ymin_control.manual_value())
        
        if self.ymax_control.is_auto():
            ymax = round(max(self.data), 0) + 10
        else:
            ymax = int(self.ymax_control.manual_value())

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)
        
        # anecdote: axes.grid assumes b=True if any other flag is
        # given even if b is set to False.
        # so just passing the flag into the first statement won't
        # work.
        #
        if self.cb_grid.IsChecked():
            self.axes.grid(True, color='gray')
        else:
            self.axes.grid(False)

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly 
        # iterate, and setp already handles this.
        #  
        pylab.setp(self.axes.get_xticklabels(), 
            visible=self.cb_xlab.IsChecked())
        
        self.plot_data.set_xdata(np.arange(len(self.data)))
        self.plot_data.set_ydata(np.array(self.data))
        
        self.canvas.draw()
    
    def on_pause_button(self, event):
        self.xem.ActivateTriggerIn(0x50, 15)
        self.paused = not self.paused
        
        self.xem.SetWireInValue(0x00, 0x41451, 0xffff)
        self.xem.SetWireInValue(0x01, 0x70a4, 0xffff)
        self.xem.SetWireInValue(0x02, 0x3f80, 0xffff)
        self.xem.SetWireInValue(0x03, 0x0000, 0xffff)
        self.xem.UpdateWireIns()
        self.xem.UpdateWireIns()
        self.xem.ActivateTriggerIn(0x50, 0)
    
    def on_update_pause_button(self, event):
        
        label = "Resume" if self.paused else "Pause"
        self.pause_button.SetLabel(label)
    
    def on_cb_grid(self, event):
        self.draw_plot()
    
    def on_cb_xlab(self, event):
        self.draw_plot()
    
    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self, 
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)
    
    def on_redraw_timer(self, event):
        # if paused do not add data, but still redraw the plot
        # (to respond to scale modifications, grid change, etc.)
        #
        if not self.paused:
            #self.data.append(self.datagen.next())
            self.xem.UpdateWireOuts()
            ## self.xem.UpdateTriggerOuts()
            ## needs to be Signed short
            prod1 = self.xem.GetWireOutValue(0x20) & 0xffff;
            print hex(prod1)
            prod2 = self.xem.GetWireOutValue(0x21) & 0xffff;
            print hex(prod2)
            self.data.append(0)
            ## self.data.append(self.M1_bias)

        
        self.draw_plot()
    
    def on_exit(self, event):
        self.Destroy()
    
    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER, 
            self.on_flash_status_off, 
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)
    
    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')

    def ConfigureXEM(self):
        dlg = wx.FileDialog(
                self, message="Open the Counters bitfile (counters.bit)", defaultDir="",
                defaultFile="/home/minosniu/fpgatest/branch-prune/fpu_ok/fp_arith.bit", wildcard="*.bit", style=wx.OPEN | wx.CHANGE_DIR
                )
        
        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if (dlg.ShowModal() == wx.ID_OK):
            bitfile = dlg.GetPath()
            
        self.xem = ok.FrontPanel()
        self.xem.OpenBySerial("")
        if (self.xem.IsOpen()):
            self.xem.LoadDefaultPLLConfiguration()
            self.pll = ok.PLL22393()
            self.pll.SetReference(48.0)        #base clock frequency
            self.baseRate = 400
            self.pll.SetPLLParameters(0, self.baseRate, 48,  True)            #multiply up to 400mhz
            self.pll.SetOutputSource(0, ok.PLL22393.ClkSrc_PLL0_0)  #clk1 
            self.clkRate = 200                                #mhz; 200 is fastest
            self.pll.SetOutputDivider(0, self.baseRate / self.clkRate)        #div4 = 100mhz; div128 = 4mhz
            self.pll.SetOutputEnable(0, True)
            self.pll.SetOutputSource(1, ok.PLL22393.ClkSrc_PLL0_0)  #clk2
            self.pll.SetOutputDivider(1, 2)        #div4 = 100 mhz
            self.pll.SetOutputEnable(1, True)
            self.xem.SetPLL22393Configuration(self.pll)
            self.xem.SetEepromPLL22393Configuration(self.pll)           
            self.xem.ConfigureFPGA(bitfile.encode('utf-8'))

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
            
        else:
            self.Close()
     

            
if __name__ == '__main__':
    app = wx.PySimpleApp()
    app.frame = GraphFrame()
    app.frame.Show()
    app.MainLoop()
