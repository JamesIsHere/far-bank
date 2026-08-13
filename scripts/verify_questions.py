from __future__ import annotations

import argparse
import copy
import json
import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Callable

from validate_p1_records import (
    PROJECT_ROOT,
    canonical_content_sha256,
    load_json,
    schema_issues,
    validate_exact_binding,
    validate_question_contract,
)


CHECKER_ID = "far-p1-question-verifier"
CHECKER_VERSION = "1.0.0"
REQUIRED_CHECK_SET_ID = "far-p1-sample-candidate-checks.v001"


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    category: str
    passed: bool
    detail: str
    evidence: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "category": self.category,
            "outcome": "pass" if self.passed else "fail",
            "detail": self.detail,
            "evidence": list(self.evidence),
        }


@dataclass
class QuestionBundle:
    identity: dict[str, Any]
    reference: dict[str, Any]
    rule: dict[str, Any]
    question: dict[str, Any]
    verification: dict[str, Any]
    review: dict[str, Any] | None

    def clone(self) -> "QuestionBundle":
        return copy.deepcopy(self)


@dataclass(frozen=True)
class DerivedReadiness:
    learner_ready: bool
    reasons: tuple[str, ...]


def load_fixture_bundle(project_root: Path = PROJECT_ROOT) -> QuestionBundle:
    fixture_dir = project_root / "fixtures" / "questions"
    return QuestionBundle(
        identity=load_json(fixture_dir / "valid-question-identity.json"),
        reference=load_json(fixture_dir / "valid-reference-version.json"),
        rule=load_json(fixture_dir / "valid-rule-version.json"),
        question=load_json(fixture_dir / "valid-question-version.json"),
        verification=load_json(fixture_dir / "valid-verification-event.json"),
        review=load_json(fixture_dir / "valid-review-event-approve.json"),
    )


def _pass(check_id: str, category: str, detail: str, *evidence: str) -> CheckResult:
    return CheckResult(check_id, category, True, detail, tuple(evidence))


def _fail(check_id: str, category: str, detail: str, *evidence: str) -> CheckResult:
    return CheckResult(check_id, category, False, detail, tuple(evidence))


def check_schema_contract(bundle: QuestionBundle, project_root: Path = PROJECT_ROOT) -> CheckResult:
    schema_dir = project_root / "schema"
    records = {
        "identity": (bundle.identity, "question-identity.schema.json"),
        "reference": (bundle.reference, "reference-version.schema.json"),
        "rule": (bundle.rule, "rule-version.schema.json"),
        "question": (bundle.question, "question-version.schema.json"),
        "verification": (bundle.verification, "verification-event.schema.json"),
    }
    if bundle.review is not None:
        records["review"] = (bundle.review, "review-event.schema.json")
    details: list[str] = []
    for record_name, (record, schema_name) in records.items():
        issues = schema_issues(load_json(schema_dir / schema_name), record, f"{record_name.upper()}_SCHEMA")
        details.extend(f"{issue.contract_id}: {issue.detail}" for issue in issues)

    if bundle.identity.get("question_id") != bundle.question.get("question_id"):
        details.append("QUESTION_IDENTITY: question version is detached from its stable identity")
    if bundle.rule.get("content_sha256") != canonical_content_sha256(bundle.rule.get("content", {})):
        details.append("RULE_CONTENT_HASH: canonical rule content does not match its envelope")

    if not any(detail.startswith("QUESTION_SCHEMA") for detail in details):
        taxonomy = load_json(project_root / "data" / "far-taxonomy.json")
        issues = validate_question_contract(
            bundle.question,
            load_json(schema_dir / "question-version.schema.json"),
            taxonomy,
            {bundle.rule["rule_version_id"]: bundle.rule},
        )
        details.extend(f"{issue.contract_id}: {issue.detail}" for issue in issues)

    if details:
        return _fail("SCHEMA_CONTRACT", "SCHEMA", "; ".join(details[:8]), *details)
    return _pass(
        "SCHEMA_CONTRACT",
        "SCHEMA",
        "Closed record shapes and cross-record structural contracts pass.",
        "Question content hash, version identity, Blueprint path, option identities, and rule/fact references resolve.",
    )


