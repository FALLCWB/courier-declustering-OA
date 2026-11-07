% Render the five Paper A figures (FIGURES-SPEC.md): figures/paper/*.m on the CSVs of scripts/paper_figure_data.py
% (datadir) and scripts/paper_fig2_positions.py (fig2dir), into outdir.
function render_paper_figures(datadir, fig2dir, outdir)
    fig1_w1_evening(datadir, outdir);
    fig2_fleet_map(fig2dir, outdir);
    fig3_f1_forest(datadir, outdir);
    fig4_q1_forest(datadir, outdir);
    fig5_q2_forest(datadir, outdir);
end
