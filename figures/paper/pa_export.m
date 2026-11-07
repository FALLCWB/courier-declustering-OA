% Export at the figure's own size (FIGURES-SPEC.md rule 1): a vector PDF through print, whose text stays in the
% standard Helvetica font (embedded afterwards with its URW clone by scripts/embed_fonts.sh), or a PNG at the given dpi.
function pa_export(fig, file, dpi)
    if nargin < 3
        sz = fig.Position(3:4);
        set(fig, 'PaperUnits', 'inches', 'PaperSize', sz, 'PaperPosition', [0 0 sz]);
        print(fig, file, '-dpdf', '-vector');
    else
        exportgraphics(fig, file, 'Resolution', dpi, 'Padding', 'figure');
    end
end
