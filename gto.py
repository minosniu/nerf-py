from pylab import *
from math import exp
from generate_sin import gen

SAMPLING_RATE = 1024
h  = 1.0/SAMPLING_RATE
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
X0_INIT=0.0
#(LPR0[j]*KPR[j]+Lcein*KSR[j]-LSR0[j]*KSR[j]-F0[j])/(KSR[j]+KPR[j])
#X1_INIT=0.9579
X1_INIT = (LPR0*KPR+LCEIN*KSR-LSR0*KSR-F0ACT)/(KSR+KPR)
X2_INIT=0.0

GAMMA_DYN = 80.0
######################

def gto_loeb_full(gammaDyn, lce, x_0, x_1, x_2):
    """ Take state variables
        Return derivatives
    """
    mingd = gammaDyn**2/(gammaDyn**2+60**2)
    dx_0 = (mingd-x_0)/0.149
    dx_1 = x_2
    ## print 'dx_0=', dx_0
    ## print 'CSS=', CSS
    ## print 'x_1=', x_1
    ## print 'x_2=', x_2
    ## print 'dx_2=', dx_2
    ## CSS[j]=(2/(1+exp(-1000*x[2+3*j])))-1; //temporary var used for dx[2+3*j]
    if (-1000.0*x_2 > 100.0):
        CSS = -1.0
    elif (-1000.0*x_2 < -100.0):
        CSS = 1.0
    else:
        CSS = (2.0 / (1.0 + exp(-1000.0*x_2) ) ) - 1.0
    sig = ((x_1-RLDFV) > 0.0) * (x_1 - RLDFV)
    #dx[2] = (1/M[0])*(KSR[0]*(*LcePtrs[0])-(KSR[0]+KPR[0])*x[1]-CSS*(B[0]*x[0])*fabs(x[2])-0.4);
    #dx[2+3*j] = (1/M[j])*(KSR[j]*(*LcePtrs[0])-(KSR[j]+KPR[j])*x[1+3*j]-CSS[j]*(B0[j]+B[j]*x[0+3*j])*sig[j]*(pow((fabs(x[2+3*j])),a[j]))-(F0[j]+F[j]*x[0+3*j])-KSR[j]*LSR0[j]+KPR[j]*LPR0[j]); //LPR'_in                    
    # @Sirish: That was BDAMP intead of B0DAMP
    #dx_2 = (1/MASS) * (KSR*lce - (KSR+KPR)*x_1 - CSS*(BDAMP*x_0)*(abs(x_2)) - 0.4)  # simpler model
   # dx_2 = (1/MASS)*(KSR*lce-(KSR+KPR)*x_1-CSS*(BDAMP_PASSIVE+BDAMP*x_0)*sig*(pow((abs(x_2)),ANONLINEAR))-(F0ACT+FACT*x_0)-KSR*LSR0+KPR*LPR0)    # complicated model. 
    dx_2 = (1/MASS)*(KSR*lce-(KSR+KPR)*x_1-CSS*(BDAMP_PASSIVE+BDAMP*x_0)*sig*(pow((abs(x_2)),0.3))-(F0ACT+FACT*x_0)-KSR*LSR0+KPR*LPR0)    # complicated model. 

    return [dx_0, dx_1, dx_2]


def ode1 (GAMMA_DYN, lce_i, x_0, x_1, x_2):
    ## Beginning of Eular's Method (ODE1)
    [dx_0, dx_1, dx_2] = bag1_loeb_full(GAMMA_DYN, lce_i, x_0, x_1, x_2)
    x_0 = x_0 + dx_0 *(1.0/SAMPLING_RATE)
    x_1 = x_1 + dx_1 *(1.0/SAMPLING_RATE)
    x_2 = x_2 + dx_2 *(1.0/SAMPLING_RATE)

    dx_0_plot.append(dx_0)
    dx_1_plot.append(dx_1)
    dx_2_plot.append(dx_2)
    x_0_plot.append(x_0)
    x_1_plot.append(x_1)
    x_2_plot.append(x_2)
    ## End of Eular's Method (ODE1)
    Ia_fiber = max(GI*(lce_i-x_1-LSR0), 0.0)
    Ia_fiber_plot.append(Ia_fiber)
    return [x_0, x_1, x_2]


def ode2 (GAMMA_DYN, lce_i, x_0, x_1, x_2):
    ## Beginning of Heun's Method
     
    [dx_0, dx_1, dx_2] = bag1_loeb_full(GAMMA_DYN, lce_i, x_0, x_1, x_2)
    xx_0 = x_0 + dx_0 *h
    xx_1 = x_1 + dx_1 *h
    xx_2 = x_2 + dx_2 *h
    [ddx_0, ddx_1, ddx_2] = bag1_loeb_full(GAMMA_DYN, lce_i, xx_0, xx_1, xx_2)
    x_0 = x_0 + (ddx_0 + dx_0) / 2.0 *h
    x_1 = x_1 + (ddx_1 + dx_1) / 2.0 *h
    x_2 = x_2 + (ddx_2 + dx_2) / 2.0 *h

    dx_0_plot.append((dx_0 + ddx_0) / 2.0)
    dx_1_plot.append((dx_1 + ddx_1) / 2.0)
    dx_2_plot.append((dx_2 + ddx_2) / 2.0)
    x_0_plot.append(x_0)
    x_1_plot.append(x_1)
    x_2_plot.append(x_2)
    ## End of Heun's Method
    Ia_fiber2 = max(GI*(lce_i-x_1-LSR0), 0.0)
    Ia_fiber_plot2.append(Ia_fiber2)
    return [x_0, x_1, x_2]


