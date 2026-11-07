% Panel letter, 9-pt bold, at the panel's top-left corner. Above the corner by default, since inside it would sit on
% data or on printed values (rule 11 check, 2026-11-06); inside, on a white box, for the maps of Fig. 2.
function pa_letter(ax, letter, S, where)
    if nargin < 4, where = 'above'; end
    if strcmp(where, 'inside')
        text(ax, 0.015, 0.985, ['(' letter ')'], 'Units', 'normalized', 'FontName', S.font, 'FontSize', S.fsLetter, ...
             'FontWeight', 'bold', 'VerticalAlignment', 'top', 'HorizontalAlignment', 'left', 'Interpreter', 'none', ...
             'BackgroundColor', 'w', 'Margin', 1);
    else
        text(ax, 0, 1.02, ['(' letter ')'], 'Units', 'normalized', 'FontName', S.font, 'FontSize', S.fsLetter, ...
             'FontWeight', 'bold', 'VerticalAlignment', 'bottom', 'HorizontalAlignment', 'left', 'Interpreter', 'none');
    end
end