def _fact_number_map(question: dict[str, Any]) -> dict[str, Decimal]:
    result: dict[str, Decimal] = {}
    for fact in question["content"]["facts"]:
        value = fact["structured_value"]
        if value["value_type"] == "number":
            result[fact["fact_id"]] = Decimal(str(value["value"]))
    return result


def evaluate_linear_combination(spec: dict[str, Any], fact_values: dict[str, Decimal]) -> Decimal:
    total = Decimal(str(spec["constant"]))
    for term in spec["terms"]:
        fact_id = term["fact_id"]
        if fact_id not in fact_values:
            raise KeyError(f"non-numeric or missing fact {fact_id}")
        total += fact_values[fact_id] * Decimal(str(term["coefficient"]))

    rounding = spec["rounding"]
    if rounding["mode"] == "none":
        return total
    quantum = Decimal(1).scaleb(-rounding["decimal_places"])
    modes = {
        "half_even": ROUND_HALF_EVEN,
        "half_up": ROUND_HALF_UP,
        "truncate": ROUND_DOWN,
    }
    return total.quantize(quantum, rounding=modes[rounding["mode"]])


def check_recompute_independent(bundle: QuestionBundle, _: Path = PROJECT_ROOT) -> CheckResult:
    check_id = "RECOMPUTE_INDEPENDENT"
    category = "RECOMPUTE"
    evidence = bundle.question["content"]["correctness_evidence"]
    if evidence["producer_component_id"] == evidence["verifier_component_id"]:
        return _fail(check_id, category, "Producer and verifier component identities are not independent.")
    if evidence["shared_deciding_function"] is not False:
        return _fail(check_id, category, "The evidence route does not explicitly exclude shared deciding logic.")
    if evidence["route"]["route_type"] != "linear_combination":
        return _fail(check_id, category, "P1 verifier has no independently executable route for this fixture type.")

    try:
        actual = evaluate_linear_combination(
            evidence["route"]["linear_combination"],
            _fact_number_map(bundle.question),
        )
    except (KeyError, ArithmeticError) as exc:
        return _fail(check_id, category, f"Independent recomputation could not execute: {exc}")

    keyed = next(option for option in bundle.question["content"]["options"] if option["is_keyed"])
    keyed_value = keyed["structured_value"]
    if keyed_value["value_type"] != "number":
        return _fail(check_id, category, "Linear recomputation cannot bind a nonnumeric keyed option.")
    expected = Decimal(str(keyed_value["value"]))
    output_unit = evidence["route"]["linear_combination"]["output_unit"]
    if keyed_value.get("unit") != output_unit:
        return _fail(check_id, category, "Recomputed and keyed units differ.")
    if actual != expected:
        return _fail(check_id, category, f"Independent result {actual} does not equal keyed structured value {expected}.")
    return _pass(
        check_id,
        category,
        f"Independent generic linear-combination route recomputed {actual} {output_unit}.",
        f"producer_component_id={evidence['producer_component_id']}",
        f"verifier_component_id={evidence['verifier_component_id']}",
        f"independence_limit={evidence['independence_limit']}",
    )


def check_rule_trace_current(bundle: QuestionBundle, _: Path = PROJECT_ROOT) -> CheckResult:
    check_id = "RULE_TRACE_CURRENT"
    category = "RULE_TRACE"
    content = bundle.question["content"]
    rule = bundle.rule
    reference = bundle.reference
    problems: list[str] = []

    if rule["content"]["currency"]["assessment"] != "current":
        problems.append("rule version is not assessed current")
    if reference["currency"]["assessment"] != "current":
        problems.append("reference version is not assessed current")
    purpose = content["authorship"]["purpose"]
    if purpose == "sample_candidate" and reference["record_purpose"] != "admitted_evidence":
        problems.append("sample candidate does not resolve to admitted evidence")
    if purpose == "schema_fixture" and reference["record_purpose"] != "schema_fixture":
        problems.append("schema fixture crossed into a non-fixture reference world")

    assertions = {item["assertion_id"] for item in rule["content"]["assertions"]}
    controlling = [citation for citation in rule["content"]["source_citations"] if citation["role"] == "controlling"]
    if not controlling:
        problems.append("rule has no controlling citation")
    for citation in controlling:
        if citation["reference_version_id"] != reference["reference_version_id"]:
            problems.append(f"unresolved controlling reference {citation['reference_version_id']}")
        if not set(citation["supports_assertion_ids"]).issubset(assertions):
            problems.append("controlling citation names an unknown assertion")
    for trace in content["rule_trace"]:
        if trace["rule_version_id"] != rule["rule_version_id"]:
            problems.append(f"unresolved rule version {trace['rule_version_id']}")
        if not set(trace["assertion_ids"]).issubset(assertions):
            problems.append("question trace names an unknown rule assertion")

    if problems:
        return _fail(check_id, category, "; ".join(problems), *problems)
    return _pass(
        check_id,
        category,
        "Every applied assertion resolves through a current exact rule and controlling reference version.",
        f"rule_version_id={rule['rule_version_id']}",
        f"reference_version_id={reference['reference_version_id']}",
        "Fixture-world currency cannot be carried into a sample-candidate claim.",
    )


