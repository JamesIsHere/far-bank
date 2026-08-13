# Gate G2 proposed amendment — coverage, variety, difficulty, and prose

STATUS: PROPOSED FOR JAMES'S RED PEN. NOT RATIFIED. NOT PART OF `goal.md`.

Date proposed: 2026-08-13  
Proposal ID: `far-g2-contract-proposal.v001`  
Evidence sample: `far-p1-g2-sample.v001`

## Why this proposal exists

The six-item first-pass sample exposed enough concrete structure to replace the
bootstrap placeholders with reviewable rules. This proposal defines what would
be enforceable after Gate G2. Until James rules on it and a dated amendment is
written into `goal.md`, none of the numbers below authorizes production or
counts a candidate as covered, difficult, varied, approved, or learner-ready.

## Proposed coverage floors

### Per representative task

- **Mapped:** at least one learner-ready MCQ mapped to the exact task.
- **MCQ-depth covered:** at least three learner-ready MCQs mapped to the exact
  task, with at least two distinct primary solution representations, at least
  two distinct challenge-mechanic tags across the set, and no pair sharing the
  same fact pattern plus distractor-model set.
- **Full task exercised:** never inferred from the preceding floors. It is
  reported only when the approved assessment format genuinely performs the
  complete task. An MCQ mapped to preparation, reconciliation, correction,
  investigation, or document-driven work ordinarily reports `false` and names
  its scope limitation.

The three-item floor is intentionally a minimum, not a sufficiency theorem. A
task fails MCQ-depth coverage if it has three cosmetic variants or three items
that exercise only one rule boundary.

### Bank and area minimums

Applying three items to each of 113 representative tasks produces 339 items but
underrepresents Area III relative to the published allocation. The proposed
minimum approved bank is therefore **353 learner-ready items**:

| FAR area | Task floor | Proposed approved-item minimum | Share at the minimum |
| --- | ---: | ---: | ---: |
| I — Financial Reporting | 47 × 3 | 141 | 39.9% |
| II — Select Balance Sheet Accounts | 40 × 3 | 120 | 34.0% |
| III — Select Transactions | 26 × 3 plus 14 depth items | 92 | 26.1% |

The extra Area III items go to tasks whose first three approved items do not
yet span the required work, representation, or challenge dimensions. Published
Blueprint weights remain design constraints, not evidence that task counts
equal exam frequency. A later bank may exceed 353 while retaining 30–40% Area
I, 30–40% Area II, and 25–35% Area III unless a dated Blueprint change requires
reconsideration.

### Coverage exclusions

- A stale, mechanically failing, quarantined, unapproved, or superseded
  question contributes zero at every level.
- One question may map to multiple tasks only when each mapping is independently
  justified. It counts once toward the bank total and may contribute to each
  valid mapping, but it cannot alone satisfy any task's depth floor.
- Coverage reports show item IDs and exact versions behind every count; no
  aggregate may conceal which items supply the claim.

## Proposed variety matrix

Each item stores one observed bin per dimension. The bank-wide floors apply to
learner-ready exact versions only. Percentages are rounded down to whole items,
so a floor is met only when the integer count is at least `ceil(total × floor)`.
Unallocated percentage leaves deliberate design freedom; it is not a hidden
category.

| Dimension | Observable bins | Proposed bank-wide floors |
| --- | --- | --- |
| Stem length | short: ≤45 words; standard: 46–90; dense: ≥91 | short ≥20%; standard ≥45%; dense ≥15% |
| Numeric fact density | low: 0–2 numeric facts; medium: 3–5; high: ≥6 | each bin ≥15% |
| Primary accounting work | conceptual recall; classification/rule selection; computation; analytical reconciliation/inference | recall ≥8%; classification/rule ≥20%; computation ≥30%; analytical ≥20% |
| Dependent solution steps | one; two to three; four or more | one ≥10%; two-to-three ≥50%; four-plus ≥10% |
| Irrelevant facts | none; one to two; three or more | none ≥30%; one-to-two ≥30%; three-plus ≥10% |
| Ask placement | direct/final sentence; indirect or embedded after setup | direct ≥60%; indirect/embedded ≥20% |
| Rule pressure | rule; timing; basis; measurement; classification; presentation; convention | each tag appears on ≥5% of items; multi-tagging allowed only with separate evidence |
| Solution representation | formula; roll-forward; journal effect; financial-statement view; rule selection; classification | each representation ≥5% |
| Elimination burden | low: one obviously invalid distractor; medium: all plausible but two fall to one rule; high: all require separate diagnosis | low ≥10%; medium ≥40%; high ≥15% |
| Realistic time pressure | low; moderate; high under the ratified time rubric | low ≥15%; moderate ≥45%; high ≥15% |

Additional anti-cloning rules:

- Every nonkey has one named misconception and a reproducible result or
  independently authored assertion fixture.
- Across the three-item minimum for one task, at least five distinct distractor
  error-model IDs appear and no two items share all three error models.
- No single stem template, accounting fact pattern, primary representation, or
  distractor family may exceed 25% of the approved bank.
- No more than 40% of approved items may contain three or more irrelevant facts.
  Noise is a tested skill, not the default writing style.
