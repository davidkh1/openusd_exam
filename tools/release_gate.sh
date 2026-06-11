#!/usr/bin/env bash
# Release gate: run before any distribution (beta or final).
#   tools/release_gate.sh             # tests + build + checks + versioned PDF
#   tools/release_gate.sh --figures   # also regenerate all renders first
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== gate 1/4: unit tests (every listing in the book)"
.venv/bin/python -m pytest tests/ -q

if [[ "${1:-}" == "--figures" ]]; then
    echo "== gate 2/4: regenerating figures (needs NVIDIA usdrecord)"
    .venv/bin/python tools/regen_figures.py
    .venv/bin/python tools/make_cover.py
else
    echo "== gate 2/4: figures skipped (pass --figures to regenerate)"
fi

echo "== gate 3/4: build"
( cd usd_exam_companion && latexmk -pdf -interaction=nonstopmode main.tex >/dev/null 2>&1 )
ERR=$(grep -cE '^!' usd_exam_companion/main.log || true)
OVER=$(grep -c 'Overfull' usd_exam_companion/main.log || true)
UNDEF=$(grep -cE 'Reference .* undefined' usd_exam_companion/main.log || true)
PAGES=$(grep -oE 'Output written on main.pdf \([0-9]+ pages' usd_exam_companion/main.log | grep -oE '[0-9]+' | head -1)
echo "   errors=$ERR overfull=$OVER undefined_refs=$UNDEF pages=$PAGES"
[[ "$ERR" == 0 && "$OVER" == 0 && "$UNDEF" == 0 ]] || { echo "GATE FAILED"; exit 1; }

echo "== gate 4/4: versioned artifact"
VERSION=$(sed -n 's/.*newcommand{\\edition}{\([^}]*\)}.*/\1/p' usd_exam_companion/styles/setup.tex | tr ' ' '_')
mkdir -p release
cp usd_exam_companion/main.pdf "release/OpenUSD_Exam_Companion_${VERSION}.pdf"
echo "GATE PASSED: release/OpenUSD_Exam_Companion_${VERSION}.pdf (${PAGES} pages)"
