# KDP Listing Draft — DO NOT PUBLISH YET

Prepared content for the Amazon KDP listing. Everything below is copy-paste
ready, but the book is still in beta revision. Pre-publish checklist at the
bottom must be green first.

## Title / subtitle

- **Title:** OpenUSD Exam Companion
- **Subtitle:** NCP-OUSD Prep Notes and Tested Examples — Cheat Sheets,
  Drills, and a 60-Question Mock Exam for the NVIDIA OpenUSD Development
  Certification

## Description (blurb)

You finished NVIDIA's Learn OpenUSD courses — and the NCP-OUSD exam is
still hard. Experienced developers report failing their first attempt after
80 hours of study. This companion covers the gap: traps, edge-case
semantics, strength ordering, and API specifics.

What makes this book different:

- **Every example is executed against real OpenUSD before printing.**
  Composition questions are answered by actually composing the stage — not
  by reasoning alone.
- **All 55 study-guide objectives, traceable.** Margin tags mark which
  numbered objective every passage serves, and a Coverage Map appendix lists
  objective → section, with clickable links.
- **A 60-question mock exam** in the official domain weighting, with an
  explained answer key and a per-domain scoring table that mirrors the real
  score report — a weak row points you at the chapter to revisit.
- **Cheat sheets, drills with solutions, and checkpoint questions** for all
  eight domains, plus field notes synthesized from certified test-takers.
- **Real tool figures**: annotated usdview screenshots and usdrecord renders,
  regenerated from the very listings printed beside them.

Written for software developers familiar with NVIDIA's Learn OpenUSD
materials. Independent publication; not affiliated with or endorsed by
NVIDIA.

## Keywords (7)

1. OpenUSD certification
2. NCP-OUSD exam prep
3. NVIDIA OpenUSD development
4. USD Universal Scene Description
5. OpenUSD practice questions
6. 3D pipeline developer certification
7. usdview usdrecord tutorial

## Categories

- Computers & Technology > Graphics & Design > 3D Graphics
- Computers & Technology > Certification Guides
- Computers & Technology > Computer Graphics

## Format & pricing

- Format: KDP ebook, **print-replica PDF** (decision: PDF-first; EPUB only if
  sales justify it)
- Price: **$0.99**
- DRM: off (the book is CC BY-NC-ND 4.0; free verbatim sharing is part of
  the strategy)
- Cover: `usd_exam_companion/cover/cover.png` (1600×2560). v1 is generated
  from the book's assets — consider a designer pass before launch.

## Pre-publish checklist (all must be green)

- [ ] Author's full cold read of the current PDF
- [ ] Heavy-revision phase declared finished; edition string set to a final
      number (currently "v0.10 Beta Edition" in `styles/setup.tex`)
- [ ] Remove the beta notice line from the colophon
      (`styles/titlepages.tex`)
- [ ] `tools/release_gate.sh --figures` passes
- [ ] Final cover art decision (keep generated v1 or commission)
- [ ] KDP account: tax/bank details verified
- [ ] Listing copy above pasted and previewed in KDP
- [ ] KDP "freely available content" consideration: the repo is public by
      design; ensure the Amazon listing offers differentiation (newest
      edition lands on Amazon first)
