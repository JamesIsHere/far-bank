# worklog.md — append-only project history

## Session s1 — 2026-08-13 — bootstrap interview and first draft

### Program boundary

- James described the long-term product as a website with high-quality CPA
  questions, configurable quizzes, sectional practice of chosen lengths,
  learner progress and skill visibility, eventual supporting lessons, and an
  administrator view of learner and content performance.
- RULING: retain that as the `cpa-learning` program vision; do not force it into
  one build goal.
- RULING: create a broad program root at `workshop/cpa-learning` and make
  `far-bank` its first Goal Method child. Do not pre-create speculative later
  children.
- METHOD: this follows the program/child pattern tested in `atlas`: root-level
  mission and cross-project rulings, independently ratified child contracts,
  and no duplicated fine-grained state at the root.

### FAR project interview rulings

- RULING: phase-gated hybrid operating mode. James ratifies gates; autonomous
  execution is allowed within ratified phases.
- RULING: target a learner actively preparing to pass the current FAR exam.
- RULING: cover the complete current FAR Blueprint, mapping the full hierarchy
  before generating questions and then working area by area.
- RULING: original four-option MCQs only for this project; TBS work is deferred.
- RULING: question difficulty includes exam execution, not merely hard
  accounting calculations. Required concerns include parsing the ask,
  identifying the end game, eliminating choices, translating prose into a
  formula or model, detecting loose ends, choosing beginning/ending/average or
  other conventions, and navigating rule-heavy gotchas.
- RULING: controlled realistic traps are allowed; genuinely ambiguous wording
  and gratuitous double negatives are forbidden.
- RULING: every learner-ready question requires automated checks and individual
  human approval. James is the initial approver.
- RULING: question variety must be enforceable. Exact dimensions and floors are
  decided after a representative first-pass sample rather than guessed before
  seeing questions.
- RULING: start from a clean baseline. Older CPA work is preserved outside the
  program as untrusted prior art, not inherited completion evidence.

### Current-source check

- The official AICPA resource page was checked on 2026-08-13. It identifies the
  Uniform CPA Examination Blueprints effective January 1, 2026 and describes
  their Area/Group/Topic, representative-task, skill-level, reference, item-
  type, and weighting information.
- Phase P0 still owes a versioned capture and exact FAR taxonomy; bootstrap
  research does not satisfy that future gate.

### Drafting decisions

- The first `goal.md` is an artifact for red pen, not a contract.
- Candidate production coverage floors and the variety matrix are staged as a
  mandatory G2 amendment. Production generation is forbidden before that
  amendment, preserving the user's request to judge variety from concrete
  samples while keeping the obligation enforceable.
- The verifier list is a drafted strawman per the Goal Method: concrete enough
  to criticize, not elicited from James as a blank-page technical interview.

### Wind-down receipt

worklog initialized; state.md written from scratch; child and program
CLAUDE.md signposts created; bootstrap scope checked for consistency. No
execution or question generation performed.

### Red-pen round 1 — G2 completion floors and variety matrix

- Candidate issue: exact question-count floors and the enforceable variety
  matrix are not guessed at bootstrap. A deliberately varied first-pass sample
  is reviewed at Gate G2; production is forbidden until the resulting floors
  become a dated contract amendment.
- James ruling: KEEP — “Yes that's approved.”
- Rationale retained from the interview: concrete questions provide a better
  basis for judging length and other variety dimensions than premature numeric
  targets.
- Contract change: none required; the draft already states the approved
  mechanism.

### Red-pen round 2 — content foundation versus learner product

- Candidate issue: `far-bank` includes only the internal review surface needed
  to inspect, revise, approve, reject, and audit questions. The learner-facing
  website, quiz assembly, accounts, progress, skill modeling, lessons, and
  administrative analytics remain later program projects.
- James ruling: KEEP — “Approved.”
- Rationale: keeping the boundary lets the child reach a verdict on question
  correctness, coverage, variety, and approval integrity without making those
  claims contingent on building the broader product.
- Contract change: none required; the Included and Explicitly deferred
  sections already state the approved boundary.

### Red-pen round 3 — accounting source standard

- Candidate issue: every accounting claim and keyed answer must trace to an
  eligible authoritative or explicitly approved reference. Secondary sources
  may explain a rule but may not silently override the controlling source.
- James ruling: KEEP — “I like that. That's really good. Approved.”
- Rationale: claim-level source traceability helps detect a shared wrong rule
  repeated consistently by the generator, solver, and explanation.
- Contract change: none required; Source and currency policy plus the RULE
  TRACE verifier already state the approved standard.

### Red-pen round 4 — version-bound human approval

- Candidate issue: approval belongs to the exact reviewed content version;
  changing approval-bound content removes learner-ready status until the new
  version is reviewed.
- James ruling: KEEP — “Approved.”
- Rationale: an approval must not become a transferable badge that silently
  survives changes to the evidence the reviewer actually judged.
- Contract change: none required; Human approval rule and APPROVAL INTEGRITY
  already state the approved behavior.

### Red-pen round 5 — preserve the official Blueprint hierarchy

- Candidate issue: the coverage spine preserves the complete official FAR
  Area → Group → Topic → representative-task → skill hierarchy instead of
  collapsing it into a simpler homegrown topic list. Teaching labels and finer
  concepts may supplement but never replace the official mapping.
- James ruling: KEEP — “That's correct. Proceed.”
- Rationale: the extra taxonomy work prevents a convenient internal topic list
  from concealing gaps in the published Blueprint structure.
- Contract change: none required; Content boundary, Question contract, and the
  TAXONOMY verifier already state the approved behavior.

### Red-pen round 6 — misconception-derived distractors

- Candidate issue: every distractor represents a named, reproducible
  misconception or error path rather than a merely plausible-looking wrong
  value. The verifier reproduces the error where the item structure permits.
- James ruling: KEEP — “Approved.”
- Rationale: wrong answers are part of the question's diagnostic and teaching
  value; random nearby numbers and generic filler cannot provide that value.
- Contract change: none required; Question contract and DISTRACTORS verifier
  already state the approved requirement.

### Red-pen round 7 — six-part diagnostic explanations

- Candidate issue: every learner-ready explanation contains all six named
  diagnostic elements—end ask, relevant/irrelevant facts, governing model,
  keyed-answer rationale, distractor error paths, and a faster or safer route.
  An element may be brief for a simple conceptual item but not omitted.
- James ruling: KEEP — “Approved.”
- Rationale: the structure turns James's exam-execution observations into an
  enforceable learner-facing requirement rather than optional explanation
  polish.
- Contract change: none required; Question contract already names all six
  required elements.

### Red-pen round 8 — honest MCQ coverage claims

- Candidate issue: an MCQ-only bank cannot honestly claim complete exercise
  of every Blueprint task, especially preparation, reconciliation,
  correction, and document-driven tasks.
- James ruling: KEEP — approve three distinct statuses: Mapped, MCQ-depth
  covered, and Full task exercised.
- Rationale: reports should prove what the chosen format actually tests rather
  than turning a valid taxonomy link into an inflated mastery claim.
- Contract change: added Coverage claim levels and strengthened the COVERAGE
  verifier to reject unsupported Full task exercised claims.

### Architecture note raised during round 8

- James began considering whether the project should use JSON files or SQL.
- Decision deferred to an artifact-first P1 architecture draft rather than a
  blank-page technical interview. Current design hypothesis: immutable,
  versioned source records; an SQL-backed internal review workflow; and
  reproducible JSON exports for verification and later program children.
- The contract should first ratify storage-independent integrity rules. The
  implementation medium remains reversible until its design artifact is
  reviewed.

### Red-pen round 9 — immutable versions and append-only review history

- Candidate issue: revisions create new immutable content versions, while
  approvals, rejections, revision requests, comments, and invalidations are
  append-only events. Current learner-ready status is derived rather than
  directly edited.
- James ruling: KEEP — “Approved.”
- Rationale: the system must prove exactly what was reviewed and explain every
  later status change, regardless of whether the implementation uses JSON,
  SQL, or both.
- Contract change: added Version and review history and strengthened APPROVAL
  INTEGRITY to require reconstruction from immutable records.

### Red-pen round 10 — bounded originality claims

- Candidate issue: automated similarity checks report the exact corpus and
  methods used and cannot prove global uniqueness or legal non-infringement.
- James ruling: KEEP — “yes.”
- Rationale: the evidentiary claim must stop where the comparison surface
  stops; stronger language would turn an incomplete search into false proof.
- Contract change: strengthened Source and currency policy and ORIGINALITY to
  require a named boundary and forbid global or legal-clearance claims.

### Red-pen round 11 — calibrate every verifier check

- Candidate issue: every gating check must first reject a purpose-built known
  defect of the type it claims to detect; passing clean data alone does not
  establish that the checker discriminates.
- James ruling: KEEP — “I agree.”
- Rationale: the verifier is itself a claim-bearing artifact and must be
  tested red before its green output can count as evidence.
- Contract change: strengthened Mechanical verifiers and Supporting checks to
  require check-to-corruption calibration evidence and new-check calibration
  debt.

### Red-pen round 12 — independent correctness evidence

- Candidate issue: the generator cannot be the sole judge of its own answer;
  each learner-ready question needs an independent correctness route suited to
  its type, without reusing the same deciding logic.
