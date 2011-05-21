import math
import struct, binascii
from scipy.io import savemat, loadmat
import os
MAT_FILE = './testcase/integrator_cases.mat'

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
x = data['x']
out = data['out']

for i in xrange(len(x)) :
    packed = ConvertType(x[i], fromType = 'f', toType = 'I')
    print "                9'd%d" % i, " : sin_n <= 32'h%0x;" % packed

## for i in xrange(len(x)) :
##     packed = ConvertType(out[i], fromType = 'f', toType = 'I')
##     print "            9'd%d" % i, " : int_sin_n <= 32'h%0x;" % packed

## print hextobinary(packed_hex)
