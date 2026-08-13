# goal.md — FAR bank foundation

STATUS: RATIFIED by James, 2026-08-13, after 16 serialized red-pen keeps and
the recorded deferral-load check. This is the governing contract. Changes to
what is allowed, forbidden, or owed require an explicit dated amendment.

## Outcome

Produce a versioned, auditable bank of original four-option FAR multiple-
choice questions mapped to the complete current CPA Exam Blueprint, with
mechanical evidence and individual human approval sufficient to determine:

1. which exact questions are learner-ready;
2. which Blueprint area, group, topic, representative task, and skill level
   each approved question covers;
3. which accounting and test-taking challenge mechanics each question tests;
4. whether the approved bank meets ratified coverage and variety floors; and
5. where meaningful FAR coverage remains insufficient.

The outcome is not “many questions exist.” It is that the project can prove
the status, correctness, provenance, coverage, variety, and approval state of
every question it claims is ready for learners.

## Baseline

Treat the project as starting from zero:

- no approved taxonomy;
- no accepted questions;
- no trusted generator or solver;
- no trusted quality oracle;
- no inherited approval decisions;
- no learner or administrator application architecture.

Existing CPA projects outside `cpa-learning/` are untrusted, read-only prior
art. Nothing from them counts toward completion unless admitted by a dated
contract amendment and independently re-sourced, regenerated, and reverified.

## Operating mode

PHASE-GATED HYBRID.

- James is the ratifier and initial human approver.
- The agent may execute autonomously inside a ratified phase.
- Human gates occur between phases and are contract elements.
- Interpretive rulings accumulate in a tagged queue rather than stalling an
  active phase. Gate rulings are presented one question per turn.
- A gate verdict covers only the medium actually reviewed. A taxonomy review
  cannot approve question quality; a sample review cannot approve bank-wide
  coverage; a hands-on review is required for the review workflow.

## Content boundary

### Included

- The complete FAR section of the current AICPA Uniform CPA Examination
  Blueprint effective January 1, 2026.
- The full published hierarchy: Area, Group, Topic, representative task, and
  tested skill level.
- Original four-option MCQs only.
- Both accounting knowledge and exam-execution mechanics.
- An internal review surface needed to inspect, approve, reject, revise, and
  comment on questions.
- Machine-readable coverage, variety, provenance, verification, and approval
  records.

### Explicitly deferred

- AUD, REG, BAR, ISC, and TCP content.
- Task-based simulations and numeric-entry items.
- A public or learner-facing website.
- Learner accounts, configurable quizzes, progress tracking, skill models,
  recommendations, and adaptive sequencing.
- Administrative learner-performance analytics.
- Lesson plans and instructional sequences.
- Commercial launch, pricing, marketing, and public publication.

These are build-later deferrals in the program vision, not promises in this
contract and not never-build fences.

## Learner and quality thesis

The target learner is actively preparing to pass the current FAR exam. The
bank assumes the learner is studying accounting; teaching every topic from
zero belongs to the deferred lesson layer.

FAR difficulty is not merely computational complexity. A useful question can
also require the learner to:

- determine what the stem ultimately asks;
- locate where the controlling subject or condition ends;
- distinguish relevant facts from noise;
- select the governing rule, basis, timing, classification, or convention;
- translate prose into a formula or accounting model;
- identify loose ends and reconcile them;
- eliminate answers using diagnostic evidence; and
- resist realistic language traps without being subjected to bad writing.

Controlled exam-style traps are allowed. Genuinely ambiguous syntax,
gratuitous double negatives, hidden assumptions, and multiple defensible
answers are forbidden.

## Question contract

Every question must carry, at minimum:

- a stable identity and content version;
- a four-option stem with exactly one defensible keyed answer;
- granular Blueprint mappings and the tested skill level;
- an accounting-rule or model identifier;
- a structured fact set sufficient to verify the answer where applicable;
- a worked solution;
- a plain-language statement of the end ask;
- relevant-fact and irrelevant-fact annotations;
- the intended solution representation or setup;
- a rationale for the keyed answer;
- a named misconception or error model for every distractor;
- one or more challenge-mechanic tags;
- source provenance and currency information;
- mechanical verification status; and
- human review status bound to the exact content version.

