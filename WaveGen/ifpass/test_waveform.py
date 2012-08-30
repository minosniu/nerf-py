'''
Created on Aug 29, 2012

@author: C. Minos Niu
'''
import unittest
import WaveGen
from pylab import plot, show #@UnusedImport
from WaveGen.utils import importPluginModulesIn, findPluginCreator
import os

def foo(inval):
    assert True, "passed"


class Test(unittest.TestCase):

    def testSeq(self):
        '''
        TEST length
        '''
        plugin_path = os.path.dirname(WaveGen.__file__) + '/plugins'
        plugin_name = "Seq"
        
        available_plugins = importPluginModulesIn(plugin_path)
        plugin_creator = findPluginCreator(plugin_name, available_plugins)
        
        param = {'SAMPLING_RATE' : 1024, \
                 'TIME' :  [0.0, 0.06, 0.07,  0.24,  0.26,  0.43,  0.44,  0.5, 0.5,  0.56, 0.57,  0.74,  0.76,  0.93,  0.94,  1.0], \
                 'VALUE' : [0.0,  0.0,  1.0,  1.0,  -1.0,  -1.0,  0.0,  0.0,  0.0,  0.0,  -1.0,  -1.0,  1.0,  1.0,  0.0,  0.0]}
        T = 4.0
        selected_plugin = plugin_creator(**param)
        some_wave = WaveGen.SomeWave()
        some_wave.bind(selected_plugin)
        wave_dut = some_wave.getAll(T = T)
        self.assertEqual(len(wave_dut), T * param['SAMPLING_RATE'], "Wrong length")
        plot(wave_dut)
        show()

#    def testTri(self):
#        dut = WaveGen(category = "Seq")

    def testSine(self):
        '''
        TEST length, discontinuity, period etc.
        '''
        plugin_path = os.path.dirname(WaveGen.__file__) + '/plugins'
        plugin_name = "Sine"
        
        available_plugins = importPluginModulesIn(plugin_path)
        plugin_creator = findPluginCreator(plugin_name, available_plugins)
        
        param = {'SAMPLING_RATE' : 1024, \
                 'BIAS' : 15.0, \
                 'F': 4.0, \
                 'AMP': 1.5}
        
        T = 4.0
        selected_plugin = plugin_creator(**param)
        waveform = WaveGen.SomeWave()
        waveform.bind(selected_plugin)
        
        sin_wave = waveform.getAll(T = T)
        self.assertEqual(len(sin_wave), T * param['SAMPLING_RATE'], "Wrong length")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()