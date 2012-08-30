'''
Created on Aug 29, 2012

@author: C. Minos Niu
'''
from scipy.signal import butter, filtfilt
from numpy import pi
from plugin import WavePlugin

class WaveGen(object):
    
    
    def __init__(self, SAMPLING_RATE = 1024, FILT = '', param = {}):
        self.SAMPLING_RATE = SAMPLING_RATE
        
        # IoC happens here. constructor() do NOT have a hard dependency on Gentor()
#        self.wave = constructor(self.SAMPLING_RATE, **param)
        self.wave = None
        self.data = []
        
#        if FILT:
#            b, a = butter(N=3, Wn=2*pi*10/SAMPLING_RATE , btype='low', analog=0, output='ba')
#            self.data = filtfilt(b=b, a=a, x=self.wave.data)
#        else:
#            self.data = self.wave.data
        
        self.getNext = self.gen().next # functional way of getting the next

    def bind(self, wave): # explicitly depends on "WavePlugin wave"
        assert isinstance(wave, WavePlugin), "Received a wave generator that's NOT a WavePlugin!"
        # Dependency injection
        self.wave = wave
        self.data = self.wave.data
    
    def gen(self):
        '''
        Using the Python Generator as a concise way to circulate through the waveform
        '''
        i = 0
        len_data = len(self.data)
        while (True):
            yield self.data[i]
            i = (i + 1) % len_data
    
    def getAll(self, T = 1.0):
        x = []
        max_n_T = int(T * self.SAMPLING_RATE)
        for i in xrange(max_n_T):
            x.append(self.getNext())
        return x
    