def check_distractor_models(bundle: QuestionBundle, _: Path = PROJECT_ROOT) -> CheckResult:
    check_id = "DISTRACTOR_MODELS"
    category = "DISTRACTORS"
    fact_values = _fact_number_map(bundle.question)
    options = bundle.question["content"]["options"]
    values: list[tuple[str, Any]] = []
    problems: list[str] = []
    for option in options:
        structured = option["structured_value"]
        values.append((structured["value_type"], structured["value"]))
        if option["is_keyed"]:
            continue
        model = option["error_model"]
        route = model["reproduction"]
        if route["route_type"] != "linear_combination":
            problems.append(f"option {option['option_id']} lacks an executable P1 reproduction route")
            continue
        try:
            reproduced = evaluate_linear_combination(route["linear_combination"], fact_values)
        except (KeyError, ArithmeticError) as exc:
            problems.append(f"option {option['option_id']} reproduction failed: {exc}")
            continue
        option_value = Decimal(str(structured["value"]))
        if reproduced != option_value:
            problems.append(f"option {option['option_id']} model produced {reproduced}, not {option_value}")
        if route["linear_combination"]["output_unit"] != structured.get("unit"):
            problems.append(f"option {option['option_id']} model unit differs from option unit")
    if len(set(values)) != 4:
        problems.append("key and distractor structured values are not distinct")
    if problems:
        return _fail(check_id, category, "; ".join(problems), *problems)
    return _pass(
        check_id,
        category,
        "All three named distractor error models reproduce their distinct option values.",
        *[f"{option['option_id']}={option['error_model']['error_model_id']}" for option in options if not option["is_keyed"]],
    )


def _numeric_tokens(text: str) -> set[Decimal]:
    tokens: set[Decimal] = set()
    for match in re.finditer(r"(?<![A-Za-z])\$?([0-9][0-9,]*(?:\.[0-9]+)?)", text):
        tokens.add(Decimal(match.group(1).replace(",", "")))
    return tokens


def check_language_fairness(bundle: QuestionBundle, _: Path = PROJECT_ROOT) -> CheckResult:
    check_id = "LANGUAGE_FAIRNESS"
    category = "LANGUAGE"
    content = bundle.question["content"]
    stem = content["stem"].strip()
    lower = stem.casefold()
    problems: list[str] = []
    double_negative_patterns = (
        r"\bnot\b[^?.]{0,60}\bnot\b",
        r"\bnot\s+incorrect\b",
        r"\bnot\s+false\b",
        r"\bexcept\b[^?.]{0,60}\bnot\b",
    )
    if any(re.search(pattern, lower) for pattern in double_negative_patterns):
        problems.append("stem contains a forbidden or gratuitous double-negative pattern")
    if not stem.endswith("?"):
        problems.append("stem does not end as a direct question")
    keyed = next(option for option in content["options"] if option["is_keyed"])
    if keyed["text"].casefold() in lower:
        problems.append("keyed answer text leaks into the stem")

    stem_numbers = _numeric_tokens(stem)
    fact_numbers = {
        Decimal(str(fact["structured_value"]["value"]))
        for fact in content["facts"]
        if fact["structured_value"]["value_type"] == "number"
    }
    if stem_numbers != fact_numbers:
        problems.append(f"stem/fact numeric mismatch: stem={sorted(stem_numbers)} facts={sorted(fact_numbers)}")
    if re.search(r"\bassum(?:e|es|ed|ing)\b", lower) and not content["assumptions"]:
        problems.append("stem asks for an assumption but no structured assumption is recorded")
    if not content["solution"]["end_ask"].strip():
        problems.append("plain-language end ask is empty")

    if problems:
        return _fail(check_id, category, "; ".join(problems), *problems)
    return _pass(
        check_id,
        category,
        "No targeted ambiguity, leakage, orphan-number, unsupported-assumption, or end-ask defect was found.",
        f"structured_numeric_fact_count={len(fact_numbers)}",
        f"structured_assumption_count={len(content['assumptions'])}",
    )


