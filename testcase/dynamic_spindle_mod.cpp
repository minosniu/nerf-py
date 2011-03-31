/*
 * FileName: New C spindle s-function for only one muscle, inputoutput port width is 1
 *                                       
 * Synopsis:
 *
 *
 * Comment: 
 * This code is to combine m-file s-function code for each single intrafusal fibers of muscle spindle of multiple muscles to a single C s-function
 *          i.e. m-file: 3 intrafusal fibers * NumofMuscles = one c-file
 *
 *
 * Date: 02-25-07
 *
 *
 * Author: Dan Song
 *
 * Bugs fixed: Modifed Activation , now input is pps not activation 0-1 - Giby Raphael
 *           
 *
 */

// S_FUNCTION_NAME is the name of the S-function as it appears in the Simulink model
#define S_FUNCTION_NAME  dynamic_spindle_mod
#define S_FUNCTION_LEVEL 2

// simstruc.h defines of the SimStruct and its associated macro definitions.
#include "simstruc.h"
#include "math.h"

//#define U(element) (*uPtrs[element])  /* Pointer to Input Port0 */

// parameters passed to the s-function: 

//Parameters for 3 intrafusal fibers, all are the vectors of length 3
//KSR,KPR,B0DAMP,BDAMP,F0ACT,FACT,CS,XII,LPRN,GI,GII,ANONLINEAR,RLDFV,LSR0,LPR0,L2ND,TAO,MASS,FSAT

//Sensory Region spring constant [10.4649 10.4649 10.4649]
#define KSR_IDX 0 //Sensory region K
#define KSR_PARAM(S) ssGetSFcnParam(S,KSR_IDX)

// Polar Region spring constant 
// Paper [0.1500 0.1500 0.1500]
// Dan [0.1127 0.1623 0.1623]
#define KPR_IDX 1 //Polar retion K
#define KPR_PARAM(S) ssGetSFcnParam(S,KPR_IDX)

//Passive Damping Coefficient [0.0605 0.0822 0.0822]
#define B0DAMP_IDX 2 //Damping B0
#define B0DAMP_PARAM(S) ssGetSFcnParam(S,B0DAMP_IDX)

//Coefficient of damping due to dyn.fusimotor input & stat fusimotor input
// Paper [0.2592  -0.046  -0.069]
// Dan [0.2356  -0.046  -0.069]
#define BDAMP_IDX 3 //Damping B1/B2
#define BDAMP_PARAM(S) ssGetSFcnParam(S,BDAMP_IDX)

//Could not find in the Table
//Dan [0 0 0]
#define F0ACT_IDX 4 //Active force F0 
#define F0ACT_PARAM(S) ssGetSFcnParam(S,F0ACT_IDX)

//Coef of force generation due to dyn. & stat. fusimotor input [0.0289 0.0636 0.0954]
#define FACT_IDX 5 //Active force F1/F2
#define FACT_PARAM(S) ssGetSFcnParam(S,FACT_IDX)

//Percentage of the secondary afferent on sensory region[1 0.7 0.7]
#define XII_IDX 6 //Percentatoin of II on sensory region, X 
#define XII_PARAM(S) ssGetSFcnParam(S,XII_IDX)

//Polar region threshold length 
// Paper [ _ 0.89 0.89]
// Dan [1 0.92 0.92]
#define LPRN_IDX 7 //PR. length above 2nd ending are stretched, LPRN 
#define LPRN_PARAM(S) ssGetSFcnParam(S,LPRN_IDX)

//Term relating the sensory regions stretch to primary afferent firing [20000 10000 10000]
#define GI_IDX 8 //Coef. stretch to prim afferent 
#define GI_PARAM(S) ssGetSFcnParam(S,GI_IDX)

//Term relating the sensory regions stretch to 2ndory afferent firing [20000 7250 7250]
#define GII_IDX 9 //Coef. stretch to 2nd afferent 
#define GII_PARAM(S) ssGetSFcnParam(S,GII_IDX)

//Non-linear velocity dependence power constant [0.3 0.3 0.3]
#define ANONLINEAR_IDX 10 //Nonlinear term, a 
#define ANONLINEAR_PARAM(S) ssGetSFcnParam(S,ANONLINEAR_IDX)

