# FAR Question Bank

An auditable, human-approved bank of original four-option FAR multiple-choice
questions mapped to the complete current CPA Exam Blueprint.

This repository contains the content foundation and internal review machinery.
It does not contain the learner-facing CPA application.

## Current status

Gate G2 is complete. The six-item cross-area sample and its exact-version
approval history are preserved, and Phase P2.0 (production-contract
enforcement) is active. No production-bank questions exist yet.

See [`state.md`](state.md) for the cold-resume snapshot, [`goal.md`](goal.md)
for the ratified contract, and [`plan.md`](plan.md) for the active work queue.

## Verification

From the repository root:

```powershell
python scripts/validate_p1_records.py
python scripts/verify_taxonomy.py data/far-taxonomy.json
python scripts/calibrate_question_verifier.py
python scripts/verify_p1_sample.py
python -m unittest discover -s tests -p "test_*.py" -v
python -m compileall -q scripts tests
```

From `review-surface/`:

```powershell
npm ci
npm run lint
npm test
```

## Data boundary

Immutable JSON question versions and append-only JSON events are canonical.
SQLite is a disposable local projection. Automated checks cannot grant human
approval, and a content change invalidates approval for the prior exact
version.
