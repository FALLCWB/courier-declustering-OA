% Forest plots of E1 (Q1, prevent) and E2 (Q2, undo) for Paper A (X9): each model minus nearest courier, per cell,
% mean with its 95% bootstrap interval, fitted behavior, arm C at 100% obedience. Dotted marks: the smallest effects
% (10% of nearest courier's mean for W1; +1 min for p90). p90 plots get a second panel from -1.5 to +2 min, with an
% arrow at the edge for each point outside it (G5 verdict, ruling 4). Input: contrasts.csv from
% sim/analysis_extension.py. Output: forest_e1_w1, forest_e1_p90, forest_e2_w1_60 and forest_e2_p90 (.pdf and .png).
% Run in MATLAB R2024b on CT 315: forest_plot_extension('<folder with contrasts.csv>')
function forest_plot_extension(folder)
    C = readtable(fullfile(folder, 'contrasts.csv'), 'TextType', 'string');
    q1 = ["scattered", "burst"]; q2 = ["big_cluster", "three_clusters", "mixed"]; levels = ["tight", "normal", "loose"];
    new5 = ["xu", "li", "auad", "zhu", "jusup"]; frozen3 = ["foodmatch", "forecast", "backpressure"];
    one("E1", "w1_rule_min", q1, levels, false, new5, "W1 difference (min)", "forest_e1_w1");
    one("E1", "p90_c2d_min", q1, levels, false, new5, "p90 order to door difference (min)", "forest_e1_p90");
    one("E2", "w1_rule_60min_after_min", q2, levels, true, [frozen3 new5], "W1 over the first 60 min, difference (min)", "forest_e2_w1_60");
    one("E2", "p90_c2d_min", q2, levels, true, [frozen3 new5], "p90 order to door difference (min)", "forest_e2_p90");

    function one(fam, metric, starts, levels, meetup, models, xlab, file)
        R = C(C.family == fam & C.metric == metric, :);
        cells = strings(0, 2);
        for s = starts, for l = levels, cells(end + 1, :) = [s l]; end, end
        if meetup, cells(end + 1, :) = ["meetup" "normal"]; end
        isP90 = metric == "p90_c2d_min";
        fig = figure('Units', 'centimeters', 'Position', [2 2 (17 + 9 * isP90) 4 + 1.2 * size(cells, 1)], 'Color', 'w', 'Visible', 'off');
        tl = tiledlayout(fig, 1, 1 + isP90, 'TileSpacing', 'compact', 'Padding', 'compact');
        tl.OuterPosition = [0 0.05 1 0.95];
        lims = {[], [-1.5 2]};
        for panel = 1:(1 + isP90)
            ax = nexttile(tl); hold(ax, 'on');
            h = gobjects(1, numel(models));
            cmap = lines(numel(models));
            for y = 1:size(cells, 1)
                for i = 1:numel(models)
                    r = R(R.scenario == cells(y, 1) & R.level == cells(y, 2) & R.model == models(i), :);
                    if isempty(r), continue, end
                    yy = size(cells, 1) - y + 1 + (i - (numel(models) + 1) / 2) * 0.08;
                    lo = r.lo; hi = r.hi; m = r.mean;
                    if panel == 2                                   % zoom: clip and mark points outside with an arrow
                        L = lims{2};
                        if m < L(1) || m > L(2)
                            edge = L(1) * (m < L(1)) + L(2) * (m > L(2));
                            text(ax, edge, yy, char(9668 * (m < L(1)) + 9658 * (m > L(2))), 'Color', cmap(i, :), ...
                                 'HorizontalAlignment', 'center', 'FontSize', 7);
                            continue
                        end
                        lo = max(lo, L(1)); hi = min(hi, L(2));
                    end
                    plot(ax, [lo hi], [yy yy], '-', 'Color', cmap(i, :), 'LineWidth', 1.1, 'HandleVisibility', 'off');
                    h(i) = plot(ax, m, yy, 'o', 'Color', cmap(i, :), 'MarkerFaceColor', cmap(i, :), 'MarkerSize', 3.5, ...
                                'DisplayName', models(i));
                    if ~isP90
                        plot(ax, -r.delta * [1 1], yy + [-0.04 0.04], ':', 'Color', [0.5 0.5 0.5], 'HandleVisibility', 'off');
                    end
                end
            end
            xline(ax, 0, 'k-', 'HandleVisibility', 'off');
            if isP90, xline(ax, 1, 'k:', 'HandleVisibility', 'off'); end
            if panel == 2, xlim(ax, lims{2}); title(ax, 'Zoom, -1.5 to +2 min', 'FontWeight', 'normal', 'FontSize', 8); end
            yticks(ax, 1:size(cells, 1));
            yticklabels(ax, flipud(strrep(cells(:, 1), '_', ' ') + ", " + cells(:, 2)));
            if panel == 2, yticklabels(ax, []); end
            ylim(ax, [0.5 size(cells, 1) + 0.5]); grid(ax, 'on'); box(ax, 'on');
        end
        xlabel(tl, xlab + ", model minus nearest courier");     % one label under both panels
        valid = isgraphics(h);
        lg = legend(h(valid), models(valid), 'NumColumns', 4); lg.Layout.Tile = 'south'; lg.Box = 'off';
        annotation('textbox', [0.55 0.0 0.45 0.03], 'String', 'This research was supported by data provided by Meituan.', ...
                   'EdgeColor', 'none', 'FontSize', 7, 'HorizontalAlignment', 'right');
        exportgraphics(fig, fullfile(folder, file + ".pdf"), 'ContentType', 'vector');
        exportgraphics(fig, fullfile(folder, file + ".png"), 'Resolution', 300);
        close(fig);
    end
end
