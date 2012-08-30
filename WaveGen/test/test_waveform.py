'''
Created on Aug 29, 2012

@author: C. Minos Niu
'''
import unittest
from core import WaveGen
from pylab import plot, show


class Test(unittest.TestCase):

    def testSeq(self):
        '''
        TEST length
        '''
        param = {'TIME' :  [0.0, 0.06, 0.07,  0.24,  0.26,  0.43,  0.44,  0.5, 0.5,  0.56, 0.57,  0.74,  0.76,  0.93,  0.94,  1.0], \
                 'VALUE' : [0.0,  0.0,  1.0,  1.0,  -1.0,  -1.0,  0.0,  0.0,  0.0,  0.0,  -1.0,  -1.0,  1.0,  1.0,  0.0,  0.0]}
        SAMPLING_RATE = 1024
        T = 4.0
        genx = WaveGen("Seq", SAMPLING_RATE, 'FilterWithButter', param)
        sin_wave = genx.getAll(T = T)
        self.assertEqual(len(sin_wave), T * SAMPLING_RATE, "Wrong length")
        plot(sin_wave)
        show()

#    def testTri(self):
#        dut = WaveGen(category = "Seq")

    def testSine(self):
        '''
        TEST length, discontinuity, period etc.
        '''
        param = {'BIAS' : 15.0, \
                 'F': 4.0, \
                 'AMP': 1.5}
        SAMPLING_RATE = 1024
        T = 4.0
        genx = WaveGen("Sine", SAMPLING_RATE, param)
        sin_wave = genx.getAll(T = T)
        self.assertEqual(len(sin_wave), T * SAMPLING_RATE, "Wrong length")
        plot(sin_wave)
        show()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()