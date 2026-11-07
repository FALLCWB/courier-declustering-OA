#!/usr/bin/env bash
# Test compile of the Paper A figures in the paper's own class (FIGURES-SPEC.md rule 11): every figure at \textwidth
# between body text, plus an empty one-column float frame; then the pages at 100% (96 dpi) and 50% (48 dpi), in
# grayscale (150 dpi), and each figure alone at 300 dpi, for the visual check.
# Usage: bash scripts/paper_figures_testpage.sh <figure_dir> <paper_dir with ieeeaccess.cls> <out_dir>
set -euo pipefail
FIG=$(realpath "$1"); PA=$2; O=$(realpath -m "$3")
rm -rf "$O"; mkdir -p "$O/tex" "$O/pages" "$O/check"
cp "$PA"/*.cls "$PA"/*.sty "$PA"/*.pfb "$PA"/*.tfm "$PA"/*.map "$PA"/*.png "$O/tex/" 2>/dev/null || true
cp "$FIG"/* "$O/tex/"
cat > "$O/tex/figtest.tex" <<'TEX'
\documentclass{ieeeaccess}
\usepackage{newtxtext,newtxmath}
\usepackage{graphicx}
\usepackage{stfloats}
\usepackage{lipsum}
\begin{document}
\history{Figure test compile.}
\doi{TEST}
\title{Figure Test Compile for Paper A}
\author{\uppercase{Test Author}\authorrefmark{1}}
\address[1]{Test address}
\markboth{Figure test}{Figure test}
\corresp{Test.}
\begin{abstract}
Test compile of the five figures at their printed width.
\end{abstract}
\maketitle
\typeout{TEXTWIDTH=\the\textwidth}\typeout{COLUMNWIDTH=\the\columnwidth}
\section{One-column float}
\lipsum[1]
\begin{figure}[!t]
\centering
\fbox{\parbox[c][1.2in][c]{\dimexpr\columnwidth-2\fboxsep-2\fboxrule}{\centering\footnotesize A one-column float is \the\columnwidth{} wide.\\ No Paper A figure uses one; all five are two-column.}}
\caption{One-column float frame at \texttt{\textbackslash columnwidth}.}
\end{figure}
\lipsum[2-3]
\begin{figure*}[!t]\centering\includegraphics[width=\textwidth]{fig1_w1_evening.pdf}\caption{Fig.~1 at \texttt{\textbackslash textwidth}.}\end{figure*}
\lipsum[4-6]
\begin{figure*}[!t]\centering\includegraphics[width=\textwidth]{fig2_fleet_map.png}\caption{Fig.~2 at \texttt{\textbackslash textwidth}.}\end{figure*}
\lipsum[7-9]
\begin{figure*}[!t]\centering\includegraphics[width=\textwidth]{fig3_f1_forest.pdf}\caption{Fig.~3 at \texttt{\textbackslash textwidth}.}\end{figure*}
\lipsum[10-12]
\begin{figure*}[!t]\centering\includegraphics[width=\textwidth]{fig4_q1_forest.pdf}\caption{Fig.~4 at \texttt{\textbackslash textwidth}.}\end{figure*}
\lipsum[13-15]
\begin{figure*}[!t]\centering\includegraphics[width=\textwidth]{fig5_q2_forest.pdf}\caption{Fig.~5 at \texttt{\textbackslash textwidth}.}\end{figure*}
\lipsum[16-24]
\EOD
\end{document}
TEX
(cd "$O/tex" && latexmk -pdf -interaction=nonstopmode -quiet figtest.tex > build.log 2>&1)
grep -E "<fig[1-5]_.*pt>" "$O/tex/figtest.log" | sed 's/^/included /'
pdftoppm -r 96 -png "$O/tex/figtest.pdf" "$O/pages/p100"
pdftoppm -r 48 -png "$O/tex/figtest.pdf" "$O/pages/p050"
pdftoppm -r 150 -gray -png "$O/tex/figtest.pdf" "$O/pages/gray"
for f in fig1_w1_evening fig3_f1_forest fig4_q1_forest fig5_q2_forest; do
  pdftoppm -r 300 -png -singlefile "$FIG/$f.pdf" "$O/check/$f"
  pdftoppm -r 300 -gray -png -singlefile "$FIG/$f.pdf" "$O/check/${f}_gray"
done
cp "$FIG/fig2_fleet_map.png" "$O/check/"
pdftoppm -r 300 -gray -png -singlefile "$O/tex/figtest.pdf" -f 3 -l 3 "$O/check/page3_gray" 2>/dev/null || true
ls "$O/pages" "$O/check" | tr '\n' ' '
