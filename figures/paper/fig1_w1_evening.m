% Paper A Fig. 1: W1 over the evening (FIGURES-SPEC.md). Two columns (the class's \textwidth, 6.99 in) x 4.4 in, panels (a) to (f): rows the big
% cluster from 17:00 and the meet-up at 19:00 (normal supply, fitted behavior, n = 150), columns the three groups (arm C
% at full obedience). Each panel: nearest courier (black), the group's models with 95% bands, and nearest courier from
% the scattered start (dashed grey); a light grey band from 20:30 to 21:00, explained in the caption.
function fig1_w1_evening(datadir, outdir)
    S = pa_style();
    T = readtable(fullfile(datadir, 'fig1_w1_evening.csv'), 'TextType', 'string');
    ref = T(T.start == "reference_scattered" & T.model == "nearest", :);
    starts = ["big_cluster", "meetup"]; ylims = [0 25; 0 15];
    W = S.W2; H = 4.4; left = 0.55; right = 0.22; gap = 0.42; top = 0.2; vgap = 0.22; bottom = 0.84;
    pw = (W - left - right - 2 * gap) / 3; ph = (H - top - vgap - bottom) / 2;
    fig = figure('Units', 'inches', 'Position', [1 1 W H], 'Color', 'w', 'Visible', 'off');
    letter = 'a';
    for r = 1:2
        y0 = bottom + (2 - r) * (ph + vgap);
        for c = 1:3
            ax = pa_axes(fig, [left + (c - 1) * (pw + gap) y0 pw ph], S);
            ax.XGrid = 'on'; ax.YGrid = 'on';
            yl = ylims(r, :);
            patch(ax, [20.5 21 21 20.5], [yl(1) yl(1) yl(2) yl(2)], S.band, 'EdgeColor', 'none', 'HandleVisibility', 'off');
            plot(ax, 17 + ref.minute / 60, ref.mean, '--', 'Color', S.ref, 'LineWidth', S.lwRef, 'HandleVisibility', 'off');
            for m = ["nearest", S.groups{c}]
                D = T(T.start == starts(r) & T.model == m, :);
                x = 17 + D.minute / 60; col = S.color(char(m));
                fill(ax, [x; flipud(x)], [D.lo; flipud(D.hi)], col, 'FaceAlpha', S.alpha, 'EdgeColor', 'none', ...
                     'HandleVisibility', 'off');
                p = plot(ax, x, D.mean, '-', 'Color', col, 'LineWidth', S.lw, 'HandleVisibility', 'off');
                if m ~= "nearest"
                    set(p, 'Marker', S.marker(char(m)), 'MarkerIndices', 1:30:numel(x), 'MarkerSize', S.ms, ...
                        'MarkerFaceColor', col, 'MarkerEdgeColor', col);
                end
            end
            xlim(ax, [17 21]); ylim(ax, yl);
            set(ax, 'XTick', 17:21, 'XTickLabel', {'17:00', '18:00', '19:00', '20:00', '21:00'}, 'XTickLabelRotation', 0);
            if r == 1, set(ax, 'XTickLabel', {}); end
            if c == 1
                ylabel(ax, 'W1 (min of riding)', 'FontName', S.font, 'FontSize', S.fs);
                ax.YLabel.Units = 'inches'; ax.YLabel.Position(1) = -0.36;     % clear of the tick labels
            else
                set(ax, 'YTickLabel', {});
            end
            pa_letter(ax, letter, S); letter = char(letter + 1);
        end
    end
    models = S.models;                                   % nearest courier first, the dashed reference last
    h = gobjects(1, numel(models) + 1);
    for i = 1:numel(models)
        col = S.color(char(models(i)));
        h(i) = plot(ax, nan, nan, '-', 'Color', col, 'LineWidth', S.lw, 'Marker', S.marker(char(models(i))), ...
                    'MarkerSize', S.ms, 'MarkerFaceColor', col, 'MarkerEdgeColor', col);
    end
    h(end) = plot(ax, nan, nan, '--', 'Color', S.ref, 'LineWidth', S.lwRef);
    labels = [arrayfun(@(m) S.name(char(m)), models, 'UniformOutput', false), {S.refName}];
    pa_legend(ax, h, labels, 4, 0.04, S);
    pa_export(fig, fullfile(outdir, 'fig1_w1_evening.pdf'));
    close(fig);
end
