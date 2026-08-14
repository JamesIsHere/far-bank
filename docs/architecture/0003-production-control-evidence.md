# ADR 0003 — P2 production-control evidence companion

Status: IMPLEMENTED FOR P2.0  
Date: 2026-08-13  
Owner: P2.0 under the ratified `goal.md` amendment

## Decision

Production-control observations live in a versioned companion record rather
than being retrofitted into approved P1 question versions. The companion binds
an exact question ID, version ID, and content SHA-256 to the ratified contract
and transports the fields needed for coverage, variety, anti-cloning,
difficulty, and targeted prose checks.

The machine-readable contract receipt is
`data/contracts/far-g2-production-contract.v001.json`. Its ratification block
binds the exact `goal.md` SHA-256 and amendment heading, and its evidence list
names the G2 records. The verifier also binds the canonical receipt hash so a
policy change cannot silently relax a gate. A real policy change requires a
dated `goal.md` amendment, a new contract version, and new red calibration.

## Derived, not mutable

The companion stores observable evidence, not `learner_ready`, approval, or a
coverage status. Eligibility still reconstructs from canonical question,
verification, review, source-currency, and version records. Stale, unapproved,
failing, superseded, or quarantined records must be removed before the bank
aggregate is evaluated.

Full-task exercise is explicit and separate from MCQ mapping and depth. A false
claim carries an MCQ scope limit; a true claim requires format evidence. The
P2.0 calibration fixtures set it false.

## Gating checks

`scripts/verify_production_controls.py` implements nine independently reported
checks:

1. ratification and exact-envelope binding;
2. item observable/bin consistency;
3. six-dimensional difficulty support;
4. targeted prose/fairness evidence;
5. total, task, area, and area-share coverage floors;
6. all ten ceiling-rounded variety floors;
7. within-task representation, mechanic, fact-pattern, and distractor-model
   diversity;
8. bank-wide template, fact-pattern, representation, distractor-family, and
   irrelevant-fact caps; and
9. area skill/solution-representation compatibility.

Every check has one purpose-built corruption under
`fixtures/production/corruptions/`. The deterministic report is
`reports/p2-production-control-calibration.json`; waivers are forbidden.

## Calibration boundary

The clean 353-record baseline is generated in memory from the 113-task
taxonomy solely to exercise whole-bank arithmetic and aggregation. Every
record is marked `calibration_fixture`; the records are not canonical question
versions, are not written into `data/production/`, receive no review events,
and contribute zero real coverage.

P2.0 does not implement the expanded correctness routes. Those remain P2.1,
and no production family may begin until its route and applicable production
controls have both been red-calibrated.