- James ruling: KEEP — “Keep.”
- Rationale: internally consistent question, answer, and explanation text can
  all share one mistake unless correctness is derived through a genuinely
  separate path.
- Contract change: added Independent correctness evidence and strengthened
  RECOMPUTE.

### Red-pen round 13 — AI authors candidates, not evidence

- Candidate issue: AI may draft question components, but AI output, agreement,
  confidence, fluency, or self-review cannot establish accounting truth,
  source authority, answer correctness, Blueprint coverage, originality, or
  human approval.
- James ruling: KEEP — “yes.”
- Rationale: authoring throughput and acceptance evidence are separate jobs;
  allowing one model to perform both would defeat the independent controls
  already ratified.
- Contract change: added AI authorship boundary and a matching prohibition.

### Red-pen round 14 — scoped revalidation after source changes

- Candidate issue: a new Blueprint or changed controlling guidance
  automatically removes affected questions from learner-ready coverage until
  their mapping, rule trace, checks, explanation, and human approval are
  revalidated. Unaffected items are not ceremonially reapproved.
- James ruling: KEEP — “yes.”
- Rationale: a durable bank must react to substantive source change without
  either serving stale content or needlessly invalidating everything.
- Contract change: added Revalidation after source change. Existing APPROVAL
  INTEGRITY already names source staleness as status-invalidating.

### Red-pen round 15 — multidimensional difficulty range

- Candidate issue: the bank deliberately spans foundational through
  high-pressure questions. Difficulty is decomposed into accounting
  complexity, step structure, reading/fact selection, rule or convention
  pressure, distractor closeness, and realistic time pressure. G2 sets the
  actual distribution after concrete review.
- James ruling: KEEP — “Yes,” with the added product insight that these
  dimensions can later support ranking or assessing learners along multiple
  difficulty dimensions.
- Rationale: one opaque difficulty label cannot distinguish knowing the
  accounting from parsing, setup, elimination, or execution pressure.
- Contract change: added Difficulty and diagnostic dimensions. `far-bank`
  owns validated item-side profiles; learner ranking and skill inference stay
  deferred to a later program child.

### Red-pen round 16 — rubric-backed structured difficulty ratings

- Candidate issue: every difficulty and challenge-mechanic rating is
  structured, defined by a written rubric, evidenced by observable item
  features, reviewed at G2, and forbidden from resting on unexplained AI
  judgment.
- James ruling: KEEP — “yes.”
- Rationale: later multidimensional learner analysis is only as trustworthy as
  the item-side dimensions it consumes; opaque labels would manufacture false
  precision.
- Contract change: strengthened Difficulty and diagnostic dimensions and the
  VARIETY verifier.

### Pre-ratification deferral-load check

Review tally:

- KEEPS: 16.
- KILLS: 0.
- PARKS: 1 implementation choice—concrete JSON/SQL architecture awaits an
  artifact-first P1 design review; storage-independent integrity rules are
  already contractual.
- SILENT SKIPS: 0 found when reconciling the interview rulings against
  `goal.md`, `plan.md`, `state.md`, and the program root.

Forward obligations and durable homes:

1. Agent, P0 (`goal.md` G1; `plan.md` P0): capture the current official FAR
   Blueprint, build and calibrate the taxonomy verifier, and render the full
   source-linked hierarchy. James owes Gate G1 taxonomy approval.
2. Agent, P1 (`goal.md` G2; `plan.md` P1): draft the concrete JSON/SQL data
   architecture, schemas, calibrated question verifier, internal review
   surface, and deliberately varied cross-area sample.
3. James, G2 (`goal.md` Variety obligation, Difficulty dimensions, G2): issue
   individual sample verdicts and ratify exact coverage floors, variety
   matrix, difficulty rubrics, and any sample-born prose rules as a dated
   contract amendment.
4. Agent, P2 (`goal.md` G3; `plan.md` P2): implement production generation and
   approval-integrity mechanics only after the G2 amendment. James owes the G3
   hands-on workflow verdict.
5. Agent and James, P3/G4 (`goal.md` Human approval rule and G4): production
   proceeds in bounded Blueprint batches; James individually approves every
   learner-ready version and issues the final named sub-verdicts.
6. Final wind-down (`goal.md` Completion proof and State files): agent runs or
   explicitly defers the method retro with a named trigger and writes
   `result.md` last only after proof exists.

Scope classification:

- FENCES for this child: no inherited completion evidence; no production
  before G2; no unapproved coverage; no hand-edited generated content; no
  unsupported full-task, global-originality, endorsement, or AI-as-evidence
  claims; no weakened verifier or waiver path.
- DEFERRALS to later program children: other CPA sections, TBS/numeric-entry
  formats, learner website, accounts, configurable quizzes, progress and skill
  inference, recommendations, adaptive sequencing, administrator analytics,
  lessons, and commercial/public launch. These are program possibilities, not
  owed deliverables with dates or current owners.
- PARKED implementation choice: JSON versus SQL versus a split. Owner is the
  P1 architecture artifact; decision occurs before the chosen storage design
  becomes expensive to change.

Counter-pressure: the red pen produced sixteen keeps and zero kills while
adding several evidence obligations. Product scope remains sharply fenced,
but verification and metadata scope grew. The execution plan must resist
turning auditability into ornamental infrastructure: every schema field,
checker, and interface element must trace to a named contract claim or gate.

### G0 — contract ratification

- James ruling: RATIFY — “yes.”
- Date: 2026-08-13.
- Bound artifact: `goal.md` after 16 serialized keeps, zero kills, one parked
  implementation choice, zero silent skips, and the deferral-load check above.
- Effect: bootstrap ends; `far-bank` becomes LIVE and Phase P0 is authorized.
- Execution boundary remains: taxonomy work only through Gate G1. Sample
  question generation is P1 work; production generation remains forbidden
  until the ratified G2 amendment exists.

### P0 execution receipt — official source through G1 package

Date: 2026-08-13.

P0.0 — official source acquisition:

- Preserved the AICPA-linked `CPA_Exam_Blueprints_2026.pdf` unchanged under
  `sources/aicpa/2026-01/`.
- Recorded retrieval authority, timestamps, visible approval/effective dates,
  115-page identity, 788,395-byte length, and SHA-256
  `0fca69b073bb0ed46b06ca51c2e1dfaec434346e628f6996fa34b19c2bc02680`.
- Confirmed `%PDF-1.7`, successful text extraction, and visual rendering of
  physical pages 1, 29, 30, 32, 35, and 46. FAR spans physical pages 29–46,
  printed FAR1–FAR18.
- Recorded rather than erased the stale embedded 2022 PDF title and Poppler
  font-weight/control-glyph extraction warnings.

P0.1 — schema layer:

- Added strict source-manifest, FAR-taxonomy, and separate supplementary-label
  schemas. Official labels remain separate from future project-authored
  concepts and teaching labels.
- Validated the preserved manifest and representative valid taxonomy fixture.
- Purpose-built malformed fixtures proved rejection of missing provenance,
  invalid FAR skill, and an empty hierarchy node.

P0.2 — verifier first and red calibration:

- Built 13 SOURCE/TAXONOMY checks covering source schema/file/hash/PDF/effective
  identity; taxonomy schema/source binding/unique IDs/parentage and order;
  exact locators; task text, hierarchy, and drawn skill; full completeness;
  and deterministic rendering.
- The producer probes PDF geometry with pdfplumber. The verifier independently
  reconstructs the tables with PyMuPDF, including vector checkmarks and drawn
  row rules.
- Fifteen calibration tests pass. Every named verifier check rejects at least
  one purpose-built corruption, and the clean representative fixture passes
  all checks not intended to enforce full-bank completeness.

P0.3 — complete extraction:

- Generated `data/far-taxonomy.json` with stable identifiers and exact official
  labels: 3 Areas, 22 Groups, 18 Topics, and 113 representative tasks.
- Reconciled 113 unique source-row locators and skill distribution: 27
  Remembering and Understanding, 67 Application, and 19 Analysis.
- Independent live verification reports zero missing or extra areas, groups,
  topics, or task rows and zero wrong task-text or skill mappings.
- `data/discrepancies.json` reports zero open taxonomy discrepancies and two
  documented nonblocking source anomalies.

P0.4 — G1 artifact:

- Rendered `reports/far-taxonomy-g1.html`, including source links, official
  allocations, stable task IDs, skill badges, full hierarchy, source identity,
  and discrepancy report.
- Cold regenerated and byte-compared the report. Stable render SHA-256 is
  `55c4ea79a22ed66db982f8aa38dcb7132528cfcbdcab130524238f432e6a9634`.
- `reports/verification.json` records 13/13 checks passing. Python compilation
  and all 15 verifier calibration tests pass.
- Attempted browser visual QA using the required browser-control skill; no
  browser backend was available. This did not substitute a different browser
  mechanism. Human G1 remains the live visual review.

Kill sweep and receipt:

- No question files or question-generation path were introduced. P1/G2 data
  architecture, coverage floors, variety matrix, difficulty rubric, review
  workflow, learner surfaces, and other CPA sections remain deferred exactly
  where the contract places them.
- No old CPA artifact was imported or counted as evidence.
- P0.0–P0.4 satisfy their exit evidence. P0.5 now waits at the named human
  terminal: James's G1 verdict on the rendered taxonomy medium.

