% Paper A Fig. 5: Q2, E2, with the frozen three on the fresh seeds 5001 to 5150 (FIGURES-SPEC.md). Two columns (the class's \textwidth, 6.99 in),
% 3.9 in high: rows W1 over the first 60 min and p90; columns the three groups; ten cell rows per panel (the three
% clustered starts at three supply levels, then the meet-up).
function fig5_q2_forest(datadir, outdir)
    S = pa_style();
    T = readtable(fullfile(datadir, 'fig5_q2_forest.csv'), 'TextType', 'string');
    levels = ["tight", "normal", "loose"];
    cells = strings(0, 2);
    for s = ["big_cluster", "three_clusters", "mixed"], for l = levels, cells(end + 1, :) = [s l]; end, end %#ok<AGROW>
    cells(end + 1, :) = ["meetup" "normal"];
    groups = ["big cluster" "1" "3"; "three clusters" "4" "6"; "mixed" "7" "9"; "meet-up" "10" "10"];
    W = S.W2; H = 3.9; left = 1.35; right = 0.12; gap = 0.25; top = 0.22; vgap = 0.55; bottom = 0.74;
    pw = (W - left - right - 2 * gap) / 3; ph = (H - top - vgap - bottom) / 2;
    fig = figure('Units', 'inches', 'Position', [1 1 W H], 'Color', 'w', 'Visible', 'off');
    w = T(T.metric == "w1_rule_60min_after_min", :);
    xlw = [floor(min([w.lo; -w.delta]) * 2) / 2, ceil(max(w.hi) * 2) / 2];
    metrics = ["w1_rule_60min_after_min", "p90_c2d_min"];
    labels = ["W1 over 60 min, difference (min)", "p90 difference (min)"];
    letter = 'a';
    for r = 1:2
        y0 = bottom + (2 - r) * (ph + vgap);
        for c = 1:3
            ax = pa_axes(fig, [left + (c - 1) * (pw + gap) y0 pw ph], S);
            o = struct('sesoi', r == 1, 'plusone', r == 2, 'separators', [3 6 9]);
            xl = xlw; if r == 2, xl = [-4 4]; end
            pa_forest(ax, T, cells, S.groups{c}, metrics(r), xl, 0.3, S, o);
            if c == 1
                pa_rowlabels(ax, cells, groups, S);
            else
                set(ax, 'YTick', 1:10, 'YTickLabel', {});
            end
            if c == 2
                xlabel(ax, labels(r), 'FontName', S.font, 'FontSize', S.fs);
            end
            pa_letter(ax, letter, S); letter = char(letter + 1);
        end
    end
    models = [S.groups{:}];
    h = pa_handles(ax, models, S);
    pa_legend(ax, h, arrayfun(@(m) S.name(char(m)), models, 'UniformOutput', false), 4, 0.04, S);
    pa_export(fig, fullfile(outdir, 'fig5_q2_forest.pdf'));
    close(fig);
end
