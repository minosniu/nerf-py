x=-10:.01:10
alpha=1.0
beta=8

y=sign(x).*(abs(x).^0.25)
y2=sign(x).*((beta*abs(x)+alpha).^0.25 - alpha^0.25)

subplot(2,1,1)
plot(x,y)
axis([-10 10 -2 2])
subplot(2,1,2)
plot(x,y2)
axis([-10 10 -2 2])