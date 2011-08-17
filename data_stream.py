"""
Sirish Nandyala
@sirishn

Opal Kelly acquisition and visualization system using Enthought Chaco and Traits

Two frames are opened: one has the plot and allows configuration of
various plot properties, and one which simulates controls for the hardware
device from which the data is being acquired; in this case, it is a mockup
random number generator whose mean and standard deviation can be controlled
by the user.
"""


from generate_sin import gen, gen4hz
from struct import pack, unpack
import os.path
import opalkelly_4_0_3.ok as ok

# Major library imports
import random
import wx


from numpy import arange, array, hstack, random

# Enthought imports
from enthought.traits.api import Array, Bool, Callable, Enum, Float, HasTraits, \
                                 Instance, Int, Trait, Range
from enthought.traits.ui.api import Group, HGroup, Item, View, spring, Handler
from enthought.pyface.timer.api import Timer

# Chaco imports
from enthought.chaco.chaco_plot_editor import ChacoPlotItem

PIPE_IN_ADDR = 0x80
BIT_FILE = "../nerfb/projects/spindle_neuron/spindle_neuron_xem6010.bit"            
class Model:
    """Opal Kelly FPGA
    """
    def __init__(self):
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
        self.pll.SetPLLParameters(0, outputRate, 48,  True)#multiply up to 400mhz
        self.pll.SetOutputSource(0, ok.PLL22393.ClkSrc_PLL0_0)  #clk1
        finalRate = 1
        self.pll.SetOutputDivider(0, outputRate / finalRate) 
        self.pll.SetOutputEnable(0, True)
        self.xem.SetPLL22393Configuration(self.pll)
        ## self.xem.SetEepromPLL22393Configuration(self.pll)
        self.xem.ConfigureFPGA(bitfile.encode('utf-8'))
        print(bitfile.encode('utf-8'))
        
    def SendPipe(self, pipeInData):
        """ Send byte stream to OpalKelly board
        """
        # print pipeInData

        buf = "" 
        for x in pipeInData:
            #print x
            buf += pack('<f', x) # convert float_x to a byte string, '<' = little endian

        if self.xem.WriteToBlockPipeIn(PIPE_IN_ADDR, 4, buf) == len(buf):
            print "%d bytes sent via PipeIn!" % len(buf)
        else:
            print "SendPipe failed!"
            
    def ReadFPGA(self, getAddr):

        """ getAddr = 0x20 -- 0x3F (maximal in OkHost)
        """
        self.xem.UpdateWireOuts()
        ## Read 1 byte output from FPGA
        outValLo = self.xem.GetWireOutValue(getAddr) & 0xffff # length = 16-bit
        outValHi = self.xem.GetWireOutValue(getAddr + 0x01) & 0xffff
        outVal = ((outValHi << 16) + outValLo) & 0xFFFFFFFF
        if (getAddr != 0x24):
            outVal = ConvertType(outVal, 'I', 'f')
        else:
            outVal = ConvertType(outVal, 'I', 'i')
        ##if (getAddr == EMG1_ADDR) | (getAddr == EMG2_ADDR):
        ##if getAddr == (EMG1_ADDR):
        ##    outVal = ConvertType(outVal, 'I', 'i')
        ## elif getAddr == UNDERFLOW_ADDR:
        ##     outVal = ConvertType(outVal, 'I', 'i')
        ##else:
        ##    outVal = ConvertType(outVal, 'I', 'f')
        ## if getAddr == DATA_OUT_ADDR[1]:
        ##      print "%2.2f" % outVal, 
        
        ## Python default int is unsigned, use pack/unpack to
        ## convert into signed
##        outVal = ConvertType(outVal, fromType = 'I', toType = 'i')
        ## if (outVal & 0x80):
        ##     outVal = -0x80 + outVal
            ## outVal = -(~(outVal - 0x1) & 0xFF)
        return outVal

class Viewer(HasTraits):
    """ This class just contains the two data arrays that will be updated
    by the Controller.  The visualization/editor for this class is a 
    Chaco plot.
    """
    
    index = Array
    
    data = Array
    data2 = Array

    plot_type = Enum("line", "scatter")
    
    # This "view" attribute defines how an instance of this class will
    # be displayed when .edit_traits() is called on it.  (See MyApp.OnInit()
    # below.)
    view = View(    ChacoPlotItem("index", "data",
                               type_trait="plot_type",
                               resizable=False,
                               x_label="Time",
                               y_label="Signal",
                               color="blue",
                               bgcolor="white",
                               border_visible=True,
                               border_width=1,
                               padding_bg_color="lightgray",
                               width=800,
                               height=380,
                               show_label=False),
                    ChacoPlotItem("index", "data2",
                               type_trait="plot_type",
                               resizable=False,
                               x_label="Time",
                               y_label="Signal",
                               color="blue",
                               bgcolor="white",
                               border_visible=True,
                               border_width=1,
                               padding_bg_color="lightgray",
                               width=800,
                               height=380,
                               show_label=False),
                                HGroup(spring, Item("plot_type", style='custom'), spring),
                                resizable = True,
                                buttons = ["OK"],
                                width=800, height=850) 