The learner-facing explanation must answer:

1. What is the question asking for?
2. Which facts matter, and which can be discarded?
3. Which rule, formula, or accounting model governs?
4. Why is the keyed answer correct?
5. What mistake does each distractor represent?
6. Is there a faster or safer test-taking route?

## Independent correctness evidence

The producer of a keyed answer may not be its sole judge. Every learner-ready
question must have an independent correctness route appropriate to its type:

- computational items independently recompute from the structured facts;
- classification, presentation, and rule-selection items trace to the
  controlling rule plus independently authored fixtures or assertions;
- complex families use a second solver or hand-worked reference cases where
  feasible; and
- every item still requires individual human approval.

An “independent” route may not merely call the same deciding function or reuse
the producer's answer as its expected value. Where full independence is not
feasible, the limitation is explicit in the item's evidence and cannot be
silently treated as equivalent proof.

## AI authorship boundary

AI may draft structured facts, stems, misconception models, answer choices,
and explanations. Every such output enters only as a candidate. AI output,
model agreement, confidence, fluency, or self-critique is not evidence of:

- accounting truth or source authority;
- answer correctness;
- Blueprint completeness or valid coverage;
- originality beyond named comparison checks; or
- human approval.

Candidate provenance records the authoring mechanism and material inputs. AI
authorship never bypasses independent correctness evidence, calibrated
verification, or individual human review.

## Variety obligation

Question variety is enforced, not inferred from item count. The final bank
must satisfy a ratified multidimensional variety matrix that addresses at
least:

- stem length and fact density;
- conceptual, computational, classification, and analytical work;
- number of reasoning or calculation steps;
- relevant versus extraneous information;
- direct versus indirect asks;
- rule, timing, basis, measurement, presentation, and convention traps;
- task representation, including formula, roll-forward, journal-effect, and
  financial-statement views where appropriate;
- distractor misconception families; and
- realistic time pressure.

Exact dimensions, bins, combinations, and minimums are deliberately not
ratified at bootstrap. Gate G2 reviews a deliberately varied first-pass
sample. Before production may continue, the findings must be folded into a
dated `goal.md` amendment containing the enforceable variety matrix and
coverage floors. Until that amendment exists, sample generation is the only
question generation authorized.

## Difficulty and diagnostic dimensions

The learner-ready bank deliberately spans foundational through high-pressure
items. It may not make every item maximally punishing, and it may not allow
cheap direct-recall items to dominate merely because they are easier to
produce.

Difficulty is multidimensional rather than one unexplained “easy / medium /
hard” label. The G2 amendment must define ratable item-side dimensions that
include at least:

- accounting complexity;
- number and dependency of reasoning or calculation steps;
- reading and fact-selection burden;
- rule, basis, timing, classification, or convention pressure;
- distractor closeness and elimination burden; and
- realistic time pressure.

The `far-bank` project owns validated question-side dimension records. It does
not rank learners or infer their abilities. A later learner/progress project
may combine these records with response evidence to estimate multidimensional
strengths and weaknesses.

Every difficulty and challenge-mechanic rating must be:

- stored as structured data;
- defined by a written rubric;
- supported by observable question features;
- included in the G2 sample review and adjustable through the G2 amendment;
  and
- independently reviewable rather than assigned solely by unexplained AI
  judgment.

For example, a high reading-burden rating may cite fact count, irrelevant-fact
count, conditional clauses, and ask placement. “The model thinks this feels
hard” is not rating evidence.

## Coverage claim levels

The project reports coverage at three distinct levels:

1. **Mapped** — at least one learner-ready MCQ is validly mapped to the
   representative task.
2. **MCQ-depth covered** — the learner-ready MCQs mapped to the task satisfy
   the ratified G2 coverage and variety floors.
3. **Full task exercised** — the approved assessment format genuinely requires
   performance of the complete representative task.

Because this project is MCQ-only, it must not claim **Full task exercised**
for preparation, reconciliation, correction, document-driven, or other tasks
whose complete performance is not genuinely elicited by MCQs. Reports must
show the limitation explicitly rather than collapsing all three levels into a
single “covered” label.

## Source and currency policy

- The official AICPA Blueprint controls examinable scope, hierarchy, task
  language, skill mappings, and published weighting.
