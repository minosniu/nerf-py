from pylab import *
from math import *
from generate_sin import gen

##############
# PARAMETERS #
##############
## KSR             [10.4649 10.4649 10.4649]
## KPR             [0.1127 0.1623 0.1623]
## B0DAMP          [0.0605 0.0822 0.0822]
## BDAMP           [0.2356 -0.046 -0.069]
## F0ACT           [0 0 0]
## FACT            [0.0289 0.0636 0.0954]
## XII             [1 0.7 0.7]
## LPRN            [1 0.92 0.92]
## GI              [20000 10000 10000]
## GII             [20000 7250 7250]
## ANONLINEAR      [0.3 0.3 0.3]
## RLDFV           [0.46 0.46 0.46]
## LSR0            [0.04 0.04 0.04]
## LPR0            [0.76 0.76 0.76]
## L2ND            [1 0.04 0.04]
## TAO             [0.192 0.185 0.0001]
## MASS            [0.0002 0.0002 0.0002]
## FSAT            [1 0.5 1]
KSR=10.4649                 
KPR=0.1127
BDAMP_PASSIVE=0.0605
BDAMP=0.2356
F0ACT=0
FACT=0.0289
XII=1
LPRN=1
GI=20000
GII=20000
ANONLINEAR=0.25
RLDFV=0.46
LSR0=0.04
LPR0=0.76
L2ND=1
TAO=0.192
MASS=0.0002
FSAT=1
LCEIN=1.0
##############


######################
# Initial Conditions #
######################
x_0=0.0
#x_0=0.64
x_1=0.9579
x_2=0.0
dx_0=0.0
dx_1=0.0
dx_2=0.0

CSS=0.0
sig=0.0
######################

gd = 80.0

n=1024
Lce = range(n)
Lce = gen()

#plot(Lce)

Ia_fiber=range(n)
x_0_plot = []
x_1_plot = []
x_2_plot = []
for i in range(n):
    mingd = gd**2/(gd**2+60**2)
    dx_0 = (mingd-x_0)/0.149
    dx_1 = x_2
    print 'dx_0=', dx_0
    print 'CSS=', CSS
    print 'x_1=', x_1
    print 'x_2=', x_2
    CSS_exp = -1000.0*x_2 
    if (-1000.0*x_2 > 200.0):
        CSS_exp = 1.0
    elif (-1000.0*x_2 < -200.0):
        CSS_exp = 0.0
    else:
        CSS_exp = exp(-1000.0*x_2)
    CSS = (2.0 / (1.0 + CSS_exp ) ) - 1.0
    #sig = ((x_1-RLDFV) > 0.0) * (x_1 - RLDFV)
    print 'dx_2=', dx_2
    #dx[2] = (1/M[0])*(KSR[0]*(*LcePtrs[0])-(KSR[0]+KPR[0])*x[1]-CSS*(B[0]*x[0])*fabs(x[2])-0.4);
    # @Sirish: That was BDAMP intead of B0DAMP
    dx_2 = (1/MASS) * (KSR*Lce[i] - (KSR+KPR)*x_1 - CSS*BDAMP*x_0*abs(x_2) - 0.4)
    Ia_fiber[i]=GI*(Lce[i]-x_1-LSR0)
    x_0 = x_0 + dx_0*(1.0/1024)
    #print x_0
    x_0_plot.append(x_0)
    x_1 = x_1 + dx_1*(1.0/1024)
    x_1_plot.append(x_1)
    x_2 = x_2 + dx_2*(1.0/1024)
    x_2_plot.append(x_2)

plot(Ia_fiber)
#print mingd
#print dx_0
#plot(x_0_plot)
show()
