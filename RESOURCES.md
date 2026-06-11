# Resources

External resources for working on the OpenUSD Exam Companion.

## Official

- [OpenUSD](https://openusd.org/) — docs, tutorials, glossary, API
  reference. The book's primary adaptation source (see PLAN.md sourcing
  policy: adapt + minimize + test + attribute; modified Apache 2.0).
- [Learn OpenUSD](https://docs.nvidia.com/learn-openusd/latest/index.html) —
  NVIDIA's course track; the study guide's Resources point here.
- [NCP-OUSD certification page](https://www.nvidia.com/en-us/learn/certification/openusd-development-professional/)
  — exam registration and the official study guide (local copy:
  `learning_materials/ncp-open-usd-development-study-guide.pdf`).
- [Alliance for OpenUSD forum](https://forum.aousd.org/) — working-group
  notes, spec discussions.

## Community

- [USD-Cookbook](https://github.com/ColinKennedy/USD-Cookbook) — Colin
  Kennedy's self-contained USD example projects. Example-mining source;
  **check the repo's license before adapting anything into the book.**
- [VFX USD Survival Guide](https://lucascheller.github.io/VFX-UsdSurvivalGuide/)
  — Luca Scheller's pipeline-TD onboarding guide; deep-pipeline complement
  to this book's exam focus.

## This project

- Book source: `usd_exam_companion/` — build with
  `latexmk -pdf -interaction=nonstopmode main.tex`
- Release gate: `tools/release_gate.sh [--figures]`
- Tests: `.venv/bin/python -m pytest tests/`
