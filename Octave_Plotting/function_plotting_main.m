clc
clear
close all
p1 = [1,5];
p2 = [7,5];
a=1;
b=2;
x = linspace(-10,10, 10000);
y = linspace(-10,10, 10000);
%y = 0.5*(10-(35)^(0.5) * (4*x^2 -32*x+63)^(0.5))
%y = 0.5*(10-(35)^(0.5) * (4*x.^2 -32.*x+63).^(0.5));
%y = (sqrt(b^2*a^2 + x.^2))/a
%y1 = -sqrt(-b^2*(a^2 - x.^2))/a;
%y2 = sqrt(-b^2*(a^2 - x.^2))/a;


for i = 1:length(x)
  for j=1:length(y)
    d_pix = 
  endfor



scatter(p1(1), p1(2))
hold on
scatter(p2(1), p2(2))




plot(x,y1) 

plot(x,y2) 