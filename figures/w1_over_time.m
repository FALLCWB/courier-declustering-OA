% W1 over the evening per model (S9, plan E8; G5 verdict ruling 5 applied). Inputs: w1_over_time.csv from
% sim/final_video.py (big-cluster start, normal supply, fitted behavior, seeds 1001 to 1030) and the per-minute curves
% of avaliacao/20261104-0031-g5-p2-gap-timing/w1_by_minute.csv (nearest courier from the scattered start, same seeds),
% drawn as a dashed grey line. Clock-time axis labels. Output: w1_over_time.pdf and .png in out_folder.
% Run in MATLAB R2024b on CT 315: w1_over_time('<csv folder>', '<w1_by_minute.csv>', '<out folder>')
function w1_over_time(folder, scattered_csv, out_folder)
    T = readtable(fullfile(folder, 'w1_over_time.csv'), 'TextType', 'string');
    P = readtable(scattered_csv, 'TextType', 'string');
    P = P(P.behavior == "fitted" & P.scenario == "scattered", :);
    models = ["nearest", "foodmatch", "forecast", "backpressure"];
    names = ["Nearest courier", "FoodMatch (bundling off)", "Forecast-aware matching", "Mirror backpressure"];
    colors = [0.20 0.20 0.20; 0.00 0.45 0.70; 0.84 0.37 0.00; 0.00 0.62 0.45];
    fig = figure('Units', 'centimeters', 'Position', [2 2 17 10], 'Color', 'w', 'Visible', 'off');
    hold on
    h = gobjects(1, numel(models) + 1);
    for i = 1:numel(models)
        S = T(T.model == models(i), :);
        x = 17 + S.minute / 60;
        fill([x; flipud(x)], [S.lo; flipud(S.hi)], colors(i, :), 'FaceAlpha', 0.15, 'EdgeColor', 'none', ...
             'HandleVisibility', 'off');
        h(i) = plot(x, S.mean, 'LineWidth', 1.5, 'Color', colors(i, :));
    end
    h(end) = plot(17 + P.minute_from_1700 / 60, P.w1_mean, '--', 'LineWidth', 1.2, 'Color', [0.6 0.6 0.6]);
    yl = [0, 5 * ceil(max(T.hi) / 5)];
    ylim(yl);
    patch([20.5 21 21 20.5], [yl(1) yl(1) yl(2) yl(2)], [0.93 0.93 0.93], 'EdgeColor', 'none', 'HandleVisibility', 'off');
    uistack(findobj(gca, 'Type', 'patch', '-and', 'FaceColor', [0.93 0.93 0.93]), 'bottom');
    text(20.47, yl(2) * 0.97, {'grey: the 30-min demand window shrinks', 'after 20:30 (no orders after 21:00)'}, 'FontSize', 7, ...
         'Color', [0.35 0.35 0.35], 'VerticalAlignment', 'top', 'HorizontalAlignment', 'right');
    xlabel('Time of day'); ylabel('W1 (min of riding)');
    xlim([17 21]); xticks(17:0.5:21);
    xticklabels(["17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00"]);
    grid on; box on
    lg = legend(h, [names "Nearest courier, scattered start"], 'Location', 'southoutside', 'Orientation', 'horizontal', ...
                'NumColumns', 3);
    lg.Box = 'off';
    annotation('textbox', [0.55 0.0 0.45 0.04], 'String', 'This research was supported by data provided by Meituan.', ...
               'EdgeColor', 'none', 'FontSize', 7, 'HorizontalAlignment', 'right');
    exportgraphics(fig, fullfile(out_folder, 'w1_over_time.pdf'), 'ContentType', 'vector');
    exportgraphics(fig, fullfile(out_folder, 'w1_over_time.png'), 'Resolution', 300);
    close(fig);
end
