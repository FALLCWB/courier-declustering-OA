% One legend per figure, outside and below the panels, horizontal (FIGURES-SPEC.md rule 5): its natural size, centred
% on the figure, with its bottom at y (inches).
function lg = pa_legend(ax, handles, labels, ncol, y, S)
    lg = legend(ax, handles, labels, 'NumColumns', ncol, 'Orientation', 'horizontal', 'Box', 'off', ...
                'FontName', S.font, 'FontSize', S.fs, 'Interpreter', 'none', 'AutoUpdate', 'off');
    lg.ItemTokenSize = [14 8];
    lg.Units = 'inches';
    drawnow;
    p = lg.Position;
    W = ax.Parent.Position(3);
    lg.Position = [(W - p(3)) / 2, y, p(3), p(4)];
end
