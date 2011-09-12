from decimal import Decimal  
def mybin(float, bit = 10):  
    """ 
    这个程序用来将十进制数转化为二进制数,也可以转化浮点数 
    用法: mybin(float, bit=10) 
    float是指要转化的十进制数，可以为浮点数 
    bit是用来指定小数点后面的位数，默认为10位。 
    函数返回字符串 
    """  
    ## 看数据是否有效  
    #import types  
    #if type(float) is not types.IntType and type(float) is not types.FloatType:  
        #print "Error,Please check your input.\n"  
        #return False  
    # 检测极性  
    negative = 0  
    if float < 0:  
        negative = 1  
        float = -1 * float  
    integer = int(float)                        # 整数部分  
    decimal = Decimal(str(float)) - integer     # 小数部分  
    integer_convert = ""         # 转化后的整数部分  
    decimal_convert = ""         # 转化后的小数部分  
    binary = ""                  # 最后的二进制数  
      
    if integer == 0:  
        binary = "0"  
    else:  
        while integer != 0:  
            result = int(integer % 2)  
            integer = integer / 2  
            integer_convert = str(result) + integer_convert   
        if decimal == 0:  
            binary = integer_convert   
        else:  
            i = 0  
            while decimal != 0 and i < bit:  
                result = int(decimal * 2)  
                decimal = decimal * 2 - result  
                decimal_convert = decimal_convert + str(result)  
                i = i + 1  
            binary = integer_convert + '.' + decimal_convert  
              
    if negative == 1:  
        binary = '-' + binary  
    return binary  
def mydec(binary):  
    """ 
    将二进制数变成十进制数，包括浮点数 
    用法：mydec(binary) 
    binary是一个字符型二进制数，可以是浮点数 
    返回一个浮点数或者整数 
    """  
    ## 检测数据有效性  
    #if binary.find('-') not in [-1,0]:  
        #print binary + "\t>>>\t" + "Error with negative symbol's place.\n"  
        #return False  
    #elif binary.find('.') != binary.rfind('.') or binary[0] == '.' or binary[-1] == '.'  or (binary.find('-') == 0 and binary.find('.') == 1 ):  
        #print binary + "\t>>>\t" + "Error with dot.\n"  
        #return False  
    #else:  
        #for i in binary:  
            #if i not in ['1','0','-','.']:  
                #print binary + "\t>>>\t" + "Error, your number can only has \"1 0 - .\" symbols.\n"  
                #return False  
    #检测极性  
    negative = 0  
    if binary[0] == '-':  
        negative = 1  
        binary = binary[1:]          
    integer = ""  
    decimal = ""  
    dot = binary.find('.')  
    if dot == -1:  
        integer = binary  
    else:  
        integer = binary[:dot]  
        decimal = binary[dot+1:]   
      
    cnt1=integer.__len__()  
    cnt2=decimal.__len__()  
    if cnt1 != 0:  
        temp = 0  
        index_reverse = range(0,cnt1)  
        for i in index_reverse:  
            temp = temp + int(integer[i]) * ( 2 ** (cnt1 - i - 1) )  
        integer = temp  
    else:  
        integer = 0  
    if cnt2 != 0:  
        temp = 0  
        index = range(1,cnt1+1)  
        for i in index:  
            temp = temp + int(decimal[ i-1 ]) * (2 ** (-1*i))  
        decimal = temp  
    else:  
        decimal = 0  
      
    result = integer + decimal  
    if negative == 1:  
        result = -1 * result  
      
    return result  
      
  
###########################  
# Test Part  
###########################  
if __name__=="__main__":  
    print "测试1-- mybin:\n"  
    for i in [125, 1.3, 2.5, 0, -1, -5.4]:  
        if mybin(i) != False:  
            print str(i) + "\t==>\t" + mybin(i) + '\n'  
          
    print "测试2-- mydev:\n"  
    for i in ['-1001.1100', '-1101','111.111','0.1101','1001','0']:  
        if mydec(i) != False:  
            print i + "\t==>\t" + str(mydec(i)) + '\n'  
    #print "测试3:\n"  
    #for i in [ '123' ]:  
        #if mybin(i) != False:  
            #print str(i) + "\t==>\t" + mybin(i) + '\n'  
    #print "测试4:\n"  
    #for i in ['123', '101.1.1.0', '112-212', '-.23', '111.', '.10']:  
        #if mydec(i) != False:  
            #print i + "\t==>\t" + str(mydec(i)) + '\n'  
