# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A study-companion book (LaTeX → PDF, intended for publication) for NVIDIA's NCP-OUSD "OpenUSD Development" certification exam, structured around NVIDIA's official study guide v1.1.0. The book lives in `usd_exam_companion/`; everything else in the repo is reference material, not part of the build. The writing roadmap and phase plan live in `PLAN.md`.

## Build

From `usd_exam_companion/`:

```bash
latexmk -pdf -interaction=nonstopmode main.tex
```

There are no LaTeX tests or linters. Compiled output (`usd_exam_companion/*.pdf`) and LaTeX build artifacts are gitignored; reference PDFs elsewhere (e.g. `learning_materials/`) are tracked.

The book targets a 6.375 × 9.25 in print trim size (set in `styles/setup.tex`) and builds to `usd_exam_companion/main.pdf`.

## Testing USD examples

Unit tests are a first-class part of this project. `tests/test_examples.py` extracts every lstlisting block verbatim from the sample-questions chapter, writes the layers to a scratch tree, and asserts against real USD that each listing parses, that composed values match the answer key, and that USD stays silent on stderr (missing `defaultPrim`, unresolved assets, and parse errors surface there even when the stage still opens). Run after any change to listings:

```bash
.venv/bin/python -m pytest tests/ -v
```

The venv (gitignored) has `usd-core` and `pytest`; recreate with `python3 -m venv .venv && .venv/bin/pip install usd-core pytest`. Every new listing lands with a test: add its file to `CHAPTER_LISTINGS` (per-chapter, in document order) and write a scenario test asserting what the book claims. A filename listed twice means the book shows one file as two listing fragments; the fixture concatenates them back before testing.

Every `lstlisting` is wrapped in an unbreakable box so examples never split across pages; a listing taller than the text column must be preceded by `\AllowListingBreak`. Margin tags (`\objref`) hyperlink each objective number to its Coverage-Map row (`\objrow` anchor) — new objectives need both ends. Recommended-resources bullets are `\href`-linked to official docs; verify any new URL resolves before printing it.

usda gotcha learned by testing: every statement in a prim or variant body needs its own line — one-liner blocks like `"red" { over "Cube" ... }` fail to parse.

### USD GUI and render tools

`usdview`, `usdrecord`, `usdcat`, and `usdchecker` are NVIDIA prebuilt binaries at `~/opt/openusd/usd_root`. The Python-based ones (`usdview`, `usdrecord`) fail with "extension class wrapper ... has not been created yet" unless the environment is sourced first:

```bash
source ~/opt/openusd/usd_root/scripts/set_usd_env.sh   # PATH, PYTHONPATH, LD_LIBRARY_PATH
usdrecord --imageWidth 800 scene.usda out.png           # headless render (Storm)
```

Use these for book figures and screenshots; keep every figure regenerable:

- `.venv/bin/python tools/regen_figures.py` re-renders the `usdrecord` figures into `usd_exam_companion/figures/` from the chapter listings themselves (same extraction as the tests), so figures can never drift from the printed code.
- GUI screenshots: launch `usdview`, dump its window with `xwd -id <window-id>`, convert with `.venv/bin/python tools/xwd2png.py in.xwd out.png` (pure Pillow, no ImageMagick).
- Figure PNGs are tracked in git. Annotations (arrows, labels) are TikZ overlays in the .tex using the `diagrams.tex` palette — never baked into the images.

## Document architecture

`main.tex` (book class) assembles `chapters/` by number prefix: `0x` intro and exam blueprint, `1x` one chapter per exam domain (Part "Domains"), `2x` sample questions and answer key (Part "Practice"). Domain names and exam weights are listed in `chapters/01-blueprint.tex` (Composition is the largest at 23%).

### Domain chapter template

All `1x-*.tex` chapters follow this exact skeleton — keep it when editing or adding domains:

