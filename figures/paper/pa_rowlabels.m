% Row labels of a forest: supply as the y tick labels, the start as a group label to their left (FIGURES-SPEC.md, Fig. 3).
% groups: rows of (label, first row, last row) counted from the top.
function pa_rowlabels(ax, cells, groups, S)
    n = size(cells, 1);
    set(ax, 'YTick', 1:n, 'YTickLabel', flip(cellstr(cells(:, 2))), 'TickLabelInterpreter', 'none');
    h = ax.Position(4);
    for g = 1:size(groups, 1)
        yc = n - (str2double(groups(g, 2)) + str2double(groups(g, 3))) / 2 + 1;
        text(ax, -0.52, (yc - 0.5) / n * h, char(groups(g, 1)), 'Units', 'inches', 'FontName', S.font, ...
             'FontSize', S.fs, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'middle', 'Interpreter', 'none');
    end
end
