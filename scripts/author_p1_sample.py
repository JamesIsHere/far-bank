from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from validate_p1_records import PROJECT_ROOT, canonical_content_sha256
from verify_questions import (
    CHECKER_ID,
    CHECKER_VERSION,
    REQUIRED_CHECK_SET_ID,
    QuestionBundle,
    derive_learner_ready,
    run_checks,
)


STAMP = "2026-08-13T20:00:00Z"
MODEL_ID = "openai-codex-gpt-5"
SAMPLE_ID = "far-p1-g2-sample.v001"
REFERENCE_ID = "far-ref-fasb-codification-live"
REFERENCE_VERSION_ID = f"{REFERENCE_ID}.v001"
RUBRIC_ID = "far-p1-proposed-difficulty-rubric.v001"


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def linear(terms: list[tuple[str, float]], unit: str = "USD", constant: float = 0) -> dict[str, Any]:
    return {
        "route_type": "linear_combination",
        "linear_combination": {
            "terms": [{"fact_id": fact_id, "coefficient": coefficient} for fact_id, coefficient in terms],
            "constant": constant,
            "output_unit": unit,
            "rounding": {"mode": "none", "decimal_places": 0},
        },
    }


def fact(
    fact_id: str,
    statement: str,
    value: float,
    *,
    relevance: str,
    use: str = "",
    reason: str = "",
    unit: str = "USD",
) -> dict[str, Any]:
    result = {
        "fact_id": fact_id,
        "statement": statement,
        "structured_value": {"value_type": "number", "value": value, "unit": unit},
        "relevance": relevance,
    }
    if relevance == "relevant":
        result["use_in_solution"] = use
    else:
        result["irrelevance_reason"] = reason
    return result


def option(
    option_id: str,
    text: str,
    value: float,
    *,
    keyed: bool = False,
    error_id: str = "",
    name: str = "",
    misconception: str = "",
    derivation: str = "",
    terms: list[tuple[str, float]] | None = None,
) -> dict[str, Any]:
    result = {
        "option_id": option_id,
        "text": text,
        "structured_value": {"value_type": "number", "value": value, "unit": "USD"},
        "is_keyed": keyed,
    }
    if not keyed:
        result["error_model"] = {
            "error_model_id": error_id,
            "name": name,
            "misconception": misconception,
            "derivation": derivation,
            "reproduction": linear(terms or []),
        }
    return result


def challenge(tag: str, evidence: str) -> dict[str, Any]:
    return {"tag": tag, "observable_evidence": [evidence]}


def difficulty(
    *,
    levels: tuple[int, int, int, int, int, int],
    rule_count: int,
    step_count: int,
    irrelevant_count: int,
    boundary_count: int,
    operation_count: int,
) -> list[dict[str, Any]]:
    definitions = (
        ("accounting_complexity", "rule_count", rule_count, "rules", "Exact rule traces applied to the item."),
        ("reasoning_steps", "dependent_step_count", step_count, "steps", "Ordered solution steps required by the authored route."),
        ("reading_fact_selection", "irrelevant_fact_count", irrelevant_count, "facts", "Structured facts excluded from the numerical end ask."),
        ("rule_convention_pressure", "classification_boundary_count", boundary_count, "boundaries", "Rule, timing, or classification boundaries the solver must distinguish."),
        ("distractor_elimination_burden", "plausible_error_model_count", 3, "models", "Each nonkey has a distinct executable error model."),
        ("realistic_time_pressure", "arithmetic_operation_count", operation_count, "operations", "Arithmetic operations in the independent keyed route."),
    )
    return [
        {
            "dimension_id": dimension_id,
            "rubric_version_id": RUBRIC_ID,
            "rubric_status": "proposed_for_g2",
            "provisional_level": level,
            "observable_measurements": [
                {
                    "measure_id": measure_id,
                    "value": value,
                    "unit": unit,
                    "interpretation": interpretation,
                }
            ],
        }
        for level, (dimension_id, measure_id, value, unit, interpretation) in zip(levels, definitions)
    ]


def rule_record(spec: dict[str, Any]) -> dict[str, Any]:
    rule_id = spec["rule_id"]
    content = {
        "title": spec["rule_title"],
        "rule_statement": spec["rule_statement"],
        "applicability": spec["rule_applicability"],
        "assertions": spec["assertions"],
        "source_citations": [
            {
                "reference_version_id": REFERENCE_VERSION_ID,
                "locator": spec["source_locator"],
                "role": "controlling",
                "supports_assertion_ids": [item["assertion_id"] for item in spec["assertions"]],
            }
        ],
        "currency": {
            "assessed_at": STAMP,
            "assessment": "current",
            "basis": spec["currency_basis"],
        },
        "authorship_provenance": {
            "purpose": "admitted_evidence",
            "mechanism": "ai_assisted",
            "created_by": "Codex",
            "model_id": MODEL_ID,
            "material_input_ids": [REFERENCE_VERSION_ID, spec["source_locator"]],
        },
    }
    return {
        "schema_version": "1.0.0",
        "rule_id": rule_id,
        "rule_version_id": f"{rule_id}.v001",
        "version_number": 1,
        "content_sha256": canonical_content_sha256(content),
        "content": content,
    }


def identity_record(spec: dict[str, Any], rule_version_id: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "question_id": spec["question_id"],
        "created_at": STAMP,
        "creation_provenance": {
            "purpose": "sample_candidate",
            "mechanism": "ai_assisted",
            "created_by": "Codex",
            "model_id": MODEL_ID,
            "material_inputs": [
                {"input_id": "far-2026-01", "input_kind": "taxonomy", "version_or_date": "2026-01", "use": "Bind the exact FAR task and skill."},
                {"input_id": rule_version_id, "input_kind": "rule", "version_or_date": "v001", "use": "Control the accounting treatment and answer."},
                {"input_id": REFERENCE_VERSION_ID, "input_kind": "source", "version_or_date": "retrieved-2026-08-13", "use": "Provide authoritative U.S. GAAP provenance."},
                {"input_id": SAMPLE_ID, "input_kind": "human_brief", "version_or_date": "v001", "use": "Bounded G2 sample design under the ratified goal."},
            ],
        },
    }