- Accounting claims must trace to an eligible authoritative or approved
  reference named in the Blueprint. Secondary references may explain a rule
  but may not silently override an authoritative source.
- Every source record includes enough identity and currency information to
  recheck it later.
- The AICPA policy on new pronouncements governs when changed accounting
  guidance becomes exam-eligible.
- No AICPA question, retired item, commercial question-bank item, or other
  copyrighted question text may be copied or closely paraphrased. Such
  materials may inform structural research only when legally available and
  clearly recorded as non-content references.
- Every originality report names the exact material actually compared and the
  comparison methods used. Automated similarity checks may support a bounded
  claim against that corpus; they may not claim global uniqueness, exhaustive
  comparison, legal clearance, or guaranteed non-infringement.
- Source disagreement is recorded with provenance and escalated; it is never
  averaged into a synthetic rule.

### Revalidation after source change

- A new FAR Blueprint or changed controlling guidance triggers an explicit
  impact analysis against question mappings and rule traces.
- Every affected question is quarantined from learner-ready status and stops
  counting toward coverage until its mapping, rule trace, mechanical checks,
  explanation, and human approval are revalidated against the new source
  version.
- Historical records remain preserved; quarantine never rewrites prior
  evidence or review events.
- Unaffected questions do not require ceremonial reapproval merely because a
  date changed. The impact analysis must identify and justify the affected
  boundary.

## Human approval rule

No question is learner-ready until both conditions hold:

1. all required automated checks pass; and
2. James individually approves that exact content version.

Automation may reject or flag an item but cannot grant final approval.
Approval records must identify the reviewer, verdict, reviewed content
version, and review time. Editing approval-bound content invalidates the
approval. Rejected and revision-requested items remain visible in audit
history but do not count toward coverage.

The review workflow must support Approve, Reject, Revise, and Comment without
requiring direct edits to generated data.

## Version and review history

- A substantive revision creates a new immutable content version; it never
  overwrites the version that was reviewed.
- Approvals, rejections, revision requests, comments, and automatic
  invalidations are append-only review events.
- Current status is derived from immutable content versions, mechanical-check
  results, and review events; it is not an independently editable truth.
- Historical versions and decisions remain auditable even when they no longer
  count toward learner-ready coverage.
- These are storage-independent rules. A later architecture ruling may use
  JSON, SQL, or both only if it preserves these invariants and reproducible
  exports.

## Decision defaults

- Questions are original four-option MCQs.
- The generator produces candidates; it never produces approvals.
- Approved coverage counts only the latest mechanically passing, individually
  approved content version.
- Blueprint weights guide coverage design but do not mechanically translate
  into item counts without the G2 ruling.
- Representative-task counts in the Blueprint do not imply relative exam
  weight.
- A single question cannot prove meaningful coverage of a representative
  task.
- Question wording favors precision first and exam realism second; difficulty
  may come from legitimate reasoning and controlled traps, never ambiguity.
- Deterministic generation, stable identifiers, and reproducible reports are
  preferred wherever feasible.
- A rejected candidate may be revised into a new version; rejection history
  is retained.

## Allowed without asking

Within a ratified phase, the agent may:

- create and revise schemas, generators, solvers, fixtures, tests, reports,
  and the internal review surface;
- reject generated candidates that fail mechanical or authored constraints;
- strengthen checks without weakening ratified requirements;
- reorganize `plan.md` and implementation details;
- record source gaps, uncertainty, scope temptations, and gate questions;
- regenerate derived artifacts; and
- choose reversible technical implementations that do not alter the contract.

## Approval required

- Ratification of this goal and every contract amendment.
- Gate G1 taxonomy approval.
- Gate G2 representative-sample review and ratification of the coverage and
  variety amendment.
- Individual learner-ready verdicts for every question.
- Any new source class that changes the source hierarchy.
- Any reduction in Blueprint scope, coverage floors, variety floors, or
  verifier strength.
- Any admission of prior CPA project artifacts.
- Final hands-on review of the internal approval workflow.
- Final project verdict.

## Forbidden

- Generating production-bank questions before the G2 amendment is ratified.
- Counting unapproved, stale-version, or mechanically failing questions as
  coverage.
