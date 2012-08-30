'''
Created on Aug 29, 2012

@author: C. Minos Niu
'''
import unittest
from core import WaveGen
from pylab import plot, show #@UnusedImport
from utils import importPluginModulesIn, findPluginCreator


class Test(unittest.TestCase):

    def testSeq(self):
        '''
        TEST length
        '''
        plugin_name = "Seq"
        loaded_plugins = importPluginModulesIn('/home/labuser/Code/nerf-py/WaveGen/plugin')
        plugin_creator = findPluginCreator(plugin_name, loaded_plugins)
        
        param = {'SAMPLING_RATE' : 1024, \
                 'TIME' :  [0.0, 0.06, 0.07,  0.24,  0.26,  0.43,  0.44,  0.5, 0.5,  0.56, 0.57,  0.74,  0.76,  0.93,  0.94,  1.0], \
                 'VALUE' : [0.0,  0.0,  1.0,  1.0,  -1.0,  -1.0,  0.0,  0.0,  0.0,  0.0,  -1.0,  -1.0,  1.0,  1.0,  0.0,  0.0]}
        T = 4.0
        selected_plugin = plugin_creator(**param)
        waveform = WaveGen()
        waveform.bind(selected_plugin)
        wave_dut = waveform.getAll(T = T)
        self.assertEqual(len(wave_dut), T * param['SAMPLING_RATE'], "Wrong length")

#    def testTri(self):
#        dut = WaveGen(category = "Seq")

    def testSine(self):
        '''
        TEST length, discontinuity, period etc.
        '''
        plugin_name = "Sine"
        loaded_plugins = importPluginModulesIn('/home/labuser/Code/nerf-py/WaveGen/plugin')
        plugin_creator = findPluginCreator(plugin_name, loaded_plugins)
        
        param = {'SAMPLING_RATE' : 1024, \
                 'BIAS' : 15.0, \
                 'F': 4.0, \
                 'AMP': 1.5}
        
        T = 4.0
        selected_plugin = plugin_creator(**param)
        waveform = WaveGen()
        waveform.bind(selected_plugin)
        
        sin_wave = waveform.getAll(T = T)
        self.assertEqual(len(sin_wave), T * param['SAMPLING_RATE'], "Wrong length")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()