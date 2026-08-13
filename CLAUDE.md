# far-bank

## Purpose

First Goal Method child of `cpa-learning`: establish a versioned, auditable,
human-approved bank of original four-option FAR multiple-choice questions,
mapped granularly to the complete current CPA Exam Blueprint. This project
builds the content foundation and its internal review machinery; it does not
build the learner-facing website.

## State

| Field | Value |
| --- | --- |
| Status | LIVE — G1 and G2 passed; P2 contract-enforcement phase active |
| Last session | James ratified the dated G2 production-contract amendment |
| Next action | P2.0: encode and red-calibrate the ratified production controls |

`state.md` is the authoritative fine-grained resume snapshot. This table is
only a signpost.

## How to run

From `far-bank/`:

- Re-extract: `python scripts/extract_far_taxonomy.py`
- Re-render: `python scripts/render_taxonomy.py`
- Verify everything: `python scripts/verify_taxonomy.py data/far-taxonomy.json`
- Run red calibrations: `python -m unittest discover -s tests -v`

## Data freshness

The source-of-truth Blueprint is the preserved AICPA Uniform CPA Examination
Blueprint effective January 1, 2026, SHA-256
`0fca69b073bb0ed46b06ca51c2e1dfaec434346e628f6996fa34b19c2bc02680`.
Its identity and retrieval record are in `sources/aicpa/2026-01/`.

## Gotchas

- GitHub CLI authentication is persisted in the Windows keyring. Inside the
  restricted sandbox, blocked API access can make `gh auth status` falsely
  report that the keyring token is invalid (often alongside a
  `127.0.0.1:9` proxy failure). Before asking James to authenticate again,
  rerun `gh auth status -h github.com` and `gh api user` with normal network
  permission. Do not infer credential loss from the sandboxed check alone.
- `goal.md` was ratified by James on 2026-08-13. Contract changes require an
  explicit dated amendment.
- The project baseline is intentionally zero. No question, taxonomy row,
  generator, oracle, or approval from an older CPA project is inherited.
- “Full Blueprint” means the complete FAR hierarchy is in scope. It does not
  mean one token question per representative task proves meaningful coverage.
- Production coverage floors, variety/anti-cloning rules, difficulty rubrics,
  prose controls, correctness routes, and architecture are ratified in the
  dated 2026-08-13 G2 amendment in `goal.md`.
- The embedded PDF title is stale (2022). The official AICPA page, visible
  cover, effective date, and preserved hash control; see the discrepancy log.

## Rules for agents

- Follow `goal.md` once ratified; before ratification, modify only bootstrap
  artifacts in response to red-pen rulings.
- `goal.md` is the contract, `plan.md` is agent-owned strategy, `state.md` is
  a rewritten cache, and `worklog.md` is append-only history.
- Generated content is regenerated, never hand-edited.
- No question becomes learner-ready through automation alone.
- A content change invalidates the question's prior human approval.
- Scope temptations are logged where written and not built.
- At each wind-down: append the worklog, rewrite state from scratch, update
  this signpost, run the kill-sweep, and leave a receipt in the worklog.
