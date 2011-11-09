## Begin parser
class node:
    def __init__(self,data,opt=None,left=None,right=None):
        self.data=data
        self.opt=opt
        self.left=left
        self.right=right

OP_HI = "*/"
OP_LO = "+-"
PAR_OPEN = "([{"
PAR_CLOSE = ")]}"
TERM_LABEL = "dx_2_"

def parse_exp(exp):
    par_cnt = 0
    reright = releft = rechop = ""
    tree = node(exp)
    for i in reversed(xrange(len(exp))):
        ch = exp[i]
        if PAR_OPEN.find(ch) != -1:
            par_cnt += 1
        elif PAR_CLOSE.find(ch) != -1:
            par_cnt -= 1
        if (par_cnt == 0) & (OP_LO.find(ch) != -1):
            left = exp[:i]
            right = exp[i+1:]
            tree.opt = ch 
            tree.left = parse_exp(left)
            tree.right = parse_exp(right)
            return tree
    for i in reversed(xrange(len(exp))):
        ch = exp[i]
        if PAR_OPEN.find(ch) != -1:
            par_cnt += 1
        elif PAR_CLOSE.find(ch) != -1:
            par_cnt -= 1
        if (par_cnt == 0) & (OP_HI.find(ch) != -1):
            left = exp[:i]
            right = exp[i+1:]
            tree.opt = ch 
            tree.left = parse_exp(left)
            tree.right = parse_exp(right)
            return tree
    if (exp[0] == '(') & (exp[-1] == ')'):
        chop = exp[1:-1]
        return parse_exp(chop)
    return tree

def disp(tree, depth, lr = ''):

    if tree.opt == None:
        return tree.data
    else:
        left_label = disp(tree.left, depth + 1, lr + 'L')
        right_label = disp(tree.right, depth + 1, lr + 'R')
        if lr == '':
            node_label = TERM_LABEL + "F%d" % depth
        else:
            node_label = TERM_LABEL + lr + "%d" % depth
        print "\n//    ", left_label, '\t' + 4* tree.opt + '\t', right_label + "    =>    " + node_label
        print "wire [31:0] %s;" % node_label
        if tree.opt == '+':
            print "add %s_add( .x(%s), .y(%s), .out(%s) );" % (node_label, left_label, right_label, node_label)
        elif tree.opt == '-':
            print "sub %s_sub( .x(%s), .y(%s), .out(%s) );" % (node_label, left_label, right_label, node_label)
        elif tree.opt == '*':
            print "mult %s_mult( .x(%s), .y(%s), .out(%s) );" % (node_label, left_label, right_label, node_label)
        elif tree.opt == '/':
            print "div %s_div( .x(%s), .y(%s), .out(%s) );" % (node_label, left_label, right_label, node_label)
        
        return node_label
        

    ## if tree.left.opt == None:
    ##     print tree.left.data + "\t@@@@\t",
    ## else:
    ##     left_label = lr + "L%d" % (depth + 1) 
    ##     print left_label + "\t@@@@\t", 
    ## if tree.right.opt == None:
    ##     print tree.right.data
    ## else:
    ##     right_label = lr + "R%d" % (depth + 1)
    ##     print right_label

    ## if tree.left.opt != None:
    ##     disp(tree.left, depth + 1, lr + 'L')
    ## if tree.right.opt != None:
    ##     disp(tree.right, depth + 1, lr + 'R')
    return 0
    

## exp = "(2/(1+exp(-1000*x[2])))-1"
## exp = "(1/M[j])*(KSR[j]*LcePtrs[0]-(KSR[j]+KPR[j])*x[1]-CSS[0]*(B0[j]+B[j]*x[0])*sig[j]*(pow((fabs(x[2])),a[j]))-(F0[j]+F[j]*x[0])-KSR[j]*LSR0[j]+KPR[j]*LPR0[j])"
exp = "C_REV_M*(C_KSR*lce-C_KSR_P_KPR*x_1-CSS*(B0+BDAMP*x_0)*(abs_x2_pow_25)-F*x_0-C_KSR_M_LSR0+C_KPR_M_LPR0)"
exp = "C_REV_M*(C_KSR*lce-C_KSR_P_KPR*x_1-CSS*(B0+BDAMP*x_0)*sig*(abs_x2_pow_25)-(F0+F*x_0)-C_KSR_M_LSR0+C_KPR_M_LPR0)"
tree = parse_exp(exp)
lbl_cnt = 0
parsed_tree = disp(tree, 0)
