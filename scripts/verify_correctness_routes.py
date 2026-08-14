from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Callable

from validate_p1_records import PROJECT_ROOT, canonical_content_sha256, load_json, schema_issues


CHECKER_ID = "far-independent-correctness-route-verifier"
CHECKER_VERSION = "1.0.0"
REQUIRED_CHECK_SET_ID = "far-p2-independent-routes.v001"
ROUTE_TYPES = (
    "percentage",
    "ratio",
    "present_value",
    "effective_interest",
    "per_share",
    "date_period_schedule",
    "conditional_rule_table",
    "journal_entry",
    "linked_roll_forward",
    "independent_assertion_fixture",
)


@dataclass(frozen=True)
class EvaluatedOutput:
    value: Any
    unit: str | None = None


@dataclass(frozen=True)
class RouteCheckResult:
    check_id: str
    route_type: str
    passed: bool
    detail: str
    evidence: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "route_type": self.route_type,
            "outcome": "pass" if self.passed else "fail",
            "detail": self.detail,
            "evidence": list(self.evidence),
        }


def _decimal(value: Any) -> Decimal:
    if isinstance(value, bool):
        raise ValueError("boolean is not a numeric input")
    return Decimal(str(value))


def _inputs(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result = {item["input_id"]: item for item in record["inputs"]}
    if len(result) != len(record["inputs"]):
        raise ValueError("input IDs are not unique")
    return result


def _numeric(inputs: dict[str, dict[str, Any]], input_id: str) -> Decimal:
    item = inputs.get(input_id)
    if item is None:
        raise ValueError(f"unknown input {input_id}")
    if item["value_type"] != "number":
        raise ValueError(f"{input_id} is not numeric")
    return _decimal(item["value"])


def _value(inputs: dict[str, dict[str, Any]], input_id: str, value_type: str | None = None) -> Any:
    item = inputs.get(input_id)
    if item is None:
        raise ValueError(f"unknown input {input_id}")
    if value_type is not None and item["value_type"] != value_type:
        raise ValueError(f"{input_id} is not {value_type}")
    return item["value"]


def _same_unit(inputs: dict[str, dict[str, Any]], input_ids: list[str]) -> str | None:
    units = {inputs[input_id].get("unit") for input_id in input_ids}
    if len(units) != 1:
        raise ValueError(f"input units differ: {sorted(str(unit) for unit in units)}")
    return next(iter(units))


def _require_keys(spec: dict[str, Any], required: set[str], optional: set[str] | None = None) -> None:
    optional = optional or set()
    missing = required - set(spec)
    extra = set(spec) - required - optional
    if missing or extra:
        raise ValueError(f"specification keys missing={sorted(missing)} extra={sorted(extra)}")


def evaluate_percentage(record: dict[str, Any]) -> EvaluatedOutput:
    spec = record["specification"]
    _require_keys(spec, {"numerator_input_id", "denominator_input_id", "scale"})
    inputs = _inputs(record)
    _same_unit(inputs, [spec["numerator_input_id"], spec["denominator_input_id"]])
    denominator = _numeric(inputs, spec["denominator_input_id"])
    if denominator == 0:
        raise ValueError("percentage denominator is zero")
    result = _numeric(inputs, spec["numerator_input_id"]) / denominator * _decimal(spec["scale"])
    return EvaluatedOutput(result, record["expected_output"].get("unit"))


def evaluate_ratio(record: dict[str, Any]) -> EvaluatedOutput:
    spec = record["specification"]
    _require_keys(spec, {"numerator_input_id", "denominator_input_id"})
    inputs = _inputs(record)
    _same_unit(inputs, [spec["numerator_input_id"], spec["denominator_input_id"]])
    denominator = _numeric(inputs, spec["denominator_input_id"])
    if denominator == 0:
        raise ValueError("ratio denominator is zero")
    return EvaluatedOutput(_numeric(inputs, spec["numerator_input_id"]) / denominator, record["expected_output"].get("unit"))


def evaluate_present_value(record: dict[str, Any]) -> EvaluatedOutput:
    spec = record["specification"]
    _require_keys(spec, {"rate_input_id", "cash_flows"})
    inputs = _inputs(record)
    rate = _numeric(inputs, spec["rate_input_id"])
    if rate <= -1:
        raise ValueError("periodic discount rate must be greater than -1")
    if not isinstance(spec["cash_flows"], list) or not spec["cash_flows"]:
        raise ValueError("present-value route requires cash flows")
    amount_ids: list[str] = []
    total = Decimal(0)
    periods_seen: set[int] = set()
    for cash_flow in spec["cash_flows"]:
        if set(cash_flow) != {"period", "amount_input_id"}:
            raise ValueError("cash-flow shape is invalid")
        period = cash_flow["period"]
        if not isinstance(period, int) or period < 0 or period in periods_seen:
            raise ValueError("cash-flow periods must be unique nonnegative integers")
        periods_seen.add(period)
        amount_ids.append(cash_flow["amount_input_id"])
        total += _numeric(inputs, cash_flow["amount_input_id"]) / ((Decimal(1) + rate) ** period)
    unit = _same_unit(inputs, amount_ids)
    return EvaluatedOutput(total, unit)


def evaluate_effective_interest(record: dict[str, Any]) -> EvaluatedOutput:
    spec = record["specification"]
    _require_keys(spec, {"carrying_amount_input_id", "effective_rate_input_id", "cash_interest_input_id", "output"})
    if spec["output"] not in {"interest_expense", "discount_amortization", "premium_amortization"}:
        raise ValueError("unsupported effective-interest output")
    inputs = _inputs(record)
    carrying = _numeric(inputs, spec["carrying_amount_input_id"])
    rate = _numeric(inputs, spec["effective_rate_input_id"])
    cash = _numeric(inputs, spec["cash_interest_input_id"])
    unit = _same_unit(inputs, [spec["carrying_amount_input_id"], spec["cash_interest_input_id"]])
    expense = carrying * rate
    value = expense if spec["output"] == "interest_expense" else expense - cash if spec["output"] == "discount_amortization" else cash - expense
    return EvaluatedOutput(value, unit)


def evaluate_per_share(record: dict[str, Any]) -> EvaluatedOutput:
    spec = record["specification"]
    _require_keys(spec, {"numerator_terms", "denominator_input_id"})
    inputs = _inputs(record)
    denominator = _numeric(inputs, spec["denominator_input_id"])
    if denominator == 0:
        raise ValueError("per-share denominator is zero")
    numerator = Decimal(0)
    term_ids: list[str] = []
    for term in spec["numerator_terms"]:
        if set(term) != {"input_id", "coefficient"}:
            raise ValueError("per-share numerator term shape is invalid")
        term_ids.append(term["input_id"])
        numerator += _numeric(inputs, term["input_id"]) * _decimal(term["coefficient"])
    _same_unit(inputs, term_ids)
    return EvaluatedOutput(numerator / denominator, record["expected_output"].get("unit"))


def evaluate_date_period_schedule(record: dict[str, Any]) -> EvaluatedOutput:
    spec = record["specification"]
    _require_keys(spec, {"start_input_id", "end_input_id", "unit", "boundary_rule"})
    if spec["unit"] not in {"days", "whole_months"}:
        raise ValueError("unsupported schedule unit")
    if spec["boundary_rule"] not in {"elapsed", "inclusive_both", "exclusive_both"}:
        raise ValueError("unsupported boundary rule")
    inputs = _inputs(record)
    start = date.fromisoformat(_value(inputs, spec["start_input_id"], "date"))
    end = date.fromisoformat(_value(inputs, spec["end_input_id"], "date"))
    if end < start:
        raise ValueError("schedule end precedes start")
    if spec["unit"] == "days":
        value = (end - start).days
        if spec["boundary_rule"] == "inclusive_both":
            value += 1
        elif spec["boundary_rule"] == "exclusive_both":
            value = max(0, value - 1)
    else:
        value = (end.year - start.year) * 12 + end.month - start.month
        if end.day < start.day:
            value -= 1
        if spec["boundary_rule"] != "elapsed":
            raise ValueError("month schedules support elapsed boundary only")
    return EvaluatedOutput(Decimal(value), spec["unit"])


def _condition_matches(inputs: dict[str, dict[str, Any]], condition: dict[str, Any]) -> bool:
    if set(condition) != {"input_id", "operator", "value"}:
        raise ValueError("condition shape is invalid")
    actual = _value(inputs, condition["input_id"])
    expected = condition["value"]
    operator = condition["operator"]
    operations: dict[str, Callable[[], bool]] = {
        "eq": lambda: actual == expected,
        "ne": lambda: actual != expected,
        "gt": lambda: actual > expected,
        "gte": lambda: actual >= expected,
        "lt": lambda: actual < expected,
        "lte": lambda: actual <= expected,
        "in": lambda: actual in expected,
    }
    if operator not in operations:
        raise ValueError(f"unsupported condition operator {operator}")
    return operations[operator]()


def evaluate_conditional_rule_table(record: dict[str, Any]) -> EvaluatedOutput:
    spec = record["specification"]
    _require_keys(spec, {"rows", "default_result"})
    inputs = _inputs(record)
    if not isinstance(spec["rows"], list) or not spec["rows"]:
        raise ValueError("conditional table has no rows")
    for row in spec["rows"]:
        if set(row) != {"conditions", "result"} or not row["conditions"]:
            raise ValueError("conditional row shape is invalid")
        if all(_condition_matches(inputs, condition) for condition in row["conditions"]):
            return EvaluatedOutput(row["result"])
    return EvaluatedOutput(spec["default_result"])


def evaluate_journal_entry(record: dict[str, Any]) -> EvaluatedOutput:
    spec = record["specification"]
    _require_keys(spec, {"lines", "required_account_directions"})
    inputs = _inputs(record)
    debit = Decimal(0)
    credit = Decimal(0)
    observed: dict[str, str] = {}
    amount_ids: list[str] = []
    for line in spec["lines"]:
        if set(line) != {"account_id", "direction", "amount_input_id", "coefficient"}:
            raise ValueError("journal line shape is invalid")
        if line["direction"] not in {"debit", "credit"} or line["account_id"] in observed:
            raise ValueError("journal direction or account identity is invalid")
        amount_ids.append(line["amount_input_id"])
        amount = _numeric(inputs, line["amount_input_id"]) * _decimal(line["coefficient"])
        if amount < 0:
            raise ValueError("journal line amount is negative")
        observed[line["account_id"]] = line["direction"]
        if line["direction"] == "debit":
            debit += amount
        else:
            credit += amount
    _same_unit(inputs, amount_ids)
    directions_match = observed == spec["required_account_directions"]
    return EvaluatedOutput(debit == credit and directions_match)


def evaluate_linked_roll_forward(record: dict[str, Any]) -> EvaluatedOutput:
    spec = record["specification"]
    _require_keys(spec, {"nodes", "output_node_id", "output_unit"})
    inputs = _inputs(record)
    nodes: dict[str, Decimal] = {}
    input_ids_used: list[str] = []
    for node in spec["nodes"]:
        if set(node) != {"node_id", "terms", "constant"} or node["node_id"] in nodes:
            raise ValueError("roll-forward node shape or identity is invalid")
        value = _decimal(node["constant"])
        for term in node["terms"]:
            if set(term) != {"ref_type", "ref_id", "coefficient"} or term["ref_type"] not in {"input", "node"}:
                raise ValueError("roll-forward term shape is invalid")
            source = _numeric(inputs, term["ref_id"]) if term["ref_type"] == "input" else nodes.get(term["ref_id"])
            if term["ref_type"] == "input":
                input_ids_used.append(term["ref_id"])
            if source is None:
                raise ValueError(f"roll-forward node {term['ref_id']} is unresolved or forward-referenced")
            value += source * _decimal(term["coefficient"])
        nodes[node["node_id"]] = value
    if spec["output_node_id"] not in nodes:
        raise ValueError("roll-forward output node is absent")
    if _same_unit(inputs, input_ids_used) != spec["output_unit"]:
        raise ValueError("roll-forward input and output units differ")
    return EvaluatedOutput(nodes[spec["output_node_id"]], spec["output_unit"])


def evaluate_independent_assertion_fixture(record: dict[str, Any], project_root: Path = PROJECT_ROOT) -> EvaluatedOutput:
    spec = record["specification"]
    _require_keys(spec, {"case_id_input_id", "reference_fixture_path"})
    inputs = _inputs(record)
    case_id = _value(inputs, spec["case_id_input_id"], "text")
    reference_root = (project_root / "fixtures/correctness-routes/reference").resolve()
    fixture_path = (project_root / spec["reference_fixture_path"]).resolve()
    if fixture_path.parent != reference_root:
        raise ValueError("assertion reference path escapes the admitted fixture directory")
    fixture_record = load_json(fixture_path)
    issues = schema_issues(load_json(project_root / "schema/assertion-reference-fixture.schema.json"), fixture_record, "ASSERTION_REFERENCE_SCHEMA")
    if issues:
        raise ValueError("assertion reference fixture is invalid: " + "; ".join(issue.detail for issue in issues[:3]))
    if fixture_record["authorship"]["component_id"] != record["reference_fixture_component_id"]:
        raise ValueError("assertion reference component binding differs")
    case_ids = [fixture["case_id"] for fixture in fixture_record["cases"]]
    if len(case_ids) != len(set(case_ids)):
        raise ValueError("assertion reference case IDs are not unique")
    for fixture in fixture_record["cases"]:
        if fixture["case_id"] == case_id:
            if not fixture["expected_assertion_ids"] or not fixture["provenance"].strip():
                raise ValueError("assertion fixture lacks expected assertions or provenance")
            return EvaluatedOutput(fixture["expected_assertion_ids"])
    raise ValueError(f"assertion fixture has no reference case {case_id}")


EVALUATORS: dict[str, Callable[[dict[str, Any]], EvaluatedOutput]] = {
    "percentage": evaluate_percentage,
    "ratio": evaluate_ratio,
    "present_value": evaluate_present_value,
    "effective_interest": evaluate_effective_interest,
    "per_share": evaluate_per_share,
    "date_period_schedule": evaluate_date_period_schedule,
    "conditional_rule_table": evaluate_conditional_rule_table,
    "journal_entry": evaluate_journal_entry,
    "linked_roll_forward": evaluate_linked_roll_forward,
}


def _rounded(value: Decimal, expected: dict[str, Any]) -> Decimal:
    rounding = expected.get("rounding", {"mode": "none", "decimal_places": 0})
    if rounding["mode"] == "none":
        return value
    quantum = Decimal(1).scaleb(-rounding["decimal_places"])
    mode = {"half_even": ROUND_HALF_EVEN, "half_up": ROUND_HALF_UP, "truncate": ROUND_DOWN}[rounding["mode"]]
    return value.quantize(quantum, rounding=mode)


def _matches_expected(actual: EvaluatedOutput, expected: dict[str, Any]) -> bool:
    if actual.unit != expected.get("unit"):
        return False
    if expected["value_type"] == "number":
        return isinstance(actual.value, Decimal) and _rounded(actual.value, expected) == _decimal(expected["value"])
    return actual.value == expected["value"]


def load_route_fixtures(project_root: Path = PROJECT_ROOT) -> list[dict[str, Any]]:
    return [load_json(path) for path in sorted((project_root / "fixtures/correctness-routes/clean").glob("*.json"))]


def check_route(record: dict[str, Any], project_root: Path = PROJECT_ROOT) -> RouteCheckResult:
    route_type = record.get("route_type", "unknown")
    check_id = f"ROUTE_{route_type.upper()}"
    problems = [issue.detail for issue in schema_issues(load_json(project_root / "schema/correctness-route.schema.json"), record, "CORRECTNESS_ROUTE_SCHEMA")]
    if problems:
        return RouteCheckResult(check_id, route_type, False, "; ".join(problems[:5]), tuple(problems))
    if record["producer_component_id"] == record["verifier_component_id"]:
        problems.append("producer and verifier components are not independent")
    if record["route_type"] == "independent_assertion_fixture":
        components = {record["producer_component_id"], record["verifier_component_id"], record["reference_fixture_component_id"]}
        if len(components) != 3:
            problems.append("assertion fixture, producer, and verifier components are not independently identified")
    if record["purpose"] == "production_evidence":
        subject = record["subject"]
        if subject["version_id"].split(".v", 1)[0] != subject["question_id"]:
            problems.append("production route subject has a detached version identity")
        question_path = project_root / "data/questions" / subject["question_id"] / "versions" / f"{subject['version_id']}.json"
        if not question_path.exists():
            problems.append(f"production route subject does not resolve: {subject['version_id']}")
        else:
            question = load_json(question_path)
            actual_subject = {key: question[key] for key in ("question_id", "version_id", "content_sha256")}
            if actual_subject != subject:
                problems.append("production route subject differs from the canonical exact version")
            if question["content_sha256"] != canonical_content_sha256(question["content"]):
                problems.append("production route resolves to a question with an invalid content hash")
    if problems:
        return RouteCheckResult(check_id, route_type, False, "; ".join(problems), tuple(problems))
    try:
        actual = evaluate_independent_assertion_fixture(record, project_root) if route_type == "independent_assertion_fixture" else EVALUATORS[route_type](record)
    except (ArithmeticError, KeyError, TypeError, ValueError) as exc:
        return RouteCheckResult(check_id, route_type, False, f"independent route could not execute: {exc}")
    if not _matches_expected(actual, record["expected_output"]):
        return RouteCheckResult(check_id, route_type, False, f"independent output {actual.value!r} {actual.unit or ''} does not match expected {record['expected_output']['value']!r} {record['expected_output'].get('unit', '')}".strip())
    return RouteCheckResult(
        check_id,
        route_type,
        True,
        f"Independent {route_type} route executed and matched its structured expected output.",
        (f"fixture_id={record['fixture_id']}", f"producer={record['producer_component_id']}", f"verifier={record['verifier_component_id']}", f"limit={record['independence_limit']}"),
    )


def run_checks(records: list[dict[str, Any]], project_root: Path = PROJECT_ROOT) -> list[RouteCheckResult]:
    by_type: dict[str, list[dict[str, Any]]] = {route_type: [] for route_type in ROUTE_TYPES}
    for record in records:
        by_type.setdefault(record.get("route_type", "unknown"), []).append(record)
    results: list[RouteCheckResult] = []
    for route_type in ROUTE_TYPES:
        matches = by_type[route_type]
        if len(matches) != 1:
            results.append(RouteCheckResult(f"ROUTE_{route_type.upper()}", route_type, False, f"expected one clean fixture, found {len(matches)}"))
        else:
            results.append(check_route(matches[0], project_root))
    extras = sorted(route_type for route_type, matches in by_type.items() if route_type not in ROUTE_TYPES and matches)
    if extras:
        results.append(RouteCheckResult("ROUTE_CATALOG", "catalog", False, f"unknown route types: {extras}"))
    return results


def main() -> int:
    results = run_checks(load_route_fixtures())
    for result in results:
        print(f"{'PASS' if result.passed else 'FAIL'} {result.check_id}: {result.detail}")
    print("LIMIT: route fixtures prove evaluator calibration only; they are not production questions or human approval.")
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
