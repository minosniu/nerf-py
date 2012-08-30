function [] = plot_Loeb_Ia_II(cond1, cond2, y_range)
labelsize = 14;
lw = 2.0;
xinit = 800;
plotlen = 1.0 * 1024;
time = [0:1/1024:1.0];

subplot(311); hold on;
load(cond1);
plot(time, lce(xinit : xinit + plotlen), 'b', 'linewidth', lw);
xlabel('Time (s)', 'fontsize', labelsize);
ylabel('Muscle stretch (%)', 'fontsize', labelsize);
% xlim([0.95 1.15]);
ylim([0.95 1.15]);
set(gca,'fontsize', labelsize);

subplot(312); hold on;
load(cond1);
plot(time, Ia(xinit : xinit + plotlen), 'b', 'linewidth', lw);
load(cond2);
plot(time, Ia(xinit : xinit + plotlen), 'r', 'linewidth', lw);
ylim([0 400]);
xlabel('Time (s)', 'fontsize', labelsize);
ylabel('Ia Firing Rate (Hz)', 'fontsize', labelsize);
set(gca,'fontsize', labelsize);


subplot(313); hold on;
load(cond1);
plot(time, II(xinit : xinit + plotlen), 'b', 'linewidth', lw);
load(cond2);
plot(time, II(xinit : xinit + plotlen), 'r', 'linewidth', lw);
ylim([0 150]);
xlabel('Time (s)', 'fontsize', labelsize);
ylabel('II Firing Rate (Hz)', 'fontsize', labelsize);
set(gca,'fontsize', labelsize);


