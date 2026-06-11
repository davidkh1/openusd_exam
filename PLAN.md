# Book Plan — OpenUSD Exam Companion

The roadmap for turning the 46-page skeleton (v0.02) into a publishable, dense,
correct, beautiful study companion for the NVIDIA NCP-OUSD certification.
Working conventions (American English, tested examples, color visuals, original
questions) live in CLAUDE.md and are not repeated here.

## Product definition

- A $0.99 PDF/Kindle companion in the spirit of "Cracking the Coding Interview":
  the most time-efficient path from "finished the courses" to "passed the exam".
- Reader: a software developer familiar with NVIDIA's Learn OpenUSD
  materials — who still finds the exam hard. The companion covers the gap:
  traps, edge-case semantics, strength ordering, API specifics. (Stated in
  the book's Preface, "Who this book is for".)
- Evidence the gap is real: a genuine attempt's section scores (private, under
  `ideas/materials_from_dropbox/my_openusd_certificate/`) landed at 48–73% per
  domain after course-level prep. Weight gotcha coverage accordingly — Data
  Modeling (48%), Content Aggregation (60%), Visualization (62%) were weakest.
- Density is the differentiator: cheat-sheet-first chapters, no filler prose,
  every page earns its place. No page limit — the book takes as many pages as
  full, correct coverage requires. Density comes from the writing style and the
  quality gates, not from a page budget.

## Quality gates (every chapter must pass all five)

1. **Correct** — every claim traceable to the official study guide or OpenUSD
   docs; every listing extracted from the .tex and executed warning-free against
   real USD (see CLAUDE.md "Testing USD examples"); composition questions verified
   by actually composing the stage and comparing with the answer key.
2. **Validated** — assets built from listings pass `UsdUtils.ComplianceChecker`
   (the `usdchecker` engine, available in the repo venv).
3. **Dense** — cheat sheet fits exactly one trim page; snippets stay 3–20 lines;
   a cold re-read asks "would this earn its place in a $0.99 dense guide?"
4. **Visual** — at least one color diagram per major concept; every spread has a
   visual anchor (diagram, listing, or callout box).
5. **Exam-aligned** — chapter objectives mirror the study guide's numbered
   objectives 1:1; nothing on the exam blueprint is uncovered. Enforced in
   print since 2026-06-11: `\objref{}` margin tags mark every passage with
   the guide objective numbers it serves (e.g. "1.10, 2.5"), and the
   Study-Guide Coverage Map appendix lists all 55 objectives → covering
   sections. New content must carry tags; the map must stay complete.

## Phase 0 — Infrastructure hardening (mostly done)

Done already: latexmk build works, `styles/` recovered from Overleaf, repo venv
with `usd-core` 26.5 + pytest, **unit-test suite live** (`tests/test_examples.py`:
every listing extracted from the .tex, parse + composed-value + silent-stderr
assertions; 10 tests green), `usdview`/`usdrecord` validated end-to-end
(rendered a book scene via Storm).

Standing rule: unit tests are a first-class part of the project — every new
listing lands together with a test that asserts what the answer key claims.

Remaining: none.
- [x] ComplianceChecker pass in the test suite (clean vs broken export in
      c13 tests; the OBJ-importer test asserts checker-clean output).

Done 2026-06-11:
- [x] Colorized listings (`styles/usdlisting.tex`): color theme + full usda
      keyword list (two keyword classes: structural + value types).
- [x] Callout boxes (`styles/callouts.tex`): `ExamTip` (green), `Gotcha`
      (orange), `DeepDive` (blue), `DrillSolution` (gray), all breakable.
- [x] TikZ diagram language (`styles/diagrams.tex`): fixed palette (one color
      per arc type) and node styles; all figures share it.
- [x] Screenshot/render pipeline validated (see "Figures and screenshots" below).

## Phase 1 — Correctness pass on the existing draft

- [x] Fix the LIVERPS cheat sheet in `10-composition.tex`: S is **Specializes**,
      not Sublayers (sublayers are part of "Local"). Done — cheat sheet, ladder
      figure, and drills all teach the corrected ordering.
- [x] Fix Question 3: option `extent` replaced with `faceVertexCounts`.
- [x] Fact-check every cheat-sheet bullet: all 8 chapters were rebuilt with
      probe-verified claims (every API behavior executed before printing).
- [x] Upgrade the answer key from bare letters to explained answers (why right,
      why each distractor is wrong); composition claims verified by tests.

## Phase 2 — Domain build-out (weight order)

**ALL EIGHT DOMAIN CHAPTERS DONE (2026-06-11).** Every chapter has: core
concepts per study-guide objective, cheat sheet, callouts, drills with inline
solutions, checkpoint questions, index entries — and every listing extracted
from the .tex and unit-tested (61 tests green). Highlights per chapter:

- Composition (23%): LIVRPS ladder + arcs diagrams, annotated usdrecord
  render, annotated usdview capture; sublayer/offset/payload listings.