def ode45 (GAMMA_DYN, lce_i, x_0, x_1, x_2):
    ## Runge-Kutta method
    ## algorithm from http://math.fullerton.edu/mathews/n2003/RungeKuttaMod.html
    [dx_0, dx_1, dx_2] = bag1_loeb_full(GAMMA_DYN, lce_i, x_0, x_1, x_2)
    x_0_k1 =   dx_0 *h                          #k1
    x_1_k1 =   dx_1 *h
    x_2_k1 =   dx_2 *h   
    
    xx_0 = x_0 + x_0_k1/2                   # yj + k1/2
    xx_1 = x_1 + x_1_k1/2  
    xx_2 = x_2 + x_2_k1/2
    
    [ddx_0, ddx_1, ddx_2] = bag1_loeb_full(GAMMA_DYN, lce_i, xx_0, xx_1, xx_2)
    x_0_k2 =   ddx_0*h/2                  #k2, not 100% sure. tj + h/2 part 
    x_1_k2 =   ddx_1*h/2
    x_2_k2 =   ddx_2*h/2
    
    xx_0 = x_0 + x_0_k2/2                   # yj + k2/2
    xx_1 = x_1 + x_1_k2/2  
    xx_2 = x_2 + x_2_k2/2
    
    [ddx_0, ddx_1, ddx_2] = bag1_loeb_full(GAMMA_DYN, lce_i, xx_0, xx_1, xx_2)
    x_0_k3 =   ddx_0 * h/2                  # k3
    x_1_k3 =   ddx_1 * h/2
    x_2_k3 =   ddx_2 * h/2
    
    xx_0 = x_0 + x_0_k3                   # yj + k3
    xx_1 = x_1 + x_1_k3  
    xx_2 = x_2 + x_2_k3
    
    [ddx_0, ddx_1, ddx_2] = bag1_loeb_full(GAMMA_DYN, lce_i, xx_0, xx_1, xx_2)
    x_0_k4 =   ddx_0 * h
    x_1_k4 =   ddx_1 * h
    x_2_k4 =   ddx_2 * h

    x_0 = x_0 + (x_0_k1 + 2*x_0_k2 +2*x_0_k3 + x_0_k4) / 6.0    
    x_1 = x_1 + (x_1_k1 + 2*x_1_k2 +2*x_1_k3 + x_1_k4) / 6.0  
    x_2 = x_2 + (x_2_k1 + 2*x_2_k2 +2*x_2_k3 + x_2_k4) / 6.0  

    #dx_0_plot.append((dx_0 + ddx_0) / 2.0)
    #dx_1_plot.append((dx_1 + ddx_1) / 2.0)
    #dx_2_plot.append((dx_2 + ddx_2) / 2.0)
    x_0_plot.append(x_0)
    x_1_plot.append(x_1)
    x_2_plot.append(x_2)
    ## End of Heun's Method
    Ia_fiber45 = max(GI*(lce_i-x_1-LSR0), 0.0)
    Ia_fiber_plot45.append(Ia_fiber45)
    return [x_0, x_1, x_2]

Lce = []
Lce = gen(SAMPLING_RATE)

#plot(Lce)

Ia_fiber=[]
Ia_fiber2=[]
Ia_fiber45=[]
x_0_plot = []
x_1_plot = []
x_2_plot = []
Ia_fiber_plot = []
Ia_fiber_plot2= []
Ia_fiber_plot45= []
dx_0_plot = []
dx_1_plot = []
dx_2_plot = []
x_0 = X0_INIT
x_1 = X1_INIT
x_2 = X2_INIT
for lce_i in Lce:
    [x_0, x_1, x_2] = ode1(GAMMA_DYN, lce_i, x_0, x_1, x_2)   # Euler's method

x_0 = X0_INIT
x_1 = X1_INIT
x_2 = X2_INIT
for lce_i in Lce:
    [x_0, x_1, x_2] = ode2(GAMMA_DYN, lce_i, x_0, x_1, x_2)   # Heun's Method
    
x_0 = X0_INIT
x_1 = X1_INIT
x_2 = X2_INIT
for lce_i in Lce:
    [x_0, x_1, x_2] = ode45(GAMMA_DYN, lce_i, x_0, x_1, x_2)   # 's Method

subplot(511)
plot(Ia_fiber_plot)
title('ODE1')
#plot(x_2_plot)
subplot(512)
plot(Ia_fiber_plot2)
title('ODE2')
#plot(dx_1_plot)
#print mingd
#print dx_0
subplot(513)
plot(Ia_fiber_plot45)
title('ODE45')
subplot(514)
plot(Lce)
title('Lce')
#subplot(515)
#plot(Lce)

show()

