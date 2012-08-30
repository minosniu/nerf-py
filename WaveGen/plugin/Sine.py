'''
Created on Aug 29, 2012

@author: C. Minos Niu
'''
import unittest
from scipy import *
from numpy import *

class Gentor(object):
    '''
    classdocs
    '''

    def __init__(self, SAMPLING_RATE, F = 1.0, BIAS = 0.0, AMP = 5.0, PHASE = 0.0):
        self.F = F
        self.BIAS = BIAS
        self.AMP = AMP
        self.PHASE = PHASE
        self.SAMPLING_RATE = SAMPLING_RATE
        dt = 1.0 / self.SAMPLING_RATE # Sampling interval in seconds
        periods = 1

        w = self.F * 2 * pi * dt
        self.max_n = int(periods * self.SAMPLING_RATE / self.F)
        n = linspace(0 , self.max_n, self.max_n)

        # MUST provide self.data
        self.data = self.AMP * sin(w * n + self.PHASE) + self.BIAS

        
class Test(unittest.TestCase):
    
    def testMultPeriods(self):
        '''
        Test the logic of sin wave, t versus n etc.
        '''
        from pylab import plot, show
        generator = Gentor(1024)
        plot(generator.data)
        show()

    
if __name__ == '__main__':

    unittest.main() 