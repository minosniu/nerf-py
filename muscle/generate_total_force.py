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
    x0 = 1       # initial length of x, arbitrary
    Kse = 136     # g / cm
    Kpe = 75      # g / cm
    b = 50        # g * s / c
#    A =   # arbitrary A. 
    
    rate_change_x = x2   # slope
    dT_0 = Kse / b * (Kpe * (x1 - x0) + b * rate_change_x - (1 + Kpe/Kse)*T_0 + A)   # passive + active = total
#    dT_0 = Kse / b * (- (1 + Kpe/Kse)*T_0 +  A)   # active part only...
  
    return dT_0





def force_length(target_length=1.0, firing_rate=50.0):
    x, dx = gen_waveform(L1 = 0.01, L2 = target_length)    # x, dx return as arrays 
    
    spikes = d_train(firing_rate = firing_rate, SAMPLING_RATE = SAMPLING_RATE)
    spike_i1 = spike_i2 = 0.0
    h_i1 = h_i2 = 0.0
    T_i = T_i1 = 0.0
    h_list=[]
    T_list=[]
    
    for spike_i, x_i, dx_i in zip(spikes, x, dx):
        h_i = active_state(spike_i1, spike_i2, h_i1, h_i2)
        h_list.append(h_i)
        spike_i1, spike_i2 = spike_i * SAMPLING_RATE, spike_i1
        h_i1, h_i2 = h_i, h_i1

        dT_i = gen_force(T_i, x_i, dx_i, A = h_i*s(x_i) )   # total force (passive + active)  
#        print dT_i
        if (x_i >= 1.0):
            T_i = T_i1 + dT_i * (1.0/SAMPLING_RATE)
        else:
            T_i = h_i*s(x_i)
        T_list.append(T_i)
        T_i1 = T_i
        

    ## smoothing the graph (averaging)
##    xtemp = arange(0, 1, 1.0/SAMPLING_RATE)
###    stemp=UnivariateSpline(x, T_list, w=None, bbox=[x[0]-100,x[-1]+100], k = 3)
##    stemp=UnivariateSpline(xtemp, T_list, w=None, s=0,k = 4)
###    xnew = linspace(0, 1, 0.1)
##    xnew = arange(0, 1, 0.1)
##    T_list_filtered = stemp(xnew)
    
    b, a = butter(N=2, Wn=2*pi*1/SAMPLING_RATE , btype='low', analog=0, output='ba')
    T_list_filtered= filtfilt(b=b, a=a, x=array(T_list))
#    return T_list[-1] 
    return T_list_filtered[-1]

#    # looping through multiple arrays 
#    for x_i, dx_i in zip(x, dx):
#        T_0 = ode2(T_0, x_i, dx_i)
#        #print T_0
#    return T_0                

if __name__ == '__main__':
    from numpy import pi, array
    from pylab import show, plot, grid
    from scipy.signal import butter, filtfilt
    
#    from numpy import *
    

    SAMPLING_RATE = 1024
    spikes = spike_train(firing_rate =40.0, SAMPLING_RATE = SAMPLING_RATE)
    spike_i1 = spike_i2 = 0.0
    A_i1 = A_i2 = 0.0
    T_i = T_i1 = 0.0
    x, dx = gen_waveform(L2 = 2.0001, SAMPLING_RATE = SAMPLING_RATE)


    A_list = []
    T_list = []
    for spike_i, x_i, dx_i in zip(spikes, x, dx):
        A_i = s(x_i) * active_state(spike_i1, spike_i2, A_i1, A_i2)
        A_list.append(A_i)
        spike_i1, spike_i2 = spike_i * SAMPLING_RATE, spike_i1
        A_i1, A_i2 = A_i, A_i1

        dT_i = d_force(T_i, x_i, dx_i, A = A_i)   # total force (passive + active)
        T_i = T_i1 + dT_i * (1.0/SAMPLING_RATE)
        T_list.append(T_i)
        T_i1 = T_i
#    subplot(211)
#    plot(T_list)
#    grid('True')

    ## curve smoothing (averaging)
    b, a = butter(N=2, Wn=2*pi*1/SAMPLING_RATE , btype='low', analog=0, output='ba')
    T_list_filtered= filtfilt(b=b, a=a, x=array(T_list))
#    print len(T_list_filtered)


#    x = linspace(0, 1, 0.1)
#    x = arange(0, 1, 1.0/SAMPLING_RATE)
#    s=UnivariateSpline(x, T_list, w=None, bbox=[x[0]-100,x[-1]+100], k = 3)
#    s=UnivariateSpline(x, T_list, w=None, s=0,k = 4)

#    xnew = linspace(0, 1, 0.1)
#    xnew = arange(0, 1, 0.1)
#    T_list_filtered = s(xnew)
#    g=interpolate.interp1d(x,T_list, kind='linear')
#    T_list_interpolated = g(xnew)
#    print T_list_interpolated[-1]
#    subplot(212)
#    plot(x, T_list,'r', xnew, T_list_filtered, 'b', xnew, T_list_interpolated, 'g')
#    plot(T_list_filtered)
    plot(A_list,'r', T_list_filtered, 'g')
#    plot(x, A_list)
    grid('True')
    show()
    


    print "len_x = %d" % len(T_list)
#    print "first = %d" % spikes[0]




