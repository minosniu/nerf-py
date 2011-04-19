import math
import struct, binascii

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


for i in xrange(30) :
    css = (2/(1+math.exp(-(i))))-1
    packed = ConvertType(css, fromType = 'f', toType = 'I')
    print "            10'd%d" % (i+1), " : out = 32'h%0x;" % packed

## print hextobinary(packed_hex)