def question_record(spec: dict[str, Any], rule: dict[str, Any]) -> dict[str, Any]:
    question_id = spec["question_id"]
    rule_version_id = rule["rule_version_id"]
    content = {
        "authorship": {
            "purpose": "sample_candidate",
            "mechanism": "ai_assisted",
            "created_by": "Codex",
            "created_at": STAMP,
            "model_id": MODEL_ID,
            "material_inputs": identity_record(spec, rule_version_id)["creation_provenance"]["material_inputs"],
        },
        "stem": spec["stem"],
        "options": spec["options"],
        "blueprint_mappings": [spec["mapping"]],
        "accounting_model_id": spec["model_id"],
        "facts": spec["facts"],
        "assumptions": spec.get("assumptions", []),
        "solution": spec["solution"],
        "correctness_evidence": {
            "evidence_id": spec["evidence_id"],
            "route": linear(spec["key_terms"]),
            "producer_component_id": "p1-sample-content-author",
            "verifier_component_id": "independent-linear-combination-checker",
            "shared_deciding_function": False,
            "authorship": {
                "mechanism": "ai_assisted",
                "created_by": "Codex",
                "created_at": STAMP,
                "model_id": MODEL_ID,
            },
            "independence_limit": "The generic checker recomputes the keyed amount solely from structured facts and coefficients; human review still owns accounting correctness, fairness, and learner readiness.",
        },
        "rule_trace": [
            {
                "rule_version_id": rule_version_id,
                "assertion_ids": [item["assertion_id"] for item in rule["content"]["assertions"]],
                "applied_to_fact_ids": [item["fact_id"] for item in spec["facts"]],
                "application": spec["rule_application"],
            }
        ],
        "challenge_mechanics": spec["challenges"],
        "difficulty_profile": spec["difficulty"],
        "originality_boundary": {
            "compared_corpus_ids": [SAMPLE_ID],
            "methods": ["Within-bank normalized exact-stem and word 5-gram pairwise comparison across the six-item P1 sample."],
            "claim_limit": "This supports only a bounded comparison within the named six-item sample; it is not an exhaustive external-corpus, non-infringement, or legal conclusion.",
        },
    }
    return {
        "schema_version": "1.1.0",
        "question_id": question_id,
        "version_id": f"{question_id}.v001",
        "version_number": 1,
        "content_sha256": canonical_content_sha256(content),
        "content": content,
    }


def verification_event(question: dict[str, Any], checks: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "event_id": f"far-verification-{question['question_id'].removeprefix('far-q-')}-v001",
        "recorded_at": STAMP,
        "subject": {
            "question_id": question["question_id"],
            "version_id": question["version_id"],
            "content_sha256": question["content_sha256"],
        },
        "checker": {"checker_id": CHECKER_ID, "checker_version": CHECKER_VERSION},
        "required_check_set_id": REQUIRED_CHECK_SET_ID,
        "input_evidence": [
            {
                "path_or_id": f"data/questions/{question['question_id']}/versions/{question['version_id']}.json",
                "sha256": question["content_sha256"],
            }
        ],
        "checks": checks,
    }


def step(number: int, instruction: str, facts: list[str], assertions: list[str], result: str) -> dict[str, Any]:
    return {"step_number": number, "instruction": instruction, "fact_ids_used": facts, "assertion_ids_used": assertions, "result": result}


