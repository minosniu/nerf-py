from numpy import *
from pylab import *
from math import exp
from decimal import *

import math
import time
import struct, binascii
import os
#from scipy.interpolate import UnivariateSpline
from generate_waveform import gen_waveform
from generate_spikes import d_train
from generate_active_state import s
from generate_active_state import active_state
from scipy.signal import butter, filtfilt

"""
Test and generate the tension curve in Eq.3 of Shadmehr and S.P.Wise
Eric W. Sohn (wonjoons at usc dot edu)

"""
SAMPLING_RATE = 1024
h  = 1.0/SAMPLING_RATE  # (= dt)
Kse = 136     # g / cm
Kpe = 75      # g / cm
b = 50        # g * s / c
#V = 6.0     # rising velocity

#rate_change_x = V * h / h  # speed. same as change in x  / dt

######################
# Initial Conditions #
######################
x0 = 1       # initial length of x, arbitrary
T_0_INIT = 0    # initial tension

# change x to induce change in T. (in Tension-length curve)

# Eq. 3 in Shedmehr, derivative of Tension in the muscle
def gen_force(T_0, x1, x2, A=0.0):
    """ Take state variables
        Return derivatives
    """
#    A =   # arbitrary A. 
    
    rate_change_x = x2   # slope
    dT_0 = Kse / b * (Kpe * (x1 - x0) + b * rate_change_x - (1 + Kpe/Kse)*T_0 + A)   # passive + active = total
#    dT_0 = Kse / b * (- (1 + Kpe/Kse)*T_0 +  A)   # active part only...
  
    return dT_0

def gen_force_activeonly(T_0, A=0.0):
    """ Take state variables
        Return derivatives
    """
#    dT_0 = Kse / b * (- (1 + Kpe/Kse)*T_0 +  A)   # active part only...
    dT_0 = Kse / b * ( A)   # active part only...


    return dT_0

"""
def ode2 (T_0, x1_i, x2_i):
    ## Beginning of Heun's Method
     
    [dT_0] = gen_force(T_0, x1_i, x2_i)
    T_0 = T_0 + dT_0 *h
    [ddT_0] = gen_force(T_0, x1_i, x2_i)
    T_0 = T_0 + (ddT_0 + dT_0) / 2.0 *h
   
    dT_0_plot.append((dT_0 + ddT_0) / 2.0)
#    T_0_plot.append(T_0)
    ## End of Heun's Method
    tension_plot.append(T_0)
    return T_0
"""



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


def force_length_activeonly(target_length=1.0, firing_rate=50.0):
    x, dx = gen_waveform(L1 = 0.01, L2 = target_length)    # x, dx return as arrays 

    
#    x = arange(0, 1, 1.0/SAMPLING_RATE)

    spikes = d_train(firing_rate = firing_rate, SAMPLING_RATE = SAMPLING_RATE)
    spike_i1 = spike_i2 = 0.0
    h_i1 = h_i2 = 0.0
    T_i = T_i1 = 0.0
    h_list=[]
    T_list=[]

    for spike_i, x_i in zip(spikes, x):
        h_i = active_state(spike_i1, spike_i2, h_i1, h_i2)
        h_list.append(h_i)
        spike_i1, spike_i2 = spike_i * SAMPLING_RATE, spike_i1
        h_i1, h_i2 = h_i, h_i1

        dT_i = gen_force_activeonly(T_i, A = h_i*s(x_i) )   # total force (passive + active)  
        T_i = T_i1 + dT_i * (1.0/SAMPLING_RATE)
        T_list.append(T_i)
        T_i1 = T_i
        
    ## smoothing the graph (averaging)    
    b, a = butter(N=2, Wn=2*pi*1/SAMPLING_RATE , btype='low', analog=0, output='ba')
    T_list_filtered= filtfilt(b=b, a=a, x=array(T_list)) 
    return T_list_filtered[-1]


if __name__ == '__main__':
    # INITIALIZATION
    T_0 = T_0_INIT

    SAMPLING_RATE = 1024

    # PLOT
    dT_0_plot = []
    T_0_plot = []
    tension = []
#    tension_plot= []
#    L2_activeonly = [0.0 + x * 0.05 for x in range (0, 20)]
    L2 = [0.001 + x * 0.05 for x in range(0, 60)]    
#    print L2_activeonly
    #L2 = [2.0]
    

#    x, dx = gen_waveform(L2 = 1.0001, SAMPLING_RATE = SAMPLING_RATE)
    force20=[]
    force30=[]
    force40=[]
    A_list = []
    T_list = []

    
    # To get Length(L2)-> Force pair, 
#    for L2_activeonly_i in L2_activeonly:
#        temp1 = force_length_activeonly(target_length=L2_activeonly_i, firing_rate = 20.0)
#        force20.append(temp1)
#        temp1 = force_length_activeonly(target_length=L2_activeonly_i, firing_rate = 30.0)
#        force30.append(temp1)
#        temp1 = force_length_activeonly(target_length=L2_activeonly_i, firing_rate = 40.0)
#        force40.append(temp1)

    for L2_i in L2:
        temp2=force_length(target_length=L2_i, firing_rate=20.0)
        force20.append(temp2)    
        temp=force_length(target_length=L2_i, firing_rate=30.0)
        force30.append(temp)
        temp=force_length(target_length=L2_i, firing_rate=40.0)
        force40.append(temp)

        
#        print temp


    print len(force20)
    #x1 = x[:, 0]      # get the 0th column, length.
    #x2 = x[:, 1]      # get the 1st column, slope.
    #print x

    # looping through multiple arrays 
    #for x1_i, x2_i in zip(x1, x2):
    #    [T_0] = ode2(T_0, x1_i, x2_i)   # Heun's Method


    ## PLOT force-length curve
#   plot(L2_activeonly+L2, force20, 'r')
#    plot(L2_activeonly+L2,force20, 'r', L2_activeonly+L2,force30, 'g', L2_activeonly+L2,force40, 'y' )
    plot(L2,force20, 'r', L2, force30, 'g', L2,force40, 'y' )

    legend(('f=20hz', 'f=30hz', 'f=40hz'))
    xlim([0, 2.5])
    ylim([0, 500])
    xlabel('length - cm')
    ylabel('force - g')
    grid(True)
    show()



