# ADR 0005 — Rebuildable review projection and exact event workflow

Status: IMPLEMENTED FOR P2.2  
Date: 2026-08-13  
Owner: P2.2 under the ratified `goal.md` amendment

## Decision

`scripts/rebuild_review_projection.py` validates every canonical JSON record,
derives exact-version state independently in Python, loads a fresh temporary
SQLite database, compares the SQL views with the cold JSON result, runs foreign
key and integrity checks, and only then atomically replaces
`build/review.sqlite`.

The SQLite file is disposable. Its projection manifest records every canonical
input path, SHA-256, and byte size plus a deterministic manifest ID. Direct SQL
edits are unsupported and disappear on rebuild.

## Normalized and derived state

The projection normalizes identities, question/rule/reference versions,
options, Blueprint mappings, difficulty evidence, rule/source links,
verification checks, review events, and source-impact subjects. Update/delete
triggers protect every canonical parent and child row.

Views derive:

- latest question version;
- latest decisive exact-version review, excluding comments;
- latest verification event and exact required-check policy match;
- latest source-impact outcome;
- rule currency and admitted/current source state;
- learner readiness; and
- coverage contribution.

No table stores editable `learner_ready`, approval, or coverage truth. Coverage
requires the complete learner-ready conditions plus a production purpose; the
G2 sample therefore remains learner-ready review evidence with zero production
coverage.

## Event and revision workflow

`ingest_review_event.py` validates exact subject binding and exclusively creates
Approve, Reject, Revise, and Comment event files. Duplicate event IDs and stale
content hashes are rejected. Automatic invalidation additionally requires the
canonical newer version and validates same-identity monotonic supersession.

`scripts/create_question_revision.py` creates a new immutable version only when
approval-bound content changes, recomputes the canonical content hash, validates
the complete question contract, and writes by exclusive creation. It also
constructs the system invalidation event for the prior version.

## Reconstruction proof

The current cold build reads 48 canonical records: 6 identities, 11 question
versions, 1 reference, 6 rules, 11 verification events, and 13 review events.
Independent JSON and SQLite derivations agree for all 11 exact versions: six
current versions are learner-ready, superseded versions are not, and production
coverage is zero.

The deterministic workflow calibration exercises all four human actions, one
revision and automatic invalidation, duplicate rejection, stale-binding
rejection, and the preserved `far-q-000102.v001` to `v002` approval boundary.

These are local P2 implementation proofs. They do not constitute the G3
hands-on verdict, authorize hosted persistence, or create production content.
