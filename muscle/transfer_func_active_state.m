% Shadmehr muscle model gives the h(t) of active_state
% h(t) = a*exp(-t/c) + b*exp(-t/d)
% H(s) = a/(s+c) + b/(s+d)
% This func: H(s) -> H(z)

a = 48144*128;
b = 45845*128;
c = 1/0.0326;
d = 1/0.034;
SAMPLING_RATE = 1024; % in Hz
num = [0 (a-b) (a*d - b*c)];
den = [1 (c+d) c*d];
tf_a = tf(num, den)
tf_a_digital = c2d(tf_a, 1/SAMPLING_RATE, 'zoh')