# FAR Bank internal review surface

Local Gate G3 hands-on package for inspecting exact FAR question versions,
exercising all four review actions, and composing append-only event proposals.

This directory is not a learner-facing site and Gate G3 is not yet approved.
The six records are the historical G2 sample, contribute zero production
coverage, and are not production-bank questions. Only James can issue the G3
verdict after exercising the bounded workflow.

The local interface is split into two focused routes:

- `/` is a four-exercise G3 decision-flow test. One sample stem and the action
  controls remain visible; the full question dossier is one disclosure away.
- `/evidence` holds gate-level reconstruction, revision, coverage, package,
  and limitation evidence.

## Rebuild the evidence input

From the `far-bank/` project root:

```text
python scripts/build_review_surface_data.py
python scripts/build_g3_package.py
```

The generated `app/review-data-v002.json` binds each question version and
content hash. `app/g3-workflow-package.json` mirrors the deterministic G3
receipt in `reports/g3-package-manifest.json`. Do not hand-edit them.

## Run locally

From `review-surface/`:

```text
npm ci --ignore-scripts --prefer-offline --no-audit --no-fund
npm run dev
```

The surface uses no account, D1, R2, remote persistence, or browser storage.
An action downloads a proposed review-event JSON file. Canonical ingestion is
a separate exclusive-create validation boundary:

```text
python scripts/ingest_review_event.py <downloaded-event.json>
```

The ingestion command runs from the project root, resolves the canonical exact
question version, validates the review-event schema and reviewer, rejects
fixture content, rejects stale hashes, and refuses to overwrite an existing
event ID.

## Verify

```text
npm run build
node --test tests/rendered-html.test.mjs
npm run lint
```

Full Python integrity tests run from the project root with
`python -m unittest discover -s tests -v`.
