% Paper A figure style (FIGURES-SPEC.md, 2026-11-06): one font at 8 pt, panel letters 9 pt bold, a fixed color and
% marker per model (Okabe-Ito based), grey reference marks behind the data, line widths in points.
function S = pa_style()
    S.font = 'Helvetica'; S.fs = 8; S.fsLetter = 9;
    % Printed widths of the paper's class (ieeeaccess.cls, test compile 2026-11-06): \textwidth 505.12 pt and
    % \columnwidth 242.67 pt, slightly under the 7.16 and 3.5 in of the generic IEEE guide; drawing at the class widths
    % keeps rule 1 (nothing scaled, 8 pt stays 8 pt).
    S.W2 = 505.12 / 72.27; S.W1 = 242.67 / 72.27;                % TeX points: 72.27 per inch
    S.models = ["nearest", "foodmatch", "forecast", "backpressure", "xu", "li", "auad", "zhu", "jusup"];
    names = {'Nearest courier', 'FoodMatch', 'Forecast-aware matching', 'Mirror backpressure', 'Xu et al.', ...
             'Li et al.', 'Auad et al. (holding)', 'Zhu et al.', 'Jusup et al.'};
    hex = {'#000000', '#0072B2', '#D55E00', '#009E73', '#E69F00', '#CC79A7', '#56B4E9', '#882255', '#117733'};
    marks = {'none', 'o', 's', 'd', '^', 'v', 'h', 'p', '>'};
    S.name = containers.Map(cellstr(S.models), names);
    S.color = containers.Map(cellstr(S.models), cellfun(@hex2rgb, hex, 'UniformOutput', false));
    S.marker = containers.Map(cellstr(S.models), marks);
    S.groups = {["foodmatch", "forecast", "backpressure"], ["xu", "li", "auad"], ["zhu", "jusup"]};
    S.refName = 'Nearest courier, scattered start';
    S.ref = hex2rgb('#8C8C8C'); S.grid = hex2rgb('#E0E0E0'); S.band = hex2rgb('#F2F2F2'); S.road = hex2rgb('#D9D9D9');
    S.lw = 1.25; S.lwRef = 1.0; S.lwGrid = 0.5; S.lwAxes = 0.75; S.ms = 4; S.alpha = 0.15;
end

function c = hex2rgb(h)
    c = sscanf(h(2:end), '%2x', [1 3]) / 255;
end
