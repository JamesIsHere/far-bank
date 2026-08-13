# ADR 0001 — Artifact-first JSON with a rebuildable SQL projection

Status: PROPOSED FOR G2 RED PEN  
Date: 2026-08-13  
Owner: P1.0 under the ratified `goal.md`

## Decision

Use a hybrid architecture with a hard authority boundary:

1. Immutable canonical JSON artifacts own authored facts, content versions,
   rule/source versions, structured verification evidence, and review events.
2. A local SQLite database is a derived projection used for fast review,
   filtering, reporting, and coverage queries.
3. The SQLite file never owns truth. It may be deleted and reconstructed from
   canonical artifacts with no information loss.
4. A later multi-user website may project the same records into PostgreSQL,
   but that migration belongs to a later child project and does not change the
   FAR bank's canonical history.

This is a P1 implementation decision, not a contract amendment. James may
revise it at Gate G2 before production scale makes it expensive to change.

## Why this boundary

Canonical JSON is diffable, reviewable, deterministic, easy to validate with
schemas, and appropriate for generated artifacts that must never be hand-
edited. Individual event files avoid the crash and merge hazards of appending
to one large JSONL file.

SQLite gives the internal review surface relational joins, indexes, aggregate
coverage queries, and transactionally rebuilt projections without turning a
binary database into the only audit record. The future web product can move
the projection to PostgreSQL when concurrency, authentication, and remote
durability become real requirements.

## Canonical record families

All paths below are logical conventions; schemas, not path names alone, enforce
record meaning.

```text
data/
  far-taxonomy.json
  questions/
    far-q-000001/
      identity.json
      versions/
        far-q-000001.v001.json
        far-q-000001.v002.json
  rules/
    far-rule-<slug>/
      versions/
        <rule-version-id>.json
  events/
    verification/
      <verification-event-id>.json
    review/
      <review-event-id>.json
    source-impact/
      <impact-event-id>.json
```

- `identity.json` is created once and contains only the stable question ID and
  creation provenance. It has no mutable status field.
- Every `versions/*.json` file is an immutable exact content version.
- Every verification result is an immutable event bound to a content hash,
  checker identity/version, input evidence, result, and execution time.
- Approve, Reject, Revise, Comment, and automatic invalidation are separate
  append-only review-event files.
- Source-change impact and quarantine decisions are events; historical source
  or question records are never rewritten.

## Stable identity and exact-version binding

- Question identity: `far-q-000001`.
- Content version: `far-q-000001.v001` with a monotonically increasing integer
  version number within the question.
- Taxonomy identity: `far-2026-01`; mappings bind both taxonomy ID and exact
  Area/Group/Topic/task IDs.
- Rule and source references bind explicit version IDs, never an unversioned
  “current rule” alias.
- Review and verification events bind:
  - question ID;
  - content version ID;
  - canonical content SHA-256; and
  - the event's own stable ID and recorded time.

The canonical content hash is computed from an explicit content payload using
UTF-8 JSON serialized with sorted keys, no insignificant whitespace, and fixed
separators. Only the outer integrity envelope that stores the resulting digest
is excluded, avoiding a self-referential hash; no approval-bound content field
is excluded. A content edit therefore creates a new version and a different
hash rather than modifying a reviewed file.

## Event semantics

Review actions are `approve`, `reject`, `revise`, `comment`, and
`auto_invalidate`.

- `comment` never changes verdict state.
- The latest decisive event for the exact version is its human verdict.
- `revise` is a verdict requesting a new content version; it does not edit the
  reviewed version.
- When a newer version is created after an approval, the system emits an
  `auto_invalidate` event for the prior approved version. Even if that event
  failed to emit, the projection must never count a non-latest version as
  learner-ready.
- Events are ordered by recorded UTC time and stable event ID. Conflicting
  decisive events at the same ordering boundary are an integrity failure, not
  a “last file wins” guess.
- Reviewer identity is explicit. The P1/G2 reviewer is James; the schema does
  not encode a magical human boolean.

No event is updated or deleted to produce a cleaner history.

## Derived learner-ready projection

`learner_ready` is calculated, never stored as editable truth. A question
version counts only when all of the following are true:

1. it is the latest immutable content version for its question identity;
2. its canonical hash matches the hash bound by every relied-upon event;
3. every required calibrated mechanical check has a current passing event;
4. the latest decisive human review event for that exact version is `approve`;
5. no later invalidation or applicable source-impact quarantine event exists;
6. every taxonomy, rule, and source reference resolves to a current admitted
   record; and
7. no unresolved integrity conflict exists.

Coverage, variety, and difficulty reports query this projection. Candidate,
rejected, stale, quarantined, and mechanically failing versions remain visible
but contribute zero learner-ready coverage.

## SQLite projection

The generated `build/review.sqlite` may contain normalized tables such as:

- `question_identity`
- `question_version`
- `question_option`
- `blueprint_mapping`
- `rule_trace`
- `verification_event`
- `review_event`
- `source_impact_event`
- `current_question_projection`
- `coverage_projection`

The projection builder performs one transaction: create a fresh database,
load and validate all canonical records, derive state, run integrity checks,
then atomically replace the prior disposable database. It records a manifest
of input file hashes and builder version. Direct SQL edits are unsupported and
must disappear on the next rebuild.

## Reconstruction proof

A cold reconstruction must be able to:

1. delete or ignore the existing SQLite projection;
2. validate every canonical JSON artifact against its schema;
3. verify file/content hashes and referential integrity;
4. replay verification, review, and source-impact events;
5. reproduce exact-version status, learner-ready state, and coverage reports;
6. rebuild the same deterministic G2 review artifact; and
7. produce a projection/input manifest whose hashes agree with the checked-in
   canonical artifacts.

Failure at any step leaves the projection unusable and no item learner-ready.

## Concurrency and future migration

P1 assumes one local reviewer and a single event-writing service. It does not
pretend individual JSON event files are a multi-user transaction system.

When a later website requires concurrent reviewers or remote durability:

- PostgreSQL becomes the operational event store for that child project;
- canonical FAR artifacts and their hashes are imported without rewriting
  history;
- the same immutable-version and append-only-event invariants remain;
- deterministic exports reproduce the artifact-shaped audit record; and
- the migration is verified by comparing reconstructed projections before and
  after import.

## Rejected alternatives

### JSON only, including all query work

Rejected because coverage, status derivation, and review filtering become
needlessly repetitive and fragile as the sample and later bank grow.

### SQLite as the sole canonical store

Rejected because the binary database would obscure review diffs, complicate
generated-artifact discipline, and make exact audit history harder to inspect
without tooling.

### PostgreSQL now

Rejected for this child because accounts, remote concurrency, deployment, and
the public/learner website are explicitly deferred. Introducing a server
database now would add operational scope without strengthening P1 evidence.

### One mutable question row with status columns

Forbidden by the ratified contract. It would overwrite reviewed content,
separate approval from its exact version, and make current status an editable
claim rather than a reproducible conclusion.

## G2 red-pen questions

The G2 package should test whether:

- individual event files are understandable enough during review;
- the projected status makes invalidated approvals visibly obvious;
- exact-version hashes are useful without overwhelming the reviewer;
- the SQLite projection provides enough filtering for sample verdicts; and
- this boundary remains credible for future multidimensional ranking without
  prematurely building learner analytics.
