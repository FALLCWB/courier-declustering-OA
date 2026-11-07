% Legend handles in the given model order: the 95% interval line with the filled marker of each model.
function h = pa_handles(ax, models, S)
    h = gobjects(1, numel(models));
    for i = 1:numel(models)
        c = S.color(char(models(i)));
        h(i) = plot(ax, nan, nan, '-', 'Color', c, 'LineWidth', S.lw, 'Marker', S.marker(char(models(i))), ...
                    'MarkerSize', S.ms, 'MarkerFaceColor', c, 'MarkerEdgeColor', c);
    end
end