### G1 — Blueprint taxonomy verdict

- James ruling: PASS — “Pass.”
- Date: 2026-08-13.
- Reviewed medium: `reports/far-taxonomy-g1.html`, bound to deterministic
  render SHA-256
  `55c4ea79a22ed66db982f8aa38dcb7132528cfcbdcab130524238f432e6a9634`.
- Bound evidence: `data/far-taxonomy.json` at 3 Areas, 22 Groups, 18 Topics,
  and 113 representative tasks; `reports/verification.json` at 13/13 passing;
  `data/discrepancies.json` at zero open taxonomy discrepancies.
- Effect: James approved the captured FAR hierarchy as complete and usable as
  the coverage spine. This verdict covers the rendered taxonomy medium only;
  it does not approve any question, sample, coverage floor, or workflow.
- Phase transition: P0 is closed. P1 representative-sample architecture and
  bounded sample work are authorized. Production generation remains forbidden
  until the explicit G2 amendment is ratified.

### P1.0 — artifact-first data architecture

- Added `docs/architecture/0001-artifact-first-hybrid.md` as a proposed G2
  red-pen artifact.
- Decision: immutable canonical JSON owns question/rule/source versions and
  individual append-only verification, review, and source-impact event files.
  A local SQLite database is a disposable, transactionally rebuilt projection
  for the review surface and reports.
- Exact-version binding uses stable question/version IDs and canonical content
  SHA-256. Learner-ready state is derived from the latest content version,
  current calibrated checks, exact-version human verdict, source currency, and
  absence of quarantine or integrity conflicts; it is never an editable field.
- The ADR names the cold-reconstruction proof, single-reviewer concurrency
  boundary, direct future PostgreSQL migration path, and rejected alternatives.
- P1.0 exit evidence is satisfied. The concrete schemas and projection DDL are
  next in P1.1; the architecture remains proposed until James's G2 red pen.

P1 opening kill sweep and resume receipt:

- No sample or production question artifact exists yet; schema and verifier
  work still precedes authoring.
- No mutable status field, sole-source binary database, learner/admin surface,
  or unratified coverage/variety floor entered the implementation.
- Cold resume: begin P1.1 from `plan.md`; `state.md` and the child/program
  signposts all identify the same active phase and next action.

### P1.1 — canonical schemas and representative fixtures

Date: 2026-08-13.

Cold-resume reconciliation:

- Read `CLAUDE.md`, `state.md`, ratified `goal.md`, `plan.md`, the latest
  `worklog.md` entries, and ADR 0001 before changing implementation.
- Confirmed G1 PASS, P1.0 completion, and P1.1 as the exact next unit. No
  question artifact existed under `data/questions/`; production remained
  fenced pending the G2 amendment.

Canonical record contracts:

- Added closed Draft 2020-12 schemas for stable question identity, immutable
  four-option question versions, versioned references, versioned accounting
  rules, exact-version verification events, append-only review events, and
  source-impact events.
- Bound reviews and verification to question ID, version ID, and canonical
  content SHA-256. Approval is a human `approve` review event, never a mutable
  question property or separate approval truth.
- Required granular Blueprint path and skill, structured facts with relevant/
  irrelevant annotations, worked solution and end ask, intended
  representation, rule/assertion trace, distractor error model for every
  nonkey, challenge-mechanic evidence, authorship/material-input provenance,
  bounded originality claim, and all six contract-named difficulty
  dimensions with observable measurements.
- P1 question provenance accepts only `schema_fixture` and
  `sample_candidate`. Production purpose is deliberately unrepresentable
  before the G2 amendment.
- Recorded ADR 0002 explaining canonical hashing, cross-record invariants,
  exact approval semantics, and the G2 fence. Provisional 1–5 fixture ratings
  are explicitly a proposed review transport shape, not ratified rubric bins,
  distributions, floors, or difficulty evidence.

Projection and reconstruction boundary:

- Added `schema/review-projection.sql` with normalized identity, version,
  option, mapping, difficulty, verification, review, and source-impact tables.
- SQLite review state is derived through views. No table has a
  `learner_ready`, `human_approved`, or editable status column.
- Update/delete triggers reject mutation of question versions and append-only
  event rows. The DDL executes successfully against a fresh in-memory SQLite
  database and its immutability trigger is exercised by test.

Fixture and rejection evidence:

- Added one complete representative fixture bundle spanning identity,
  reference, rule, question, verification, human approve-event shape, and
  source-impact shape. Every content-bearing fixture is explicitly schema-
  only; its reference is synthetic and currency-uncertain, so it cannot be
  mistaken for admitted evidence or a G2 sample verdict.
- Added eight declarative corruptions: missing provenance, three options,
  duplicate option text, multiple keyed answers, opaque `hard` difficulty,
  a nonexistent/mismatched Blueprint path, post-hash content mutation, and a
  mutable `learner_ready` shortcut.
- `scripts/validate_p1_records.py` validates schemas, canonical hashes,
  question/version identity, A–D and normalized option uniqueness, solution-
  key binding, six unique difficulty dimensions, live taxonomy path/skill
  resolution, rule/assertion/fact references, source citations, and exact
  event bindings.

Verification receipt:

- `python scripts/validate_p1_records.py` — PASS.
- `python -m unittest discover -s tests -v` — PASS, 21/21, including all prior
  P0 red calibrations and six P1.1 schema/projection tests.
- `python -m compileall -q scripts tests` — PASS.
- G1 taxonomy render SHA-256 remains
  `55c4ea79a22ed66db982f8aa38dcb7132528cfcbdcab130524238f432e6a9634`.

Kill sweep and phase receipt:

- No canonical sample or production question was created; `data/questions/`
  remains absent. The only question-shaped records are fixture-only inputs.
- No production generator, coverage/variety floor, ratified difficulty
  rubric, learner surface, account, analytics, mutable approval field, or
  learner-ready claim entered the implementation.
- P1.1 exit evidence is satisfied. P1.2 is active next: build named question
  checks and red-calibrate every individual gate before sample authoring.

### P1.2 — question verifier and red calibration

Date: 2026-08-13.

Owning-layer repair before verifier implementation:

- Mapping the independent RECOMPUTE and DISTRACTORS checks exposed a P1.1
  schema gap: the record required worked prose but did not encode an
  independently executable correctness route or mechanically reproducible
  distractor route.
- Repaired the owning question schema before sample authoring, advancing it to
  1.1.0. Added structured option values, explicit assumptions, producer versus
  verifier component identities, a required `shared_deciding_function=false`
  declaration, an independence limitation, generic linear-combination or
  assertion-fixture routes, and executable distractor reproductions.
- Regenerated the fixture question/rule hashes and all illustrative exact-
  version event bindings. The clean P1.1 fixture bundle remained green. This
  strengthened the ratified contract; it did not weaken a check or add a
  waiver.

Verifier implementation:

- Added `scripts/verify_questions.py` with eight individually reported P1
  checks: `SCHEMA_CONTRACT`, `RECOMPUTE_INDEPENDENT`, `RULE_TRACE_CURRENT`,
  `DISTRACTOR_MODELS`, `LANGUAGE_FAIRNESS`, `ORIGINALITY_BOUNDARY`,
  `APPROVAL_INTEGRITY`, and `VARIETY_EVIDENCE`.
- Independent recomputation consumes structured facts and a generic evidence
  route; it does not read the keyed rationale or call a producer deciding
  function. The fixture records the remaining AI-authorship limitation.
- The rule check resolves exact assertions and controlling references and
  separates closed fixture-world currency from the admitted evidence required
  for a real sample candidate.
- Language checks target declared mechanical defects: gratuitous double
  negatives, missing direct question form, answer leakage, orphan numeric
  facts, unsupported assumption language, and missing end ask. A green result
  is not treated as a general prose-quality oracle.
- Added derived-readiness logic. Passing in-memory checks and an approve-shaped
  fixture do not suffice: the exact current verification event, admitted and
  current evidence, exact hash binding, required reviewer, and non-fixture
  purpose are independently required.

Red calibration:

- Added eight purpose-built verifier corruptions, exactly one owned red case
  per individual check: missing provenance; wrong independent coefficient;
  superseded rule; distractor model producing the key; gratuitous double
  negative; global uniqueness/legal-clearance claim; content edit leaving
  review and verification bound to the old hash; and a false observable
  difficulty count.
- Added `scripts/calibrate_question_verifier.py`. It starts from the clean
  fixture, isolates each corruption, requires the named check to fail, rejects
  missing or duplicate check calibration, and emits deterministic structured
  evidence rather than one opaque pass flag.
- Generated `reports/p1-verifier-calibration.json`: 8 individual checks, 8
  observed red corruptions, 0 waivers, and 0 uncalibrated checks. Deterministic
  SHA-256 is
  `a23440334601e619ff47cd01898d7e0c102dc60a3e2c59b2f2dd8c105106a50f`.

Verification receipt:

- `python scripts/validate_p1_records.py` — PASS.
- `python scripts/verify_questions.py` — PASS, 8/8 clean fixture checks.
- `python scripts/calibrate_question_verifier.py` — PASS, 8 red calibrations,
  0 waivers.
