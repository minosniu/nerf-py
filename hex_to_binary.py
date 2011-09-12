import math
import struct, binascii

def hextobinary(hex_string):
    s = int(hex_string, 16) 
    num_digits = int(math.ceil(math.log(s) / math.log(2)))
    digit_lst = ['0'] * num_digits
    idx = num_digits
    while s > 0:
        idx -= 1
        if s % 2 == 1: digit_lst[idx] = '1'
        s = s / 2
    return ''.join(digit_lst)

packed = struct.pack('f', 12.34)
print packed
packed_hex = binascii.hexlify(packed)
print packed_hex

print hextobinary(packed_hex)