SPECS: list[dict[str, Any]] = [
    {
        "question_id": "far-q-000101",
        "rule_id": "far-rule-oci-components",
        "rule_title": "Pretax other comprehensive income components",
        "rule_statement": "Unrealized holding gains and losses on available-for-sale debt securities are excluded from earnings and reported in other comprehensive income, while trading-security changes, realized disposal results, and ordinary dividends are included in net income rather than OCI.",
        "rule_applicability": "For-profit entities applying U.S. GAAP to the stated pretax security and income items.",
        "assertions": [
            {"assertion_id": "assertion-afs-debt-oci", "claim": "An unrealized holding gain on an available-for-sale debt security is reported in OCI before tax."},
            {"assertion_id": "assertion-earnings-items-excluded", "claim": "Trading-security gains, realized disposal losses, and dividend income are earnings items, not current-period OCI components."},
        ],
        "source_locator": "FASB ASC 320-10-35-1(b) and 220-10-45-10A (live official Codification)",
        "currency_basis": "The live official Codification locators and FASB-hosted Update 2016-01 materials were cross-checked on 2026-08-13; no effective amendment affecting this treatment was identified.",
        "stem": "A company reports a $14,000 unrealized gain on an available-for-sale debt security, a $6,000 unrealized gain on a trading security, a $5,000 realized loss on an equipment sale, and $2,000 of dividend income. What pretax amount should the company report in other comprehensive income?",
        "facts": [
            fact("fact-afs-gain", "The unrealized gain on available-for-sale debt is $14,000.", 14000, relevance="relevant", use="Included in pretax OCI."),
            fact("fact-trading-gain", "The unrealized trading-security gain is $6,000.", 6000, relevance="irrelevant", reason="Trading-security changes are reported in earnings."),
            fact("fact-equipment-loss", "The realized equipment-sale loss is $5,000.", 5000, relevance="irrelevant", reason="A realized disposal loss is reported in earnings."),
            fact("fact-dividend-income", "Dividend income is $2,000.", 2000, relevance="irrelevant", reason="Ordinary dividend income is reported in earnings."),
        ],
        "options": [
            option("A", "$14,000 of pretax OCI", 14000, keyed=True),
            option("B", "$20,000", 20000, error_id="error-include-trading", name="Include trading gain", misconception="Treats every unrealized security gain as OCI.", derivation="$14,000 + $6,000 = $20,000.", terms=[("fact-afs-gain", 1), ("fact-trading-gain", 1)]),
            option("C", "$9,000", 9000, error_id="error-net-realized-loss", name="Net realized loss", misconception="Nets an earnings loss against OCI.", derivation="$14,000 - $5,000 = $9,000.", terms=[("fact-afs-gain", 1), ("fact-equipment-loss", -1)]),
            option("D", "$16,000", 16000, error_id="error-include-dividend", name="Include dividend income", misconception="Treats ordinary dividend income as OCI.", derivation="$14,000 + $2,000 = $16,000.", terms=[("fact-afs-gain", 1), ("fact-dividend-income", 1)]),
        ],
        "mapping": {"taxonomy_id": "far-2026-01", "area_id": "far.area.1", "group_id": "far.area.1.group.a", "topic_id": "far.area.1.group.a.topic.3", "representative_task_id": "far.area.1.group.a.topic.3.task.002", "skill_level": "remembering_and_understanding", "mapping_rationale": "The item requires identifying which stated item is classified in OCI.", "mcq_scope_limit": "The MCQ tests classification of a bounded set and does not prepare a complete statement of comprehensive income."},
        "model_id": "far-model-oci-classification",
        "solution": {
            "end_ask": "Identify and total the stated pretax OCI components.",
            "representation": {"kind": "classification", "setup": "Pretax OCI = included OCI items; exclude items reported in net income."},
            "steps": [
                step(1, "Classify each item as OCI or earnings.", ["fact-afs-gain", "fact-trading-gain", "fact-equipment-loss", "fact-dividend-income"], ["assertion-afs-debt-oci", "assertion-earnings-items-excluded"], "Only the available-for-sale debt unrealized gain is OCI."),
                step(2, "Total the included OCI items.", ["fact-afs-gain"], ["assertion-afs-debt-oci"], "$14,000."),
            ],
            "keyed_answer_option_id": "A", "keyed_answer_rationale": "Only the $14,000 unrealized gain on available-for-sale debt is a current-period OCI item.", "faster_or_safer_route": "First eliminate the three items explicitly reported in earnings; the remaining amount is OCI.",
        },
        "evidence_id": "evidence-oci-classification", "key_terms": [("fact-afs-gain", 1)],
        "rule_application": "The rule includes the available-for-sale debt gain and excludes the three earnings items.",
        "challenges": [challenge("classification", "Four familiar income-related items cross the OCI-versus-earnings boundary."), challenge("elimination_leverage", "Three options each embody one named over-inclusion or netting error."), challenge("financial_statement_view", "The end ask is a pretax statement-of-comprehensive-income amount.")],
        "difficulty": difficulty(levels=(1, 1, 2, 2, 2, 1), rule_count=1, step_count=2, irrelevant_count=3, boundary_count=2, operation_count=0),
    },
    {
        "question_id": "far-q-000102",
        "rule_id": "far-rule-indirect-operating-cash-flow",
        "rule_title": "Indirect-method operating cash flow reconciliation",
        "rule_statement": "Under the indirect method, net income is adjusted for noncash items, gains or losses whose cash effects belong outside operating activities, and changes in operating assets and liabilities; dividends paid are financing cash flows.",
        "rule_applicability": "For-profit entity statement of cash flows using the indirect method.",
        "assertions": [
            {"assertion_id": "assertion-indirect-reconciliation", "claim": "Add depreciation and operating-liability increases, subtract disposal gains and operating-asset increases, and add operating-asset decreases in reconciling net income to operating cash flow."},
            {"assertion_id": "assertion-dividends-financing", "claim": "Cash dividends paid are financing cash outflows and do not adjust operating cash flow."},
        ],
        "source_locator": "FASB ASC 230-10-45-28 through 45-29 and 230-10-45-15 (live official Codification)",
        "currency_basis": "The live official Codification locators and FASB-hosted Statement 95 materials were cross-checked on 2026-08-13; no effective amendment affecting the stated classifications was identified.",
        "stem": "A company using the indirect method reports net income of $120,000, depreciation expense of $25,000, a gain on sale of equipment of $8,000, an $18,000 increase in accounts receivable, a $7,000 decrease in inventory, a $6,000 increase in accounts payable, and $10,000 of cash dividends paid. All stated working-capital changes relate to operations. What amount should the company report as net cash provided by operating activities?",
        "facts": [
            fact("fact-net-income", "Net income is $120,000.", 120000, relevance="relevant", use="Starting point for the indirect reconciliation."),
            fact("fact-depreciation", "Depreciation expense is $25,000.", 25000, relevance="relevant", use="Added back as a noncash expense."),
            fact("fact-sale-gain", "The equipment-sale gain is $8,000.", 8000, relevance="relevant", use="Subtracted because the gain is included in net income."),
            fact("fact-ar-increase", "Accounts receivable increased $18,000.", 18000, relevance="relevant", use="Subtracted as an operating-asset increase."),
            fact("fact-inventory-decrease", "Inventory decreased $7,000.", 7000, relevance="relevant", use="Added as an operating-asset decrease."),
            fact("fact-ap-increase", "Accounts payable increased $6,000.", 6000, relevance="relevant", use="Added as an operating-liability increase."),
            fact("fact-dividends-paid", "Cash dividends paid are $10,000.", 10000, relevance="irrelevant", reason="Dividends paid are a financing cash flow."),
        ],
        "assumptions": [{"assumption_id": "assumption-working-capital-operating", "statement": "All stated working-capital changes relate to operating activities.", "basis": "explicit_in_stem"}],
        "options": [
            option("A", "$132,000", 132000, keyed=True),
            option("B", "$150,000", 150000, error_id="error-omit-receivable-change", name="Omit receivable increase", misconception="Fails to subtract the operating-asset increase.", derivation="$120,000 + $25,000 - $8,000 + $7,000 + $6,000 = $150,000.", terms=[("fact-net-income", 1), ("fact-depreciation", 1), ("fact-sale-gain", -1), ("fact-inventory-decrease", 1), ("fact-ap-increase", 1)]),
            option("C", "$148,000", 148000, error_id="error-add-sale-gain", name="Add sale gain", misconception="Adds rather than subtracts a gain already included in net income.", derivation="$120,000 + $25,000 + $8,000 - $18,000 + $7,000 + $6,000 = $148,000.", terms=[("fact-net-income", 1), ("fact-depreciation", 1), ("fact-sale-gain", 1), ("fact-ar-increase", -1), ("fact-inventory-decrease", 1), ("fact-ap-increase", 1)]),
            option("D", "$122,000", 122000, error_id="error-subtract-dividends", name="Subtract financing dividend", misconception="Treats dividends paid as an operating adjustment.", derivation="$132,000 - $10,000 = $122,000.", terms=[("fact-net-income", 1), ("fact-depreciation", 1), ("fact-sale-gain", -1), ("fact-ar-increase", -1), ("fact-inventory-decrease", 1), ("fact-ap-increase", 1), ("fact-dividends-paid", -1)]),
        ],
        "mapping": {"taxonomy_id": "far-2026-01", "area_id": "far.area.1", "group_id": "far.area.1.group.a", "topic_id": "far.area.1.group.a.topic.5", "representative_task_id": "far.area.1.group.a.topic.5.task.001", "skill_level": "application", "mapping_rationale": "The item applies the indirect reconciliation to supporting balances and transactions.", "mcq_scope_limit": "The MCQ computes one operating subtotal and does not prepare the complete statement or disclosures."},
        "model_id": "far-model-indirect-cash-flow",
        "solution": {
            "end_ask": "Reconcile net income to net cash provided by operating activities.",
            "representation": {"kind": "formula", "setup": "CFO = net income + noncash expenses - disposal gains - operating-asset increases + operating-asset decreases + operating-liability increases."},
            "steps": [
                step(1, "Separate operating reconciliation items from the financing dividend.", ["fact-dividends-paid"], ["assertion-dividends-financing"], "Exclude the $10,000 dividend from CFO."),
                step(2, "Assign each operating adjustment its indirect-method sign.", ["fact-depreciation", "fact-sale-gain", "fact-ar-increase", "fact-inventory-decrease", "fact-ap-increase"], ["assertion-indirect-reconciliation"], "Add depreciation, inventory decrease, and payables increase; subtract the gain and receivables increase."),
                step(3, "Apply the signed adjustments to net income.", ["fact-net-income", "fact-depreciation", "fact-sale-gain", "fact-ar-increase", "fact-inventory-decrease", "fact-ap-increase"], ["assertion-indirect-reconciliation"], "$120,000 + $25,000 - $8,000 - $18,000 + $7,000 + $6,000 = $132,000."),
            ],
            "keyed_answer_option_id": "A", "keyed_answer_rationale": "The correctly signed operating adjustments reconcile net income to $132,000; dividends paid stay in financing.", "faster_or_safer_route": "Mark each change with a plus or minus before doing arithmetic, and cross out the financing dividend.",
        },
        "evidence_id": "evidence-indirect-cfo", "key_terms": [("fact-net-income", 1), ("fact-depreciation", 1), ("fact-sale-gain", -1), ("fact-ar-increase", -1), ("fact-inventory-decrease", 1), ("fact-ap-increase", 1)],
        "rule_application": "The indirect-method signs are applied to each operating fact; the financing dividend is excluded.",
        "challenges": [challenge("formula_translation", "Six operating facts must be translated into a signed reconciliation."), challenge("fact_selection", "The financing dividend is stated with otherwise operating-reconciliation data."), challenge("time_pressure", "Five signed arithmetic operations follow the classification pass."), challenge("journal_effect", "Working-capital account direction determines the cash-flow adjustment sign.")],
        "difficulty": difficulty(levels=(3, 3, 3, 3, 3, 3), rule_count=1, step_count=3, irrelevant_count=1, boundary_count=4, operation_count=5),
    },
    {
        "question_id": "far-q-000103",
        "rule_id": "far-rule-cash-equivalent-original-maturity",
        "rule_title": "Cash-equivalent original-maturity convention",
        "rule_statement": "Cash equivalents are short-term, highly liquid investments readily convertible to known cash and so near maturity that interest-rate risk is insignificant; generally only investments with an original maturity to the holder of three months or less qualify.",
        "rule_applicability": "For-profit entity classifying highly liquid investments as cash equivalents under U.S. GAAP.",
        "assertions": [
            {"assertion_id": "assertion-three-month-original-maturity", "claim": "Apply the generally three-month-or-less test from the acquisition date to maturity, not from the reporting date."},
            {"assertion_id": "assertion-cash-included", "claim": "Unrestricted checking deposits are cash and are included with qualifying cash equivalents."},
        ],
        "source_locator": "FASB ASC Master Glossary definitions of Cash and Cash Equivalents (also reflected in ASC 230-10-20)",
        "currency_basis": "The live official Codification glossary and FASB-hosted EITF Issue 16-A materials reproducing the definition were cross-checked on 2026-08-13; no effective amendment affecting the convention was identified.",
        "stem": "At year-end, a company has $40,000 in an unrestricted checking account. It also holds a $25,000 Treasury bill acquired with 76 days to maturity, a $30,000 Treasury note acquired with 106 days to maturity, and $15,000 of commercial paper acquired with 95 days to maturity. All three investments are highly liquid and readily convertible to known cash; the Treasury note pays 5% interest. What total should the company report as cash and cash equivalents?",
        "facts": [
            fact("fact-checking", "The unrestricted checking balance is $40,000.", 40000, relevance="relevant", use="Included as cash."),
            fact("fact-tbill", "The Treasury bill amount is $25,000.", 25000, relevance="relevant", use="Included because its original maturity to the holder is within three months."),
            fact("fact-tbill-days", "The Treasury bill had 76 days to maturity when acquired.", 76, relevance="relevant", use="Establishes that the bill meets the original-maturity convention.", unit="days"),
            fact("fact-tnote", "The Treasury note amount is $30,000.", 30000, relevance="irrelevant", reason="Its original maturity to the holder exceeds three months."),
            fact("fact-tnote-days", "The Treasury note had 106 days to maturity when acquired.", 106, relevance="irrelevant", reason="This exceeds the generally three-month original-maturity convention.", unit="days"),
            fact("fact-paper", "The commercial paper amount is $15,000.", 15000, relevance="irrelevant", reason="Its original maturity to the holder exceeds three months."),
            fact("fact-paper-days", "The commercial paper had 95 days to maturity when acquired.", 95, relevance="irrelevant", reason="This exceeds the generally three-month original-maturity convention.", unit="days"),
            fact("fact-note-rate", "The Treasury note interest rate is 5%.", 5, relevance="irrelevant", reason="The coupon rate does not replace the stated original-maturity test.", unit="percent"),
        ],
        "assumptions": [{"assumption_id": "assumption-liquid-known-cash", "statement": "All three investments are highly liquid and readily convertible to known amounts of cash.", "basis": "explicit_in_stem"}],
        "options": [
            option("A", "$65,000", 65000, keyed=True),
            option("B", "$95,000", 95000, error_id="error-include-nearby-note", name="Include Treasury note", misconception="Uses short remaining maturity at year-end instead of original maturity to the holder.", derivation="$40,000 + $25,000 + $30,000 = $95,000.", terms=[("fact-checking", 1), ("fact-tbill", 1), ("fact-tnote", 1)]),
            option("C", "$80,000", 80000, error_id="error-include-commercial-paper", name="Include commercial paper", misconception="Treats a 95-day original maturity as within three months.", derivation="$40,000 + $25,000 + $15,000 = $80,000.", terms=[("fact-checking", 1), ("fact-tbill", 1), ("fact-paper", 1)]),
            option("D", "$40,000", 40000, error_id="error-exclude-all-investments", name="Exclude all investments", misconception="Treats cash equivalents as cash deposits only.", derivation="Include only the $40,000 checking balance.", terms=[("fact-checking", 1)]),
        ],
        "mapping": {"taxonomy_id": "far-2026-01", "area_id": "far.area.2", "group_id": "far.area.2.group.a", "topic_id": None, "representative_task_id": "far.area.2.group.a.task.001", "skill_level": "application", "mapping_rationale": "The item applies the cash-equivalent definition to calculate the reported balance.", "mcq_scope_limit": "The MCQ tests a bounded maturity classification and not all restrictions, overdrafts, or presentation issues."},
        "model_id": "far-model-cash-equivalents",
        "solution": {
            "end_ask": "Calculate the cash and cash equivalents total using original maturity to the holder.",
            "representation": {"kind": "classification", "setup": "Cash and cash equivalents = unrestricted cash + qualifying investments acquired with three months or less to maturity."},
            "steps": [
                step(1, "Classify each investment using maturity at acquisition.", ["fact-tbill", "fact-tbill-days", "fact-tnote", "fact-tnote-days", "fact-paper", "fact-paper-days", "fact-note-rate"], ["assertion-three-month-original-maturity"], "Only the 76-day Treasury bill qualifies; 106 days and 95 days exceed the convention, and the coupon rate is not decisive."),
                step(2, "Add qualifying cash and investments.", ["fact-checking", "fact-tbill"], ["assertion-cash-included", "assertion-three-month-original-maturity"], "$40,000 + $25,000 = $65,000."),
            ],
            "keyed_answer_option_id": "A", "keyed_answer_rationale": "The checking deposit and 76-day Treasury bill qualify; the other investments exceed three months at acquisition.", "faster_or_safer_route": "Circle the acquisition-to-maturity days first; ignore the coupon rate and eliminate investments over three months.",
        },
        "evidence_id": "evidence-cash-equivalents", "key_terms": [("fact-checking", 1), ("fact-tbill", 1)],
        "rule_application": "The acquisition-date maturity convention includes the Treasury bill and excludes the longer-original-maturity instruments.",
        "challenges": [challenge("convention", "The three-month test is measured from acquisition, not from year-end."), challenge("fact_selection", "The coupon rate and nonqualifying investment amounts are numerical noise for the end ask."), challenge("language_trap", "A Treasury note can be near maturity at year-end yet fail based on original maturity to the holder."), challenge("classification", "Cash, qualifying equivalents, and nonqualifying short-term investments must be separated.")],
        "difficulty": difficulty(levels=(2, 2, 4, 4, 3, 2), rule_count=1, step_count=2, irrelevant_count=5, boundary_count=3, operation_count=1),
    },
    {
        "question_id": "far-q-000104",
        "rule_id": "far-rule-inventory-rollforward-reconciliation",
        "rule_title": "Inventory cost rollforward and physical reconciliation",
        "rule_statement": "Inventory is measured on a cost basis subject to applicable subsequent-measurement rules; a cost rollforward adds inventory purchases and subtracts cost assigned to goods sold and supplier returns, and the resulting book balance is reconciled to inventory on hand.",
        "rule_applicability": "For-profit entity inventory carried at cost where no lower-measurement adjustment is stated.",
        "assertions": [
            {"assertion_id": "assertion-inventory-cost-balance", "claim": "Ending book inventory equals beginning inventory plus purchases minus cost of goods sold minus returns to suppliers for the stated fact pattern."},
            {"assertion_id": "assertion-reconcile-physical", "claim": "The general-ledger balance is adjusted to the supported physical inventory amount when the difference is valid and no other reconciling item remains."},
        ],
        "source_locator": "FASB ASC 330-10-30-1 and 330-10-35-1A through 35-1B (live official Codification)",
        "currency_basis": "The live official Codification locators and FASB-hosted Update 2015-11 materials were cross-checked on 2026-08-13; no effective amendment affecting cost measurement for these facts was identified.",
        "stem": "An inventory analyst is reconciling records that show beginning inventory of $180,000, purchases received of $520,000, cost of goods sold of $470,000, returns to suppliers of $20,000, and a supported physical count of $205,000. Sales revenue was $700,000. All inventory amounts are at cost, no write-down is indicated, and the source records are complete. What adjustment should be made to the inventory general ledger?",
        "facts": [
            fact("fact-beginning-inventory", "Beginning inventory is $180,000.", 180000, relevance="relevant", use="Opening balance in the rollforward."),
            fact("fact-purchases", "Purchases received are $520,000.", 520000, relevance="relevant", use="Added to the rollforward."),
            fact("fact-cogs", "Cost of goods sold is $470,000.", 470000, relevance="relevant", use="Subtracted from the rollforward."),
            fact("fact-supplier-returns", "Returns to suppliers are $20,000.", 20000, relevance="relevant", use="Subtracted from purchases in the rollforward."),
            fact("fact-physical-inventory", "Supported physical inventory is $205,000.", 205000, relevance="relevant", use="Target supported ending balance."),
            fact("fact-sales-revenue", "Sales revenue is $700,000.", 700000, relevance="irrelevant", reason="Revenue does not enter this cost-basis inventory rollforward."),
        ],
        "assumptions": [
            {"assumption_id": "assumption-records-complete", "statement": "The stated source records are complete and the physical count is supported.", "basis": "explicit_in_stem"},
            {"assumption_id": "assumption-inventory-at-cost", "statement": "All inventory amounts are measured at cost and no lower-measurement adjustment is indicated.", "basis": "explicit_in_stem"},
        ],
        "options": [
            option("A", "$5,000 decrease", -5000, keyed=True),
            option("B", "$5,000 increase", 5000, error_id="error-reverse-adjustment", name="Reverse adjustment direction", misconception="Computes book minus physical instead of the adjustment needed to move book to physical.", derivation="$210,000 book - $205,000 physical = a mistaken $5,000 increase.", terms=[("fact-beginning-inventory", 1), ("fact-purchases", 1), ("fact-cogs", -1), ("fact-supplier-returns", -1), ("fact-physical-inventory", -1)]),
            option("C", "No adjustment", 0, error_id="error-assume-agreement", name="Assume records agree", misconception="Stops after accepting the physical count without comparing it to the rollforward.", derivation="Records a zero adjustment.", terms=[("fact-beginning-inventory", 0)]),
            option("D", "$25,000 decrease", -25000, error_id="error-omit-supplier-returns", name="Omit supplier returns", misconception="Leaves returned goods in the book rollforward.", derivation="$205,000 - ($180,000 + $520,000 - $470,000) = a $25,000 decrease.", terms=[("fact-physical-inventory", 1), ("fact-beginning-inventory", -1), ("fact-purchases", -1), ("fact-cogs", 1)]),
        ],
        "mapping": {"taxonomy_id": "far-2026-01", "area_id": "far.area.2", "group_id": "far.area.2.group.c", "topic_id": None, "representative_task_id": "far.area.2.group.c.task.004", "skill_level": "analysis", "mapping_rationale": "The item reconciles inventory source data to the general-ledger amount and determines the adjustment.", "mcq_scope_limit": "The MCQ supplies resolved source data and does not fully exercise investigation across documents or correction entries."},
        "model_id": "far-model-inventory-rollforward",
        "solution": {
            "end_ask": "Determine the signed adjustment that moves book inventory to the supported physical amount.",
            "representation": {"kind": "roll_forward", "setup": "Book ending inventory = beginning + purchases - COGS - supplier returns; adjustment = physical - book."},
            "steps": [
                step(1, "Build the book inventory rollforward.", ["fact-beginning-inventory", "fact-purchases", "fact-cogs", "fact-supplier-returns"], ["assertion-inventory-cost-balance"], "$180,000 + $520,000 - $470,000 - $20,000 = $210,000."),
                step(2, "Compare supported physical inventory with the book balance.", ["fact-physical-inventory"], ["assertion-reconcile-physical"], "$205,000 - $210,000 = $(5,000)."),
                step(3, "Translate the signed difference into the ledger action.", ["fact-physical-inventory"], ["assertion-reconcile-physical"], "Decrease inventory by $5,000."),
            ],
            "keyed_answer_option_id": "A", "keyed_answer_rationale": "Book inventory is $210,000 and supported physical inventory is $205,000, so the ledger must decrease $5,000.", "faster_or_safer_route": "Write the rollforward signs before calculating, then use target minus book to preserve adjustment direction.",
        },
        "evidence_id": "evidence-inventory-adjustment", "key_terms": [("fact-physical-inventory", 1), ("fact-beginning-inventory", -1), ("fact-purchases", -1), ("fact-cogs", 1), ("fact-supplier-returns", 1)],
        "rule_application": "The cost rollforward yields the book balance, which is compared with the supported physical amount to derive the signed adjustment.",
        "challenges": [challenge("roll_forward", "Five cost-basis facts form a source-data reconciliation."), challenge("fact_selection", "Sales revenue is plausible business data but irrelevant to the inventory cost rollforward."), challenge("elimination_leverage", "Adjustment direction and omitted supplier returns diagnose two distractors."), challenge("journal_effect", "A negative target-minus-book difference requires a credit to inventory.")],
        "difficulty": difficulty(levels=(3, 3, 2, 3, 3, 3), rule_count=1, step_count=3, irrelevant_count=1, boundary_count=3, operation_count=4),
    },
    {
        "question_id": "far-q-000105",
        "rule_id": "far-rule-loss-contingency-range",
        "rule_title": "Loss contingency range measurement",
        "rule_statement": "When a probable loss is reasonably estimable as a range and no amount within the range is a better estimate than another, the minimum amount in the range is accrued; a merely reasonably possible separate loss is not accrued.",
        "rule_applicability": "For-profit entity loss contingencies under U.S. GAAP with the stated likelihood and estimability conclusions.",
        "assertions": [
            {"assertion_id": "assertion-range-minimum", "claim": "Accrue the minimum of a probable loss range when no point in the range is a better estimate."},
            {"assertion_id": "assertion-possible-not-accrued", "claim": "Do not accrue a separate loss assessed as reasonably possible rather than probable."},
        ],
        "source_locator": "FASB ASC 450-20-25-2 and 450-20-30-1 (live official Codification)",
        "currency_basis": "The live official Codification locators and FASB-hosted 2023 Financial Reporting Issues Conference materials reproducing paragraph 450-20-30-1 were cross-checked on 2026-08-13; no effective amendment affecting this measurement rule was identified.",
        "stem": "A company concludes that a litigation loss is probable and estimates the loss between $300,000 and $500,000, with no amount in the range a better estimate than another. A separate claim has a reasonably possible loss of $200,000. What total loss should the company accrue?",
        "facts": [
            fact("fact-range-minimum", "The probable loss range minimum is $300,000.", 300000, relevance="relevant", use="Accrued because no point is a better estimate."),
            fact("fact-range-maximum", "The probable loss range maximum is $500,000.", 500000, relevance="irrelevant", reason="The maximum is not accrued when no point is a better estimate."),
            fact("fact-possible-loss", "The separate reasonably possible loss is $200,000.", 200000, relevance="irrelevant", reason="A reasonably possible loss is not accrued under the stated facts."),
        ],
        "options": [
            option("A", "$300,000 accrued", 300000, keyed=True),
            option("B", "$500,000", 500000, error_id="error-accrue-range-maximum", name="Accrue maximum", misconception="Uses conservatism to select the high end despite no better estimate.", derivation="Accrue the $500,000 maximum.", terms=[("fact-range-maximum", 1)]),
            option("C", "$400,000", 400000, error_id="error-accrue-midpoint", name="Accrue midpoint", misconception="Averages the endpoints without evidence that the midpoint is a better estimate.", derivation="($300,000 + $500,000) / 2 = $400,000.", terms=[("fact-range-minimum", 0.5), ("fact-range-maximum", 0.5)]),
            option("D", "$700,000", 700000, error_id="error-accrue-possible-loss", name="Accrue possible claim", misconception="Adds a merely reasonably possible claim to the probable range maximum.", derivation="$500,000 + $200,000 = $700,000.", terms=[("fact-range-maximum", 1), ("fact-possible-loss", 1)]),
        ],
        "mapping": {"taxonomy_id": "far-2026-01", "area_id": "far.area.3", "group_id": "far.area.3.group.b", "topic_id": None, "representative_task_id": "far.area.3.group.b.task.002", "skill_level": "application", "mapping_rationale": "The item applies recognition and range-measurement rules to calculate the accrued contingency.", "mcq_scope_limit": "The MCQ calculates one accrual and does not draft the full journal entry or disclosures."},
        "model_id": "far-model-loss-contingency-range",
        "solution": {
            "end_ask": "Calculate the amount accrued for the stated loss contingencies.",
            "representation": {"kind": "rule_selection", "setup": "Accrual = minimum of probable estimable range when no point is better; exclude reasonably possible claim."},
            "steps": [
                step(1, "Select the measurement rule for the probable range.", ["fact-range-minimum", "fact-range-maximum"], ["assertion-range-minimum"], "Use the $300,000 minimum because no amount is a better estimate."),
                step(2, "Apply the likelihood threshold to the separate claim.", ["fact-possible-loss"], ["assertion-possible-not-accrued"], "Exclude the $200,000 reasonably possible loss from accrual."),
            ],
            "keyed_answer_option_id": "A", "keyed_answer_rationale": "The minimum of the probable range is accrued, and the separate reasonably possible claim is not accrued.", "faster_or_safer_route": "Underline 'no amount is a better estimate' and 'reasonably possible'; those phrases determine the minimum and exclusion without averaging.",
        },
        "evidence_id": "evidence-contingency-range", "key_terms": [("fact-range-minimum", 1)],
        "rule_application": "The minimum of the probable range is selected and the separate reasonably possible loss is excluded.",
        "challenges": [challenge("convention", "The minimum-of-range rule applies only because no point is a better estimate."), challenge("rule_selection", "The probable range and reasonably possible claim require different recognition outcomes."), challenge("language_trap", "The midpoint and maximum appear prudent but are unsupported by the stated estimation conclusion."), challenge("elimination_leverage", "Likelihood wording eliminates the option that accrues both matters.")],
        "difficulty": difficulty(levels=(2, 2, 2, 4, 3, 2), rule_count=1, step_count=2, irrelevant_count=2, boundary_count=3, operation_count=0),
    },
    {
        "question_id": "far-q-000106",
        "rule_id": "far-rule-subsequent-event-recognition",
        "rule_title": "Recognized and nonrecognized subsequent events",
        "rule_statement": "A subsequent event is recognized when it provides additional evidence about conditions existing at the balance-sheet date; an event evidencing conditions arising after that date is not recognized in those statements, although material nonrecognized events may require disclosure.",
        "rule_applicability": "For-profit entity evaluating events after year-end but before financial statements are issued.",
        "assertions": [
            {"assertion_id": "assertion-recognized-subsequent-event", "claim": "Recognize the effects of subsequent evidence about a condition that existed at the balance-sheet date."},
            {"assertion_id": "assertion-nonrecognized-subsequent-event", "claim": "Do not adjust for a condition arising after the balance-sheet date; disclose it if material under the applicable requirements."},
        ],
        "source_locator": "FASB ASC 855-10-25-1, 855-10-25-3, and 855-10-50-2 (live official Codification)",
        "currency_basis": "The live official Codification locators and FASB-hosted 2025 agenda-consultation materials quoting the recognition principle were cross-checked on 2026-08-13; no effective amendment affecting these facts was identified.",
        "stem": "Before issuing its year-end financial statements, a company learns that a customer owing $90,000 entered bankruptcy because of severe financial difficulty already present at year-end; no credit loss has yet been recorded for that receivable. A warehouse with a carrying amount of $400,000 was destroyed by a fire that began after year-end. The company also settles a year-end lawsuit for $60,000 after having accrued $35,000. After distinguishing adjustment from disclosure, what total additional loss should the company recognize in its year-end financial statements?",
        "facts": [
            fact("fact-bankrupt-receivable", "The receivable supported as impaired at year-end is $90,000.", 90000, relevance="relevant", use="Recognized because the bankruptcy confirms a year-end condition."),
            fact("fact-fire-loss", "The post-year-end warehouse carrying amount is $400,000.", 400000, relevance="irrelevant", reason="The fire condition arose after year-end and is not recognized in the year-end statements."),
            fact("fact-lawsuit-settlement", "The lawsuit settled for $60,000.", 60000, relevance="relevant", use="Provides the final amount for a year-end condition."),
            fact("fact-lawsuit-accrual", "The company already accrued $35,000 for the lawsuit.", 35000, relevance="relevant", use="Subtracted to obtain the additional lawsuit loss."),
        ],
        "assumptions": [{"assumption_id": "assumption-no-prior-credit-loss", "statement": "No credit loss has yet been recorded for the bankrupt customer's receivable.", "basis": "explicit_in_stem"}],
        "options": [
            option("A", "$115,000", 115000, keyed=True),
            option("B", "$490,000", 490000, error_id="error-recognize-fire-omit-lawsuit", name="Recognize fire and omit lawsuit update", misconception="Adjusts for the post-year-end fire but overlooks the lawsuit increment.", derivation="$90,000 + $400,000 = $490,000.", terms=[("fact-bankrupt-receivable", 1), ("fact-fire-loss", 1)]),
            option("C", "$515,000", 515000, error_id="error-recognize-all-events", name="Recognize all events", misconception="Includes the nonrecognized fire along with both recognized adjustments.", derivation="$90,000 + $400,000 + ($60,000 - $35,000) = $515,000.", terms=[("fact-bankrupt-receivable", 1), ("fact-fire-loss", 1), ("fact-lawsuit-settlement", 1), ("fact-lawsuit-accrual", -1)]),
            option("D", "$150,000", 150000, error_id="error-ignore-prior-accrual", name="Ignore prior lawsuit accrual", misconception="Adds the full settlement rather than only the increment over the existing accrual.", derivation="$90,000 + $60,000 = $150,000.", terms=[("fact-bankrupt-receivable", 1), ("fact-lawsuit-settlement", 1)]),
        ],
        "mapping": {"taxonomy_id": "far-2026-01", "area_id": "far.area.3", "group_id": "far.area.3.group.g", "topic_id": None, "representative_task_id": "far.area.3.group.g.task.003", "skill_level": "analysis", "mapping_rationale": "The item requires analyzing three event narratives to derive adjustment and disclosure consequences.", "mcq_scope_limit": "The MCQ derives a numerical adjustment but does not draft complete note disclosures or investigate source documents."},
        "model_id": "far-model-subsequent-events",
        "solution": {
            "end_ask": "Total only the additional year-end losses supported by recognized subsequent events.",
            "representation": {"kind": "financial_statement_view", "setup": "Additional loss = confirmed year-end receivable loss + (lawsuit settlement - existing accrual); exclude post-year-end fire from recognition."},
            "steps": [
                step(1, "Classify each event by when its underlying condition arose.", ["fact-bankrupt-receivable", "fact-fire-loss", "fact-lawsuit-settlement", "fact-lawsuit-accrual"], ["assertion-recognized-subsequent-event", "assertion-nonrecognized-subsequent-event"], "Recognize the bankruptcy evidence and lawsuit update; do not recognize the later-arising fire in the year-end amounts."),
                step(2, "Calculate the additional lawsuit loss.", ["fact-lawsuit-settlement", "fact-lawsuit-accrual"], ["assertion-recognized-subsequent-event"], "$60,000 - $35,000 = $25,000."),
                step(3, "Total the recognized additional losses.", ["fact-bankrupt-receivable", "fact-lawsuit-settlement", "fact-lawsuit-accrual"], ["assertion-recognized-subsequent-event"], "$90,000 + $25,000 = $115,000."),
            ],
            "keyed_answer_option_id": "A", "keyed_answer_rationale": "The bankruptcy confirms a year-end loss of $90,000 and the lawsuit needs another $25,000; the later-arising fire is not recognized.", "faster_or_safer_route": "Draw a year-end line: put pre-existing conditions on the adjustment side, later-arising conditions on the disclosure-only side, then subtract any amount already accrued.",
        },
        "evidence_id": "evidence-subsequent-events", "key_terms": [("fact-bankrupt-receivable", 1), ("fact-lawsuit-settlement", 1), ("fact-lawsuit-accrual", -1)],
        "rule_application": "The bankruptcy and lawsuit provide evidence about year-end conditions; the post-year-end fire is excluded from recognition and remains a disclosure consideration.",
        "challenges": [challenge("timing", "Three events must be placed on the correct side of the year-end condition boundary."), challenge("fact_selection", "The largest amount belongs to a nonrecognized event and is excluded from the numerical adjustment."), challenge("financial_statement_view", "The solver must distinguish additional recognized loss from disclosure-only information."), challenge("end_ask_location", "The numerical end ask follows a dense three-event narrative."), challenge("elimination_leverage", "Options reveal fire recognition and failure to net the prior accrual.")],
        "difficulty": difficulty(levels=(4, 3, 4, 4, 4, 4), rule_count=1, step_count=3, irrelevant_count=1, boundary_count=3, operation_count=2),
    },
]