- `python -m unittest discover -s tests -v` — PASS, 25/25. Tests include
  deterministic byte equality against the checked-in calibration report and
  proof that the synthetic approve-shaped fixture cannot become learner-ready.
- `python -m compileall -q scripts tests` — PASS.

Kill sweep and phase receipt:

- `data/questions/` remains absent. No G2 sample or production candidate was
  authored while calibrating the verifier.
- Scan found no true mutable learner-ready/human-approved field, production-
  candidate purpose, nonzero waiver count, coverage/variety floor, ratified
  difficulty claim, learner surface, or account/analytics feature.
- The G1 taxonomy render hash remains
  `55c4ea79a22ed66db982f8aa38dcb7132528cfcbdcab130524238f432e6a9634`.
- P1.2 exit evidence is satisfied. P1.3 is active next: the smallest exact-
  version internal review surface, still without G3 workflow approval claims.

### P1.3 — local exact-version review surface

Date: 2026-08-13.

Skill and implementation path:

- Used the Sites-building skill because P1.3 is an internal review interface.
  Its capability path applied because this is an existing evidence project
  with durable audit records, not a one-shot public site.
- Read the skill's persistence guidance. The Goal Method's ratified canonical
  JSON/append-only-event boundary controls: D1, R2, browser storage, accounts,
  remote persistence, and hosting remain absent. The interface cannot become
  the authority for approvals.
- The supplied Bash initializer could not run because this Windows host has no
  Bash runtime. Copied the identical bundled vinext starter into the isolated
  `review-surface/` directory and installed its lockfile instead. Removed the
  starter loading surface, optional auth/database examples, Drizzle, and
  loading-skeleton dependency.

Exact-version evidence surface:

- Added a responsive, evidence-first internal surface under `review-surface/`.
  It displays the exact question/version/hash; candidate-only and zero-
  coverage status; full stem/options/key; Blueprint hierarchy and MCQ scope
  limit; relevant/irrelevant facts; end ask, setup, steps, rationale, and
  faster route; reproducible distractor models; rule/reference trace;
  challenge-mechanic and difficulty evidence; all eight verifier results;
  visible review history; and an exact input-file manifest.
- Added `scripts/build_review_surface_data.py`. It reconstructs the display
  input from canonical fixture, taxonomy, rule/reference, and verifier
  evidence, computes input hashes, and deterministically writes
  `review-surface/app/review-data.json` rather than allowing hand edits.
- Review-data SHA-256 is
  `a59265ea2cea44c6a0171d59b0598436b1423af5a4d321e82546d46b73647b6d`.

Append-only review boundary:

- Added a keyboard-accessible action composer for Approve, Reject, Revise,
  and Comment. It binds question ID, version ID, content hash, James reviewer
  identity, action, comment, and UTC time into a downloadable event proposal.
- Corrected the client boundary so the display-only `version_number` cannot
  leak into the schema-closed event subject.
- Added `scripts/ingest_review_event.py` as the canonical write boundary. It
  validates the event schema, exact content binding, James reviewer identity,
  and canonical question-version path; rejects fixture content and stale
  hashes; and uses exclusive file creation so an event ID cannot overwrite
  history.
- The surface visibly warns that any substantive content edit creates a new
  immutable version and prior approval cannot carry forward.

Integrity and readiness evidence:

- Added three Python integrity tests: deterministic exact-bound render data;
  fixture-event refusal; and exact-bound exclusive event creation with stale-
  hash and duplicate-ID rejection.
- Added two server-render tests proving the evidence sections, candidate-only
  hold, exact version/hash, all four actions, local-only scope, and absence of
  starter/account/database surface.
- Started the local surface and received HTTP 200. Rendered HTML contained the
  exact-version heading, `Not learner-ready`, edit-invalidation warning, all
  eight check results, and action composer.
- Attempted the required in-app browser preview through the Browser skill; the
  runtime returned `No browser is available`. No standalone browser tool was
  substituted, and no visual or G3 hands-on approval is claimed.
- The local development server was stopped after validation.

Verification receipt:

- `python scripts/validate_p1_records.py` — PASS.
- `python scripts/verify_questions.py` — PASS, 8/8.
- `python scripts/calibrate_question_verifier.py` — PASS, 8/8 red calibrated,
  0 waivers.
- `python scripts/build_review_surface_data.py` — PASS,
  `learner_ready=False`, 8 checks rendered.
- `python scripts/verify_taxonomy.py data/far-taxonomy.json` — PASS, 13/13.
- `python -m unittest discover -s tests -v` — PASS, 28/28.
- `python -m compileall -q scripts tests` — PASS.
- `npm run build` in `review-surface/` — PASS.
- `node --test tests/rendered-html.test.mjs` — PASS, 2/2.
- `npm run lint` — PASS, zero warnings/errors.

Kill sweep and phase receipt:

- `data/questions/` and `data/events/review/` remain absent. The surface has
  not created a G2 sample, production item, James verdict, or canonical event.
- D1/R2 remain null; no deployment, account, learner surface, analytics,
  mutable approval, coverage/variety floor, ratified difficulty claim, or G3
  workflow claim entered the implementation.
- P1.3 exit evidence is satisfied by deterministic rendering, explicit
  candidate-only readiness, exact-bound append-only event tests, and server-
  rendered surface checks. P1.4 bounded cross-area sample authoring is active.

### P1.4 — deliberately varied cross-area sample

Date: 2026-08-13.

Source boundary and sample design:

- Used the PDF workflow to extract and visually inspect FAR2 through FAR5 of
  the preserved 2026 Blueprint. Confirmed the three-area boundary, all three
  tested skill levels, default entity assumptions, and the Blueprint's express
  eligibility of the FASB Accounting Standards Codification.
- Cross-checked only primary FASB materials for the selected rules. Added
  `far-ref-fasb-codification-live.v001` as admitted authoritative evidence,
  bounded to the exact cited ASC locators and explicitly subject to live-source
  revalidation.
- Chose the smallest useful six-item sample: two items per FAR area, collectively
  spanning remembering and understanding, application, and analysis. Families
  are OCI, indirect cash flow, cash-equivalent original maturity, inventory
  reconciliation, contingency range measurement, and subsequent events.

Candidate artifacts:

- Added deterministic authoring in `scripts/author_p1_sample.py`; generated
  stable identities and immutable v001 question records `far-q-000101` through
  `far-q-000106`, six rule versions, one reference version, and six exact-bound
  verification events.
- Every item contains four unique options and one key, granular Blueprint
  mapping, structured relevant/irrelevant facts, explicit assumptions, worked
  solution, faster route, rule trace, an independent linear recomputation,
  three executable distractor error models, challenge evidence, all six
  proposed difficulty dimensions, and bounded within-sample originality
  language.
- Added `data/sample/p1/manifest.json`; SHA-256 is
  `d98043c3437dc1653eaafdb905b28116796449b6c073121a4d091faca0fd0ec5`.

Approval-integrity repair:

- Sample authoring exposed that `QuestionBundle` required a review record even
  before a human had acted. Requiring one would have forced a fabricated James
  verdict or semantically false system event.
- Made review state optional in the verifier. Existing review evidence remains
  schema- and hash-bound when present; an absent review passes integrity but
  fails readiness for missing decisive approval, human actor, and required
  reviewer.
- Added a regression test for the unreviewed state. Recalibrated all eight
  checks without waiver. The deterministic calibration report now hashes to
  `d2c5127c0b654748dea86ad6d7c145b11d79ab4b3794901db4745d03853ffba0`;
  regenerated fixture review data hashes to
  `eb1ec93a066aa1ed4f12fbf4fac693bc85b44c8205c77480b2542d0473d250f8`.

Sample verification:

- Added `scripts/verify_p1_sample.py` and three regression tests. The report
  proves six items, all three Areas, all three skill levels, 13 distinct
  challenge tags, all 48 item checks passing, zero canonical review events,
  zero normalized exact stem duplicates, and every item candidate-only.
- Generated `reports/p1-sample-verification.json`; SHA-256 is
  `21d0d9b77a0e41d21bfc13a8351abeda59f7be3e42c0985616df2e550a05ce0a`.
  Its originality claim is limited to the named six-item within-bank corpus;
  it makes no external-corpus, legal, approval, learner-readiness, or coverage-
  floor claim.

Verification receipt:

- `python scripts/validate_p1_records.py` — PASS.
- `python scripts/verify_questions.py` — PASS, 8/8.
- `python scripts/calibrate_question_verifier.py` — PASS, 8/8 red calibrated,
  zero waivers.
- `python scripts/verify_p1_sample.py` — PASS, 6 items / 3 Areas / 3 skills,
  all candidate-only.
- `python scripts/verify_taxonomy.py data/far-taxonomy.json` — PASS, 13/13.
- `python -m unittest discover -s tests -v` — PASS, 32/32.
- `python -m compileall -q scripts tests` — PASS.
- `npm run build` in `review-surface/` — PASS.
- `node --test tests/rendered-html.test.mjs` — PASS, 2/2.
- `npm run lint` — PASS, zero warnings/errors.

Kill sweep and phase receipt:

- `data/events/review/` remains absent. No human verdict, learner-ready state,
  production candidate, approved coverage, or G3 workflow claim was created.
- No coverage floor, variety quota, ratified difficulty rubric, learner/admin
  surface, account, analytics, deployment, D1/R2 persistence, or other CPA
  section entered the implementation.
