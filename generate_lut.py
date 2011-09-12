def ConvertType(val, fromType, toType):
    return unpack(toType, pack(fromType, val))[0]

if __name__ == '__main__':
    from pylab import *
    from generate_sin import *
    from struct import pack, unpack
    x = gen()
    for i in xrange(len(x)) :
        packed = ConvertType(x[i], fromType = 'f', toType = 'I')
        print "                10'd%d" % i, " : sin_n <= 32'h%0x;" % packed
    plot(x)
    show()
    print "len_x = %d" % len(x)