```latex
\DomainHeader{<Domain Name>}{<weight>\%}
\begin{Objectives}  \item ...  \end{Objectives}
\begin{Resources}   \item ...  \end{Resources}
\CheatSheetTitle
\begin{itemize}[leftmargin=*] ... \end{itemize}
\DrillsTitle
\subsection*{Drill 1: <title>}
<prompt text> \AnswerLines{6}
\subsection*{Mini-checklist (tick when mastered)}
% itemize with \item[$\square$] entries
```

Practice questions (`20-sample-questions.tex`): `\Question{N}` (compact header macro), a `\textbf{Domain:}` tag, optional `lstlisting` blocks holding small `.usda` snippets, then A–D answer choices in a `Choices` environment. Answers go in `21-answer-key.tex` (typeset as that chapter's closing "Answer Key" section), never inline with the question.

### Custom macros (`styles/`)

- `styles/macros.tex` — `\DomainHeader{name}{weight}` (starts the chapter and prints the exam weight), list environments `Objectives` and `Resources`, `\CheatSheetTitle`, `\DrillsTitle`, `\AnswerLines{n}` (n ruled lines for handwritten answers — deliberately not PDF form fields; David rejected fillable forms).
- `styles/usdlisting.tex` — defines a `USDA` listings language and makes it the `lstlisting` default. New usda keywords used in listings (e.g. `payload`, `references`) must be added to its `morekeywords` list to get highlighted.
- `styles/setup.tex` — packages (`tikz`, `xcolor`, `enumitem`, `hyperref`, `makeidx`…), the trim-size geometry, and book metadata (title, subtitle, edition, CC0 license).
- `styles/titlepages.tex` — `\HalfTitlePage`, `\TitlePage`, `\ColophonPage`.

## Content rules

- American English, matching NVIDIA's own materials ("Customizing USD", "Data Modeling", "Visualization"); chapter filenames use the same spellings.
- Every example must pass the workflow in "Testing USD examples" — never publish invented output or untested layer snippets.
- Use color visualizations generously: composition/scenegraph diagrams, color-coded listings, colored callout boxes. `styles/setup.tex` already loads `xcolor` and `tikz` for this.
- Practice questions must be original: match the real exam's topic distribution, difficulty, and question/option lengths, but never reproduce actual exam questions. The exam-dump PDFs under `ideas/` are calibration reference only.
- Keep USD snippets tiny (3–20 lines) — the book's stated study method is reasoning about minimal layers ("which layer wins and why", LIVRPS).
- Examples are developed on Linux but must read OS-neutral: relative forward-slash asset paths, no shell-specific steps in book text, cross-platform USD tooling only.
- Listings show their output (Josuttis-style): any listing that prints carries the result inline as a comment (`# prints: ...`, `# True`), and the test suite asserts exactly those claims.
- The "produces" idiom (adopted from the official OpenUSD tutorials): a Python listing, the `\produces` connector, then the usda it authored via `ExportToString()`. Lines the code authored start with `;;` in the .tex (rendered bold amber, marker invisible). The output listing maps to a `.out` file in `CHAPTER_LISTINGS` and a test asserts each printed line appears verbatim in the real export.
- Callout boxes, by intent: ExamTip (what the exam rewards), Gotcha (verified failure modes), DeepDive (architecture context), FieldNote (synthesized test-taker experience — keep sourced from real write-ups, never invented), DrillSolution.

## Reference material (not built)

- `learning_materials/ncp-open-usd-development-study-guide.pdf` — the official NVIDIA study guide the book mirrors.
- `ideas/materials_from_dropbox/` (untracked) — NVIDIA course exercise files (`examples/` has runnable `.py`/`.usd` files per domain: composition_arcs, instancing, asset_structure, data_exchange), exam reviews, webinar notes, and the publishing plan in `book_openusd/book_openusd_info.txt`.
- `ideas/materials_from_dropbox/book_openusd/overleaf_project/` — a downloaded snapshot of the Overleaf project. Its chapters equal the repo's first-draft commit (the repo is ahead of it); `styles/` was imported from here. Treat the repo, not Overleaf, as the source of truth.
- NVIDIA's Learn OpenUSD docs: https://docs.nvidia.com/learn-openusd/latest/index.html