- All sample correctness routes are linear; the G2 package must state this
  bounded limitation rather than imply production-family completeness.
- P1.4 exit evidence is satisfied. P1.5 is active next: render the six-item
  stable G2 queue and draft the proposed amendment and evidence package.

### P1.5 — G2 package and proposed amendment

Date: 2026-08-13.

Canonical-layout correction:

- Auditing P1.4 against ADR 0001 found that the initial sample generator placed
  question and rule versions one directory above the documented `versions/`
  boundary. Corrected the generator and moved only the twelve new generated
  version files into canonical version directories.
- Regenerated the manifest, verification report, review data, and package
  hashes. The current P1.4 manifest/report hashes supersede the earlier receipt:
  manifest `702cf9d0c7ff04ebf78507f672575cc1b1ac202a76dd2fdf8406cd045518abe9`;
  sample verification
  `ced71e6b486c22bdf78c51b0f19df9b4ce8b39b5825a0024d5bbaa0ce4670012`.
- Added a regression proving a downloaded sample event resolves the canonical
  question `versions/` path and can be exclusively ingested without fixture
  bypass. No canonical review event was created by the test.

Stable G2 review queue:

- Replaced the P1.3 fixture-only review-data input with the six-item P1 sample
  manifest. `scripts/build_review_surface_data.py` now deterministically binds
  all question, rule, reference, verification, taxonomy, calibration, and
  sample-report inputs.
- Reworked the local review surface into one stable six-item queue with anchor
  navigation, exact-version identity/hash, zero-readiness holds, full evidence,
  and an independent Approve/Reject/Revise/Comment composer for each item.
- The queue explicitly shows zero approved items, zero coverage contribution,
  and zero canonical human events. Current review-data SHA-256 is
  `4a8dfd4746ca56132332c43c62f73bd9e782fcd705e5025913ad091e4d4f5fcf`.

Proposed amendment and package:

- Added `docs/gates/g2-proposed-amendment.md`, SHA-256
  `6130ba3f90a709af2caff6c78490a2e52fc2f6817de4bda6c8b16ffead39acde`.
  It is visibly unratified and proposes the coverage floors, ten-row variety
  matrix, anti-cloning rules, six observable difficulty rubrics, prose/fairness
  rules, correctness-route expansion, and artifact-first architecture ruling.
- The proposed minimum is 353 learner-ready items: at least three per each of
  113 tasks, with Area III depth added to keep area design within the published
  allocation. This remains a red-pen proposal, not a contract change.
- Added `scripts/build_g2_package.py` and two deterministic package tests.
  `reports/g2-package-manifest.json` hashes every gate artifact, names the
  sequential rulings, preserves limitations, and reports six candidates, zero
  learner-ready items, zero coverage, and zero canonical review events.
- Package SHA-256 is
  `2d7d71f350533edc742712e4c66660aa17390ccb4c0c17baeeace29118ab03c5`.

Sites skill boundary:

- Used the Sites-building capability path because P1.5 changed an existing
  internal interface. Preserved its structure, lockfile, accessibility,
  responsive layout, and Cloudflare-compatible build.
- The ratified project requires a local internal audit surface and defers
  hosting. Therefore the skill's normal hosting and social-preview handoff did
  not apply; D1/R2 remain null and no deployment or external persistence was
  created. Its preview rule also forbade unrequested browser screenshots, so no
  browser visual or G3 hands-on claim was made.

Verification receipt:

- P1 schema validation — PASS.
- Clean question verifier — PASS, 8/8.
- Red calibration — PASS, 8/8, zero waivers.
- Sample authoring and verification — PASS, six items / three Areas / three
  skills / all candidate-only.
- Review queue build — PASS, six items / zero ready.
- G2 package build — PASS, ready for human gate and explicitly unratified.
- Taxonomy verification — PASS, 13/13.
- `python -m unittest discover -s tests -v` — PASS, 35/35.
- Python compilation — PASS.
- Review-surface production build — PASS.
- Review-surface lint — PASS, zero warnings/errors.
- Server-render tests — PASS, 2/2.

Kill sweep and phase receipt:

- Canonical review event count is zero. No item approval, learner-ready state,
  coverage contribution, or production authorization was created.
- No `goal.md` amendment, coverage floor, variety rule, difficulty rubric, or
  prose rule was silently ratified. All proposal language remains outside the
  governing contract pending James's serialized rulings.
- No production generator, other CPA section, learner/admin product, account,
  analytics, hosting, D1/R2 persistence, public site, or G3 claim entered scope.
- P1.5 exit evidence is satisfied. P1.6 Gate G2 is active at the human
  terminal: present `far-q-000101.v001` and request one exact-version verdict.

### P1.6 — G2 candidate 1 verdict

Date: 2026-08-13.

- Presented only `far-q-000101.v001`, content SHA-256
  `498115370269dc604843721dcd928931d6d57cd3e488b1a87143ddda42988400`,
  including stem, options, key, rationale, mapping, and exact source boundary.
- James verdict: **APPROVE**.
- Created and canonically ingested append-only event
  `far-review-far-q-000101-approve-20260813t1743203278866z`, recorded at
  `2026-08-13T17:43:20.3278866Z`. Ingestion validated the event schema, James
  actor identity, canonical `versions/` path, exact version/hash binding, and
  exclusive event ID creation.
- Reconstructed candidate 1 with the canonical review event: 8/8 checks pass,
  `learner_ready=true`, and zero readiness hold reasons.
- This verdict covers only candidate 1's exact version. It does not approve any
  other candidate, policy proposal, workflow, coverage claim, or production.
- The immutable P1.5 gate-opening package remains unchanged; the review event
  is the live append-only P1.6 ledger. Candidate 2 is next.

### P1.6 — G2 candidate 2 verdict

Date: 2026-08-13.

- Presented only `far-q-000102.v001`, content SHA-256
  `0a53576a16fd6ceb945d250ebe41b079e403e2a3480ba2dfbaaa24a2670b31a4`,
  including the indirect-method stem, options, key, calculation, mapping, and
  financing classification of dividends paid.
- James verdict: **APPROVE**.
- Created and canonically ingested append-only event
  `far-review-far-q-000102-approve-20260813t1745427415381z`, recorded at
  `2026-08-13T17:45:42.7415381Z`. Ingestion validated the event schema, James
  actor identity, canonical `versions/` path, exact version/hash binding, and
  exclusive event ID creation.
- Reconstructed candidate 2 with the canonical review event: 8/8 checks pass,
  `learner_ready=true`, and zero readiness hold reasons. Canonical review event
  count is two.
- This verdict covers only candidate 2's exact version. Candidate 3 is next.

### P1.6 — G2 candidate 3 verdict

Date: 2026-08-13.

- Presented only `far-q-000103.v001`, content SHA-256
  `bb68ed75e4c9d08b52f91db482a623d45fe6516399f064385748431c8ad807a6`,
  including the cash-equivalent original-maturity convention, options, key,
  classification, calculation, and Blueprint mapping.
- James verdict: **APPROVE**.
- Created and canonically ingested append-only event
  `far-review-far-q-000103-approve-20260813t1746487692623z`, recorded at
  `2026-08-13T17:46:48.7692623Z`. Exact version/hash, James identity, schema,
  canonical path, and exclusive creation all validated.
- Reconstructed candidate 3 with the canonical review event: 8/8 checks pass,
  `learner_ready=true`, and zero hold reasons. Canonical review event count is
  three.
- This verdict covers only candidate 3's exact version. Candidate 4 is next.

### P1.6 — G2 candidate 4 verdict

Date: 2026-08-13.

- Presented only `far-q-000104.v001`, content SHA-256
  `cd25c31fb659432408501b65bc9e57f88cdeae042b342137b89bc5a0238b5614`,
  including the inventory roll-forward, physical-to-book reconciliation,
  adjustment direction, options, key, and analysis mapping.
- James verdict: **APPROVE**.
- Created and canonically ingested append-only event
  `far-review-far-q-000104-approve-20260813t1747575788051z`, recorded at
  `2026-08-13T17:47:57.5788051Z`. Exact version/hash, James identity, schema,
  canonical path, and exclusive creation all validated.
- Reconstructed candidate 4 with the canonical review event: 8/8 checks pass,
  `learner_ready=true`, and zero hold reasons. Canonical review event count is
  four.
- This verdict covers only candidate 4's exact version. Candidate 5 is next.

### P1.6 — answer-position comment and immutable sample revision

Date: 2026-08-13.

- James commented on `far-q-000105.v001`: “The sample cannot use answer A as
  the correct position for every item.” Recorded the comment without turning
  it into an accounting rejection as canonical append-only event
  `far-review-far-q-000105-comment-20260813t1749459935313z`, exactly bound to
  v001 hash `927cd265746bfb68773d846e5a675f461d8ce8dda92f37bc258f59afb9d1efb4`.
- Treated the feedback as a sample-wide variety defect. Preserved candidate 1
  v001 and issued immutable v002 versions for candidates 2–6 by reordering
  options only. The current keyed-position sequence is A, B, C, D, B, C, for a
  distribution of A=1, B=2, C=2, D=1.
- Preserved every v001 question, verification, verdict, and opening artifact.
  Archived the exact opening manifest and sample report as
  `manifest.v001.json` and `p1-sample-verification.v001.json`.
