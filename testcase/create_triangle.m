%  Function:       create_triangle.m
% 
%  Description:    Generate test cases based on Mileusnic et al 2006 JNP.
%                  Create a triangle function for spindle model input,
%                  starting length L1 (units: L0), final length L2 (units: 
%                  L0), ramp slope V (units: L0/s). Time step 0.001 s. Time
%                  vector length 5s. Start point of triangle: 1s. 
% 
%  Date:           03-31-11
%  
%  Author:         Boshuo Wang, boshuowa@usc.edu
% 
%  Output:         triangle.mat, variable name: data
% 
%  Others:         .mat file is input for spindle_test_triangle.mdl
% 

L1=0.90;        %min length     (Mileusnic et al 2006 JNP)
L2=1.08;        %max length
V=0.18;         %rising velocity (L0/s)

dt=0.001;
t=linspace(0,5,5/dt+1);

L=ones(size(t))*L1;

tstart=1;

n1=tstart/dt+1;n2=round((L2-L1)/V/dt);

L(n1:n1+n2-1) = L(n1:n1+n2-1)  +linspace(0,(L2-L1),n2);

L(n1+n2:n1+n2*2-1)=L(n1+n2:n1+n2*2-1)+linspace((L2-L1),0,n2);

plot(t,L);

data=[t;L];
save triangle.mat data