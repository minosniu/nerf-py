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
    print lr+"%d:" % depth, tree.opt, 

    if tree.opt == None:
        print tree.data 
        return 0
    if tree.left.opt == None:
        print tree.left.data,
    else:
        left_label = lr + "L%d" % (depth + 1)
        print left_label,
    if tree.right.opt == None:
        print tree.right.data
    else:
        right_label = lr + "R%d" % (depth + 1)
        print right_label
    if tree.left.opt != None:
        disp(tree.left, depth + 1, lr + 'L')
    if tree.right.opt != None:
        disp(tree.right, depth + 1, lr + 'R')
    return 0
    

## exp = "(2/(1+exp(-1000*x[2])))-1"
## exp = "(1/M[j])*(KSR[j]*LcePtrs[0]-(KSR[j]+KPR[j])*x[1]-CSS[0]*(B0[j]+B[j]*x[0])*sig[j]*(pow((fabs(x[2])),a[j]))-(F0[j]+F[j]*x[0])-KSR[j]*LSR0[j]+KPR[j]*LPR0[j])"
exp = "GII[j]*(X[j]*L2nd[j]/LSR0[j]*(LcePtrs[0]-x[1]-LSR0[j])+(1-X[j])*L2nd[j]/LPR0[j]*(LcePtrs[0]-(LcePtrs[0]-x[1]-LSR0[j])-LSR0[j]-LPRN[j]))"
exp = "(Ia_fiber[j]>0)*Ia_fiber[j]*(Ia_fiber[j]<100000)+(Ia_fiber[j]>100000)*100000"
exp = "((a1+a2)+(b1+b2))*((c1+c2)+(d1+d2))"
exp = "GII[j]*(X[j]*L2nd[j]/LSR0[j]*(LcePtrs[0]-x[1]-LSR0[j])+(1-X[j])*L2nd[j]/LPR0[j]*(LcePtrs[0]-(LcePtrs[0]-x[1]-LSR0[j])-LSR0[j]-LPRN[j]))"
exp = "GI[j]*(LcePtrs[0]-x[1]-LSR0[j])"
exp = "(2/(1+exp(-1000*x[2])))-1"
tree = parse_exp(exp)
lbl_cnt = 0
disp(tree, 0)