//Fascicle length below which force production is zero [0.46 0.46 0.46]
#define RLDFV_IDX 11 //Turn on the L-dependence of F-V, R 
#define RLDFV_PARAM(S) ssGetSFcnParam(S,RLDFV_IDX)

//Sensory region rest length [0.04 0.04 0.04]
#define LSR0_IDX 12 //SR. resting length, LSR0
#define LSR0_PARAM(S) ssGetSFcnParam(S,LSR0_IDX)
 
//Polar region resting length [0.76 0.76 0.76]
#define LPR0_IDX 13 //PR. resting length, LPR0
#define LPR0_PARAM(S) ssGetSFcnParam(S,LPR0_IDX)

//Secondary afferent rest length [1 0.04 0.04]
#define L2ND_IDX 14 //Secondary afferent rest length
#define L2ND_PARAM(S) ssGetSFcnParam(S,L2ND_IDX)

//Low pass filter time constant 
// Paper [0.149 0.205 _ ]
// Dan [0.192 0.185 0.0001]
#define TAO_IDX 15 //Time constant, tao
#define TAO_PARAM(S) ssGetSFcnParam(S,TAO_IDX)

//Intrafusal fiber mass [0.0002 0.0002 0.0002]
#define MASS_IDX 16 //Mass
#define MASS_PARAM(S) ssGetSFcnParam(S,MASS_IDX)

//Saturation Frequency 
//Dan implemented it as Activation 
// Paper [60 60 90] pps
// Dan [1 0.5 1]
#define FSAT_IDX 17 //  Saturation freq. fs
#define FSAT_PARAM(S) ssGetSFcnParam(S,FSAT_IDX)

//Initial Length of Lce - variable
// Put from resting length of muscle in musculoskeletal model
#define LCEIN_IDX 18 // Initial length of Lce
#define LCEIN_PARAM(S) ssGetSFcnParam(S,LCEIN_IDX)

#define NPARAMS 19

#define min(x,y) ((x)>(y)?(y):(x))
#define max(x,y) x > y ? x : y


/* Function: mdlCheckParameters 
*  Description: Validates parameters: verifies if parameters are double and whether they include only one element
*/
#define MDL_CHECK_PARAMETERS
#if defined(MDL_CHECK_PARAMETERS) && defined(MATLAB_MEX_FILE)

