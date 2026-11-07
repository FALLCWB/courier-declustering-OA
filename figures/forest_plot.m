% Forest plot of the F1 paired differences (S9, plan E8; G5 verdict ruling 4 applied): each model minus nearest
% courier, per start and supply level, W1 and p90 order to door, mean with its 95% bootstrap interval; dotted lines
% mark the smallest effects of interest. The p90 plot gets a second panel from -1.5 to +2 min, with an arrow at the
% edge for each point outside it. Input: contrasts.csv from sim/analysis.py. Output: forest_w1 and forest_p90
% (.pdf and .png) in out_folder.
% Run in MATLAB R2024b on CT 315: forest_plot('<folder with contrasts.csv>', '<out folder>')
function forest_plot(folder, out_folder)
    C = readtable(fullfile(folder, 'contrasts.csv'), 'TextType', 'string');
    C = C(C.family == "F1", :);
    models = ["foodmatch", "forecast", "backpressure"];
    names = ["FoodMatch (bundling off)", "Forecast-aware matching", "Mirror backpressure"];
    colors = [0.00 0.45 0.70; 0.84 0.37 0.00; 0.00 0.62 0.45];
    metrics = ["W1", "p90"];
    xlabels = ["W1 difference (min), model minus nearest courier", "p90 order to door difference (min), model minus nearest courier"];
    starts = ["big_cluster", "three_clusters", "mixed", "scattered", "burst"];
    levels = ["tight", "normal", "loose"];
    zoom = [-1.5 2];
    for k = 1:numel(metrics)
        isP90 = metrics(k) == "p90";
        fig = figure('Units', 'centimeters', 'Position', [2 2 (17 + 9 * isP90) 20], 'Color', 'w', 'Visible', 'off');
        tl = tiledlayout(fig, 1, 1 + isP90, 'TileSpacing', 'compact', 'Padding', 'compact');
        tl.OuterPosition = [0 0.04 1 0.96];   % room for the data note at the bottom
        for panel = 1:(1 + isP90)
            ax = nexttile(tl);
            hold(ax, 'on');
            labels = strings(0); y = 0; h = gobjects(1, numel(models));
            for s = numel(starts):-1:1
                for l = numel(levels):-1:1
                    y = y + 1;
                    labels(y) = strrep(starts(s), '_', ' ') + ", " + levels(l);
                    for i = 1:numel(models)
                        R = C(C.metric == metrics(k) & C.scenario == starts(s) & C.level == levels(l) & C.model == models(i), :);
                        if isempty(R), continue, end
                        yy = y + (i - 2) * 0.22;
                        lo = R.lo; hi = R.hi; m = R.mean;
                        if panel == 2                       % zoom: an arrow at the edge for a point outside
                            if m < zoom(1) || m > zoom(2)
                                edge = zoom(1) * (m < zoom(1)) + zoom(2) * (m > zoom(2));
                                text(ax, edge, yy, char(9668 * (m < zoom(1)) + 9658 * (m > zoom(2))), 'Color', colors(i, :), ...
                                     'HorizontalAlignment', 'center', 'FontSize', 8);
                                continue
                            end
                            lo = max(lo, zoom(1)); hi = min(hi, zoom(2));
                        end
                        plot(ax, [lo hi], [yy yy], '-', 'Color', colors(i, :), 'LineWidth', 1.2, 'HandleVisibility', 'off');
                        h(i) = plot(ax, m, yy, 'o', 'Color', colors(i, :), 'MarkerFaceColor', colors(i, :), 'MarkerSize', 4);
                        if metrics(k) == "W1"
                            plot(ax, -R.delta * [1 1], yy + [-0.1 0.1], ':', 'Color', [0.5 0.5 0.5], 'HandleVisibility', 'off');
                        end
                    end
                end
            end
            xline(ax, 0, 'k-', 'HandleVisibility', 'off');
            if isP90, xline(ax, 1, 'k:', 'HandleVisibility', 'off'); end
            yticks(ax, 1:y); yticklabels(ax, labels); ylim(ax, [0.4 y + 0.6]);
            if panel == 2
                xlim(ax, zoom); yticklabels(ax, []);
                title(ax, 'Zoom, -1.5 to +2 min (arrows: points outside)', 'FontWeight', 'normal', 'FontSize', 8);
            end
            grid(ax, 'on'); box(ax, 'on');
        end
        xlabel(tl, xlabels(k));                         % one label under both panels
        if metrics(k) == "W1"
            hr = plot(ax, nan, nan, ':', 'Color', [0.5 0.5 0.5]); rule = "Smallest effect (10% of nearest W1)";
        else
            hr = plot(ax, nan, nan, 'k:'); rule = "Delivery-cost threshold (+1 min)";
        end
        valid = isgraphics(h);
        lg = legend(ax, [h(valid) hr], [names(valid) rule], 'NumColumns', 2); lg.Layout.Tile = 'south'; lg.Box = 'off';
        annotation('textbox', [0.55 0.0 0.45 0.03], 'String', 'This research was supported by data provided by Meituan.', ...
                   'EdgeColor', 'none', 'FontSize', 7, 'HorizontalAlignment', 'right');
        exportgraphics(fig, fullfile(out_folder, "forest_" + lower(metrics(k)) + ".pdf"), 'ContentType', 'vector');
        exportgraphics(fig, fullfile(out_folder, "forest_" + lower(metrics(k)) + ".png"), 'Resolution', 300);
        close(fig);
    end
end