- Because candidates 2–4 changed exact versions after approval, canonically
  ingested three system `auto_invalidate` events against their v001 records.
  Each names its v002 superseding version; the original approvals remain in
  append-only history and do not carry forward.
- Candidate 1 v001 remains exact-approved and learner-ready. Candidates 2–6
  current versions are pending exact-version verdicts. Coverage contribution
  remains zero because G2 is not ratified.
- Updated current sample verification and review rendering to resolve review
  history by exact version. Current manifest SHA-256 is
  `55983818321d309109e966a26261cb63730bf494ac2a0c97d27f799277b78670`;
  current verification-report SHA-256 is
  `aefa846a5580354ac2f7a807b1a5d7f1b4d689c0f254ec42f40279116e79e8dc`;
  current review-data SHA-256 is
  `0af447fbb338449b60b540089cb8153d1147c20b7e110f7c4f8be82514272fe9`.
- Verification: current sample passes 48/48 checks across six items, three
  Areas, and three skills; 35/35 Python tests pass; taxonomy passes 13/13;
  Python compilation passes; review-surface lint passes; production build and
  server-render tests pass 2/2. The first build attempt hit sandbox `spawn
  EPERM`; the approved subprocess-capable rerun passed.
- Gate sequence restarts at candidate 2 v002 because candidate 2's approval
  was bound to superseded v001. Only one exact-version verdict will be
  requested per turn.

### P1.6 — G2 candidate 2 v002 verdict

Date: 2026-08-13.

- Presented only `far-q-000102.v002`, content SHA-256
  `6b3fe7f5b502ff45cb2e52be012132a75485945ec0aa902f970c865d40c2d8d3`,
  with the correct answer moved to position B under the balanced sample.
- James verdict: **APPROVE** (entered as “Appove” and unambiguously normalized
  to Approve in the immediately preceding exact-version prompt).
- Created and canonically ingested append-only event
  `far-review-far-q-000102-approve-20260813t1757462466055z`, recorded at
  `2026-08-13T17:57:46.2466055Z`. Schema, James identity, canonical path,
  exact v002/hash binding, and exclusive creation validated.
- Reconstructed current queue state: candidates 1 and 2 are learner-ready;
  candidates 3–6 are pending; coverage contribution remains zero. All 48
  current item checks pass.
- Hardened stateful queue tests so additional serialized approvals are checked
  against derived current state instead of a permanently hard-coded approval
  count. Python tests pass 35/35; the production review-surface build and
  server-render tests pass 2/2.
- This approval covers only candidate 2 v002. Candidate 3 v002 is next.

### P1.6 — G2 candidate 3 v002 verdict

Date: 2026-08-13.

- Presented only `far-q-000103.v002`, content SHA-256
  `516c241e69ef58bf823bd9d8cc83591fbefecfa0aaeaa9c26e048f54dd5f717e`,
  with the cash-equivalent key in position C.
- James verdict: **APPROVE**.
- Created and canonically ingested append-only event
  `far-review-far-q-000103-approve-20260813t1759350701839z`, recorded at
  `2026-08-13T17:59:35.0701839Z`. Exact v002/hash binding, James identity,
  schema, canonical path, and exclusive creation validated.
- Reconstructed current queue: candidates 1–3 are learner-ready; candidates
  4–6 are pending; coverage contribution remains zero. Current sample
  verification passes and Python tests pass 35/35.
- This approval covers only candidate 3 v002. Candidate 4 v002 is next.

### P1.6 — G2 candidate 4 v002 verdict

Date: 2026-08-13.

- Presented only `far-q-000104.v002`, content SHA-256
  `9bf70057d1044c2c5efd14ea83d8b899d9f9a5674e75f207f6ce6a7f1fea85e9`,
  with the inventory-reconciliation key in position D.
- James verdict: **APPROVE**.
- Created and canonically ingested append-only event
  `far-review-far-q-000104-approve-20260813t1800466452056z`, recorded at
  `2026-08-13T18:00:46.6452056Z`. Exact v002/hash binding, James identity,
  schema, canonical path, and exclusive creation validated.
- Reconstructed current queue: candidates 1–4 are learner-ready; candidates
  5–6 are pending; coverage contribution remains zero. Current sample
  verification passes and Python tests pass 35/35.
- This approval covers only candidate 4 v002. Candidate 5 v002 is next.

### P1.6 — G2 candidate 5 v002 verdict

Date: 2026-08-13.

- Presented only `far-q-000105.v002`, content SHA-256
  `347b2387873b626926adec98d1b5e17130c573285cfd40b7b889a637f5437be1`,
  the corrected contingency item with its key in position B.
- James verdict: **APPROVE** (entered as “Aprpove” and unambiguously normalized
  to Approve in the immediately preceding exact-version prompt).
- Created and canonically ingested append-only event
  `far-review-far-q-000105-approve-20260813t1802488764121z`, recorded at
  `2026-08-13T18:02:48.8764121Z`. Exact v002/hash binding, James identity,
  schema, canonical path, and exclusive creation validated.
- The earlier v001 Comment remains history and does not conflict with this
  v002 approval; the revised option order resolves the noted sample defect.
- Reconstructed current queue: candidates 1–5 are learner-ready; candidate 6
  is pending; coverage contribution remains zero. Current sample verification
  passes and Python tests pass 35/35.
- This approval covers only candidate 5 v002. Candidate 6 v002 is next.

### P1.6 — G2 candidate 6 v002 verdict and item-review completion

Date: 2026-08-13.

- Presented only `far-q-000106.v002`, content SHA-256
  `5cce1108d25cc564ba5b7df23544c55c78155105a7e4e116daa981a0bb9fb639`,
  with the subsequent-events key in position C.
- James verdict: **APPROVE**.
- Created and canonically ingested append-only event
  `far-review-far-q-000106-approve-20260813t1804492948352z`, recorded at
  `2026-08-13T18:04:49.2948352Z`. Exact v002/hash binding, James identity,
  schema, canonical path, and exclusive creation validated.
- All six current exact versions now reconstruct `learner_ready=true`; all 48
  current item checks pass. The balanced key distribution remains A=1, B=2,
  C=2, D=1. Coverage contribution remains zero pending the policy rulings and
  dated G2 amendment.
- Python tests pass 35/35. The completed six-approval production review-surface
  build passes and its rendered HTML tests pass 2/2. A stale render assertion
  that permanently required a pending item was replaced with a state-valid
  readiness assertion.
- The six item verdicts are complete. The next serialized G2 decision is the
  combined per-task and area coverage-floor proposal.

### P1.6 — G2 coverage-floor policy ruling

Date: 2026-08-13.

- Presented the complete proposed coverage ruling as one decision: Mapped at
  one learner-ready MCQ per representative task; MCQ-depth covered at three
  learner-ready MCQs per task with representation, challenge, and anti-clone
  conditions; and Full task exercised never inferred from MCQ counts.
- Presented the minimum bank arithmetic: 47 Area I tasks × 3 = 141; 40 Area II
  tasks × 3 = 120; 26 Area III tasks × 3 plus 14 depth items = 92; total =
  **353 learner-ready items**. Retained the 30–40% / 30–40% / 25–35% area
  ranges as the bank grows.
- Presented the exclusions: stale, failing, quarantined, unapproved, and
  superseded versions count zero; multi-task mapping requires independent
  justification and counts once in the bank total; every aggregate resolves
  to exact item versions.
- James ruling: **APPROVE**.
- Effect: the coverage-floor decision is accepted for the eventual dated G2
  amendment but is not yet part of `goal.md` and does not authorize production
  by itself. The next serialized ruling is variety row 1, stem length.

### P1.6 — G2 variety ruling 1: stem length

Date: 2026-08-13.

- Presented the proposed learner-ready bank bins and floors: short ≤45 words at
  ≥20%; standard 46–90 words at ≥45%; dense ≥91 words at ≥15%.
- Made the 353-item minimum concrete as at least 71 short, 159 standard, and 53
  dense items, with whole-item floors rounded up and the unallocated share left
  as deliberate design freedom.
- James ruling: **APPROVE** (entered as “Aporv” and unambiguously normalized to
  Approve in the immediately preceding single-ruling prompt).
- Effect: the stem-length row is accepted for the eventual dated G2 amendment;
  it is not yet active in `goal.md`. Next is variety row 2, numeric fact
  density.

### P1.6 — G2 variety ruling 2: numeric fact density

Date: 2026-08-13.

- Presented the proposed learner-ready bank bins: low 0–2 numeric facts,
  medium 3–5, and high ≥6, with each bin at ≥15%.
- Made the 353-item minimum concrete as at least 53 items in each bin, with the
  remaining 55% available for deliberate distribution.
- James ruling: **APPROVE** (entered as “eApprove” and unambiguously normalized
  to Approve in the immediately preceding single-ruling prompt).
- Effect: numeric fact density is accepted for the eventual dated G2 amendment
  but is not yet active in `goal.md`. Next is variety row 3, primary accounting
  work.

### P1.6 — G2 variety ruling 3: primary accounting work

Date: 2026-08-13.

- Presented four mutually exclusive primary-work bins and floors for
  learner-ready exact versions: conceptual recall ≥8%; classification/rule
  selection ≥20%; computation ≥30%; analytical reconciliation/inference ≥20%.
