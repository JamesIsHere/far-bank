from __future__ import annotations

import copy
import hashlib
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from validate_p1_records import PROJECT_ROOT, load_json, schema_issues, taxonomy_task_index


CHECKER_ID = "far-production-control-verifier"
CHECKER_VERSION = "1.0.0"
REQUIRED_CHECK_SET_ID = "far-g2-production-controls.v001"
CONTRACT_PATH = Path("data/contracts/far-g2-production-contract.v001.json")
CONTRACT_CANONICAL_SHA256 = "7dae5c70e23e52028bf851473670285f3853dcd583af32ff926827eeaacc1a45"

REPRESENTATIONS = (
    "formula",
    "roll_forward",
    "journal_effect",
    "financial_statement_view",
    "rule_selection",
    "classification",
)
RULE_PRESSURES = ("rule", "timing", "basis", "measurement", "classification", "presentation", "convention")
DIFFICULTY_DIMENSIONS = (
    "accounting_complexity",
    "reasoning_steps",
    "reading_fact_selection",
    "rule_convention_pressure",
    "distractor_elimination_burden",
    "realistic_time_pressure",
)
EXPLANATION_ELEMENTS = (
    "answer",
    "rule",
    "fact_application",
    "calculation_or_reasoning",
    "distractor_diagnoses",
    "faster_or_safer_route",
)


@dataclass(frozen=True)
class ControlCheckResult:
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


def _pass(check_id: str, category: str, detail: str, *evidence: str) -> ControlCheckResult:
    return ControlCheckResult(check_id, category, True, detail, tuple(evidence))


def _fail(check_id: str, category: str, detail: str, *evidence: str) -> ControlCheckResult:
    return ControlCheckResult(check_id, category, False, detail, tuple(evidence))


def load_contract(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    return load_json(project_root / CONTRACT_PATH)


def _ordered_tasks(taxonomy: dict[str, Any]) -> list[dict[str, str]]:
    tasks: list[dict[str, str]] = []
    for area in taxonomy["areas"]:
        for group in area["groups"]:
            candidates = list(group["tasks"])
            for topic in group["topics"]:
                candidates.extend(topic["tasks"])
            for task in candidates:
                tasks.append({"task_id": task["id"], "area_id": area["id"], "skill_level": task["skill_level"]})
    return tasks


def _stem_bin(word_count: int) -> str:
    return "short" if word_count <= 45 else "standard" if word_count <= 90 else "dense"


def _numeric_bin(count: int) -> str:
    return "low" if count <= 2 else "medium" if count <= 5 else "high"


def _steps_bin(count: int) -> str:
    return "one" if count == 1 else "two_to_three" if count <= 3 else "four_plus"


def _irrelevant_bin(count: int) -> str:
    return "none" if count == 0 else "one_to_two" if count <= 2 else "three_plus"


def _accounting_level(observation: dict[str, Any]) -> int:
    interactions = observation["accounting_interaction_count"]
    if interactions >= 4 or observation["accounting_has_exception_or_judgment"]:
        return 5
    if interactions == 3:
        return 4
    if interactions == 2:
        return 3
    if observation["rule_boundary_count"] >= 1:
        return 2
    return 1


def _reasoning_level(observation: dict[str, Any]) -> int:
    steps = observation["dependent_step_count"]
    if steps >= 5 and observation["branch_or_reconciliation_loop"]:
        return 5
    return min(4, steps)


def _reading_level(observation: dict[str, Any]) -> int:
    facts = observation["total_fact_count"]
    irrelevant = observation["irrelevant_fact_count"]
    clauses = observation["conditional_clause_count"]
    if facts >= 11:
        return 5
    if facts >= 8 or irrelevant >= 3 or clauses >= 3:
        return 4
    if facts >= 6 or irrelevant >= 2:
        return 3
    if facts >= 4 or irrelevant >= 1:
        return 2
    return 1


def _rule_level(observation: dict[str, Any]) -> int:
    return min(5, observation["rule_boundary_count"] + 1)


def _elimination_level(observation: dict[str, Any]) -> int:
    return {"low": 1, "medium": 3, "high": 4}[observation["elimination_burden"]]


def _time_level(observation: dict[str, Any]) -> int:
    seconds = observation["estimated_time_seconds"]
    operations = observation["operation_count"]
    if seconds > 150 or operations >= 8:
        return 5
    if seconds >= 91 or operations >= 5:
        return 4
    if seconds >= 61 or operations >= 3:
        return 3
    if seconds >= 31 or operations >= 2:
        return 2
    return 1


DIFFICULTY_DERIVERS: dict[str, Callable[[dict[str, Any]], int]] = {
    "accounting_complexity": _accounting_level,
    "reasoning_steps": _reasoning_level,
    "reading_fact_selection": _reading_level,
    "rule_convention_pressure": _rule_level,
    "distractor_elimination_burden": _elimination_level,
    "realistic_time_pressure": _time_level,
}


def _difficulty_profile(observation: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "dimension_id": dimension,
            "rubric_version_id": "far-g2-six-dimensional-difficulty.v001",
            "level": DIFFICULTY_DERIVERS[dimension](observation),
            "observable_evidence": [f"fixture observation supports {dimension}"],
            "human_review_flag": None,
        }
        for dimension in DIFFICULTY_DIMENSIONS
    ]


