% Paper A Fig. 2: the fleet on the map (FIGURES-SPEC.md). Two columns (the class's \textwidth, 6.99 in) x 4.0 in, a 300-dpi PNG at printed size
% (made from this vector PDF after its fonts are embedded, so the text is Helvetica):
% rows nearest courier and constrained mean-field RL (Jusup et al., 100% obedient), columns 17:00, 17:30 and 18:00;
% mixed start, normal supply, seed 1001. Same extent and scale in every panel; roads #D9D9D9 at 0.3 pt; couriers as
% 2.5-pt dots by state; a 5-km scale bar in panel (a).
function fig2_fleet_map(fig2dir, outdir)
    S = pa_style();
    P = readtable(fullfile(fig2dir, 'fig2_positions.csv'), 'TextType', 'string');
    R = readmatrix(fullfile(fig2dir, 'fig2_roads.csv'));
    models = ["nearest", "jusup"]; rowNames = {'Nearest courier', 'Jusup et al.'};
    minutes = [0 30 60]; colNames = {'17:00', '17:30', '18:00'};
    states = ["idle", "pickup", "loaded"];
    stateNames = {'Idle', 'Riding to a pickup or waiting', 'Carrying food'};
    stateColor = {[0 114 178] / 255, [230 159 0] / 255, [204 121 167] / 255};
    W = S.W2; H = 4.0; left = 0.22; right = 0.04; gap = 0.06; top = 0.2; vgap = 0.06; bottom = 0.3;
    pw = (W - left - right - 2 * gap) / 3; ph = (H - top - vgap - bottom) / 2;
    % one extent for every panel: the couriers' 1st to 99th percentiles, widened to the panel's shape so the map fills it
    xr = prctile(P.lng, [1 99]); yr = prctile(P.lat, [1 99]);
    lat0 = mean(yr); kx = 111.32 * cosd(lat0); ky = 110.57;
    wk = diff(xr) * kx; hk = diff(yr) * ky; r = pw / ph;
    if wk / hk < r
        xr = mean(xr) + [-0.5 0.5] * r * hk / kx;
    else
        yr = mean(yr) + [-0.5 0.5] * wk / r / ky;
    end
    xr = mean(xr) + [-0.5 0.5] * diff(xr) * 1.03; yr = mean(yr) + [-0.5 0.5] * diff(yr) * 1.03;
    X = [R(:, 1) R(:, 3) nan(size(R, 1), 1)]'; Y = [R(:, 2) R(:, 4) nan(size(R, 1), 1)]';
    fig = figure('Units', 'inches', 'Position', [1 1 W H], 'Color', 'w', 'Visible', 'off');
    letter = 'a';
    for r = 1:2
        y0 = bottom + (2 - r) * (ph + vgap);
        for c = 1:3
            ax = pa_axes(fig, [left + (c - 1) * (pw + gap) y0 pw ph], S);
            plot(ax, X(:), Y(:), '-', 'Color', S.road, 'LineWidth', 0.3, 'HandleVisibility', 'off');
            Q = P(P.model == models(r) & P.minute == minutes(c), :);
            for k = 1:3
                q = Q(Q.state == states(k), :);
                plot(ax, q.lng, q.lat, 'o', 'MarkerSize', 2.5, 'MarkerFaceColor', stateColor{k}, ...
                     'MarkerEdgeColor', 'none', 'LineStyle', 'none', 'HandleVisibility', 'off');
            end
            set(ax, 'XLim', xr, 'YLim', yr, 'DataAspectRatio', [1 cosd(lat0) 1], 'XColor', 'none', 'YColor', 'none', ...
                'XTick', [], 'YTick', []);
            if r == 1
                text(ax, 0.5, 1.0, colNames{c}, 'Units', 'normalized', 'FontName', S.font, 'FontSize', S.fs, ...
                     'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom');
            end
            if c == 1
                text(ax, -0.03, 0.5, rowNames{r}, 'Units', 'normalized', 'FontName', S.font, 'FontSize', S.fs, ...
                     'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', 'Rotation', 90);
            end
            if r == 1 && c == 1                          % 5-km scale bar in panel (a)
                len = 5 / (111.32 * cosd(lat0));
                x1 = xr(2) - 0.04 * diff(xr) - len; yb = yr(1) + 0.06 * diff(yr);
                plot(ax, [x1 x1 + len], [yb yb], 'k-', 'LineWidth', 1.0, 'HandleVisibility', 'off');
                text(ax, x1 + len / 2, yb + 0.015 * diff(yr), '5 km', 'FontName', S.font, 'FontSize', S.fs, ...
                     'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom');
            end
            pa_letter(ax, letter, S, 'inside'); letter = char(letter + 1);
        end
    end
    h = gobjects(1, 3);
    for k = 1:3
        h(k) = plot(ax, nan, nan, 'o', 'MarkerSize', 4, 'MarkerFaceColor', stateColor{k}, 'MarkerEdgeColor', 'none', ...
                    'LineStyle', 'none');
    end
    pa_legend(ax, h, stateNames, 3, 0.03, S);
    pa_export(fig, fullfile(outdir, 'fig2_fleet_map.pdf'));        % rasterized to a 300-dpi PNG after the fonts are embedded
    close(fig);
end
