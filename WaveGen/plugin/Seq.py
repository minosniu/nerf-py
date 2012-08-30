'''
Created on Aug 29, 2012

@author: C. Minos Niu
'''
import unittest
from scipy import *
from numpy import *
from plugin import WavePlugin

class Gentor(WavePlugin):
    '''
    classdocs
    '''

    def __init__(self, SAMPLING_RATE, TIME = [0.0, 0.1, 0.9, 1.0], VALUE = [0.0, 0.0, 200.0, 200.0], FILT = 'Butter'):
        dt = 1.0 / SAMPLING_RATE # Sampling interval in seconds
        
        len_x = int(TIME[-1] * SAMPLING_RATE) + 1
        x = []
        N = [int(t / dt) for t in TIME]
        
        for n1, l1, n2, l2 in zip(N[0:-1], VALUE[0:-1], N[1:], VALUE[1:]):
            n_seg = n2 - n1;
            x = x + ([l1 + i * (l2 - l1) / n_seg for i in xrange(n_seg)])
        
        # MUST provide self.data
        self.data = x

        
class Test(unittest.TestCase):
    
    def testMultPeriods(self):
        '''
        Test the logic of sin wave, t versus n etc.
        '''
        from pylab import plot, show
        x = Gentor(1024, TIME =  [0.0, 0.06, 0.07,  0.24,  0.26,  0.43,  0.44,  0.5, 0.5,  0.56, 0.57,  0.74,  0.76,  0.93,  0.94,  1.0],\
            VALUE = [0.0,  0.0,  1.0,  1.0,  -1.0,  -1.0,  0.0,  0.0,  0.0,  0.0,  -1.0,  -1.0,  1.0,  1.0,  0.0,  0.0], FILT = 'Butter')
        generator = Gentor(1024)
        plot(generator.data)
        show()

    
if __name__ == '__main__':

    unittest.main() 

