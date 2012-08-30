import sys
from SeqGenerator import SeqGenerator
from SineGenerator import SineGenerator

class Waveclass(object):
    
    
    def __init__(self, category):
        assert category in globals(), "No generator is called '%s'!" % category
        constructor = globals()[category] 
        self.wave = constructor()
    
    



