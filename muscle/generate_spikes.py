from numpy import *
from pylab import *
from math import exp
from decimal import *
import math
import struct, binascii
import os

import matplotlib.pyplot 
import matplotlib.pyplot  as pyplot
from scipy import * 
from scipy.integrate import quad

def spike_train(T=1.0, firing_rate=5, SAMPLING_RATE=1024):
#    for t_i in t:   
#        temp = (s if (t_i % (firing_interval*R) == 0) else 0)
#        dtrain.append(temp)
    max_n = int(T * SAMPLING_RATE)
    n = linspace(0 , max_n, max_n)
    dtrain = []
    for i in xrange(len(n)):   
        spike = (1 if ((i-1) % int(1.0/firing_rate*SAMPLING_RATE) == 0) else 0)
        dtrain.append(spike)
    return dtrain


if __name__ == '__main__':
    from pylab import *
    spikes = spike_train(firing_rate = 20)
    plot(spikes)
    show()
    print "len_x = %d" % len(spikes)
