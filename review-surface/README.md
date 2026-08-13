# FAR Bank internal review surface

Local P1.3 evidence surface for inspecting one exact FAR question version and
composing append-only review-event proposals.

This directory is not a learner-facing site and is not approved as the G3
workflow. The current record is a synthetic schema fixture, contributes zero
coverage, and cannot become learner-ready.

## Rebuild the evidence input

From the `far-bank/` project root:

```text
python scripts/build_review_surface_data.py
```

The generated `app/review-data.json` binds the question version and content
hash and includes its source-file manifest. Do not hand-edit it.

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
