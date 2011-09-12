from numpy import *
from pylab import *
from decimal import *
import math

# generate a step-like x (list) and its dereivative dx (list) for a fixed L2.
# these lists will be used to generate a force-length curve by plugging in them into shadmehr eq 3.  
# For passive force generation, L1 = rest_length = 1.0 (cm).

def gen_waveform(L1 = 1.0, L2 = 2.0, T =1.0, SAMPLING_RATE = 1024):
    """ f = 1.0 # in Hz, continuous freq
        return length(step) and velocity as lists
    """    
    dt = 1.0 / SAMPLING_RATE # Sampling interval in seconds

    max_n = int(T * SAMPLING_RATE) - 1
#    n = linspace(0 , max_n + 1, max_n + 1)
    ramp_speed = 20.0 # equals to slope of the ramp, cm / s
#    print L2
    rising_range = (L2-L1)/ramp_speed/dt
#    print rising_range

    x_up = [L1 + i*(L2-L1)/(rising_range) for i in xrange(max_n) if i <= rising_range ]
    x_stay1 = [L2 for i in xrange(int(max_n - rising_range + 1))]
    x_down = [L1 + (max_n-i)*(L2-L1)/(rising_range) for i in xrange(max_n+1) if i >= max_n-rising_range]
#    x_stay2 = [L1 for i in xrange(max_n)]
    x =  x_up + x_stay1 #+ x_down 
    dx = diff(x+[x[-1]]) /dt

    return x, dx



if __name__ == '__main__':
    from pylab import *
    x, dx = gen_waveform(L2=1.0101)
    
    subplot(211)
    plot(x)
    subplot(212)
    plot(dx)
    show()
    print "len_x = %d" % len(dx)