class Controller(HasTraits):
    nerfModel = Model() 
    pipeInData = gen()
    nerfModel.SendPipe(pipeInData)

    # A reference to the plot viewer object
    viewer = Instance(Viewer)
    
    # Some parameters controller the random signal that will be generated
    distribution_type = Enum("1 Hz", "4 Hz")
    clk_divider = Range(0,1000)
    def _clk_divider_default(self): return 1000
    nerfModel.xem.SetWireInValue(0x02, 1000)
    nerfModel.xem.SetWireInValue(0x00, 0)
    nerfModel.xem.UpdateWireIns()
    nerfModel.xem.ActivateTriggerIn(0x50, 7)
	
    # The max number of data points to accumulate and show in the plot
    max_num_points = Int(100)
    
    # The number of data points we have received; we need to keep track of
    # this in order to generate the correct x axis data series.
    num_ticks = Int(0)
    
    # private reference to the random number generator.  this syntax
    # just means that self._generator should be initialized to
    # random.normal, which is a random number function, and in the future
    # it can be set to any callable object.
    _generator = Trait(random.normal, Callable)
    
    view = View(Item('clk_divider'),
                Group('distribution_type', 
                      'max_num_points',
                      orientation="vertical"),
                      buttons=["OK", "Cancel"])
    
    def timer_tick(self, *args):
        """ Callback function that should get called based on a wx timer
        tick.  This will generate a new random datapoint and set it on
        the .data array of our viewer object.
        """
        # Generate a new number and increment the tick count
        #new_val = self._generator(self.mean, self.stddev)
        new_val = self.nerfModel.ReadFPGA(0x22)
        new_val2 = self.nerfModel.ReadFPGA(0x20)
        self.num_ticks += 1
        
        # grab the existing data, truncate it, and append the new point.
        # This isn't the most efficient thing in the world but it works.
        cur_data = self.viewer.data
        new_data = hstack((cur_data[-self.max_num_points+1:], [new_val]))
        #new_index = arange(self.num_ticks - len(new_data) + 1, self.num_ticks+0.01)
        new_index = arange(-(0.1*(len(new_data))), 0.0 , 0.1)
        
        self.viewer.index = new_index
        self.viewer.data = new_data
        cur_data = self.viewer.data2
        new_data = hstack((cur_data[-self.max_num_points+1:], [new_val2]))
        self.viewer.data2 = new_data 
        return

    def _clk_divider_changed(self):
        #print 'clk divider at %s' % self.clk_divider 
        self.nerfModel.xem.SetWireInValue(0x02, self.clk_divider)
        self.nerfModel.xem.UpdateWireIns()
        self.nerfModel.xem.ActivateTriggerIn(0x50, 7)

    def _distribution_type_changed(self):
        # This listens for a change in the type of distribution to use.
        if self.distribution_type == "1 Hz":
        	pipeInData = gen()
    		self.nerfModel.SendPipe(pipeInData)
        else:
            pipeInData = gen4hz()
            self.nerfModel.SendPipe(pipeInData)
            print self.clk_divider


# wxApp used when this file is run from the command line.

class MyApp(wx.PySimpleApp):
    
    def OnInit(self, *args, **kw):
        viewer = Viewer()
        controller = Controller(viewer = viewer)
        
        # Pop up the windows for the two objects
        viewer.edit_traits()
        controller.edit_traits()
        
        # Set up the timer and start it up
        self.setup_timer(controller)
        return True


    def setup_timer(self, controller):
        # Create a new WX timer
        timerId = wx.NewId()
        self.timer = wx.Timer(self, timerId)
        
        # Register a callback with the timer event
        self.Bind(wx.EVT_TIMER, controller.timer_tick, id=timerId)
        
        # Start up the timer!  We have to tell it how many milliseconds
        # to wait between timer events.  For now we will hardcode it
        # to be 100 ms, so we get 10 points per second.
        self.timer.Start(25.0, wx.TIMER_CONTINUOUS)
        return

def ConvertType(val, fromType, toType):
    return unpack(toType, pack(fromType, val))[0]

# This is called when this example is to be run in a standalone mode.
if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()    

# EOF
