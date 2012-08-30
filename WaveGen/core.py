'''
Created on Aug 29, 2012

@author: C. Minos Niu
'''
import glob, imp
from os.path import join, basename, splitext
from scipy.signal import butter, filtfilt
from numpy import pi

def importPluginModulesIn(directory):
    modules = {}
    for path in glob.glob(join(directory,'[!_]*.py')): # list .py files not starting with '_'
        name, ext = splitext(basename(path))
        modules[name] = imp.load_source(name, path)
    return modules   

class WaveGen(object):
    
    
    def __init__(self, category, SAMPLING_RATE = 1024, FILT = '', param = {}):
        self.SAMPLING_RATE = SAMPLING_RATE
        
        loaded_plugins = importPluginModulesIn('/Users/minos_niu/Code/nerf-py/WaveGen/plugin')
        assert category in loaded_plugins, "No generator is called '%s' in ./plugin/!" % category
        constructor = loaded_plugins[category].Gentor
        
        # IoC happens here. constructor() do NOT have a hard dependency on Gentor()
        self.wave = constructor(self.SAMPLING_RATE, **param)
        
        if FILT:
            b, a = butter(N=3, Wn=2*pi*10/SAMPLING_RATE , btype='low', analog=0, output='ba')
            self.data = filtfilt(b=b, a=a, x=self.wave.data)
        else:
            self.data = self.wave.data
        
        self.getNext = self.gen().next # functional way of getting the next

    
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
    
    