def build_clean_calibration_bank(project_root: Path = PROJECT_ROOT) -> list[dict[str, Any]]:
    """Build synthetic control records. They are never canonical questions or coverage evidence."""
    taxonomy = load_json(project_root / "data" / "far-taxonomy.json")
    tasks = _ordered_tasks(taxonomy)
    area_three_tasks = [task["task_id"] for task in tasks if task["area_id"] == "far.area.3"]
    records: list[dict[str, Any]] = []
    for task in tasks:
        copies = 4 if task["task_id"] in area_three_tasks[:14] else 3
        for task_ordinal in range(copies):
            index = len(records)
            question_id = f"far-q-{900001 + index:06d}"
            stem_words = (30, 60, 60, 100, 60)[index % 5]
            numeric_facts = (1, 4, 7)[index % 3]
            irrelevant = (0, 0, 1, 1, 3)[index % 5]
            steps = (1, 2, 3, 2, 3, 2, 3, 4, 4, 5)[index % 10]
            elimination = ("low", "medium", "medium", "medium", "high")[index % 5]
            time_bin = ("low", "moderate", "moderate", "moderate", "high")[index % 5]
            seconds, operations = {"low": (25, 1), "moderate": (75, 3), "high": (120, 6)}[time_bin]
            primary_work = (
                "conceptual_recall",
                "classification_rule_selection",
                "classification_rule_selection",
                "computation",
                "computation",
                "computation",
                "analytical_reconciliation_inference",
                "analytical_reconciliation_inference",
                "analytical_reconciliation_inference",
                "classification_rule_selection",
            )[index % 10]
            if index == 0:
                primary_work = "computation"
            pressure = RULE_PRESSURES[index % len(RULE_PRESSURES)]
            observation = {
                "stem_word_count": stem_words,
                "stem_length_bin": _stem_bin(stem_words),
                "numeric_fact_count": numeric_facts,
                "total_fact_count": max(3, numeric_facts + irrelevant),
                "numeric_fact_density_bin": _numeric_bin(numeric_facts),
                "primary_accounting_work": primary_work,
                "dependent_step_count": steps,
                "branch_or_reconciliation_loop": steps >= 5,
                "dependent_steps_bin": _steps_bin(steps),
                "irrelevant_fact_count": irrelevant,
                "conditional_clause_count": 0,
                "irrelevant_facts_bin": _irrelevant_bin(irrelevant),
                "ask_placement": "indirect_embedded" if index % 5 == 4 or index == 0 else "direct_final_sentence",
                "indirect_ask_deliberate": index % 5 == 4 or index == 0,
                "solution_end_ask": "Determine the required accounting conclusion.",
                "rule_pressure_tags": [pressure],
                "rule_boundary_count": index % 5,
                "accounting_interaction_count": (index % 4) + 1,
                "accounting_has_exception_or_judgment": False,
                "primary_solution_representation": REPRESENTATIONS[index % len(REPRESENTATIONS)],
                "elimination_burden": elimination,
                "estimated_time_seconds": seconds,
                "observed_time_seconds": None,
                "realistic_time_pressure_bin": time_bin,
                "operation_count": operations,
                "stem_template_id": f"stem-template-{index % 8}",
                "fact_pattern_id": f"fact-pattern-{index}",
                "distractor_family_id": f"distractor-family-{index % 12}",
                "distractor_error_model_ids": [
                    f"error-model-{value}"
                    for value in (
                        (0, 1, 2),
                        (2, 3, 4),
                        (0, 3, 5),
                        (1, 4, 6),
                    )[task_ordinal]
                ],
                "challenge_mechanic_tags": [pressure, f"task-slot-{task_ordinal}"],
            }
            observation["distractor_reproduction_supported_ids"] = list(observation["distractor_error_model_ids"])
            records.append(
                {
                    "schema_version": "1.0.0",
                    "purpose": "calibration_fixture",
                    "contract_id": "far-g2-production-contract.v001",
                    "subject": {
                        "question_id": question_id,
                        "version_id": f"{question_id}.v001",
                        "content_sha256": hashlib.sha256(f"calibration-fixture-{index}".encode()).hexdigest(),
                    },
                    "mapping": {
                        "area_id": task["area_id"],
                        "representative_task_ids": [task["task_id"]],
                        "primary_task_id": task["task_id"],
                        "skill_level": task["skill_level"],
                        "multi_task_justification": None,
                        "full_task_exercised": False,
                        "full_task_evidence": None,
                        "mcq_scope_limit": "Calibration MCQ metadata cannot establish that the full representative task is exercised.",
                    },
                    "observations": observation,
                    "difficulty_profile": _difficulty_profile(observation),
                    "prose_evidence": {
                        "structured_token_count": numeric_facts,
                        "stem_token_count": numeric_facts,
                        "irrelevant_fact_annotations": irrelevant,
                        "framework": "for_profit_us_gaap",
                        "framework_named_when_required": True,
                        "answer_changing_assumptions_traced": True,
                        "negative_exception_deliberate": False,
                        "double_negative_screen_passed": True,
                        "options_parallel": True,
                        "options_mutually_exclusive": True,
                        "options_normalized_unique": True,
                        "options_units_consistent": True,
                        "absolute_claims": 0,
                        "absolute_claims_traced": 0,
                        "explanation_element_ids": list(EXPLANATION_ELEMENTS),
                        "distractor_explanation_count": 3,
                    },
                }
            )
    return records