static void mdlCheckParameters(SimStruct *S)
  {
      
      /* Check 0th parameter: KSR */
      {
          if (!mxIsDouble(KSR_PARAM(S)) ||
              mxGetNumberOfElements(KSR_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in KSR do not correspond to number intrafusal fibers");
              return;
          }
      }
      
      /* Check 1th parameter: KPR */
      {
          if (!mxIsDouble(KPR_PARAM(S)) ||
              mxGetNumberOfElements(KPR_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in KPR do not correspond to number intrafusal fibers");
              return;
          }
      }
      
      /* Check 2th parameter: B0DAMP */
      {
          if (!mxIsDouble(B0DAMP_PARAM(S)) ||
              mxGetNumberOfElements(B0DAMP_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in B0DAMP do not correspond to number intrafusal fibers");
              return;
          }
      }
      
      /* Check 3th parameter: BDAMP */
      {
          if (!mxIsDouble(BDAMP_PARAM(S)) ||
              mxGetNumberOfElements(BDAMP_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in BDAMP do not correspond to number intrafusal fibers");
              return;
          }
      }
      
      /* Check 4th parameter: F0ACT */
      {
          if (!mxIsDouble(F0ACT_PARAM(S)) ||
              mxGetNumberOfElements(F0ACT_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in F0ACT do not correspond to number intrafusal fibers");
              return;
          }
      }
      
      
      /* Check 5th parameter: FACT */
      {
          if (!mxIsDouble(FACT_PARAM(S)) ||
              mxGetNumberOfElements(FACT_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in FACT do not correspond to number intrafusal fibers");
              return;
          }
      }
      
      
      /* Check 6th parameter: XII */
      {
          if (!mxIsDouble(XII_PARAM(S)) ||
              mxGetNumberOfElements(XII_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in XII do not correspond to number intrafusal fibers");
              return;
          }
      }
      
      /* Check 7th parameter: LPRN */
      {
          if (!mxIsDouble(LPRN_PARAM(S)) ||
              mxGetNumberOfElements(LPRN_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in LPRN do not correspond to number intrafusal fibers");
              return;
          }
      }
      
      /* Check 8th parameter: GI */
      {
          if (!mxIsDouble(GI_PARAM(S)) ||
              mxGetNumberOfElements(GI_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in GI do not correspond to number intrafusal fibers");
              return;
          }
      }
      
      /* Check 9th parameter: GII */
      {
          if (!mxIsDouble(GII_PARAM(S)) ||
              mxGetNumberOfElements(GII_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in GII do not correspond to number intrafusal fibers");
              return;
          }
      }
      
      /* Check 10th parameter: ANONLINEAR */
      {
          if (!mxIsDouble(ANONLINEAR_PARAM(S)) ||
              mxGetNumberOfElements(ANONLINEAR_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in ANONLINEAR do not correspond to number intrafusal fibers");
              return;
          }
      }
     
      /* Check 11th parameter: RLDFV */
      {
          if (!mxIsDouble(RLDFV_PARAM(S)) ||
              mxGetNumberOfElements(RLDFV_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in RLDFV do not correspond to number intrafusal fibers");
              return;
          }
      }
      
      /* Check 12th parameter: LSR0 */
      {
          if (!mxIsDouble(LSR0_PARAM(S)) ||
              mxGetNumberOfElements(LSR0_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in LSR0 do not correspond to number intrafusal fibers");
              return;
          }
      }
      
      /* Check 13th parameter: LPR0 */
      {
          if (!mxIsDouble(LPR0_PARAM(S)) ||
              mxGetNumberOfElements(LPR0_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in LPR0 do not correspond to number intrafusal fibers");
              return;
          }
      }
      
      /* Check 14th parameter: L2ND */
      {
          if (!mxIsDouble(L2ND_PARAM(S)) ||
              mxGetNumberOfElements(L2ND_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in L2ND do not correspond to number intrafusal fibers");
              return;
          }
      }
      
      /* Check 15th parameter: TAO */
      {
          if (!mxIsDouble(TAO_PARAM(S)) ||
              mxGetNumberOfElements(TAO_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in TAO do not correspond to number intrafusal fibers");
              return;
          }
      }
      
  
      /* Check 16th parameter: MASS */
      {
          if (!mxIsDouble(MASS_PARAM(S)) ||
              mxGetNumberOfElements(MASS_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in MASS do not correspond to number intrafusal fibers");
              return;
          }
      }
      
      /* Check 17th parameter: FSAT */
      {
          if (!mxIsDouble(FSAT_PARAM(S)) ||
              mxGetNumberOfElements(FSAT_PARAM(S)) != 3) {
              ssSetErrorStatus(S,"Number of parameters in FSAT do not correspond to number intrafusal fibers");
              return;
          }
      }
      
   
      /* Check 18th parameter: LCEIN */
      {
          if (!mxIsDouble(LCEIN_PARAM(S)) ||
              mxGetNumberOfElements(LCEIN_PARAM(S)) != 1) {
              ssSetErrorStatus(S,"LCEIN should be a scalar");
              return;
          }
      }
  }
  
#endif 


/* Function: mdlInitializeSizes 
 * Description: This function checks the number of parameters, sets the number of continuous states using parameters, sets
 *              number and size of input and output ports, directfeedthrough property, and number of sample times. 
 *              ssSetOptions specifies that there are no exception used in this code. 
 */
static void mdlInitializeSizes(SimStruct *S)
{
        
    // Check the number of parameters
    ssSetNumSFcnParams(S, NPARAMS);  
    if (ssGetNumSFcnParams(S) != ssGetSFcnParamsCount(S)) {
        ssSetErrorStatus(S,"Missing parameters");
        return;
    }

    ssSetNumContStates(S, 9);
        
    //Set the number of input signals and the width of those inputs
    if (!ssSetNumInputPorts(S, 3)) return;
    ssSetInputPortWidth(S, 0, 1); //[0] Gamma_dynamic (0-1)
    ssSetInputPortWidth(S, 1, 1); //[1] Gamma_static (0-1)
    ssSetInputPortWidth(S, 2, 1); //[2] Fascicle length Lce (0-1)
    
    //DirectFeedthrough is activated because input value are used in mdlOutput method
    ssSetInputPortDirectFeedThrough(S, 0, 1);
	ssSetInputPortDirectFeedThrough(S, 1, 1);
    ssSetInputPortDirectFeedThrough(S, 2, 1);
    
    // Set number of output signals and dimension
    if (!ssSetNumOutputPorts(S, 2)) return;
    ssSetOutputPortWidth(S, 0, 1); //[0] Ia (Hz)
    ssSetOutputPortWidth(S, 1, 1); //[1] II (Hz)
    
    // Set number of sample time to be used
    ssSetNumSampleTimes(S, 1);
    
    // Specify that there are no execptions in the code. This makes the simulation execute faster
    ssSetOptions(S, SS_OPTION_EXCEPTION_FREE_CODE); 
}


/* Function: mdlInitializeSampleTimes 
 * Description: This function specifies that the S-function block runs in continuous time
 */
static void mdlInitializeSampleTimes(SimStruct *S)
{
    ssSetSampleTime(S, 0, CONTINUOUS_SAMPLE_TIME);
    ssSetOffsetTime(S, 0, 0.0);
    ssSetModelReferenceSampleTimeDefaultInheritance(S); 
}


/* Function: mdlInitializeConditions 
*  Description: This function is call at the start of the simulation. The function is called
*              to initialize the continuous state vector after calling the ssGetContStates() method.
*/
#define MDL_INITIALIZE_CONDITIONS   
#if defined(MDL_INITIALIZE_CONDITIONS)
static void mdlInitializeConditions(SimStruct *S)
{   

      real_T           *x0                    = ssGetContStates(S);
      real_T*          KSR                    = mxGetPr(KSR_PARAM(S));
      real_T*          KPR                    = mxGetPr(KPR_PARAM(S));
      real_T*          F0                     = mxGetPr(F0ACT_PARAM(S));
      real_T*          LSR0                   = mxGetPr(LSR0_PARAM(S));
      real_T*          LPR0                   = mxGetPr(LPR0_PARAM(S));
      real_T           Lcein                  = *mxGetPr(LCEIN_PARAM(S));
    
      int_T  j   = 0; //index for 3 intrafusal fibers
    
	// Initialize states
        for (j=0; j<3;j++){
			x0[0+3*j] = 0; //act_in       
			x0[1+3*j] =(LPR0[j]*KPR[j]+Lcein*KSR[j]-LSR0[j]*KSR[j]-F0[j])/(KSR[j]+KPR[j]); //LPR_in       
			x0[2+3*j] = 0.0; //LPR'_in
        }
  
    
}  
#endif /* MDL_INITIALIZE_CONDITIONS */


/* Function: mdlStart 
*  Description: This function is called only once and can be used for states 
*              that do not need to be initialize another time. 
*/
#define MDL_START  
#if defined(MDL_START) 
static void mdlStart(SimStruct *S){
}
#endif /*  MDL_START */

/* Function: mdlOutputs =======================================================
 * Description: This function estimates the output using the states values and 
 *              input signals.
 */
#define MDL_OUTPUTS 
#if defined(MDL_OUTPUTS) 
static void mdlOutputs(SimStruct *S, int_T tid){
    real_T *x                   = ssGetContStates(S);
   

    // Access to input signals
    InputRealPtrsType gdPtrs       = ssGetInputPortRealSignalPtrs(S,0);
    InputRealPtrsType gsPtrs       = ssGetInputPortRealSignalPtrs(S,1);
    InputRealPtrsType LcePtrs      = ssGetInputPortRealSignalPtrs(S,2);

    // Access output signal 
    real_T *IaPtrs                 = ssGetOutputPortRealSignal(S,0);
    real_T *IIPtrs                 = ssGetOutputPortRealSignal(S,1);
    
      real_T*          KSR                    = mxGetPr(KSR_PARAM(S));
      real_T*          KPR                    = mxGetPr(KPR_PARAM(S));
      real_T*          B0                     = mxGetPr(B0DAMP_PARAM(S));
      real_T*          B                      = mxGetPr(BDAMP_PARAM(S));
      real_T*          F0                     = mxGetPr(F0ACT_PARAM(S));
      real_T*          F                      = mxGetPr(FACT_PARAM(S));
      real_T*          X                      = mxGetPr(XII_PARAM(S));
      real_T*          LPRN                   = mxGetPr(LPRN_PARAM(S));
      real_T*          GI                     = mxGetPr(GI_PARAM(S));
      real_T*          GII                    = mxGetPr(GII_PARAM(S));
      real_T*          a                      = mxGetPr(ANONLINEAR_PARAM(S));
      real_T*          R                      = mxGetPr(RLDFV_PARAM(S));
      real_T*          LSR0                   = mxGetPr(LSR0_PARAM(S));
      real_T*          LPR0                   = mxGetPr(LPR0_PARAM(S));
      real_T*          L2nd                   = mxGetPr(L2ND_PARAM(S));
      real_T*          tao                    = mxGetPr(TAO_PARAM(S));
      real_T*          M                      = mxGetPr(MASS_PARAM(S));
      real_T*          fs                     = mxGetPr(FSAT_PARAM(S));

      int_T             j                     = 0; //index for 3 intrafusal fibers: 1,2,3
     real_T             Ia_fiber[3];              //dynamic for up to 3*15=45 intrafusal fibers 
     real_T             II_fiber[3];
     real_T             Ia_bag2chain=0;          
     real_T             Ia_bag1=0;
     real_T             Ia_muscle=0;
     real_T             II_muscle=0;

 		
		Ia_bag2chain = 0;
		II_muscle = 0;
        for (j=0; j<3;j++){
        //2. below get primary and secondary sensory ending for jth intrafusal fiber of spindle in ith muscle and then the Ia and II output for the spindle in ith muscle
            ////code in m-file s-function mdloutput: sys(1)=GI*(u(2)-x(2)-LSR0);%Ia
            ////code in m-file s-function mdloutput: sys(2)=GII*(X*L2nd/LSR0*(u(2)-x(2)-LSR0)+(1-X)*L2nd/LPR0*(u(2)-(u(2)-x(2)-LSR0)-LSR0-LPRN));%II
          //2.1 Ia:
            Ia_fiber[j]=GI[j]*(*LcePtrs[0]-x[1+3*j]-LSR0[j]);
			//Limit Ia_fiber to Min_Freq = 0Hz and Max_Freq = 100000 Hz
            Ia_fiber[j]=(Ia_fiber[j]>0)*Ia_fiber[j]*(Ia_fiber[j]<100000)+(Ia_fiber[j]>100000)*100000;
            
            //if-else below is for getting Primary sensory of bag2 + chain fibers and compare to the primary sensory of bag1
            if (j==0){
                Ia_bag1 =Ia_fiber[j];        //Primary sensory of bag1 fiber are added together
            }
            else {
                Ia_bag2chain +=Ia_fiber[j]; //Primary sensory of bag2 and chain fibers are added together
            }
          //2.2 II:
            II_fiber[j]=GII[j]*(X[j]*L2nd[j]/LSR0[j]*(*LcePtrs[0]-x[1+3*j]-LSR0[j])+(1-X[j])*L2nd[j]/LPR0[j]*(*LcePtrs[0]-(*LcePtrs[0]-x[1+3*j]-LSR0[j])-LSR0[j]-LPRN[j]));
            //Limit II_fiber output to Min_Freq = 0Hz and Max_Freq = 100000Hz
			II_fiber[j]=(II_fiber[j]>0)*II_fiber[j]*(II_fiber[j]<100000)+(II_fiber[j]>100000)*100000;
            //The if below is simply linear adding II_bag2 and II_chain to get II output of the spindle of ith muscle
            if (j>0){
                II_muscle +=II_fiber[j];
            }
    
    }  
//The function below is for "partial occlusion" for adding Ia_bag2chain and Ia_bag1 to get Ia output of the spindle of ith muscle
// Partial Occlusion = Larger + S*Smaller
Ia_muscle =(Ia_bag1*0.156+Ia_bag2chain)*((Ia_bag1-Ia_bag2chain)<=0)+(Ia_bag1+Ia_bag2chain*0.156)*((Ia_bag1-Ia_bag2chain)>0);
IaPtrs[0] = Ia_muscle;
IIPtrs[0] = II_muscle;
}
#endif /*  MDL_OUTPUTS */



#define MDL_DERIVATIVES  
#if defined(MDL_DERIVATIVES)
/* Function: mdlDerivatives =================================================
*  Description: This method is used to update derivatives of continuous states.
*              Derivatives correpond to integrators'inputs 
*/
  static void mdlDerivatives(SimStruct *S)
  {
    real_T *dx                  = ssGetdX(S);
    real_T *x                   = ssGetContStates(S);
    
 
     // Access to input signals
    InputRealPtrsType gdPtrs       = ssGetInputPortRealSignalPtrs(S,0);
    InputRealPtrsType gsPtrs       = ssGetInputPortRealSignalPtrs(S,1);
    InputRealPtrsType LcePtrs      = ssGetInputPortRealSignalPtrs(S,2);

   
    //Fascicles 
      real_T*          KSR                    = mxGetPr(KSR_PARAM(S));
      real_T*          KPR                    = mxGetPr(KPR_PARAM(S));
      real_T*          B0                     = mxGetPr(B0DAMP_PARAM(S));
      real_T*          B                      = mxGetPr(BDAMP_PARAM(S));
      real_T*          F0                     = mxGetPr(F0ACT_PARAM(S));
      real_T*          F                      = mxGetPr(FACT_PARAM(S));
      real_T*          X                      = mxGetPr(XII_PARAM(S));
      real_T*          LPRN                   = mxGetPr(LPRN_PARAM(S));
      real_T*          GI                     = mxGetPr(GI_PARAM(S));
      real_T*          GII                    = mxGetPr(GII_PARAM(S));
      real_T*          a                      = mxGetPr(ANONLINEAR_PARAM(S));
      real_T*          R                      = mxGetPr(RLDFV_PARAM(S));
      real_T*          LSR0                   = mxGetPr(LSR0_PARAM(S));
      real_T*          LPR0                   = mxGetPr(LPR0_PARAM(S));
      real_T*          L2nd                   = mxGetPr(L2ND_PARAM(S));
      real_T*          tao                    = mxGetPr(TAO_PARAM(S));
      real_T*          M                      = mxGetPr(MASS_PARAM(S));
      real_T*          fs                     = mxGetPr(FSAT_PARAM(S));
      
      int_T             j                     = 0; //index for 3 intrafusal fibers: 1,2,3
     real_T             CSS[3];                          
     real_T             sig[3]; 
     real_T             Mingd=0;
     real_T             Mings=0;

////code in m-file s-function derivative: sys(1)=(min(u(1)/fs,1)-x(1))/tao;% scaled activation (linear approximation, without fs-act conversoin for systems model simulation uses)
////code in m-file s-function derivative: sys(2)=x(3);
////code in m-file s-function derivative:    CSS=2/(1+exp(-1000*x(3)))-1;
////code in m-file s-function derivative:    rr=x(2)-R; sig=(rr>0)+0*(rr<=0); Here combine sig*rr to sig
////code in m-file s-function derivative: sys(3)=(1/M)*(KSR*u(2)-(KSR+KPR)*x(2)-CS*(B0+B*x(1))*sig*(x(2)-R)*abs(x(3))^.3-(F0+F*x(1))-KSR*LSR0+KPR*LPR0); % with LPR*KPR 
        for (j=0; j<3;j++){
      //1. below is for state integration
            //dx[0] first state representing gamma dynamic or static of jth intrafusal fiber in the spindle of ith muscle
            /*if (j==0) {  //when it's bag1 intrafusal fiber, activation is from gd-gamma dynamic input "*gdPtrs"
                Mingd=((*gdPtrs[0]/fs[j])<1)*(*gdPtrs[0]/fs[j])+((*gdPtrs[0]/fs[j])>=1);
                dx[0+3*j] = (Mingd-x[0+3*j])/tao[j]; // this is implementing ((min(((*gdPtrs)/fs[j]),1))-x[0+3*j])/tao[j]; 
                //dx[0+3*j] = (min((*gdPtrs[0]/fs[j]),1)-x[0+3*j])/tao[j]; // this is implementing ((min(((*gdPtrs)/fs[j]),1))-x[0+3*j])/tao[j]; 
            }
            else   {     //when it's bag2 and chain, activation is from gs-gamma static input "*gsPtrs"
                Mings=((*gsPtrs[0]/fs[j])<1)*(*gsPtrs[0]/fs[j])+((*gsPtrs[0]/fs[j])>=1); 
                dx[0+3*j] = (Mings-x[0+3*j])/tao[j]; // this is implementing ((min(((*gdPtrs)/fs[j]),1))-x[0+3*j])/tao[j]; 
                //dx[0+3*j] = (min((*gsPtrs[0]/fs[j]),1)-x[0+3*j])/tao[j]; // this is implementing ((min(((*gdPtrs)/fs[j]),1))-x[0+3*j])/tao[j]; 
            } //dx[1] second state representing LPR (polar region length) of jth intrafusal fiber in the spindle of ith muscle
			*/
			
			
			 if (j==0) {  //when it's bag1 intrafusal fiber, activation is from gd-gamma dynamic input "*gdPtrs"                
				Mingd=pow((*gdPtrs[0]),2)/((pow((*gdPtrs[0]),2))+pow(60,2));
                dx[0+3*j] = (Mingd-x[0+3*j])/0.149; // this is implementing ((min(((*gdPtrs)/fs[j]),1))-x[0+3*j])/tao[j]; 
                //dx[0+3*j] = (min((*gdPtrs[0]/fs[j]),1)-x[0+3*j])/tao[j]; // this is implementing ((min(((*gdPtrs)/fs[j]),1))-x[0+3*j])/tao[j]; 
            }
            else if (j==1)   {     //when it's bag2 and chain, activation is from gs-gamma static input "*gsPtrs"
                Mings=pow((*gsPtrs[0]),2)/((pow((*gsPtrs[0]),2))+pow(60,2));
                dx[0+3*j] = (Mings-x[0+3*j])/0.205; // this is implementing ((min(((*gdPtrs)/fs[j]),1))-x[0+3*j])/tao[j]; 
                //dx[0+3*j] = (min((*gsPtrs[0]/fs[j]),1)-x[0+3*j])/tao[j]; // this is implementing ((min(((*gdPtrs)/fs[j]),1))-x[0+3*j])/tao[j]; 
            } //dx[1] second state representing LPR (polar region length) of jth intrafusal fiber in the spindle of ith muscle
			else if (j==2){
				dx[0+3*j] = 0.0;
			}
			
			x[0+3*2] = pow((*gsPtrs[0]),2)/((pow((*gsPtrs[0]),2))+pow(90,2));
			        
			dx[1+3*j] = x[2+3*j];   
            CSS[j]=(2/(1+exp(-1000*x[2+3*j])))-1; //temporary var used for dx[2+3*j]
            sig[j]=((x[1+3*j]-R[j])>0.0)*(x[1+3*j]-R[j]);                   //temporary var used for dx[2+3*j]
            
			//dx[2] third state representing LPR' (polar region velocity) of jth intrafusal fiber in the spindle of ith muscle
            dx[2+3*j] = (1/M[j])*(KSR[j]*(*LcePtrs[0])-(KSR[j]+KPR[j])*x[1+3*j]-CSS[j]*(B0[j]+B[j]*x[0+3*j])*sig[j]*(pow((fabs(x[2+3*j])),a[j]))-(F0[j]+F[j]*x[0+3*j])-KSR[j]*LSR0[j]+KPR[j]*LPR0[j]); //LPR'_in                    
		
		}    
  }
#endif /* MDL_DERIVATIVES */



/* Function: mdlTerminate 
 * Description: This method is called at the end of a simulation.
 */
static void mdlTerminate(SimStruct *S)
{
}



#ifdef  MATLAB_MEX_FILE    /* Is this file being compiled as a MEX-file? */
#include "simulink.c"      /* MEX-file interface mechanism */
#else
#include "cg_sfun.h"       /* Code generation registration function */
#endif