- Hand-editing generated question artifacts.
- Copying or closely paraphrasing protected question-bank content.
- Using question count as a substitute for coverage or variety proof.
- Silently weakening a verifier, moving a baseline, or granting a waiver to
  obtain green status.
- Treating style fluency as evidence of accounting correctness.
- Treating AI output, agreement, confidence, or self-review as acceptance
  evidence for any learner-ready status requirement.
- Building deferred learner, administrator, lesson, or other-section features
  under this contract.
- Claiming exam equivalence, endorsement, or affiliation with AICPA or NASBA.

## Phase gates

### G0 — Contract ratification

James explicitly ratifies `goal.md` after serialized red-pen rounds and a
deferral-load check. Phase 0 begins only after the signature is recorded.

### G1 — Blueprint taxonomy

Review medium: rendered, source-linked taxonomy plus discrepancy report.

James rules whether the captured FAR hierarchy is complete and usable as the
coverage spine. No questions exist at this gate.

### G2 — Representative first-pass sample

Review medium: the internal review surface containing a deliberately varied
sample spanning all FAR areas and multiple challenge mechanics.

Each sample item receives an individual verdict. The gate also decides the
enforceable coverage floors, variety matrix, and any prose-quality rules that
the sample reveals. Those decisions become a dated contract amendment before
production generation begins.

### G3 — Review workflow

Review medium: hands-on use of Approve, Reject, Revise, and Comment flows,
including proof that a content edit invalidates approval and that only valid
approvals affect coverage.

### G4 — Final FAR bank

Review medium: coverage and variety reports, sampled source and arithmetic
evidence, unresolved-gap ledger, and hands-on review of approved items.

Final verdicts are separated into:

- accounting correctness;
- writing fairness and instructional usefulness;
- Blueprint coverage and variety;
- review/audit integrity; and
- learner-readiness of the approved set.

A failure must name its fix axis. Between final attempts, work is bounded to
the failed axis and already ratified gate items.

## Mechanical verifiers — draft strawman for red pen

The verifier is built before production generation and must be calibrated by
deliberately driving every check red with known corruptions. Each individual
check must reject at least one purpose-built defect of the kind it claims to
detect before that check may gate real content; a suite that has only passed
clean data is not calibrated.

1. **SOURCE** — official Blueprint capture identity, hierarchy, source links,
   and currency records are complete.
2. **TAXONOMY** — every FAR Area/Group/Topic/task/skill relationship is valid,
   uniquely identified, and reproducibly rendered.
3. **SCHEMA** — every candidate conforms to the question contract and contains
   four unique options with one key.
4. **RECOMPUTE** — numeric or structured answers independently recompute from
   the recorded facts, conventions, and rounding rules without reusing the
   producer's deciding logic.
5. **RULE TRACE** — every keyed answer and explanation traces to a current,
   approved accounting-rule record.
6. **DISTRACTORS** — each distractor is reproduced by its named error model,
   differs from the key and other options, and remains plausible under the
   stated facts.
7. **LANGUAGE** — forbidden ambiguity patterns, gratuitous double negatives,
   orphan facts/numbers, unsupported assumptions, and answer leakage are
   rejected or flagged for review.
8. **ORIGINALITY** — exact and near-duplicate checks run within the bank and
   against any legally held exclusion corpus. The report names its comparison
   boundary and rejects global-uniqueness or legal-clearance language.
9. **APPROVAL INTEGRITY** — approval binds to the exact content version;
   mutation, failed checks, or source staleness removes learner-ready status.
   Current status reconstructs from immutable versions and append-only events.
10. **COVERAGE** — only learner-ready items count, and the ratified G2 floors
    are satisfied at every required taxonomy level. Reports distinguish
    Mapped, MCQ-depth covered, and Full task exercised and reject unsupported
    level-three claims.
11. **VARIETY** — the approved bank satisfies the ratified G2 variety matrix;
    cosmetically different clones cannot fill distinct cells. Difficulty and
    challenge ratings conform to the ratified rubrics and carry observable
    evidence.
12. **REPRODUCIBILITY** — generation and reports are stable under the recorded
    inputs, with rejection reasons counted so strictness churn is visible.

The final contract may strengthen or reorganize these checks during red pen.
No implementation begins from this strawman before ratification.