def check_originality_boundary(bundle: QuestionBundle, _: Path = PROJECT_ROOT) -> CheckResult:
    check_id = "ORIGINALITY_BOUNDARY"
    category = "ORIGINALITY"
    content = bundle.question["content"]
    boundary = content["originality_boundary"]
    combined = " ".join(boundary["methods"] + [boundary["claim_limit"]]).casefold()
    forbidden = (
        "globally unique",
        "global uniqueness",
        "legal clearance",
        "guaranteed non-infringement",
        "guaranteed originality",
    )
    found = [phrase for phrase in forbidden if phrase in combined]
    problems: list[str] = []
    if found:
        problems.append(f"unsupported originality claim: {', '.join(found)}")
    if content["authorship"]["purpose"] == "sample_candidate":
        methods = " ".join(boundary["methods"]).casefold()
        if "within-bank" not in methods or not boundary["compared_corpus_ids"]:
            problems.append("sample candidate lacks a named within-bank comparison boundary")
    if problems:
        return _fail(check_id, category, "; ".join(problems), *problems)
    return _pass(
        check_id,
        category,
        "Originality language stays within the exact named comparison boundary.",
        f"compared_corpus_ids={boundary['compared_corpus_ids']}",
        f"claim_limit={boundary['claim_limit']}",
    )


def check_approval_integrity(bundle: QuestionBundle, project_root: Path = PROJECT_ROOT) -> CheckResult:
    check_id = "APPROVAL_INTEGRITY"
    category = "APPROVAL_INTEGRITY"
    problems: list[str] = []
    if bundle.review is not None:
        review_schema = load_json(project_root / "schema" / "review-event.schema.json")
        problems.extend(issue.detail for issue in schema_issues(review_schema, bundle.review, "REVIEW_SCHEMA"))
        problems.extend(issue.detail for issue in validate_exact_binding(bundle.review, bundle.question))
    problems.extend(issue.detail for issue in validate_exact_binding(bundle.verification, bundle.question))
    if bundle.question["content_sha256"] != canonical_content_sha256(bundle.question["content"]):
        problems.append("question content changed after its exact-version hash was recorded")
    if bundle.review is not None and bundle.review["action"] == "approve" and bundle.review["actor"]["actor_type"] != "human":
        problems.append("approve action is not human-authored")
    if problems:
        return _fail(check_id, category, "; ".join(problems[:8]), *problems)
    return _pass(
        check_id,
        category,
        "Existing review evidence, if any, and verification evidence bind the exact immutable content hash.",
        f"version_id={bundle.question['version_id']}",
        f"content_sha256={bundle.question['content_sha256']}",
        "An absent review event is valid candidate state and grants no approval.",
    )