def reference_record() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "reference_id": REFERENCE_ID,
        "reference_version_id": REFERENCE_VERSION_ID,
        "version_number": 1,
        "record_purpose": "admitted_evidence",
        "authority_class": "authoritative_accounting",
        "identity": {
            "issuer": "Financial Accounting Standards Board",
            "title": "FASB Accounting Standards Codification - live official research system",
            "document_id": "FASB-ASC-LIVE",
            "publication_or_update_date": "2009-06-30",
            "effective_from": "2009-09-15",
            "effective_through": None,
        },
        "retrieval": {
            "retrieved_at": STAMP,
            "locator": "https://asc.fasb.org/",
            "content_identity": "Live official FASB Codification research system; exact Topic-Subtopic-Section-Paragraph locators are recorded in each rule version.",
        },
        "currency": {
            "assessed_at": STAMP,
            "assessment": "current",
            "basis": "FASB identifies the Codification as the single official source of authoritative nongovernmental U.S. GAAP. Exact sample locators were cross-checked against the live system and official FASB-hosted materials on 2026-08-13; mutable live content must be rechecked on source change.",
        },
        "admission_basis": "The ratified source hierarchy and the 2026 FAR Blueprint expressly name the FASB Accounting Standards Codification as eligible controlling authority. This record admits only the exact locators used by the six-item P1 sample.",
    }


