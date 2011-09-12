from math import exp
#from decimal import *

import math
import time
import struct, binascii
import os
from generate_stretch import gen_waveform
from generate_spikes import spike_train
from generate_active_force import s, active_state


"""
Test and generate the tension curve in Eq.3 of Shadmehr and S.P.Wise
Eric W. Sohn (wonjoons at usc dot edu)

"""

# change x to induce change in T. (in Tension-length curve)

# Eq. 3 in Shedmehr, derivative of Tension in the muscle
def d_force(T_0, x1, x2, A=0.0):
    """ Take state variables
        Return derivatives
    """
    x0 = 1.0       # initial length of x, arbitrary
    Kse = 136.0     # g / cm
    Kpe = 75.0      # g / cm
    b = 50.0        # g * s / c
#    A =   # arbitrary A. 
    
    rate_change_x = x2   # slope
    if x1 > x0:
        dT_0 = Kse / b * (Kpe * (x1 - x0) + b * rate_change_x - (1 + Kpe/Kse)*T_0 + A)   # passive + active = total
    else:
        dT_0 = Kse / b * (b * rate_change_x - (1 + Kpe/Kse) * T_0 + A)
#    dT_0 = Kse / b * (- (1 + Kpe/Kse)*T_0 +  A)   # active part only...
  
    return dT_0
  

if __name__ == '__main__':
    from numpy import pi, array
    from pylab import show, plot, grid
    from scipy.signal import butter, filtfilt
    
#    from numpy import *
    

    SAMPLING_RATE = 1024
    spikes = spike_train(firing_rate =20.0, SAMPLING_RATE = SAMPLING_RATE)
    spike_i1 = spike_i2 = 0.0
    h_i1 = h_i2 = 0.0
    T_i = T_i1 = 0.0
    x, dx = gen_waveform(L2 = 1.011, SAMPLING_RATE = SAMPLING_RATE)


    A_list = []
    T_list = []
    for spike_i, x_i, dx_i in zip(spikes, x, dx):
        h_i = active_state(spike_i1, spike_i2, h_i1, h_i2)
        A_list.append(h_i *s(x_i) )
        spike_i1, spike_i2 = spike_i * SAMPLING_RATE, spike_i1
        h_i1, h_i2 = h_i, h_i1

       # dT_i = d_force(T_i, x_i, dx_i, A = h_i*s(x_i))   # total force (passive + active)
        dT_i = d_force(T_i, 1.0, 0.0, A = h_i*s(x_i))   # total force (passive + active)
        T_i = T_i1 + dT_i * (1.0/SAMPLING_RATE)
        T_list.append(T_i)
        T_i1 = T_i
#    subplot(211)
#    plot(T_list)
#    grid('True')

    ## curve smoothing (averaging)
    b, a = butter(N=2, Wn=2*pi*1/SAMPLING_RATE , btype='low', analog=0, output='ba')
    T_list_filtered= filtfilt(b=b, a=a, x=array(T_list))
    plot(T_list,'r', T_list_filtered, 'g')
    grid('True')
    show()
    
    print "len_x = %d" % len(T_list)




