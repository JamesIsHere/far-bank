# plan.md — P2 contract enforcement and review workflow

Agent-owned current strategy under the ratified `goal.md` and its ratified
2026-08-13 G2 amendment. James passed G1 and G2. P2 may implement the ratified
production controls and internal review workflow; it does not authorize G3,
future human approvals, learner/admin product scope, hosting, or public launch.

## Unit queue

### P1.0 — Artifact-first data architecture — COMPLETE

- Decide the concrete JSON/SQL boundary from the immutable-version,
  append-only-review, deterministic-verification, and future-ranking needs.
- Write an architecture decision record with entities, ownership, identifiers,
  version boundaries, event semantics, and migration path.
- Keep taxonomy and authored content versioned independently so a Blueprint
  change can quarantine affected mappings without rewriting history.
- Exit evidence: the design can reconstruct exact content, verification,
  approval, and coverage state without mutable status shortcuts.

### P1.1 — Schemas and representative fixtures — COMPLETE

- Define question candidate/version, option, fact, solution, distractor error
  model, rule/source trace, Blueprint mapping, challenge mechanic, difficulty,
  verification, review event, and exact-version approval records.
- Encode the current question contract while leaving G2-owned numeric floors
  and variety distributions explicitly unratified.
- Build clean and malformed fixtures before sample authoring.
- Exit evidence: schemas accept a complete representative candidate and reject
  missing provenance, non-four-option items, duplicate options, multiple keys,
  opaque difficulty labels, invalid mappings, and mutable approval shortcuts.

### P1.2 — Question verifier and red calibration — COMPLETE

- Implement the P1-applicable portions of SCHEMA, RECOMPUTE, RULE TRACE,
  DISTRACTORS, LANGUAGE, ORIGINALITY-boundary, APPROVAL INTEGRITY, and VARIETY.
- Separate producer logic from correctness evidence and store structured check
  results rather than a single pass flag.
- Give every individual check at least one purpose-built red corruption before
  it can gate the sample.
- Exit evidence: calibration report maps each check to its rejected defect;
  no waived or uncalibrated check is greenwashed.

### P1.3 — Internal review surface — COMPLETE

- Build the smallest local review surface that can display the exact candidate
  version, answer and worked solution, source/rule trace, Blueprint path,
  distractor models, challenge mechanics, difficulty evidence, and check
  results.
- Expose Approve, Reject, Revise, and Comment event shapes without claiming G3
  hands-on workflow approval.
- Make any content edit visibly invalidate approval for the prior exact
  version; sample verdicts remain append-only events.
- Exit evidence: the surface supports individual G2 verdicts and cannot make
  an unverified candidate appear learner-ready.

### P1.4 — Deliberately varied cross-area sample — COMPLETE

- Author a bounded sample spanning all three FAR areas, all FAR Blueprint skill
  levels, and multiple accounting and exam-execution challenge mechanics.
- Vary length, computational burden, reading burden, ask placement, relevant
  versus irrelevant facts, formula/model translation, elimination leverage,
  and controlled language traps.
- Include at least one item that tests a small mechanical convention or
  “gotcha,” not only technically large transactions.
- Exit evidence: every candidate passes the calibrated mechanical checks and
  is visibly marked candidate-only pending James's individual verdict.

### P1.5 — G2 package and proposed amendment — COMPLETE

- Render the sample in the review surface with one stable review queue.
- Produce proposed—not yet enforceable—coverage floors, variety matrix,
  difficulty rubrics, prose rules, and the concrete JSON/SQL decision for
  James's red pen.
- Include limitations, bounded originality claim, source currency, and any
  unresolved disagreement without smoothing them away.
- Exit evidence: deterministic review artifact plus verifier and calibration
  reports are ready for Gate G2.

### P1.6 — Gate G2 — COMPLETE

- Present one sample candidate per turn for an individual verdict.
- After all item verdicts, present the coverage/variety/difficulty and prose
  decisions one ruling per turn.
- Record every verdict append-only and bind it to the exact content version.
- Production begins only after all required rulings are folded into an explicit
  dated G2 contract amendment ratified by James.

### P2.0 — Encode the ratified production contract — COMPLETE

- Extend schemas and reports for every ratified coverage, variety,
  anti-cloning, difficulty, and prose field without rewriting existing
  immutable versions.
- Build calibrated checks for whole-bank floors, concentration caps,
  within-task diversity, within-area compatibility, and six-dimensional
  difficulty evidence.
- Add a machine-readable ratification receipt tying the rules to the exact
  dated amendment and evidence paths.
- Exit evidence: every new gating check rejects a purpose-built corruption;
  clean fixtures pass with zero waivers, and current sample history remains
  reconstructible.

### P2.1 — Expand independent correctness routes — COMPLETE

- Implement and red-calibrate the formula, schedule, conditional-rule,
  journal-entry, linked-roll-forward, and nonnumeric assertion-fixture routes
  required by the amendment.
- Keep producer deciding logic separate from verifier logic and explicitly
  bound unsupported families.
- Exit evidence: each admitted production family has an executable independent
  route and at least one known-bad rejected fixture.

### P2.2 — Rebuildable local projection and event workflow — COMPLETE

- Build the disposable SQLite projection transactionally from canonical JSON.
- Implement hands-on Approve, Reject, Revise, and Comment flows through the
  validated exclusive-ingestion boundary.
- Demonstrate that content revision creates a new version, prior approval does
  not carry forward, and only exact current approvals affect readiness and
  coverage.
- Exit evidence: cold reconstruction and the local projection agree, including
  stale/superseded histories and zero mutable approval shortcuts.

### P2.3 — Gate G3 review package — ACTIVE: HUMAN VERDICT PENDING

- Render a bounded hands-on workflow package covering all four actions,
  revision invalidation, exact-version readiness, and coverage effects.
- Run accessibility, keyboard, integrity, build, lint, and reconstruction
  checks and preserve limitations.
- Exit evidence: James can exercise the workflow and issue the G3 verdict; no
  G3 approval is inferred from automated checks.

Automated package status: deterministic receipt, structural accessibility and
keyboard contract, integrity, reconstruction, build, lint, and rendered HTML
checks pass. Live interaction remains the human Gate G3 exercise; the in-app
browser had no active session during package preparation and is not recorded as
an automated pass.

## Unit exit rule

A unit is done only when its artifacts exist, its named checks pass, and its
evidence is appended to `worklog.md`. A working UI or plausible sample is not
completion without exact-version evidence.

## Active fences

- Production work must satisfy the ratified G2 amendment; no family may proceed
  before its independent route and new gating checks are red-calibrated.
- No question is learner-ready merely because it passes checks or appears in
  the review surface.
- No AI output is correctness, originality, or difficulty evidence by itself.
- No copied or closely paraphrased AICPA, retired, or commercial-bank item.
- Use only the ratified coverage/variety floors and six-dimensional difficulty
  rubric; no opaque easy/medium/hard label.
- No public/learner website, accounts, adaptive model, lesson plan, or learner
  analytics in this phase.

## Scope temptations — log, do not build

- Full production batching and final-bank scale remain P3 work after G3.
- Hands-on workflow approval belongs to G3 even if the event model is built now.
- Learner and administrator product surfaces remain later program children.