- Made the 353-item minimum concrete as at least 29 recall, 71
  classification/rule, 106 computation, and 71 analytical items, leaving the
  unallocated share flexible.
- James ruling: **APPROVE**.
- Effect: the primary-accounting-work row is accepted for the eventual dated
  G2 amendment but is not yet active in `goal.md`. Next is variety row 4,
  dependent solution steps.

### P1.6 — G2 variety ruling 4: dependent solution steps

Date: 2026-08-13.

- Presented the proposed dependent-step bins and learner-ready bank floors:
  one step ≥10%; two to three steps ≥50%; four or more steps ≥10%.
- Made the 353-item minimum concrete as at least 36 one-step, 177
  two-to-three-step, and 36 four-plus-step items. Clarified that decorative
  subdivisions do not count as dependent reasoning steps.
- James ruling: **APPROVE**.
- Effect: the dependent-solution-step row is accepted for the eventual dated
  G2 amendment but is not yet active in `goal.md`. Next is variety row 5,
  irrelevant facts.

### P1.6 — G2 variety ruling 5: irrelevant facts

Date: 2026-08-13.

- Presented the proposed irrelevant-fact bins and learner-ready bank floors:
  none ≥30%; one to two ≥30%; three or more ≥10%.
- Made the 353-item minimum concrete as at least 106 items with none, 106 with
  one or two, and 36 with three or more. Retained the boundary that irrelevant
  facts test selection rather than provide decorative noise; the separate
  high-noise maximum remains an upcoming anti-cloning ruling.
- James ruling: **APPROVE**.
- Effect: the irrelevant-facts row is accepted for the eventual dated G2
  amendment but is not yet active in `goal.md`. Next is variety row 6, ask
  placement.

### P1.6 — G2 variety ruling 6: ask placement

Date: 2026-08-13.

- Presented the proposed ask-placement floors for learner-ready exact versions:
  direct/final-sentence ≥60%; indirect or embedded after setup ≥20%.
- Made the 353-item minimum concrete as at least 212 direct and 71 indirect or
  embedded asks, with the remaining 70 items distributable between the bins.
  Retained the requirement that an indirect ask be deliberate and restated
  unambiguously in the structured solution.
- James ruling: **APPROVE**.
- Effect: the ask-placement row is accepted for the eventual dated G2
  amendment but is not yet active in `goal.md`. Next is variety row 7, rule
  pressure.

### P1.6 — G2 variety ruling 7: rule pressure

Date: 2026-08-13.

- Presented seven rule-pressure tags—rule, timing, basis, measurement,
  classification, presentation, and convention—with each required on ≥5% of
  learner-ready items.
- Made the 353-item minimum concrete as at least 18 evidenced appearances per
  tag. Retained multi-tagging only when every tag has separate observable
  evidence; tags cannot be added solely to satisfy a floor.
- James ruling: **APPROVE**.
- Effect: the rule-pressure row is accepted for the eventual dated G2
  amendment but is not yet active in `goal.md`. Next is variety row 8, solution
  representation.

### P1.6 — G2 variety ruling 8: solution representation

Date: 2026-08-13.

- Presented six primary solution representations—formula, roll-forward,
  journal effect, financial-statement view, rule selection, and
  classification—with each required on ≥5% of learner-ready items.
- Made the 353-item minimum concrete as at least 18 items per representation.
  Each item records one primary representation based on the actual solution
  organization rather than vocabulary alone.
- James ruling: **APPROVE**.
- Effect: the solution-representation row is accepted for the eventual dated
  G2 amendment but is not yet active in `goal.md`. Next is variety row 9,
  elimination burden.

### P1.6 — G2 variety ruling 9: elimination burden

Date: 2026-08-13.

- Presented the proposed elimination-burden bins and learner-ready bank floors:
  low—one obviously invalid distractor—≥10%; medium—all choices plausible but
  two distractors fall to one rule—≥40%; high—each distractor requires a
  separate diagnosis—≥15%.
- Made the 353-item minimum concrete as at least 36 low, 142 medium, and 53 high
  items. Retained the requirement that each rating resolve to the item's named
  distractor error models.
- James ruling: **APPROVE**.
- Effect: the elimination-burden row is accepted for the eventual dated G2
  amendment but is not yet active in `goal.md`. Next is variety row 10,
  realistic time pressure.

### P1.6 — G2 variety ruling 10: realistic time pressure

Date: 2026-08-13.

- Presented learner-ready bank floors of low ≥15%, moderate ≥45%, and high
  ≥15%, concrete at the 353-item minimum as 53 low, 159 moderate, and 53 high.
- Closed the proposal's three-bin/five-level ambiguity by explicitly mapping
  low to time-rubric levels 1–2, moderate to level 3, and high to levels 4–5.
  Estimated and observed completion times remain separate, with recorded human
  recalibration required to update observed evidence.
- James ruling: **APPROVE**.
- Effect: the realistic-time-pressure row and its explicit rubric mapping are
  accepted for the eventual dated G2 amendment but are not yet active in
  `goal.md`. All ten variety-matrix rows are decided. Next is anti-cloning rule
  1, nonkey misconception evidence.

### P1.6 — G2 anti-cloning ruling 1: nonkey evidence

Date: 2026-08-13.

- Presented the rule that every nonkey has one named misconception or error
  path plus either a reproducible route yielding the exact wrong result or an
  independently authored assertion fixture for nonnumeric content, all bound
  to the displayed option.
- Explicitly forbade random nearby values, generic filler, and unsupported
  plausibility as distractor evidence.
- James ruling: **APPROVE**.
- Effect: anti-cloning rule 1 is accepted for the eventual dated G2 amendment
  but is not yet active in `goal.md`. Next is anti-cloning rule 2, within-task
  distractor diversity.

### P1.6 — G2 anti-cloning ruling 2: within-task distractor diversity

Date: 2026-08-13.

- Presented the rule that the three-item minimum for any representative task
  must contain at least five distinct distractor error-model IDs across its
  nine nonkeys and that no two items may share the same complete set of three
  error models.
- Retained partial misconception reuse when genuinely applicable while
  forbidding cloned distractor sets from satisfying task-depth coverage.
- James ruling: **APPROVE**.
- Effect: anti-cloning rule 2 is accepted for the eventual dated G2 amendment
  but is not yet active in `goal.md`. Next is anti-cloning rule 3, the bank-wide
  concentration cap.

### P1.6 — G2 anti-cloning ruling 3: bank-wide concentration cap

Date: 2026-08-13.

- Presented a maximum 25% share for any single stem template, accounting fact
  pattern, primary solution representation, or distractor family among
  learner-ready exact versions.
- Made the 353-item minimum concrete as no more than 88 items in any one such
  category. Required stable identifiers or reproducible classification evidence
  so the cap can be mechanically audited.
- James ruling: **APPROVE**.
- Effect: anti-cloning rule 3 is accepted for the eventual dated G2 amendment
  but is not yet active in `goal.md`. Next is anti-cloning rule 4, the
  high-noise maximum.

### P1.6 — G2 anti-cloning ruling 4: high-noise maximum

Date: 2026-08-13.

- Presented a maximum of 40% of learner-ready items with three or more
  irrelevant facts, concrete at the 353-item minimum as no more than 141.
- Reconciled the cap with the approved 10% minimum: the high-noise category is
  36–141 items at the minimum bank size. Retained the principle that noise is
  a tested fact-selection skill rather than the default writing style.
- James ruling: **APPROVE**.
- Effect: anti-cloning rule 4 is accepted for the eventual dated G2 amendment
  but is not yet active in `goal.md`. Next is anti-cloning rule 5, applicable
  within-area skill and representation coverage.

### P1.6 — G2 anti-cloning ruling 5: within-area breadth

Date: 2026-08-13.

- Presented the rule that every FAR area contains at least one learner-ready
  item in every skill level applicable to that area and every solution
  representation genuinely compatible with its content.
- Required reports to show the area-by-skill and area-by-representation matrix
  plus explicit rationales for excluded combinations. Inapplicable combinations
  are documented rather than forced.
- James ruling: **APPROVE**.
- Effect: anti-cloning rule 5 is accepted for the eventual dated G2 amendment
  but is not yet active in `goal.md`. All ten variety rows and five
  anti-cloning rules are decided. Next is difficulty rubric 1, accounting
  complexity.

### P1.6 — G2 difficulty ruling 1: accounting complexity

Date: 2026-08-13.

- Presented the five levels: one familiar rule/no exception; one rule plus one
  boundary; two interacting rules or one exception; three interacting
  rules/conditions; and four-plus interactions or judgment with competing
  treatments.
- Required the item to identify the exact rules, boundaries, exceptions, or
  competing treatments supporting the level; topic reputation and unexplained
  “feels hard” judgments cannot raise it.
- James ruling: **APPROVE**.
- Effect: difficulty rubric 1 is accepted for the eventual dated G2 amendment
  but is not yet active in `goal.md`. Next is rubric 2, reasoning steps.

### P1.6 — G2 difficulty ruling 2: reasoning steps

Date: 2026-08-13.

- Presented levels 1–4 as one through four dependent reasoning steps and level
  5 as five-plus dependent steps with at least one branch or reconciliation
  loop.