def calibration_ids() -> dict[str, str]:
    report = json.loads((PROJECT_ROOT / "reports" / "p1-verifier-calibration.json").read_text(encoding="utf-8"))
    return {item["check_id"]: item["calibration_fixture_id"] for item in report["checks"]}


def placeholder_checks(ids: dict[str, str]) -> list[dict[str, Any]]:
    categories = {
        "SCHEMA_CONTRACT": "SCHEMA", "RECOMPUTE_INDEPENDENT": "RECOMPUTE", "RULE_TRACE_CURRENT": "RULE_TRACE",
        "DISTRACTOR_MODELS": "DISTRACTORS", "LANGUAGE_FAIRNESS": "LANGUAGE", "ORIGINALITY_BOUNDARY": "ORIGINALITY",
        "APPROVAL_INTEGRITY": "APPROVAL_INTEGRITY", "VARIETY_EVIDENCE": "VARIETY",
    }
    return [{"check_id": check_id, "category": category, "outcome": "pass", "detail": "Generation-time placeholder replaced by actual verifier output.", "evidence": [], "calibration_fixture_ids": [ids[check_id]]} for check_id, category in categories.items()]


def build() -> None:
    reference = reference_record()
    write_json(PROJECT_ROOT / "data" / "references" / f"{REFERENCE_VERSION_ID}.json", reference)
    ids = calibration_ids()
    manifest_entries: list[dict[str, str]] = []

    for spec in SPECS:
        rule = rule_record(spec)
        identity = identity_record(spec, rule["rule_version_id"])
        question = question_record(spec, rule)
        provisional = verification_event(question, placeholder_checks(ids))
        bundle = QuestionBundle(identity, reference, rule, question, provisional, None)
        first_results = run_checks(bundle)
        if any(not result.passed for result in first_results):
            failures = "; ".join(f"{result.check_id}: {result.detail}" for result in first_results if not result.passed)
            raise RuntimeError(f"{question['question_id']} failed before emission: {failures}")
        checks = [dict(result.as_dict(), calibration_fixture_ids=[ids[result.check_id]]) for result in first_results]
        verification = verification_event(question, checks)
        bundle.verification = verification
        final_results = run_checks(bundle)
        if any(not result.passed for result in final_results):
            failures = "; ".join(f"{result.check_id}: {result.detail}" for result in final_results if not result.passed)
            raise RuntimeError(f"{question['question_id']} failed final verification: {failures}")
        readiness = derive_learner_ready(bundle, final_results)
        if readiness.learner_ready or "required_reviewer_missing" not in readiness.reasons:
            raise RuntimeError(f"{question['question_id']} did not remain candidate-only: {readiness.reasons}")

        question_dir = PROJECT_ROOT / "data" / "questions" / question["question_id"]
        identity_path = question_dir / "identity.json"
        question_path = question_dir / "versions" / f"{question['version_id']}.json"
        rule_path = PROJECT_ROOT / "data" / "rules" / rule["rule_id"] / "versions" / f"{rule['rule_version_id']}.json"
        verification_path = PROJECT_ROOT / "data" / "events" / "verification" / f"{verification['event_id']}.json"
        write_json(identity_path, identity)
        write_json(question_path, question)
        write_json(rule_path, rule)
        write_json(verification_path, verification)
        manifest_entries.append({
            "question_id": question["question_id"],
            "identity_path": identity_path.relative_to(PROJECT_ROOT).as_posix(),
            "question_path": question_path.relative_to(PROJECT_ROOT).as_posix(),
            "rule_path": rule_path.relative_to(PROJECT_ROOT).as_posix(),
            "reference_path": f"data/references/{REFERENCE_VERSION_ID}.json",
            "verification_path": verification_path.relative_to(PROJECT_ROOT).as_posix(),
        })

    manifest = {
        "schema_version": "1.0.0",
        "sample_id": SAMPLE_ID,
        "generated_at": STAMP,
        "purpose": "Bounded candidate-only cross-area sample for Gate G2 review; no item is learner-ready or counts toward coverage.",
        "items": manifest_entries,
    }
    write_json(PROJECT_ROOT / "data" / "sample" / "p1" / "manifest.json", manifest)
    print(f"PASS authored {len(manifest_entries)} candidate-only P1 sample items")


if __name__ == "__main__":
    build()
