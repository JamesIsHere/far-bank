# ADR 0004 — P2 independent correctness-route layer

Status: IMPLEMENTED FOR P2.1  
Date: 2026-08-13  
Owner: P2.1 under the ratified `goal.md` amendment

## Decision

Expanded correctness routes use a versioned companion record governed by
`schema/correctness-route.schema.json`. This avoids rewriting the approved P1
question versions while providing a production-evidence shape that must bind a
future exact question ID, version ID, and content SHA-256. Every route also
binds `far-g2-production-contract.v001`.

Calibration records are explicitly `calibration_fixture` and cannot carry an
exact production subject. They identify producer and verifier components,
state that no deciding function is shared, transport structured inputs and
expected output, and preserve a route-specific independence limit.

## Admitted executable routes

`scripts/verify_correctness_routes.py` independently evaluates:

1. percentage formulas;
2. ratios;
3. present-value cash-flow schedules;
4. effective-interest expense and premium/discount amortization;
5. per-share numerators and denominators;
6. date and whole-period schedules with explicit boundary conventions;
7. ordered conditional rule tables and classification results;
8. journal-entry balance and required account direction;
9. linked, ordered roll-forward nodes; and
10. nonnumeric assertion cases loaded from a separately authored reference
    artifact.

Decimal arithmetic and explicit rounding avoid binary-float answer decisions.
Routes reject missing inputs, zero denominators, inconsistent units, invalid
dates or boundaries, forward roll-forward references, unbalanced or
misdirected journal entries, and unresolved assertion cases.

## Independent assertion artifact

Nonnumeric calibration cases live in
`fixtures/correctness-routes/reference/classification-assertions.json` under
`schema/assertion-reference-fixture.schema.json`. The producer, route verifier,
and reference-fixture component IDs must all differ. The evaluator loads and
validates the separate artifact and binds its component ID before using a case.

This is structural independence inside a synthetic fixture world. The cases
are not accounting authority or correctness evidence for a real item.

## Red calibration and boundary

Each admitted route has one clean fixture and one purpose-built known-bad
fixture under `fixtures/correctness-routes/`. The deterministic receipt is
`reports/p2-correctness-route-calibration.json`; all 10/10 routes reject their
known-bad case with zero waivers.

The fixtures do not create questions, review events, learner readiness, or
coverage. A production family must bind one of these executable route shapes
to an exact production version and independently support the accounting inputs
and rule choice. The route result alone cannot grant approval.