- Limited counts to necessary accounting/problem-solving dependencies;
  restated facts, formatting, and decorative subdivision cannot raise a level.
- James ruling: **APPROVE** (capitalization normalized from “APprove”).
- Effect: difficulty rubric 2 is accepted for the eventual dated G2 amendment
  but is not yet active in `goal.md`. Next is rubric 3, reading and fact
  selection.

### P1.6 — G2 difficulty ruling 3: reading and fact selection

Date: 2026-08-13.

- Presented the five levels: ≤3 facts/no irrelevant facts; 4–5 facts or one
  irrelevant; 6–7 facts or two irrelevant; 8–10 facts or three-plus irrelevant
  facts/conditional clauses; and 11-plus facts with dependencies across
  passages or exhibits.
- Required facts and relevance classifications to be structured and traceable
  to the stem or an identified exhibit; raw word count alone does not determine
  this dimension.
- James ruling: **APPROVE**.
- Effect: difficulty rubric 3 is accepted for the eventual dated G2 amendment
  but is not yet active in `goal.md`. Next is rubric 4, rule and convention
  pressure.

### P1.6 — G2 difficulty ruling 4: rule and convention pressure

Date: 2026-08-13.

- Presented the five levels: direct application/no nearby boundary; one named
  boundary; two boundaries or one controlled convention trap; three boundaries
  or timing/basis interaction; and four-plus boundaries with demanding but
  defensible exception analysis.
- Required each boundary or trap to resolve through the rule trace to the facts
  that activate it. Ambiguity and hidden answer-changing conventions remain
  forbidden.
- James ruling: **APPROVE**.
- Effect: difficulty rubric 4 is accepted for the eventual dated G2 amendment
  but is not yet active in `goal.md`. Next is rubric 5, distractor/elimination
  burden.

### P1.6 — G2 difficulty ruling 5: distractor/elimination burden

Date: 2026-08-13.

- Presented the five levels: one obviously invalid distractor; three distinct
  errors with one readily eliminated; all plausible with two falling to one
  rule; separate diagnoses with one numerically close; and separate diagnoses
  plus competing intermediate results or convention traps.
- Required the assigned level to resolve through the three named error models
  and their reproduced results or assertion fixtures.
- James ruling: **APPROVE**.
- Effect: difficulty rubric 5 is accepted for the eventual dated G2 amendment
  but is not yet active in `goal.md`. Next is rubric 6, realistic time pressure.

### P1.6 — G2 difficulty ruling 6: realistic time pressure

Date: 2026-08-13.

- Presented the five levels: ≤30 seconds and ≤1 operation; 31–60 seconds or 2
  operations; 61–90 seconds or 3–4 operations; 91–150 seconds or 5–7
  operations; and >150 seconds or 8-plus operations/branching review.
- Retained separate estimated and observed human completion times and connected
  the rubric to the approved bank bins: low levels 1–2, moderate level 3, high
  levels 4–5.
- James ruling: **APPROVE**.
- Effect: difficulty rubric 6 is accepted for the eventual dated G2 amendment
  but is not yet active in `goal.md`. All six dimensions are decided. Next is
  the shared difficulty-application rules.

### P1.6 — G2 difficulty application-rules ruling

Date: 2026-08-13.

- Presented the shared rules: use the highest level only when its observable
  condition exists; keep estimated and observed time separate; when descriptors
  conflict, record the lower supported level and flag human review; preserve
  the six-number diagnostic profile without averaging it into an opaque label.
- James ruling: **APPROVE**.
- Effect: the shared application rules are accepted for the eventual dated G2
  amendment but are not yet active in `goal.md`. The complete difficulty section
  is decided. Next is the combined prose/fairness ruling.

### P1.6 — G2 prose and fairness ruling

Date: 2026-08-13.

- Presented the ten combined rules covering direct or explicitly tagged asks;
  structured fact/stem parity; explicit special entity/framework facts;
  prohibition of hidden answer-changing assumptions; realistic annotated
  irrelevant facts; controlled negative phrasing; parallel, exclusive, unique,
  unit-consistent options; key-leakage and unsupported-absolute prevention;
  complete six-part diagnostic explanations; and the bounded role of mechanical
  language checks versus James's human judgment.
- James ruling: **APPROVE**.
- Effect: the prose/fairness section is accepted for the eventual dated G2
  amendment but is not yet active in `goal.md`. Next is the correctness-route
  expansion obligation.

### P1.6 — G2 correctness-route expansion ruling

Date: 2026-08-13.

- Presented the pre-production obligation to add and red-calibrate independent
  routes for percentage/ratio/present-value/effective-interest/per-share
  formulas, date and period schedules, conditional rule tables and
  classification assertions, journal-entry balance and direction, linked-
  subtotal roll-forwards, and independently authored nonnumeric reference
  fixtures.
- Retained the prohibition on any production family whose verifier route is
  neither executable nor explicitly bounded, and on shared producer deciding
  logic serving as independent verification.
- James ruling: **APPROVE**.
- Effect: correctness-route expansion is accepted for the eventual dated G2
  amendment but is not yet active in `goal.md`. Next is the artifact-first
  hybrid architecture ruling.

### P1.6 — G2 artifact-first hybrid architecture ruling

Date: 2026-08-13.

- Presented the architecture ruling: immutable JSON versions and append-only
  JSON events are canonical; SQLite is a disposable, transactionally rebuilt
  local projection; the review surface proposes but cannot grant approvals;
  canonical ingestion validates and exclusively creates event files; and cold
  JSON reconstruction must reproduce review, readiness, and coverage state.
- Retained the boundary that this does not select hosted persistence, accounts,
  a learner application, or public deployment.
- James ruling: **APPROVE**.
- Effect: architecture is accepted for the eventual dated G2 amendment but is
  not yet active there. Every substantive G2 item and policy ruling is now
  decided. Next is the consolidated dated amendment and one final ratification
  ruling.

### P1.6 — consolidated dated G2 amendment drafted

Date: 2026-08-13.

- Added `goal.md` section `DRAFT amendment — 2026-08-13 — Gate G2 production
  contract`, consolidating every individually approved item-derived policy:
  coverage, ten variety rows, five anti-cloning rules, six difficulty rubrics
  and application rules, prose/fairness, correctness-route expansion, and the
  artifact-first hybrid architecture.
- The draft names exact project-relative evidence paths and pre-production
  commands, preserves all product/deployment deferrals, and states that it
  authorizes only P2 after final ratification—not G3, future item versions, or
  public/product scope.
- The status is explicitly pending final ratification, so production remains
  forbidden. Current `goal.md` SHA-256 is
  `78d084d92bec1ecffca24266022133c8d98116a4d95a7a140afe4e320490601e`.
- Arithmetic audit passed: 113 tasks; Area minimums 141 + 120 + 92 = 353;
  whole-item examples 20%=71, 45%=159, 15%=53, 5%=18; 25% maximum=88 and
  40% maximum=141 at the minimum bank size.
- Next and only remaining G2 ruling: ratify or reject/revise the consolidated
  dated amendment as a whole.

### G2 — consolidated dated amendment ratified

Date: 2026-08-13.

- Presented the exact consolidated amendment in `goal.md`, then SHA-256
  `78d084d92bec1ecffca24266022133c8d98116a4d95a7a140afe4e320490601e`,
  for a final Ratify/Reject/Revise/Comment ruling.
- James ruling: **RATIFIED** — “Ratified.”
- Changed the heading from draft to amendment and its status to `RATIFIED BY
  JAMES — 2026-08-13` without altering its substantive provisions. Ratified
  `goal.md` SHA-256 is
  `e58830c7308da16485138988babc4f52b9a459e5a24696a5fa1dedb4bc315b1a`.
- Effect: Gate G2 is closed, P1 is complete, and P2 is authorized only within
  the amendment. G3, future exact question versions, final-bank sufficiency,
  learner/admin product scope, accounts, hosting, and public launch remain
  unapproved.
- Rewrote `plan.md` for P2.0 contract enforcement, P2.1 correctness-route
  expansion, P2.2 rebuildable projection/event workflow, and P2.3 G3 package.
  Updated the child and program-root `CLAUDE.md` signposts to P2.0.

Verification receipt:

- `python scripts/validate_p1_records.py` — PASS.
- `python scripts/verify_taxonomy.py data/far-taxonomy.json` — PASS, 13/13,
  taxonomy counts 3 Areas / 22 Groups / 18 Topics / 113 tasks.
- `python scripts/calibrate_question_verifier.py` — PASS, 8/8 red
  calibrations, zero waivers.
- `python scripts/verify_p1_sample.py` — PASS, six items, six learner-ready,
  48/48 checks.
- `python -m unittest discover -s tests -p "test_*.py"` — PASS, 35/35.
- `python -m compileall -q scripts tests` — PASS.
- `npm run lint` in `review-surface/` — PASS.
- `npm test` in `review-surface/` — PASS production build and 2/2 rendered-HTML
  tests.

Kill sweep and phase receipt:

- No `result.md`, production generator, production-bank data, G3 approval,
  final coverage claim, learner/admin application, account system, analytics,
  hosted persistence, or public deployment exists.
- All six current G2 versions remain exact-approved and reconstructible; the
  historical opening package and superseded-version events remain intact.
- P1.6 exit evidence is satisfied. P2.0 is the active unit.