- Data Exchange (15%): clean-export exemplar, round-trip, traversal skeleton,
  USD→glTF mapping diagram, usdchecker + ComputeExtentFromPlugins.
- Pipeline Development (14%): asset interface pattern (+ diagram), model
  hierarchy contiguity rule (verified: orphan component is NOT a model),
  GetCompositionAssetDependencies path gate, resolver role, flatten delivery.
- Data Modeling (13%): property taxonomy diagram, type-zoo listing, indexed
  faceVarying primvars, customData vs attributes, extent-after-edit.
- Debugging (11%): GetPropertyStack provenance, MuteLayer bisection,
  SdfChangeBlock batching (100-prim demo), TfDebug switches, symptom→tool
  decision-tree figure.
- Content Aggregation (10%): instance proxies (authoring raises — verified),
  edit-all vs edit-one flows, PointInstancer + invisibleIds with render
  showing the hidden-instance gap.
- Visualization (8%): primvar-driven UsdPreviewSurface network (render proves
  it: two colors, one material) + network graph figure, GeomSubset,
  purpose/visibility, UsdLux.
- Customizing USD (6%): plugin-map figure, schema.usda source (typed + API +
  codeless), CollectionAPI apply demo, custom kinds plugInfo, resolver vs
  file-format vs SceneIndex boundaries, ABI pinning.

Chapter template v2 (extends the current skeleton):
1. `\DomainHeader` + Objectives + Resources (unchanged, mirrors study guide)
2. Cheat sheet — exactly one page (unchanged)
3. **Core concepts** — new: dense, diagram-led explanation of each objective;
   one worked micro-example per concept, all tested
4. **Gotchas & exam tips** — new: callout boxes; harvested from drills, the
   Medium/people reviews in `ideas/`, and the author's own exam recollections
5. Drills with answer lines + inline solution in a tinted box below the lines,
   plus 2–4 checkpoint questions per chapter
6. Index entries (`\index{}`) — the index is currently empty

No page budget — each domain gets as many pages as its objectives require.
Keep depth roughly proportional to exam weight (Composition 23% → deepest
chapter, Customizing USD 6% → lightest) so coverage mirrors the exam, and let
the density gate ("would this earn its place?") control length, not a count.

Raw material: NVIDIA course exercise files under
`ideas/materials_from_dropbox/examples/` (composition_arcs, instancing,
asset_structure, data_exchange) — adapt into original micro-examples, test each.

## Phase 2.5 — Deepening backlog (no page budget; add until objectives are saturated)

Sourcing policy (2026-06-11): adapt examples from openusd.org and https://docs.nvidia.com/learn-openusd/latest/index.html
tutorials where
the study guide references them — the guide's Resources point almost
exclusively there, so structural alignment helps readers. License is OpenUSD's
modified Apache 2.0: adaptation with attribution is fine, including
commercially. Rules: adapt and minimize (never transcribe prose), run every
adapted example through the test harness, attribute in the caption or
Resources, add a colophon credit line if adoption becomes substantial.
Best candidates: "Transformations, Time-Sampled Animation, and Layer Offsets"
(→ Data Modeling time-samples item), "Simple Shading in USD" (→ UsdUVTexture
item), "End to End Example" (→ Pipeline cross-check).

First-pass chapters cover every objective; these are the known thin spots
where honest depth adds pages:

- [x] Composition: worked `inherits` (broadcast) and `specializes`
      (fallback) examples — §3.3.7, tested.
- [x] Data Exchange: OBJ→USD importer in 25 lines (§6.3.4), tested —
      output is ComplianceChecker-clean.
- [x] Data Modeling: time samples/TimeCode (linear vs held, Default-time
      trap) + XformCommonAPI — §7.3.6–7.3.7, tested.
- [x] Debugging: runnable `Trace` listing (named scope asserted in the
      reporter output by tests). Layer Stack screenshot done earlier.
- [x] Data Modeling: usdview properties-panel capture of the type-zoo prim
      (Figure 7.2, annotated — relationship vs asset path made visual).
- [x] Content Aggregation: per-instance `orientations`/`scales` (quath
      syntax verified) + AddTarget prototype listing, tested.
- [x] Visualization: UsdUVTexture network + authored Camera + DistantLight
      in one scene, rendered through the authored camera (Figure), tested.
- [x] Customizing USD: registration end-to-end — the book's own
      plugInfo.json is registered in a subprocess by the test suite;
      codeless-schema flow described honestly (usdGenSchema generates the
      Types block).
- [x] Practice part: Phase 3 delivered (below).

## Phase 3 — Question bank and mock exam

**DONE 2026-06-11.** Sixty original questions (mixed-domain order
approximating the official weights: Comp 12, DE 9, DM 9, DT 7, CA 6, VIS 6,
PD 6, CU 4, exam-craft 1), 90-minute closed-book framing, three
listing-based scenario questions verified by the test suite, and an
explained key opening with a Certiverse-style per-domain scoring table that
points each weak row at its chapter. Original content only — calibrated to
the official sample-question style, never to dump material.

