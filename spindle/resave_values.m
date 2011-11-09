%% Save to file
% Ia = fr_Ia.signals.values;
% II = fr_II.signals.values;
% lce = muscle_length.signals.values;


%% Cond 1 ::Plot conditions Dyn Lo -> Hi, Sta Lo
figure(1); 
cond_name = 'dyn_LH_sta_L.pdf'
plot_Loeb_Ia_II('Loeb_spindle_ramphold_d40_s40', 'Loeb_spindle_ramphold_d80_s40');
set(gcf, 'PaperPosition', [0 0 8.5 4]);
print('-dpdf', cond_name);

%% Cond 2 :: Plot conditions Dyn Lo -> Hi, Sta Hi
figure(2); 
cond_name = 'dyn_LH_sta_H.pdf';
plot_Loeb_Ia_II('Loeb_spindle_ramphold_d40_s80', 'Loeb_spindle_ramphold_d80_s80');
set(gcf, 'PaperPosition', [0 0 8.5 4]);
set(gcf, 'PaperSize', [8.5 4]);
print('-dpdf', cond_name);


%% Cond 3 :: Plot conditions Dyn Lo, Sta Lo -> Hi
figure(3); 
cond_name = 'dyn_L_sta_LH.pdf';
plot_Loeb_Ia_II('Loeb_spindle_ramphold_d40_s40', 'Loeb_spindle_ramphold_d40_s80');
set(gcf, 'PaperPosition', [0 0 8.5 4]);
set(gcf, 'PaperSize', [8.5 4]);
print('-dpdf', cond_name);


%% Cond 4 :: Plot conditions Dyn Hi, Sta Lo -> Hi
figure(4); 
cond_name = 'dyn_H_sta_LH.pdf';
plot_Loeb_Ia_II('Loeb_spindle_ramphold_d80_s40', 'Loeb_spindle_ramphold_d80_s80');
set(gcf, 'PaperPosition', [0 0 8.5 4]);
set(gcf, 'PaperSize', [8.5 4]);
print('-dpdf', cond_name);


