% One forest panel (FIGURES-SPEC.md rules 7, 9 and 10): cell rows from top to bottom, the models dodged inside a row in
% legend order, the 95% interval as a line and the mean as the model's marker (filled when the contrast is established
% after Holm, open when not). Grey reference marks behind the data: the zero line, the smallest-effect tick at -delta
% (opts.sesoi) and the dotted +1 min line (opts.plusone). A mean outside the limits is drawn as an arrowhead at the limit
% with its value printed beside it; an interval is cut at the limits.
% T: table (scenario, level, model, metric, mean, lo, hi, delta, established); cells: n x 2 strings (scenario, level).
function pa_forest(ax, T, cells, models, metric, xl, dodge, S, opts)
    n = size(cells, 1);
    xlim(ax, xl); ylim(ax, [0.5 n + 0.5]);
    ax.XGrid = 'on'; ax.YGrid = 'off';
    xline(ax, 0, '-', 'Color', S.ref, 'LineWidth', S.lwAxes, 'HandleVisibility', 'off', 'Layer', 'bottom');
    if opts.plusone
        xline(ax, 1, ':', 'Color', S.ref, 'LineWidth', S.lwRef, 'HandleVisibility', 'off', 'Layer', 'bottom');
    end
    for b = opts.separators
        yline(ax, n - b + 0.5, '-', 'Color', S.grid, 'LineWidth', S.lwGrid, 'HandleVisibility', 'off', 'Layer', 'bottom');
    end
    k = numel(models);
    perIn = diff(xl) / ax.Position(3);                  % data units per inch along x
    lineH = 0.10 * n / ax.Position(4);                  % stacking pitch: 0.1 in, above the 0.08-in digit height
    for y = 1:n
        clipL = zeros(0, 4); clipR = zeros(0, 4);       % [value, arrow y, model index, established], legend order
        yc = n - y + 1;
        R = T(T.scenario == cells(y, 1) & T.level == cells(y, 2) & T.metric == metric, :);
        if opts.sesoi && ~isempty(R) && -R.delta(1) >= xl(1)
            plot(ax, -R.delta(1) * [1 1], yc + [-0.42 0.42], '-', 'Color', S.ref, 'LineWidth', S.lwAxes, ...
                 'HandleVisibility', 'off');
        end
        for i = 1:k
            m = models(i);
            r = R(R.model == m, :);
            if isempty(r), continue, end
            yy = yc + ((k + 1) / 2 - i) * dodge;
            c = S.color(char(m)); mk = S.marker(char(m));
            est = r.established(1);
            if isstring(est) || ischar(est), est = strcmpi(string(est), "true"); end   % CSV text "True"/"False"
            face = c; if ~est, face = [1 1 1]; end
            lo = max(r.lo(1), xl(1)); hi = min(r.hi(1), xl(2));
            if hi > lo
                plot(ax, [lo hi], [yy yy], '-', 'Color', c, 'LineWidth', S.lw, 'HandleVisibility', 'off');
            end
            mu = r.mean(1);
            if mu < xl(1) || mu > xl(2)
                if mu < xl(1)
                    edge = xl(1); arrow = '<'; clipL(end + 1, :) = [mu yy i est]; %#ok<AGROW>
                else
                    edge = xl(2); arrow = '>'; clipR(end + 1, :) = [mu yy i est]; %#ok<AGROW>
                end
                plot(ax, edge, yy, arrow, 'MarkerSize', S.ms, 'MarkerFaceColor', face, ...
                     'MarkerEdgeColor', c, 'LineWidth', 0.75, 'HandleVisibility', 'off');
            else
                plot(ax, mu, yy, mk, 'MarkerSize', S.ms, 'MarkerFaceColor', face, 'MarkerEdgeColor', c, ...
                     'LineWidth', 0.75, 'HandleVisibility', 'off');
            end
        end
        % each cut value beside its arrows, with the model's own marker before it (Filipe, 2026-11-06: "▲ -9.9"), in the
        % dodge order (top model first), stacked 0.1 in apart and centred on the arrows; a white box as tall as the digits
        % (0.085 in, under the text and the data) keeps the grey reference lines off the digits without covering the
        % neighbouring value. Left limit: arrow, marker, value; right limit: marker, value, arrow.
        for side = 1:2
            v = clipL; if side == 2, v = clipR; end
            k2 = size(v, 1);
            if k2 == 0, continue, end
            for j = 1:k2
                yj = mean(v(:, 2)) + ((k2 + 1) / 2 - j) * lineH;
                m = models(v(j, 3)); c = S.color(char(m)); face = c;
                if ~v(j, 4), face = [1 1 1]; end
                if side == 1
                    plot(ax, xl(1) + 0.075 * perIn, yj, S.marker(char(m)), 'MarkerSize', S.ms, 'MarkerFaceColor', face, ...
                         'MarkerEdgeColor', c, 'LineWidth', 0.75, 'HandleVisibility', 'off');
                    t = text(ax, xl(1) + 0.113 * perIn, yj, sprintf('%.1f', v(j, 1)), 'FontName', S.font, 'FontSize', S.fs, ...
                             'HorizontalAlignment', 'left', 'VerticalAlignment', 'middle', 'Interpreter', 'none');
                    digit_box(ax, t, yj, perIn, n);
                else
                    t = text(ax, xl(2) - 0.075 * perIn, yj, sprintf('%.1f', v(j, 1)), 'FontName', S.font, 'FontSize', S.fs, ...
                             'HorizontalAlignment', 'right', 'VerticalAlignment', 'middle', 'Interpreter', 'none');
                    digit_box(ax, t, yj, perIn, n);
                    e = t.Extent;
                    plot(ax, e(1) - 0.04 * perIn, yj, S.marker(char(m)), 'MarkerSize', S.ms, 'MarkerFaceColor', face, ...
                         'MarkerEdgeColor', c, 'LineWidth', 0.75, 'HandleVisibility', 'off');
                end
            end
        end
    end
end


function digit_box(ax, t, yj, perIn, n)
    % white rectangle the height of the digits (0.085 in) behind a printed value, under every data object
    e = t.Extent;
    h = 0.085 * n / ax.Position(4);
    p = patch(ax, e(1) - 0.01 * perIn + [0 1 1 0] * (e(3) + 0.02 * perIn), yj + [-1 -1 1 1] * h / 2, 'w', ...
              'EdgeColor', 'none', 'HandleVisibility', 'off');
    uistack(p, 'bottom');
end
