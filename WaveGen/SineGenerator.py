'''
Created on Aug 29, 2012

@author: C. Minos Niu
'''
import unittest
from scipy import *
from numpy import *

class SineGenerator(object):
    '''
    classdocs
    '''

    def __init__(self, F, BIAS, AMP, PHASE, T = 2.0, SAMPLING_RATE = 1024):
        self.F = F
        self.BIAS = BIAS
        self.AMP = AMP
        self.PHASE = PHASE
        self.T = T
        self.SAMPLING_RATE = SAMPLING_RATE
        dt = 1.0 / self.SAMPLING_RATE # Sampling interval in seconds
        periods = 1

        w = self.F * 2 * pi * dt
        self.max_n = int(periods * self.SAMPLING_RATE / self.F)
        n = linspace(0 , self.max_n, self.max_n)

        self.sine_list = self.AMP * sin(w * n + self.PHASE) + self.BIAS
        
        self.getNext = self.gen().next # functional way of getting the next

    
    def gen(self):
        '''
        Python iterator way to generate one period of waveform
        '''
        i = 0
        while (True):
            yield self.sine_list[i]
            i = (i + 1) % self.max_n
    
    def getAll(self):
        x = []
        max_n_T = int(self.T * self.SAMPLING_RATE)
        for i in xrange(max_n_T):
            x.append(self.getNext())
        return x

        
class Test(unittest.TestCase):

    def testGetNext(self):
    # GenSine by filling the whole list in once
        SAMPLING_RATE = 1024
        T = 1.5
        genx = SineGenerator(F = 1.0, BIAS = 0.0, AMP = 2.0*pi*1.0*0.1, PHASE = pi/2)
        sin_wave = []
        for i in xrange(int(T * SAMPLING_RATE)):
            sin_wave.append(genx.getNext())
        subplot(211)
        plot(sin_wave)
        show()
        self.assertEqual(len(sin_wave), T * SAMPLING_RATE, "Wrong length")

    def testGetAll(self):
    # GenSine by generating points one by one
        SAMPLING_RATE = 1024
        T = 4.0
        genx = SineGenerator(F = 1.0, BIAS = 0.0, AMP = 2.0*pi*1.0*0.1, PHASE = pi/2, T = T)
        sin_wave = genx.getAll()
        subplot(212)
        plot(sin_wave)
        show()
        self.assertEqual(len(sin_wave), T * SAMPLING_RATE, "Wrong length")

    
if __name__ == '__main__':
    from pylab import plot, show, subplot
    unittest.main() 