## Supporting checks

- Hand-worked fixtures created independently of the production generator.
- Corruption suite proving each mechanical verifier can fail.
- Calibration evidence maps every verifier check to its known-bad fixture and
  observed rejection; adding a new gating check adds a new calibration debt.
- Cross-solver comparison for computational families where feasible.
- Cold reconstruction of coverage and approval reports from source records.
- Blind or answer-isolated review of a sample where practical.
- Accessibility, keyboard, and data-integrity checks for the internal review
  surface.
- Full-project test, lint, and static checks established before production.

## Completion proof

`result.md` may be written only when all of the following concrete artifacts
exist and their ratified checks pass:

- the versioned official-source capture;
- the machine-readable complete FAR taxonomy and rendered G1 report;
- the ratified G2 coverage/variety amendment;
- question, rule, source, review, and approval schemas;
- generators, independent solvers, fixtures, and rejection ledger;
- the calibrated mechanical verifier and corruption evidence;
- the internal review surface and its integrity tests;
- the candidate bank and immutable review history;
- the learner-ready approved bank;
- coverage, variety, source-currency, originality-boundary, and unresolved-gap
  reports;
- evidence for all named gates and individual approvals;
- a final verifier report with zero waivers;
- a final human verdict across all G4 sub-verdicts;
- `worklog.md`, current `state.md`, and the final method retro or a recorded
  deferral trigger; and
- `result.md`, written last.

The G2 amendment must replace these descriptive artifact names with exact
project-relative paths and commands before production begins. No paths means
no completion proof.

## Iteration and recovery

- Design and calibrate the verifier before the producer.
- Generate from the feasible set and record every rejection reason.
- A failing item is fixed at its owning layer: source, taxonomy, facts, solver,
  distractor model, articulation, or review record.
- Never patch a generated output to satisfy a check.
- If a human verdict fails, build only the named fix axis plus previously
  ratified gate items, then represent the relevant medium.
- After a crash or context loss, resume from `state.md`, verify it against
  `worklog.md` and disk artifacts, and continue from the named next action.

## Blocker rule

Difficulty, long runtime, uncertainty, and first failures are not blockers.
An agent-side blocker requires concrete evidence, no safe in-scope fallback,
and the same condition across three consecutive turns.

If the block is in the world—a required James verdict, inaccessible source,
or external dependency—the project becomes ON HOLD with a named resumption
trigger in `state.md` and `CLAUDE.md`; the agent blocker threshold does not
apply.

## State files

- `goal.md`: human-ratified contract; amendments are explicit and dated.
- `plan.md`: agent-owned current strategy; freely rewritten.
- `state.md`: cold-resume cache; rewritten from scratch at wind-down.
- `worklog.md`: append-only decisions, evidence, and `METHOD:` observations.
- `result.md`: created last, only after completion proof.
- `CLAUDE.md`: brief signpost pointing to `state.md`, never a duplicate state
  ledger.

## Amendment — 2026-08-13 — Gate G2 production contract

**RATIFIED BY JAMES — 2026-08-13.** Every provision below is operative. Gate G2
is closed and P2 is authorized within this amendment's exact boundaries.

This amendment is derived from proposal `far-g2-contract-proposal.v001` at
`docs/gates/g2-proposed-amendment.md`, the reviewed current queue
`far-p1-g2-sample.v002` at `data/sample/p1/manifest.json`, and the exact-version
review events under `data/events/review/`.

### Coverage floors

- **Mapped:** at least one learner-ready exact-version MCQ maps to each of the
  113 representative tasks.
- **MCQ-depth covered:** at least three learner-ready MCQs map to the task; the
  set contains at least two primary solution representations and two distinct
  challenge-mechanic tags, and no pair shares both the same fact pattern and
  distractor-model set. Three cosmetic variants or one repeated rule boundary
  do not establish depth.
- **Full task exercised:** never follows from mapping or MCQ-depth counts. It is
  true only when the approved format actually performs the full task.
  Preparation, reconciliation, correction, investigation, and document-driven
  MCQ mappings ordinarily remain false with an explicit scope limitation.
