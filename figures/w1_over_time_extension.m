% W1 over the evening for the ten models (X9, Paper A). Input: w1_over_time_extension.csv from
% scripts/x9_w1_over_time.py (normal supply, fitted behavior, arm C at 100% obedience, seeds 1001 on).
% Rows: the big cluster (from 17:00) and the meet-up (from 19:00); columns: arm A, arm B, arm C. Each tile shows its
% arm's models with nearest courier, and nearest courier from the scattered start as a dashed grey line (G5 verdict,
% ruling 5). Clock-time axis labels. Output: w1_over_time_extension.pdf and .png.
% Run in MATLAB R2024b on CT 315: w1_over_time_extension('<folder with the csv>')
function w1_over_time_extension(folder)
    T = readtable(fullfile(folder, 'w1_over_time_extension.csv'), 'TextType', 'string');
    arms = {["nearest", "foodmatch", "forecast", "backpressure", "xu", "li", "jahanshahi"], ["nearest", "auad"], ...
            ["nearest", "zhu", "jusup"]};
    armNames = ["Arm A: which courier", "Arm B: when to assign", "Arm C: moving idle couriers (100% obedient)"];
    names = containers.Map(["nearest", "foodmatch", "forecast", "backpressure", "xu", "li", "jahanshahi", "auad", "zhu", "jusup"], ...
        ["Nearest courier", "FoodMatch (bundling off)", "Forecast-aware matching", "Mirror backpressure", "Xu et al.", ...
         "Li et al.", "Jahanshahi et al. (DQN)", "Auad et al.", "Zhu et al.", "Jusup et al."]);
    colors = containers.Map(["nearest", "foodmatch", "forecast", "backpressure", "xu", "li", "jahanshahi", "auad", "zhu", "jusup"], ...
        {[0.20 0.20 0.20], [0.00 0.45 0.70], [0.84 0.37 0.00], [0.00 0.62 0.45], [0.80 0.47 0.65], [0.94 0.89 0.26], ...
         [0.34 0.71 0.91], [0.90 0.60 0.00], [0.00 0.45 0.70], [0.84 0.37 0.00]});
    starts = ["big_cluster", "meetup"];
    startNames = ["Big cluster at 17:00", "Meet-up at 19:00"];
    ref = T(T.start == "reference_scattered", :);
    yl = [0, 5 * ceil(max(T.hi) / 5)];
    fig = figure('Units', 'centimeters', 'Position', [2 2 26 15], 'Color', 'w', 'Visible', 'off');
    tl = tiledlayout(fig, 2, 3, 'TileSpacing', 'compact', 'Padding', 'compact');
    tl.OuterPosition = [0 0.04 1 0.96];
    for r = 1:2
        for c = 1:3
            ax = nexttile(tl); hold(ax, 'on');
            x = 17 + ref.minute / 60;
            plot(ax, x, ref.mean, '--', 'Color', [0.6 0.6 0.6], 'LineWidth', 1.2, 'DisplayName', 'Nearest courier, scattered start');
            for m = arms{c}
                S = T(T.start == starts(r) & T.model == m, :);
                x = 17 + S.minute / 60;
                fill(ax, [x; flipud(x)], [S.lo; flipud(S.hi)], colors(m), 'FaceAlpha', 0.12, 'EdgeColor', 'none', ...
                     'HandleVisibility', 'off');
                plot(ax, x, S.mean, 'LineWidth', 1.4, 'Color', colors(m), 'DisplayName', names(m));
            end
            ylim(ax, yl); xlim(ax, [17 21]); grid(ax, 'on'); box(ax, 'on');
            xticks(ax, 17:21); xticklabels(ax, ["17:00", "18:00", "19:00", "20:00", "21:00"]);
            if r == 1, title(ax, armNames(c), 'FontWeight', 'normal', 'FontSize', 9); end
            if c == 1, ylabel(ax, {startNames(r), 'W1 (min of riding)'}); end
            if r == 2, xlabel(ax, 'Time of day'); end
            lg = legend(ax, 'Location', 'southoutside', 'NumColumns', 2, 'FontSize', 6); lg.Box = 'off';
        end
    end
    annotation('textbox', [0.55 0.0 0.45 0.03], 'String', 'This research was supported by data provided by Meituan.', ...
               'EdgeColor', 'none', 'FontSize', 7, 'HorizontalAlignment', 'right');
    exportgraphics(fig, fullfile(folder, 'w1_over_time_extension.pdf'), 'ContentType', 'vector');
    exportgraphics(fig, fullfile(folder, 'w1_over_time_extension.png'), 'Resolution', 300);
    close(fig);
end
