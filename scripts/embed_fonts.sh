#!/usr/bin/env bash
# Embed the fonts of the Paper A figure PDFs (FIGURES-SPEC.md; IEEE asks for embedded fonts). MATLAB's print writes the
# text in the standard, non-embedded Helvetica; Ghostscript embeds its metric-identical URW clone (Nimbus Sans), subset.
# The page size and the vector drawing are kept. Usage: bash scripts/embed_fonts.sh <in.pdf> <out.pdf>
set -euo pipefail
gs -q -o "$2" -sDEVICE=pdfwrite -dEmbedAllFonts=true -dSubsetFonts=true -dCompatibilityLevel=1.6 -dAutoRotatePages=/None \
   -dPDFSETTINGS=/prepress "$1"