def check_ratification_binding(contract: dict[str, Any], records: list[dict[str, Any]], project_root: Path = PROJECT_ROOT) -> ControlCheckResult:
    problems: list[str] = []
    contract_hash = hashlib.sha256(json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    if contract_hash != CONTRACT_CANONICAL_SHA256:
        problems.append(f"contract receipt hash {contract_hash} is not the checker-bound ratified receipt")
    problems.extend(issue.detail for issue in schema_issues(load_json(project_root / "schema/production-contract.schema.json"), contract, "PRODUCTION_CONTRACT_SCHEMA"))
    evidence_schema = load_json(project_root / "schema/production-control-evidence.schema.json")
    for index, record in enumerate(records):
        problems.extend(f"record {index}: {issue.detail}" for issue in schema_issues(evidence_schema, record, "PRODUCTION_EVIDENCE_SCHEMA"))
        if record.get("contract_id") != contract.get("contract_id"):
            problems.append(f"record {index} does not bind the ratified contract")
    goal_path = project_root / contract["ratification"]["goal_path"]
    actual_hash = hashlib.sha256(goal_path.read_bytes()).hexdigest()
    if actual_hash != contract["ratification"]["goal_sha256"]:
        problems.append(f"goal hash {actual_hash} does not match the ratification receipt")
    if contract["ratification"]["amendment_heading"] not in goal_path.read_text(encoding="utf-8"):
        problems.append("ratified amendment heading is absent from goal.md")
    if problems:
        return _fail("RATIFICATION_BINDING", "CONTRACT", "; ".join(problems[:6]), *problems)
    return _pass("RATIFICATION_BINDING", "CONTRACT", "Contract, goal hash, and all exact-version evidence envelopes are bound.", f"contract_sha256={contract_hash}", f"goal_sha256={actual_hash}", f"record_count={len(records)}")


def check_item_observations(contract: dict[str, Any], records: list[dict[str, Any]], project_root: Path = PROJECT_ROOT) -> ControlCheckResult:
    task_index = taxonomy_task_index(load_json(project_root / "data/far-taxonomy.json"))
    problems: list[str] = []
    for record in records:
        subject = record["subject"]
        mapping = record["mapping"]
        obs = record["observations"]
        if subject["version_id"].split(".v", 1)[0] != subject["question_id"]:
            problems.append(f"{subject['version_id']} is detached from its question ID")
        resolved = task_index.get(mapping["primary_task_id"])
        if resolved is None or resolved["area_id"] != mapping["area_id"] or resolved["skill_level"] != mapping["skill_level"]:
            problems.append(f"{subject['version_id']} has an unresolved primary task/path/skill")
        if mapping["primary_task_id"] not in mapping["representative_task_ids"]:
            problems.append(f"{subject['version_id']} primary task is absent from its mappings")
        if len(mapping["representative_task_ids"]) > 1 and not mapping["multi_task_justification"]:
            problems.append(f"{subject['version_id']} lacks multi-task justification")
        if mapping["full_task_exercised"] and not mapping["full_task_evidence"]:
            problems.append(f"{subject['version_id']} claims the full task without format evidence")
        if not mapping["mcq_scope_limit"].strip():
            problems.append(f"{subject['version_id']} has no explicit MCQ scope limit")
        expected_bins = {
            "stem_length_bin": _stem_bin(obs["stem_word_count"]),
            "numeric_fact_density_bin": _numeric_bin(obs["numeric_fact_count"]),
            "dependent_steps_bin": _steps_bin(obs["dependent_step_count"]),
            "irrelevant_facts_bin": _irrelevant_bin(obs["irrelevant_fact_count"]),
        }
        for field, expected in expected_bins.items():
            if obs[field] != expected:
                problems.append(f"{subject['version_id']} {field}={obs[field]}, expected {expected}")
        if obs["total_fact_count"] < obs["numeric_fact_count"] + obs["irrelevant_fact_count"]:
            problems.append(f"{subject['version_id']} total facts undercount numeric plus irrelevant facts")
        if (obs["ask_placement"] == "indirect_embedded") != obs["indirect_ask_deliberate"]:
            problems.append(f"{subject['version_id']} indirect ask lacks a deliberate tag")
        if not obs["solution_end_ask"].strip():
            problems.append(f"{subject['version_id']} has no restated end ask")
        if set(obs["distractor_error_model_ids"]) != set(obs["distractor_reproduction_supported_ids"]):
            problems.append(f"{subject['version_id']} has a nonkey without reproduction/assertion support")
    if problems:
        return _fail("ITEM_OBSERVABLE_CONSISTENCY", "ITEM_CONTROLS", "; ".join(problems[:6]), *problems)
    return _pass("ITEM_OBSERVABLE_CONSISTENCY", "ITEM_CONTROLS", "Exact subjects, taxonomy paths, observable counts, and derived bins agree.", f"record_count={len(records)}")


def check_difficulty_observations(contract: dict[str, Any], records: list[dict[str, Any]], project_root: Path = PROJECT_ROOT) -> ControlCheckResult:
    problems: list[str] = []
    for record in records:
        profile = {entry["dimension_id"]: entry for entry in record["difficulty_profile"]}
        if set(profile) != set(DIFFICULTY_DIMENSIONS) or len(profile) != 6:
            problems.append(f"{record['subject']['version_id']} does not record all six dimensions once")
            continue
        for dimension, derive in DIFFICULTY_DERIVERS.items():
            expected = derive(record["observations"])
            entry = profile[dimension]
            if entry["level"] != expected:
                problems.append(f"{record['subject']['version_id']} {dimension} level {entry['level']} is not supported level {expected}")
            if not entry["observable_evidence"]:
                problems.append(f"{record['subject']['version_id']} {dimension} lacks evidence")
        time_level = profile["realistic_time_pressure"]["level"]
        expected_time_bin = "low" if time_level <= 2 else "moderate" if time_level == 3 else "high"
        if record["observations"]["realistic_time_pressure_bin"] != expected_time_bin:
            problems.append(f"{record['subject']['version_id']} time-pressure bin disagrees with the six-dimensional profile")
    if problems:
        return _fail("DIFFICULTY_OBSERVABLE_CONSISTENCY", "DIFFICULTY", "; ".join(problems[:6]), *problems)
    return _pass("DIFFICULTY_OBSERVABLE_CONSISTENCY", "DIFFICULTY", "All six unaveraged levels are supported by observable conditions.", f"profile_count={len(records)}")


def check_prose_evidence(contract: dict[str, Any], records: list[dict[str, Any]], project_root: Path = PROJECT_ROOT) -> ControlCheckResult:
    problems: list[str] = []
    required_elements = set(EXPLANATION_ELEMENTS)
    for record in records:
        obs = record["observations"]
        prose = record["prose_evidence"]
        version = record["subject"]["version_id"]
        if prose["structured_token_count"] != prose["stem_token_count"]:
            problems.append(f"{version} structured/stem number-date-threshold counts differ")
        if prose["irrelevant_fact_annotations"] != obs["irrelevant_fact_count"]:
            problems.append(f"{version} irrelevant facts are not individually annotated")
        if prose["framework"] != "for_profit_us_gaap" and not prose["framework_named_when_required"]:
            problems.append(f"{version} special framework is unnamed")
        boolean_fields = ("answer_changing_assumptions_traced", "double_negative_screen_passed", "options_parallel", "options_mutually_exclusive", "options_normalized_unique", "options_units_consistent")
        for field in boolean_fields:
            if not prose[field]:
                problems.append(f"{version} prose control {field} failed")
        if prose["absolute_claims"] != prose["absolute_claims_traced"]:
            problems.append(f"{version} has an untraced absolute claim")
        if not required_elements.issubset(prose["explanation_element_ids"]):
            problems.append(f"{version} explanation omits a ratified diagnostic element")
        if prose["distractor_explanation_count"] != 3:
            problems.append(f"{version} does not explain every distractor")
    if problems:
        return _fail("PROSE_FAIRNESS_EVIDENCE", "PROSE", "; ".join(problems[:6]), *problems)
    return _pass("PROSE_FAIRNESS_EVIDENCE", "PROSE", "Every item carries the targeted, auditable prose/fairness evidence fields.", f"record_count={len(records)}", "Mechanical evidence is not human approval or proof of fairness.")


def check_coverage_floors(contract: dict[str, Any], records: list[dict[str, Any]], project_root: Path = PROJECT_ROOT) -> ControlCheckResult:
    taxonomy = load_json(project_root / "data/far-taxonomy.json")
    tasks = set(taxonomy_task_index(taxonomy))
    by_task = Counter(record["mapping"]["primary_task_id"] for record in records)
    by_area = Counter(record["mapping"]["area_id"] for record in records)
    coverage = contract["coverage"]
    problems: list[str] = []
    if len(records) < coverage["minimum_bank_items"]:
        problems.append(f"bank has {len(records)} records, below {coverage['minimum_bank_items']}")
    for task_id in sorted(tasks):
        if by_task[task_id] < coverage["minimum_per_task"]:
            problems.append(f"{task_id} has {by_task[task_id]} primary items, below {coverage['minimum_per_task']}")
    for area_id, floor in coverage["area_item_floors"].items():
        if by_area[area_id] < floor:
            problems.append(f"{area_id} has {by_area[area_id]} items, below {floor}")
        share = by_area[area_id] / len(records) if records else 0
        permitted = coverage["area_percentage_ranges"][area_id]
        if not permitted["minimum"] <= share <= permitted["maximum"]:
            problems.append(f"{area_id} share {share:.3f} is outside {permitted['minimum']:.2f}-{permitted['maximum']:.2f}")
    if problems:
        return _fail("COVERAGE_FLOORS", "COVERAGE", "; ".join(problems[:6]), *problems)
    return _pass("COVERAGE_FLOORS", "COVERAGE", "The calibration bank meets all task, area, total, and area-share floors.", f"tasks={len(tasks)}", f"items={len(records)}", *(f"{area}={by_area[area]}" for area in sorted(by_area)))


def _variety_counts(records: list[dict[str, Any]]) -> dict[str, Counter[str]]:
    counts: dict[str, Counter[str]] = {
        "stem_length": Counter(), "numeric_fact_density": Counter(), "primary_accounting_work": Counter(),
        "dependent_steps": Counter(), "irrelevant_facts": Counter(), "ask_placement": Counter(),
        "rule_pressure": Counter(), "primary_solution_representation": Counter(),
        "elimination_burden": Counter(), "realistic_time_pressure": Counter(),
    }
    for record in records:
        obs = record["observations"]
        counts["stem_length"][obs["stem_length_bin"]] += 1
        counts["numeric_fact_density"][obs["numeric_fact_density_bin"]] += 1
        counts["primary_accounting_work"][obs["primary_accounting_work"]] += 1
        counts["dependent_steps"][obs["dependent_steps_bin"]] += 1
        counts["irrelevant_facts"][obs["irrelevant_facts_bin"]] += 1
        counts["ask_placement"][obs["ask_placement"]] += 1
        counts["rule_pressure"].update(obs["rule_pressure_tags"])
        counts["primary_solution_representation"][obs["primary_solution_representation"]] += 1
        counts["elimination_burden"][obs["elimination_burden"]] += 1
        counts["realistic_time_pressure"][obs["realistic_time_pressure_bin"]] += 1
    return counts


def check_variety_floors(contract: dict[str, Any], records: list[dict[str, Any]], project_root: Path = PROJECT_ROOT) -> ControlCheckResult:
    counts = _variety_counts(records)
    problems: list[str] = []
    for dimension, bins in contract["variety_floors"].items():
        for bin_name, floor in bins.items():
            required = math.ceil(len(records) * floor)
            if counts[dimension][bin_name] < required:
                problems.append(f"{dimension}.{bin_name} has {counts[dimension][bin_name]}, below ceil({len(records)}×{floor})={required}")
    if problems:
        return _fail("VARIETY_FLOORS", "VARIETY", "; ".join(problems[:6]), *problems)
    return _pass("VARIETY_FLOORS", "VARIETY", "All ten ratified variety dimensions meet their ceiling-rounded floors.", f"items={len(records)}", "unallocated_share_is_permitted=true")


def check_within_task_diversity(contract: dict[str, Any], records: list[dict[str, Any]], project_root: Path = PROJECT_ROOT) -> ControlCheckResult:
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_task[record["mapping"]["primary_task_id"]].append(record)
    problems: list[str] = []
    for task_id, items in by_task.items():
        if len(items) < contract["coverage"]["minimum_per_task"]:
            continue
        minimum = items[: contract["coverage"]["minimum_per_task"]]
        representations = {item["observations"]["primary_solution_representation"] for item in minimum}
        mechanics = {tag for item in minimum for tag in item["observations"]["challenge_mechanic_tags"]}
        model_sets = [frozenset(item["observations"]["distractor_error_model_ids"]) for item in minimum]
        models = set().union(*model_sets)
        if len(representations) < 2:
            problems.append(f"{task_id} minimum has fewer than two solution representations")
        if len(mechanics) < 2:
            problems.append(f"{task_id} minimum has fewer than two challenge mechanics")
        if len(models) < 5:
            problems.append(f"{task_id} minimum has only {len(models)} distinct distractor models")
        if len(set(model_sets)) != len(model_sets):
            problems.append(f"{task_id} repeats a complete three-model distractor set")
        for left_index, left in enumerate(minimum):
            for right in minimum[left_index + 1 :]:
                if left["observations"]["fact_pattern_id"] == right["observations"]["fact_pattern_id"] and set(left["observations"]["distractor_error_model_ids"]) == set(right["observations"]["distractor_error_model_ids"]):
                    problems.append(f"{task_id} contains a cloned fact-pattern/distractor-set pair")
    if problems:
        return _fail("WITHIN_TASK_DIVERSITY", "ANTI_CLONING", "; ".join(problems[:6]), *problems)
    return _pass("WITHIN_TASK_DIVERSITY", "ANTI_CLONING", "Every task minimum has representation, mechanic, fact-pattern, and distractor-model diversity.", f"tasks={len(by_task)}")


def check_concentration_caps(contract: dict[str, Any], records: list[dict[str, Any]], project_root: Path = PROJECT_ROOT) -> ControlCheckResult:
    problems: list[str] = []
    caps = contract["concentration_caps"]
    fields = ("stem_template_id", "fact_pattern_id", "primary_solution_representation", "distractor_family_id")
    for field in fields:
        counts = Counter(record["observations"][field] for record in records)
        for value, count in counts.items():
            if count / len(records) > caps[field]:
                problems.append(f"{field}={value} occupies {count}/{len(records)}, above {caps[field]:.0%}")
    noisy = sum(record["observations"]["irrelevant_facts_bin"] == "three_plus" for record in records)
    if noisy / len(records) > caps["irrelevant_facts_three_plus"]:
        problems.append(f"three-plus irrelevant facts occupy {noisy}/{len(records)}, above {caps['irrelevant_facts_three_plus']:.0%}")
    if problems:
        return _fail("BANK_CONCENTRATION_CAPS", "ANTI_CLONING", "; ".join(problems[:6]), *problems)
    return _pass("BANK_CONCENTRATION_CAPS", "ANTI_CLONING", "Template, fact-pattern, representation, distractor-family, and noise caps pass.", f"items={len(records)}")


def check_area_compatibility(contract: dict[str, Any], records: list[dict[str, Any]], project_root: Path = PROJECT_ROOT) -> ControlCheckResult:
    by_area: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_area[record["mapping"]["area_id"]].append(record)
    problems: list[str] = []
    for row in contract["area_compatibility"]:
        items = by_area[row["area_id"]]
        skills = {item["mapping"]["skill_level"] for item in items}
        representations = {item["observations"]["primary_solution_representation"] for item in items}
        for skill in row["applicable_skills"]:
            if skill not in skills:
                problems.append(f"{row['area_id']} lacks applicable skill {skill}")
        for representation in row["applicable_representations"]:
            if representation not in representations:
                problems.append(f"{row['area_id']} lacks compatible representation {representation}")
        for exclusion in row["excluded_combinations"]:
            if not exclusion["rationale"].strip():
                problems.append(f"{row['area_id']} has an exclusion without rationale")
    if problems:
        return _fail("AREA_COMPATIBILITY_MATRIX", "COMPATIBILITY", "; ".join(problems[:6]), *problems)
    return _pass("AREA_COMPATIBILITY_MATRIX", "COMPATIBILITY", "Every area covers each ratified applicable skill and compatible representation.", f"areas={len(by_area)}")


CHECKS: tuple[Callable[[dict[str, Any], list[dict[str, Any]], Path], ControlCheckResult], ...] = (
    check_ratification_binding,
    check_item_observations,
    check_difficulty_observations,
    check_prose_evidence,
    check_coverage_floors,
    check_variety_floors,
    check_within_task_diversity,
    check_concentration_caps,
    check_area_compatibility,
)


def run_checks(contract: dict[str, Any], records: list[dict[str, Any]], project_root: Path = PROJECT_ROOT) -> list[ControlCheckResult]:
    return [check(contract, records, project_root) for check in CHECKS]


def main() -> int:
    contract = load_contract()
    records = build_clean_calibration_bank()
    results = run_checks(contract, records)
    for result in results:
        print(f"{'PASS' if result.passed else 'FAIL'} {result.check_id}: {result.detail}")
    print("LIMIT: synthetic calibration records contribute zero production coverage and grant no approval.")
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
