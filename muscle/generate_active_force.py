from generate_spikes import spike_train
#from generate_muscle_cmn import gen_force
from generate_stretch import gen_waveform
#from scipy.interpolate import UnivariateSpline
#from scipy import interpolate



# Generate active state component in the muscle stretch

def active_state(x_i1, x_i2, y_i1, y_i2): 
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
    """
    a1 = 2.185
    a2 = -2.176
    b0 = 1.0
    b1 = -1.942
    b2 = 0.943
    
    y_i = a1*x_i1 + a2* x_i2 - b1 * y_i1 - b2*y_i2
    
    return y_i


## S function (weight function) to give parabola-like weight to A(x) 

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

if __name__ == '__main__':
    
    from pylab import show, plot
    SAMPLING_RATE=1024

    spikes = spike_train(firing_rate =20.0, SAMPLING_RATE = SAMPLING_RATE)
    spike_i1 = spike_i2 = 0.0
    A_i1 = A_i2 = 0.0
    x_i = 1.0
    #x, dx = gen_waveform(L2 = 1.0001, SAMPLING_RATE = SAMPLING_RATE)


    A_list = []
    
    for spike_i in spikes:
        A_i = s(x_i) * active_state(spike_i1, spike_i2, A_i1, A_i2)
        A_list.append(A_i)
        spike_i1, spike_i2 = spike_i * SAMPLING_RATE, spike_i1
        A_i1, A_i2 = A_i, A_i1

#        dT_i = gen_force(T_i, x_i, dx_i, A = A_i)   # total force (passive + active)
    plot(A_list)
    show()    