- The minimum learner-ready bank is **353** exact versions: Area I **141**
  (47 tasks × 3), Area II **120** (40 × 3), and Area III **92** (26 × 3 plus
  14 depth items). As the bank grows, Area I remains 30–40%, Area II 30–40%,
  and Area III 25–35% unless a dated Blueprint change triggers revalidation.
- Stale, failing, quarantined, unapproved, or superseded versions count zero.
  Multi-task mappings require independent justification, count once in the
  bank total, and cannot alone satisfy any task-depth floor. Every aggregate
  coverage claim resolves to exact item IDs and versions.

### Variety matrix

Floors apply only to learner-ready exact versions. Percentage floors use
`ceil(total × floor)`; unallocated share is deliberate design freedom.

| Dimension | Observable bins | Enforceable bank-wide floors |
| --- | --- | --- |
| Stem length | short ≤45 words; standard 46–90; dense ≥91 | short ≥20%; standard ≥45%; dense ≥15% |
| Numeric fact density | low 0–2; medium 3–5; high ≥6 | each ≥15% |
| Primary accounting work | conceptual recall; classification/rule selection; computation; analytical reconciliation/inference | recall ≥8%; classification/rule ≥20%; computation ≥30%; analytical ≥20% |
| Dependent solution steps | one; two-to-three; four-plus | one ≥10%; two-to-three ≥50%; four-plus ≥10%; decorative subdivision does not count |
| Irrelevant facts | none; one-to-two; three-plus | none ≥30%; one-to-two ≥30%; three-plus ≥10% |
| Ask placement | direct/final sentence; indirect or embedded after setup | direct ≥60%; indirect/embedded ≥20%; indirect asks are deliberate, tagged, and restated in `solution.end_ask` |
| Rule pressure | rule; timing; basis; measurement; classification; presentation; convention | every tag ≥5%; multi-tags require separate observable evidence |
| Primary solution representation | formula; roll-forward; journal effect; financial-statement view; rule selection; classification | every representation ≥5%; one evidence-based primary representation per item |
| Elimination burden | low: one obviously invalid distractor; medium: all plausible but two fall to one rule; high: separate diagnosis for each | low ≥10%; medium ≥40%; high ≥15%; named error models support the bin |
| Realistic time pressure | low = rubric levels 1–2; moderate = level 3; high = levels 4–5 | low ≥15%; moderate ≥45%; high ≥15% |

Estimated and observed completion times are separate fields. Observed human
data changes calibration only through a recorded revalidation event.

### Anti-cloning rules

1. Every nonkey has one named misconception/error path and either an executable
   reproduction yielding its exact result or an independently authored
   assertion fixture for a nonnumeric answer. Random nearby values, generic
   filler, and unsupported plausibility are forbidden.
2. Across each task's three-item minimum, at least five distinct distractor
   error-model IDs appear among nine nonkeys, and no two items share the same
   complete three-model set. Genuine partial reuse is allowed.
3. No single stem template, accounting fact pattern, primary solution
   representation, or distractor family exceeds 25% of the learner-ready bank.
   Stable identifiers or reproducible classification evidence make each cap
   auditable.
4. Items with three-plus irrelevant facts are at least 10% and no more than 40%
   of the bank. Noise tests fact selection; it is not the default prose style.
5. Every FAR area includes at least one learner-ready item for every applicable
   skill and every genuinely compatible solution representation. Reports show
   the area matrices and explicit rationales for excluded combinations;
   incompatible combinations are documented rather than forced.

### Six-dimensional difficulty rubric

No aggregate easy/medium/hard field is permitted. Each level records its
observable evidence.

| Dimension | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- |
| Accounting complexity | one familiar rule; no exception | one rule plus one boundary | two interacting rules or one exception | three interacting rules/conditions | four-plus interactions or judgment with competing treatments |
| Reasoning steps | one dependent step | two | three | four | five-plus with a branch or reconciliation loop |
| Reading/fact selection | ≤3 facts; no irrelevant facts | 4–5 facts or one irrelevant | 6–7 facts or two irrelevant | 8–10 facts or three-plus irrelevant facts/conditional clauses | 11-plus facts with dependencies across passages/exhibits |
| Rule/convention pressure | direct application; no nearby boundary | one named boundary | two boundaries or one controlled convention trap | three boundaries or timing/basis interaction | four-plus boundaries with demanding, defensible exception analysis |
| Distractor/elimination burden | one obviously invalid distractor | three distinct errors; one readily eliminated | all plausible; two fall to one rule | separate diagnoses and one numerically close | separate diagnoses plus competing intermediate results or convention traps |
| Realistic time pressure | ≤30 seconds and ≤1 operation | 31–60 seconds or 2 operations | 61–90 seconds or 3–4 operations | 91–150 seconds or 5–7 operations | >150 seconds or 8-plus operations/branching review |

