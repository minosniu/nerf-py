'''
Created on Aug 29, 2012

@author: C. Minos Niu
'''
from scipy.signal import butter, filtfilt
from numpy import pi
from WaveGen.plugin import PluginProtocol

class SomeWave(object):
    
    
    def __init__(self, SAMPLING_RATE = 1024, FILT = '', param = {}):
        self.SAMPLING_RATE = SAMPLING_RATE
        
        # IoC happens here. constructor() do NOT have a hard dependency on Gentor()
#        self.wave = constructor(self.SAMPLING_RATE, **param)
        self.wave = None
        
#        if FILT:
#            b, a = butter(N=3, Wn=2*pi*10/SAMPLING_RATE , btype='low', analog=0, output='ba')
#            self.data = filtfilt(b=b, a=a, x=self.wave.data)
#        else:
#            self.data = self.wave.data
        
        self.getNext = self.gen().next # functional way of getting the next

    def bind(self, wave_from_plugin): # explicitly depends on "WavePlugin wave"
        assert len(wave_from_plugin.data) > 0, "Waveform contains 0 points, check the plugin."
        # Dependency injection
        self.wave = wave_from_plugin
    
    def gen(self):
        '''
        Using the Python Generator as a concise way to circulate through the waveform
        '''
        i = 0
        len_data = len(self.wave.data)
        while (True):
            yield self.wave.data[i]
            i = (i + 1) % len_data
    
    def getAll(self, T = 1.0):
        x = []
        max_n_T = int(T * self.SAMPLING_RATE)
        for i in xrange(max_n_T):
            x.append(self.getNext())
        return x
    