def _measurement_map(question: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for dimension in question["content"]["difficulty_profile"]:
        for measure in dimension["observable_measurements"]:
            result[measure["measure_id"]] = measure["value"]
    return result


def check_variety_evidence(bundle: QuestionBundle, _: Path = PROJECT_ROOT) -> CheckResult:
    check_id = "VARIETY_EVIDENCE"
    category = "VARIETY"
    content = bundle.question["content"]
    problems: list[str] = []
    for mechanic in content["challenge_mechanics"]:
        if not mechanic["observable_evidence"] or any(not item.strip() for item in mechanic["observable_evidence"]):
            problems.append(f"challenge mechanic {mechanic['tag']} lacks observable evidence")

    measurements = _measurement_map(bundle.question)
    expected = {
        "rule_count": len(content["rule_trace"]),
        "dependent_step_count": len(content["solution"]["steps"]),
        "irrelevant_fact_count": sum(fact["relevance"] == "irrelevant" for fact in content["facts"]),
        "plausible_error_model_count": sum(not option["is_keyed"] for option in content["options"]),
    }
    correctness = content["correctness_evidence"]["route"]
    if correctness["route_type"] == "linear_combination":
        expected["arithmetic_operation_count"] = max(0, len(correctness["linear_combination"]["terms"]) - 1)
    for measure_id, expected_value in expected.items():
        if measurements.get(measure_id) != expected_value:
            problems.append(f"{measure_id} records {measurements.get(measure_id)!r}, expected observable value {expected_value}")
    if any(dimension["rubric_status"] != "proposed_for_g2" for dimension in content["difficulty_profile"]):
        problems.append("P1 fixture claims a ratified difficulty rubric before G2")
    if problems:
        return _fail(check_id, category, "; ".join(problems), *problems)
    return _pass(
        check_id,
        category,
        "Challenge and provisional difficulty records carry checkable observable evidence.",
        *[f"{key}={value}" for key, value in sorted(expected.items())],
        "No variety distribution or difficulty rubric is treated as ratified.",
    )


CHECKS: tuple[Callable[[QuestionBundle, Path], CheckResult], ...] = (
    check_schema_contract,
    check_recompute_independent,
    check_rule_trace_current,
    check_distractor_models,
    check_language_fairness,
    check_originality_boundary,
    check_approval_integrity,
    check_variety_evidence,
)


def run_checks(bundle: QuestionBundle, project_root: Path = PROJECT_ROOT) -> list[CheckResult]:
    return [check(bundle, project_root) for check in CHECKS]


def result_by_id(results: list[CheckResult], check_id: str) -> CheckResult:
    return next(result for result in results if result.check_id == check_id)


def derive_learner_ready(
    bundle: QuestionBundle,
    results: list[CheckResult],
    required_reviewer_id: str = "james",
) -> DerivedReadiness:
    reasons: list[str] = []
    if bundle.question["content"]["authorship"]["purpose"] == "schema_fixture":
        reasons.append("schema_fixture_not_eligible")
    if bundle.reference["record_purpose"] != "admitted_evidence":
        reasons.append("reference_not_admitted")
    if bundle.reference["currency"]["assessment"] != "current":
        reasons.append("reference_not_current")
    if bundle.rule["content"]["currency"]["assessment"] != "current":
        reasons.append("rule_not_current")

    failed = [result.check_id for result in results if not result.passed]
    if failed:
        reasons.append(f"failed_checks:{','.join(failed)}")

    expected_check_ids = {result.check_id for result in results}
    event_passes = {
        check["check_id"]
        for check in bundle.verification["checks"]
        if check["outcome"] == "pass"
    }
    if bundle.verification["required_check_set_id"] != REQUIRED_CHECK_SET_ID:
        reasons.append("verification_check_set_not_current")
    if not expected_check_ids.issubset(event_passes):
        reasons.append("verification_event_incomplete")

    binding_problems = validate_exact_binding(bundle.verification, bundle.question)
    if bundle.review is not None:
        binding_problems += validate_exact_binding(bundle.review, bundle.question)
    if binding_problems:
        reasons.append("exact_version_binding_invalid")
    if bundle.question["content_sha256"] != canonical_content_sha256(bundle.question["content"]):
        reasons.append("content_hash_invalid")
    if bundle.review is None or bundle.review["action"] != "approve":
        reasons.append("latest_decisive_review_not_approve")
    if bundle.review is None or bundle.review["actor"]["actor_type"] != "human":
        reasons.append("approval_not_human")
    if bundle.review is None or bundle.review["actor"]["actor_id"] != required_reviewer_id:
        reasons.append("required_reviewer_missing")
    return DerivedReadiness(not reasons, tuple(reasons))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the calibrated P1 FAR question checks against the fixture bundle.")
    parser.parse_args()
    results = run_checks(load_fixture_bundle())
    for result in results:
        print(f"{'PASS' if result.passed else 'FAIL'} {result.check_id}: {result.detail}")
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
