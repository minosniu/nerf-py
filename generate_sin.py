from numpy import *

def gen():
    f = 2 # in Hz
    SAMPLING_RATE = 1024
    T = 1.0 / SAMPLING_RATE # in seconds
    PERIODS = 2
    BIAS = 1.0
    AMP = 0.2

    w = f * 2 * pi * T
    max_n = int((2*pi  * PERIODS / w) - 1)
    n = linspace(0 , max_n + 1, max_n + 1)

    x = AMP * sin(w * n) + BIAS
    return x


if __name__ == '__main__':
    from pylab import *
    x = gen()
    plot(x)
    show()
    print "len_x = %d" % len(x)
