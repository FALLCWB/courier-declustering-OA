% Paper A Fig. 4: Q1, E1 (FIGURES-SPEC.md). Two columns (the class's \textwidth, 6.99 in) x 2.5 in, four panels of the six Q1 cells: (a) W1 of the
% learned assignment and holding models, (b) W1 of the models moving idle couriers, (c) and (d) the same for p90.
function fig4_q1_forest(datadir, outdir)
    S = pa_style();
    T = readtable(fullfile(datadir, 'fig4_q1_forest.csv'), 'TextType', 'string');
    levels = ["tight", "normal", "loose"];
    cells = [repmat("scattered", 3, 1) levels'; repmat("burst", 3, 1) levels'];
    groups = ["scattered" "1" "3"; "burst" "4" "6"];
    learned = ["xu", "li", "auad"]; moving = ["zhu", "jusup"];
    W = S.W2; H = 2.5; left = 1.18; right = 0.12; g1 = 0.2; g2 = 0.32; top = 0.22; bottom = 0.74;
    pw = (W - left - right - 2 * g1 - g2) / 4; ph = H - top - bottom;
    x0 = left + [0, pw + g1, 2 * pw + g1 + g2, 3 * pw + 2 * g1 + g2];
    fig = figure('Units', 'inches', 'Position', [1 1 W H], 'Color', 'w', 'Visible', 'off');
    ax = gobjects(1, 4);
    for i = 1:4, ax(i) = pa_axes(fig, [x0(i) bottom pw ph], S); end
    w = T(T.metric == "w1_rule_min", :);
    xl = [floor(min([w.lo; -w.delta]) * 2) / 2, ceil(max(w.hi) * 2) / 2];
    o1 = struct('sesoi', true, 'plusone', false, 'separators', 3);
    o2 = struct('sesoi', false, 'plusone', true, 'separators', 3);
    pa_forest(ax(1), T, cells, learned, "w1_rule_min", xl, 0.25, S, o1);
    pa_forest(ax(2), T, cells, moving, "w1_rule_min", xl, 0.25, S, o1);
    pa_forest(ax(3), T, cells, learned, "p90_c2d_min", [-3 4], 0.25, S, o2);
    pa_forest(ax(4), T, cells, moving, "p90_c2d_min", [-3 4], 0.25, S, o2);
    pa_rowlabels(ax(1), cells, groups, S);
    for i = 2:4, set(ax(i), 'YTick', 1:6, 'YTickLabel', {}); end
    for i = 1:2, xlabel(ax(i), 'W1 difference (min)', 'FontName', S.font, 'FontSize', S.fs); end
    for i = 3:4, xlabel(ax(i), 'p90 difference (min)', 'FontName', S.font, 'FontSize', S.fs); end
    for i = 1:4, pa_letter(ax(i), char('a' + i - 1), S); end
    models = [learned moving];
    h = pa_handles(ax(4), models, S);
    pa_legend(ax(4), h, arrayfun(@(m) S.name(char(m)), models, 'UniformOutput', false), 5, 0.04, S);
    pa_export(fig, fullfile(outdir, 'fig4_q1_forest.pdf'));
    close(fig);
end