Apply the highest level only when its observable condition exists. If two
descriptors conflict, record the lower supported level and flag human review.
Keep estimated and observed time separate. Preserve the six-number diagnostic
profile without averaging it into one label.

### Prose and fairness rules

1. The final sentence is a direct question unless an indirect ask is deliberate,
   tagged, and restated unambiguously in `solution.end_ask`.
2. Every number, date, threshold, and stated assumption has a structured record;
   every structured fact appears in the stem or an identified exhibit.
3. Default for-profit/U.S.-GAAP assumptions follow the Blueprint. NFP,
   governmental, public-company, and special-purpose-framework facts name the
   entity and framework explicitly.
4. An answer-changing assumption is explicit in the stem or traces to
   controlling authority. Hidden answer-changing conventions are forbidden.
5. Irrelevant facts are realistic and individually annotated. Orphan numbers
   and decorative noise are forbidden.
6. Negative phrasing is limited to deliberate exception testing. Double
   negatives, `not incorrect`, and mixed `except/not` constructions are
   forbidden.
7. Options are grammatically parallel, mutually exclusive, unique after
   normalization, and consistent in units, dates, rounding, and sign language.
8. The stem cannot leak the key. Absolute words such as `always` and `never`
   require controlling authority or are treated as leakage.
9. Every explanation contains the six ratified diagnostic elements and states
   why every distractor is wrong under the facts.
10. Mechanical language checks are targeted screens, not proof of clarity,
    fairness, or instructional value. James's exact-version verdict owns those
    judgments.

### Correctness-route expansion before production

Before any production family is generated, add and red-calibrate independent
verifier routes for:

- percentage, ratio, present-value, effective-interest, and per-share formulas;
- date and period schedules;
- conditional rule tables and classification assertions;
- journal-entry balance and account-direction checks;
- roll-forwards with multiple linked subtotals; and
- independently authored reference fixtures for nonnumeric questions.

No production family may proceed unless its route is executable or explicitly
bounded. Producer deciding logic cannot serve as independent verification.

### Artifact-first hybrid architecture

- Immutable JSON question versions and append-only JSON events are canonical.
- SQLite is a disposable, transactionally rebuilt local projection.
- The review surface proposes events but cannot directly grant approval.
- Canonical ingestion validates and exclusively creates each event file.
- Cold reconstruction from canonical JSON reproduces review, readiness, and
  coverage state.
- Hosted persistence, accounts, learner/admin applications, and public
  deployment remain deferred.

### Exact G2 and production evidence

- Current sample manifest: `data/sample/p1/manifest.json`.
- Historical gate-opening manifest: `data/sample/p1/manifest.v001.json`.
- Current sample verification: `reports/p1-sample-verification.v002.json`.
- Gate-opening receipt: `reports/g2-package-manifest.json`.
- Current review data: `review-surface/app/review-data-v002.json`.
- Canonical review ledger: `data/events/review/`.
- Proposed policy source: `docs/gates/g2-proposed-amendment.md`.
- Architecture records: `docs/architecture/0001-artifact-first-hybrid.md` and
  `docs/architecture/0002-p1-record-contracts.md`.
- Required pre-production commands include:
  `python scripts/validate_p1_records.py`,
  `python scripts/verify_taxonomy.py data/far-taxonomy.json`,
  `python scripts/calibrate_question_verifier.py`,
  `python scripts/verify_p1_sample.py`,
  `python -m unittest discover -s tests -p "test_*.py"`,
  `python -m compileall -q scripts tests`,
  `npm run lint` from `review-surface/`, and
  `npm test` from `review-surface/`.

Ratification of this amendment closes G2 and authorizes P2 only within these
terms. It does not approve the G3 workflow, any future question version,
learner/admin product scope, hosting, or public launch.
