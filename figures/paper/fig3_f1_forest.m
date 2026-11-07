% Paper A Fig. 3: first round, F1 (FIGURES-SPEC.md). Two columns (the class's \textwidth, 6.99 in) x 3.6 in: (a) W1 and (b) p90 differences against
% nearest courier, 15 start-supply rows grouped by start, the three untrained assignment models.
function fig3_f1_forest(datadir, outdir)
    S = pa_style();
    T = readtable(fullfile(datadir, 'fig3_f1_forest.csv'), 'TextType', 'string');
    starts = ["big_cluster", "three_clusters", "mixed", "scattered", "burst"];
    names = ["big cluster", "three clusters", "mixed", "scattered", "burst"];
    levels = ["tight", "normal", "loose"];
    cells = strings(0, 2);
    for s = starts, for l = levels, cells(end + 1, :) = [s l]; end, end %#ok<AGROW>
    groups = [names' string(1:3:13)' string(3:3:15)'];
    models = ["foodmatch", "forecast", "backpressure"];
    W = S.W2; H = 3.6; left = 1.35; right = 0.12; gap = 0.25; top = 0.22; bottom = 0.78;
    pw = (W - left - right - gap) / 2; ph = H - top - bottom;
    fig = figure('Units', 'inches', 'Position', [1 1 W H], 'Color', 'w', 'Visible', 'off');
    ax1 = pa_axes(fig, [left bottom pw ph], S);
    ax2 = pa_axes(fig, [left + pw + gap bottom pw ph], S);
    w = T(T.metric == "W1", :);
    xl = [floor(min([w.lo; -w.delta]) * 4) / 4, ceil(max(w.hi) * 4) / 4];
    opts = struct('sesoi', true, 'plusone', false, 'separators', [3 6 9 12]);
    pa_forest(ax1, T, cells, models, "W1", xl, 0.28, S, opts);
    opts.sesoi = false; opts.plusone = true;
    pa_forest(ax2, T, cells, models, "p90", [-3 3], 0.28, S, opts);
    pa_rowlabels(ax1, cells, groups, S);
    set(ax2, 'YTick', 1:size(cells, 1), 'YTickLabel', {});
    xlabel(ax1, 'W1 difference (min)', 'FontName', S.font, 'FontSize', S.fs);
    xlabel(ax2, 'p90 difference (min)', 'FontName', S.font, 'FontSize', S.fs);
    pa_letter(ax1, 'a', S); pa_letter(ax2, 'b', S);
    h = pa_handles(ax2, models, S);
    pa_legend(ax2, h, arrayfun(@(m) S.name(char(m)), models, 'UniformOutput', false), 3, 0.04, S);
    pa_export(fig, fullfile(outdir, 'fig3_f1_forest.pdf'));
    close(fig);
end
