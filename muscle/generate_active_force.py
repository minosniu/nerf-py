from generate_spikes import spike_train
#from generate_muscle_cmn import gen_force
from generate_stretch import gen_waveform

from generate_sequence import gen as gen_ramp
from math import exp
#from scipy.interpolate import UnivariateSpline
#from scipy import interpolate



# Generate active state component in the muscle stretch

def active_state(x_i0, x_i1, x_i2, y_i1, y_i2): 
    """ Transfer function (TF) Coefficients for 
        imp_res= 48144*exp(-t/R/0.0326)-45845*exp(-t/R/0.034), 
        1. Laplace teransform to get TF. (s domain) (tf)
        2. convert continuous-time to discrete time (c2d)
        e.g. Transfer function:
           2.185 z - 2.176
        ---------------------
        z^2 - 1.942 z + 0.943

        x_i1: spike [n-1]
        x_i2: spike [n-2]
        y_i1: A[n-1]  (prev active state #)
        y_i2: A[n-2]  (prev prev active state #)
            b0 = 0.0
    b1 = 2.185
    b2 = -2.176
    a0 = 1.0
    a1 = -1.942
    a2 = 0.943   
    """
    
    
    """ New from ta=0.0326 tb=0.036
Transfer function:
  2299 z^2 - 2364 z
----------------------
z^2 - 1.944 z + 0.9445
    """
    b0 = 2299.0
    b1 = -2289.0
    b2 = 0.0
    a0 = 1.0
    a1 = -1.942
    a2 = 0.943 

#    scaling_bits = 10
#    scaling_factor = 1024#0x01 << scaling_bits
    
#    int_gain = 512

#    b1 = int(2.185 * int_gain * scaling_factor)
#    b2 = -int(2.176 * int_gain  * scaling_factor)
#    a0 = int(1.0  * scaling_factor)
#    a1 = -int(1.942  * scaling_factor )
#    a2 = int(0.943  * scaling_factor )
    
#    xx1 = int(x_i1 / a0)
#    xx2 = int(x_i2 / a0)
#    yy1 = int(y_i1 / a0)
#    yy2 = int(y_i2 / a0)
#    
#    ba1 = int(b1 / a0)
#    ba2 = int(b2 / a0)
#    
#    print b1,  b2,  a0,  a1,  a2
    #print xx1,  xx2, yy1,  yy2

    
    #y_i = int((b1*xx1 + b2* xx2 - a1 * yy1 - a2*yy2) )
    t0 =  b0*x_i0
    t1 =  b1*x_i1
    t2 =  b2*x_i2
    t3 =  a1 * y_i1 
    t4 =  a2 * y_i2 
    
    y_i0 = t0 + t1 + t2 - t3 - t4
    #y_i = ((b1*x_i1 + b2* x_i2 - a1 * y_i1 - a2*y_i2) / a0)
    #y_i = int (b1*x_i1 + b2* x_i2 - a1 * y_i1 - a2*y_i2) >> scaling_bits
    
    return y_i0




def active_state_fuglevand(x_i1, x_i2, y_i1, y_i2): 
    """ Transfer function (TF) Coefficients for 
       
    """
    T_twitch = 0.001
    euler_e = 2.718
    P =1 #(arbitary)
    neg1 = -1
    neg2 = -2
    tau = 0.03
    A_twitch = exp(-T_twitch/tau)
      
      
    b0 = 0.0
    b1 = P*euler_e*T_twitch*A_twitch
    b2 = 0.0
    a0 = 1.0
    a1 = neg2*A_twitch
    a2 = A_twitch*A_twitch   
#    scaling_bits = 10
#    scaling_factor = 1024#0x01 << scaling_bits
    

    
#    xx1 = int(x_i1 / a0)
#    xx2 = int(x_i2 / a0)
#    yy1 = int(y_i1 / a0)
#    yy2 = int(y_i2 / a0)
#    
#    ba1 = int(b1 / a0)
#    ba2 = int(b2 / a0)
#    
#    print b1,  b2,  a0,  a1,  a2
    #print xx1,  xx2, yy1,  yy2

    
    #y_i = int((b1*xx1 + b2* xx2 - a1 * yy1 - a2*yy2) )
    t1 =  b1*x_i1
    t2 =  b2*x_i2
    t3 =  a1 * y_i1 
    t4 =  a2 * y_i2 
    
    y_i = t1 + t2 - t3 - t4
    #y_i = ((b1*x_i1 + b2* x_i2 - a1 * y_i1 - a2*y_i2) / a0)
    #y_i = int (b1*x_i1 + b2* x_i2 - a1 * y_i1 - a2*y_i2) >> scaling_bits
    
    return y_i




def s(x = 1.0):
#    print x
    if x < 0.5:
        weighted = 0.0
    elif x < 1.0:
        weighted = -4.0*x**2 + 8.0*x-3.0 
    elif x <= 2.0:
        weighted = -x**2 + 2.0*x
    else: 
        weighted = 0.0
#    weighted = 1
#    print weighted 
    return weighted

def gen_h_diff_eq(firing_rate = 10,  SAMPLING_RATE = 1024):
    spikes = spike_train(firing_rate =firing_rate, SAMPLING_RATE = SAMPLING_RATE)
#    spikes = gen_ramp(T = [0.0, 0.1, 0.11, 0.65, 0.66, 1.0], L = [0.0, 0.0, 1.4, 1.4, 0.0, 0.0], FILT = False)
    spike_i1 = spike_i2 = 0.0
    h_i = h_i1 = h_i2 = 0.0
    x_i = 1.0
    
    h_list = []
    
    for spike_i in spikes:
        h_i = active_state(spike_i, spike_i1, spike_i2, h_i1, h_i2)
#        h_i = active_state_fuglevand(spike_i1, spike_i2, h_i1, h_i2)
        
        h_list.append(h_i )
        spike_i1, spike_i2 = int(spike_i  ), spike_i1
        h_i1, h_i2 = h_i, h_i1
    
    return h_list

if __name__ == '__main__':
    
    from pylab import show, plot
    
    SAMPLING_RATE=1024
    
    hs = gen_h_diff_eq(firing_rate = 2)
 
    plot(hs)
    show()    


