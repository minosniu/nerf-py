%  Function:       create_sinusoid.m
% 
%  Description:    Generate test cases based on Mileusnic et al 2006 JNP.
%                  Create a cosine function for spindle model input,
%                  average length L1 (units: L0), amplitude A (units: L0),
%                  frequency 1Hz. Time step 0.001 s. Time vector length 5s. 
%                  Start point of cosine: 1s. 
% 
%  Date:           03-31-11
%  
%  Author:         Boshuo Wang, boshuowa@usc.edu
% 
%  Output:         triangle.mat, variable name: data
% 
%  Others:   	   .mat file is input for spindle_test_sinusoid.mdl

L1=0.995;   %average length (Mileusnic et al 2006 JNP)
A=0.012;    %amplitude
fs=1;       %frequency
T = 5;      %1 second of data
SAMPLING_RATE=1024;

%dt=0.001
dt = 1/SAMPLING_RATE;
t=linspace(0,T,T/dt+1);


L=ones(size(t))*(L1+A);

tstart=T*0.2;  % 

n_start=tstart/dt+1;n_end=1/fs/dt;
L(n_start:n_start+n_end-1) = L(n_start:n_start+n_end-1)  + A*(cos(2*pi*(0:dt:1-dt))-1);

plot(t,L);

data=[t;L];
save sinusoid.mat data
