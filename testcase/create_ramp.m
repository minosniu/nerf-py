%  Function:       create_ramp.m
% 
%  Description:    Generate test cases based on Mileusnic et al 2006 JNP.
%                  Create a ramp function for spindle model input, starting
%                  length L1 (units: L0), final length L2(units: L0),
%                  ramp slope V (units: L0/s). Time step 0.001 s. Time
%                  vector length 5s. Start point of ramp: 1s. 
% 
%  Date:           03-31-11
%  
%  Author:         Boshuo Wang, boshuowa@usc.edu
% 
%  Output:         ramp.mat, variable name: data
% 
%  Others:         .mat file is input for spindle_test_ramp.mdl
% 



L1=0.95;    %min length  /  L0   (Mileusnic et al 2006 JNP)
L2=1.08;    %max length  /  L0
V=0.66;     %rising velocity (L0/s)
T = 1;      %1 second of data

SAMPLING_RATE = 1024;
%dt=0.001
dt = 1/SAMPLING_RATE;
t=linspace(0,T,T/dt+1);

L=ones(size(t))*L1;

tstart=T*0.2;

n_start=tstart/dt+1;n_end=round((L2-L1)/V/dt);


L(n_start:n_start+n_end-1) = L(n_start:n_start+n_end-1)+ linspace(0,(L2-L1),n_end);
L(n_start+n_end:end)=L2;

plot(t,L);

data=[t;L];
save ramp.mat data