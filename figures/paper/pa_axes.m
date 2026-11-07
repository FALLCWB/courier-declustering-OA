% An axes at an exact position in inches with the Paper A style (FIGURES-SPEC.md rules 2, 7 and 8).
function ax = pa_axes(fig, pos, S)
    ax = axes(fig, 'Units', 'inches', 'Position', pos, 'FontName', S.font, 'FontSize', S.fs, 'LineWidth', S.lwAxes, ...
              'TickDir', 'out', 'Box', 'off', 'Layer', 'bottom', 'GridColor', S.grid, 'GridAlpha', 1, ...
              'XColor', [0 0 0], 'YColor', [0 0 0], 'TickLength', [0.012 0.012]);
    try
        ax.GridLineWidth = S.lwGrid;
    catch
    end
    hold(ax, 'on');
end