- Method: build a topic × difficulty histogram from the third-party question
  PDFs under `ideas/` (calibration only — never copy), then write **original**
  questions to the same distribution, including question/option length.
- Deliverables: per-domain checkpoint questions (Phase 2), plus one full
  60-question / 90-minute mock exam mirroring the real format, plus the
  explained answer key.
- Every scenario question is composed and executed before inclusion — same
  harness as Phase 0.

## Phase 4 — Beauty pass

- [x] All diagrams on the shared TikZ styles (true by construction: every
      figure uses `styles/diagrams.tex` nodes and palette).
- [x] Screenshots/renders where pixels matter: 6 usdrecord renders + 3
      annotated usdview captures across Composition, Content Aggregation,
      Data Modeling, Debugging, Visualization, and the answer key — all
      regenerable from the chapter listings.
- [x] Typography pass: Latin Modern (scalable, no PK bitmaps), widow/club
      penalties + ragged bottom, zero overfull boxes maintained across all
      141 pages, mock-exam answer letters rebalanced (15/16/15/14). A final
      human cold-read before release is still recommended.
- [x] Cover v1 generated from the book's own assets
      (`tools/make_cover.py` → `usd_exam_companion/cover/cover.png`,
      1600×2560 KDP size). Final cover art remains a release-time decision.
- [x] Kindle decision: PDF print-replica first (decision 3, made
      2026-06-11); EPUB only if sales justify it.

## Phase 5 — Release

- [ ] Full gate run: build clean, `tools/test_examples.py` green, fact-check
      sign-off per chapter.
- [ ] Beta readers (certification-webinar/forum contacts, reviewers from
      `ideas/people_reviews/`).
- [ ] KDP setup at $0.99; version bump from v0.02 (edition string is in
      `styles/setup.tex`); errata page/workflow.
- [ ] Later spinoff (separate project): training-question website.

## Figures and screenshots — tooling facts (verified 2026-06-11)

- Unit tests / composition checks: the repo venv (`usd-core` 26.5) — full `pxr`
  API and `UsdUtils.ComplianceChecker`, no imaging.
- Renders and GUI screenshots: NVIDIA prebuilt binaries at
  `~/opt/openusd/usd_root` (`usdview`, `usdrecord`, `usdcat`, `usdchecker`).
  Must `source ~/opt/openusd/usd_root/scripts/set_usd_env.sh` first.
  Validated: `usdrecord` rendered a book scene via Storm; `usdview` GUI
  launches cleanly (`--quitAfterStartup` smoke test).
- Examples are authored on Linux but stay OS-neutral (see CLAUDE.md content
  rules); the toolchain above has Windows/macOS equivalents.
- Reproducibility rule: every figure's source lives in the repo
  (`figures/src/*.usda` + a regeneration script with fixed camera, window size,
  and renderer settings). Screenshots are re-capturable, never one-off.

## Decisions (all resolved 2026-06-11)

1. **Mock exam: 60 questions / 90 minutes**, mirroring the real exam.
2. **Drill solutions: inline, after each drill.** Design guard: solution goes in
   a tinted box *below* the answer area so the eye doesn't land on it before
   the attempt.
   Amendment 2026-06-11: AcroForm fillable fields were tried and **rejected**
   (David does not expect readers to type into the PDF). Drills keep ruled
   lines for print; PDF readers work drills as recall-then-check — the preface
   says so explicitly.
3. **Kindle: PDF print-replica first**; EPUB only if sales justify it.
4. usdview source: NVIDIA prebuilt binaries (installed and validated).
5. Page count: no limit — the whole book, as many pages as it takes
   (supersedes the earlier ~100-page target).
6. **Style sources** (decided 2026-06-11, from `ideas/books_i_like` +
   `people_reviews`): van der Linden's *Expert C* → **Field Note** boxes
   carrying real test-taker experience (purple, alongside ExamTip/Gotcha/
   DeepDive); Josuttis → every listing shows its output inline as comments,
   asserted by tests; Meyers' *Effective C++* "Things to Remember" →
   retained as our imperative mini-checklists; CtCI → Phase 3 mock-exam
   mechanics (timed, no references, distractor-elimination drills).
   `people_reviews` (N. Chaubey's Medium guide; B. Mayoral Arauz's LinkedIn
   write-up — failed first attempt despite 2 years of Omniverse + 80h study)
   synthesized into the blueprint chapter's "Field notes from test-takers"
   section + Field Note boxes. The NVIDIA certification webinar PDF remains
   unmined.
7. **License: CC BY-NC-ND 4.0** (decided 2026-06-11). David is fine with free
   verbatim sharing of the PDF; commercial rights and derivatives stay with
   the author — the modern form of the Self-Service-Linux model. Known
   tradeoff, accepted: legal free copies will circulate, and KDP's
   "freely available content" policy may need the Amazon listing to offer
   differentiation (e.g., latest edition first on Amazon).