- Every area must contain at least one learner-ready item in every applicable
  skill level and every representation that is genuinely compatible with its
  content. Inapplicable combinations are recorded, not forced.

## Proposed difficulty rubric

Difficulty remains six-dimensional. No aggregate `easy`, `medium`, or `hard`
field is allowed. Each level requires the recorded observable feature; prose
intuition alone cannot assign it.

| Dimension | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- |
| Accounting complexity | one familiar rule, no exception | one rule plus one boundary | two interacting rules or one exception | three interacting rules/conditions | four-plus interactions or judgment with competing treatments |
| Reasoning steps | one dependent step | two | three | four | five or more, with at least one branch or reconciliation loop |
| Reading and fact selection | ≤3 facts, no irrelevant facts | 4–5 facts or one irrelevant fact | 6–7 facts or two irrelevant facts | 8–10 facts or three-plus irrelevant facts/conditional clauses | 11-plus facts with dependencies across passages or exhibits |
| Rule/convention pressure | direct application, no nearby boundary | one named boundary | two boundaries or one controlled convention trap | three boundaries or timing/basis interaction | four-plus boundaries with a defensible but demanding exception analysis |
| Distractor/elimination burden | one obviously invalid distractor | three distinct errors, at least one readily eliminated | all plausible; two fall to one rule | each requires separate diagnosis and one is numerically close | separate diagnoses plus competing intermediate results or convention traps |
| Realistic time pressure | ≤30 seconds, ≤1 operation | 31–60 seconds or 2 operations | 61–90 seconds or 3–4 operations | 91–150 seconds or 5–7 operations | >150 seconds or 8-plus operations/branching review |

Rules for applying the rubric:

- The highest satisfied descriptor is used only when its observable condition is
  present; a model may not raise a level because an item “feels hard.”
- Time is initially estimated from operations and review burden, then calibrated
  against human completion data when such data exists. Estimated and observed
  time remain separate fields.
- If two descriptors conflict, the lower supported level is recorded and the
  conflict is flagged for human review.
- The six-number profile is diagnostic. It is not averaged into a single label.

## Proposed prose and fairness rules

1. The final sentence is a direct question unless an indirect ask is deliberate,
   tagged, and restated unambiguously in `solution.end_ask`.
2. Every number, date, quoted threshold, and stated assumption in the stem has a
   structured record. Every structured fact appears in the stem or an identified
   exhibit.
3. Default for-profit/U.S.-GAAP assumptions follow the Blueprint. NFP,
   governmental, public-company, or special-purpose-framework facts name the
   entity and framework explicitly.
4. An assumption material to the key is explicit in the stem or traces to a
   controlling rule. Hidden conventions that change the answer are forbidden.
5. Irrelevant facts are realistic, individually annotated, and limited by the
   variety matrix. Orphan numbers and decorative noise are forbidden.
6. Negative phrasing is used only when the tested skill requires exception
   identification. Double negatives, `not incorrect`, and mixed
   `except/not` constructions are forbidden.
7. Options are grammatically parallel, mutually exclusive, unique after
   normalization, and use consistent units, dates, rounding, and sign language.
8. The stem cannot leak the keyed option text. Absolute words such as `always`
   and `never` require controlling authority or are treated as leakage.
9. The explanation answers all six questions in the ratified learner-facing
   contract and names why each distractor is wrong under the stated facts.
10. A mechanical language pass is a targeted screen, never general proof of
    clarity, fairness, or instructional usefulness; James's item verdict owns
    those judgments.

## Proposed correctness-route expansion before production

The P1 sample deliberately uses linear structured recomputation so the initial
independent checker can execute every item. That proves the current route but
does not cover production families. Before production generation, the verifier
must add and red-calibrate independent routes for:

- percentage, ratio, present-value, effective-interest, and per-share formulas;
- date and period schedules;
- conditional rule tables and classification assertions;
- journal-entry balance and account-direction checks;
- roll-forwards with multiple linked subtotals; and
- independently authored reference fixtures for nonnumeric questions.

No production family may use a route the verifier cannot execute or explicitly
bound. Shared producer logic remains forbidden.

## Proposed architecture ruling

Ratify ADR 0001's artifact-first hybrid for the next phase:

- immutable JSON versions and append-only JSON events remain canonical;
- SQLite remains a disposable, transactionally rebuilt local projection;
- the review surface proposes events but cannot directly grant approval;
- canonical ingestion exclusively creates a validated event file; and
- cold reconstruction from JSON must reproduce review and coverage state.

This ruling does not select hosted persistence, accounts, a learner application,
or a public deployment. Those remain deferred.

## Required G2 rulings

The gate is complete only after James rules, one decision at a time, on:

1. each of the six exact sample versions;
2. the per-task and area coverage floors;
3. each variety-matrix row and anti-cloning rule;
4. the six difficulty rubrics and application rules;
5. the prose/fairness rules;
6. the correctness-route expansion obligation; and
7. the artifact-first hybrid architecture.

Accepted decisions must be copied into an explicit dated `goal.md` amendment.
Rejected or revised decisions remain in history but do not authorize production.
