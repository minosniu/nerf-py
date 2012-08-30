import math
import struct, binascii
from scipy.io import savemat, loadmat
import os
from numpy import *
from pylab import *
from math import exp
from decimal import *



##MAT_FILE = './testcase/firing_intervals.mat'
MAT_FILE = './testcase/triangle.mat'

def hextobinary(hex_string):
    s = int(hex_string, 16) 
    num_digits = 32 ##int(math.ceil(math.log(s) / math.log(2)))
    digit_lst = ['0'] * num_digits
    idx = num_digits
    while s > 0:
        idx -= 1
        if s % 2 == 1: digit_lst[idx] = '1'
        s = s / 2
    return ''.join(digit_lst)

def ConvertType(val, fromType, toType):
    return struct.unpack(toType, struct.pack(fromType, val))[0]


assert os.path.exists(MAT_FILE.encode('utf-8')), ".mat waveform file NOT found!"
data = loadmat(MAT_FILE)
x = data['data']
x = transpose(x)
#x1 = x[:, 0]      # get the 0th column, length.
x = x[:, 1]      # get the 1st column, slope.

len(x)
plot(x)
show()


#for i in xrange(len(x)) :
#    packed = x[i]
#    #ConvertType(x[i], fromType = 'f', toType = 'I')
#    print "                11'd%d" % i, " : isi = 11'h%0x;" % packed

