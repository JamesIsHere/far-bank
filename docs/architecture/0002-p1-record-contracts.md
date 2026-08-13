# ADR 0002 — P1 canonical record contracts

Status: IMPLEMENTED FOR P1; DIFFICULTY RUBRIC AND DISTRIBUTIONS PROPOSED FOR G2  
Date: 2026-08-13  
Owner: P1.1 under the ratified `goal.md`

## Decision

The artifact-first boundary in ADR 0001 is implemented as six immutable JSON
record families plus one source-impact event family:

- `question-identity.schema.json` owns stable identity and creation
  provenance, never question status;
- `question-version.schema.json` owns every approval-bound content field;
- `reference-version.schema.json` records source identity, authority class,
  retrieval evidence, and a dated currency assessment;
- `rule-version.schema.json` binds structured claims to exact reference
  versions and locators;
- `verification-event.schema.json` records individual calibrated check results
  for one exact question version;
- `review-event.schema.json` represents Approve, Reject, Revise, Comment, and
  automatic invalidation as append-only actions; and
- `source-impact-event.schema.json` preserves quarantine, revalidation, and
  bounded unaffected findings after a reference changes.

An approval is an `approve` review event produced by a human actor and bound
to question ID, version ID, and canonical content SHA-256. There is no approval
row and no editable `learner_ready`, `approved`, or `status` property on a
question. The SQLite projection in `schema/review-projection.sql` retains this
boundary and derives the latest exact-version review action through views.

## Canonical content hash

Question and rule hashes cover the complete `content` object serialized as
UTF-8 JSON with sorted keys, `ensure_ascii=false`, and separators `(',', ':')`.
The outer schema/version/identity/hash envelope is excluded. Review and
verification events bind the stored hash as well as the stable and versioned
identifiers. `scripts/validate_p1_records.py` recomputes the hash rather than
trusting it.

## Cross-record contracts

JSON Schema supplies closed record shapes, required provenance, conditional
event actors, four-option cardinality, one keyed option, structured facts,
and evidence-bearing difficulty records. The P1 schema-contract validator adds
the relationships that Draft 2020-12 cannot express by itself:

- question/version-number agreement and canonical hash agreement;
- option IDs A–D and normalized option-text uniqueness;
- solution-key agreement;
- each of the six contract-named difficulty dimensions exactly once;
- exact resolution of taxonomy/task/path/skill relationships;
- rule, assertion, fact, and solution-step reference resolution; and
- exact question/version/hash binding for verification, review, and source-
  impact events.

These are schema-layer integrity contracts, not the calibrated content-quality
verifier owed by P1.2.

## G2 fence

The six difficulty dimensions come from the ratified bootstrap contract, but
their 1–5 values and fixture rubric are explicitly marked
`proposed_for_g2`. They are a reviewable transport shape, not an enforceable
rubric, difficulty claim, production distribution, or coverage/variety floor.
The fixture reference and rule are explicitly synthetic and uncertain; they
cannot substantiate a real question. The representative fixture is not a G2
sample item and makes no correctness, originality, approval, or learner-ready
claim.

The P1 schemas accept only `schema_fixture` and `sample_candidate` question
purposes. A production purpose is deliberately absent until the G2 amendment
authorizes production. No production quota, learner surface, or mutable status
is introduced by this decision.

## Exit evidence

Run:

```text
python scripts/validate_p1_records.py
python -m unittest discover -s tests -v
```

The corruption definitions under `fixtures/questions/corruptions/` are
applied to the clean representative record. Each names the exact contract that
must reject it. They cover missing provenance, non-four-option content,
duplicate option text, multiple keys, opaque difficulty, invalid Blueprint
mapping, content mutation/hash mismatch, and a mutable approval shortcut.

## P1.2 owning-layer correction

P1.2 verifier design exposed a missing part of the original P1.1 content
shape: the schema had a worked solution and prose distractor derivations but
did not yet encode the independent correctness route or mechanically
executable distractor reproductions required by `goal.md`. The question
schema was advanced to version 1.1.0 before sample authoring.

Version 1.1.0 adds structured option values, a producer/verifier separation
declaration, an independently executable correctness route, executable or
fixture-backed distractor reproduction routes, and explicit assumptions. The
fixture content hash and all illustrative exact-version bindings were
regenerated. This is a repair at the owning schema layer, not a relaxation or
contract amendment.
