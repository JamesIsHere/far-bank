from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from author_p1_sample import verification_event
from validate_p1_records import PROJECT_ROOT, canonical_content_sha256, load_json
from verify_questions import QuestionBundle, derive_learner_ready, run_checks


STAMP = "2026-08-13T20:15:00Z"
SAMPLE_ID = "far-p1-g2-sample.v002"
TARGET_KEYS = {
    "far-q-000102": "B",
    "far-q-000103": "C",
    "far-q-000104": "D",
    "far-q-000105": "B",
    "far-q-000106": "C",
}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def revised_question(question: dict[str, Any], target_key: str) -> dict[str, Any]:
    revised = copy.deepcopy(question)
    content = revised["content"]
    original_options = content["options"]
    keyed = next(option for option in original_options if option["is_keyed"])
    distractors = [option for option in original_options if not option["is_keyed"]]
    target_index = "ABCD".index(target_key)
    reordered = distractors[:]
    reordered.insert(target_index, keyed)
    for option_id, option in zip("ABCD", reordered):
        option["option_id"] = option_id

    content["options"] = reordered
    content["solution"]["keyed_answer_option_id"] = target_key
    content["authorship"]["created_at"] = STAMP
    content["authorship"]["material_inputs"].append(
        {
            "input_id": "far-g2-answer-position-comment-20260813",
            "input_kind": "human_brief",
            "version_or_date": "2026-08-13",
            "use": "Rebalance keyed answer positions across the six-item G2 sample following James's exact-version comment.",
        }
    )
    content["correctness_evidence"]["authorship"]["created_at"] = STAMP
    content["originality_boundary"]["compared_corpus_ids"] = [SAMPLE_ID]
    revised["version_id"] = f"{question['question_id']}.v002"
    revised["version_number"] = 2
    revised["content_sha256"] = canonical_content_sha256(content)
    return revised


def build() -> None:
    manifest_path = PROJECT_ROOT / "data" / "sample" / "p1" / "manifest.json"
    opening_manifest_path = manifest_path.with_name("manifest.v001.json")
    opening_report = PROJECT_ROOT / "reports" / "p1-sample-verification.json"
    opening_report_snapshot = PROJECT_ROOT / "reports" / "p1-sample-verification.v001.json"
    manifest = load_json(manifest_path)
    if manifest["sample_id"] != "far-p1-g2-sample.v001":
        raise RuntimeError("answer-position revision expects the v001 opening manifest")
    if not opening_manifest_path.exists():
        opening_manifest_path.write_bytes(manifest_path.read_bytes())
    if opening_report.exists() and not opening_report_snapshot.exists():
        opening_report_snapshot.write_bytes(opening_report.read_bytes())

    calibration = load_json(PROJECT_ROOT / "reports" / "p1-verifier-calibration.json")
    calibration_ids = {
        item["check_id"]: item["calibration_fixture_id"] for item in calibration["checks"]
    }

    revised_entries: list[dict[str, str]] = []
    for entry in manifest["items"]:
        question_id = entry["question_id"]
        if question_id not in TARGET_KEYS:
            revised_entries.append(entry)
            continue

        question = revised_question(load_json(PROJECT_ROOT / entry["question_path"]), TARGET_KEYS[question_id])
        identity = load_json(PROJECT_ROOT / entry["identity_path"])
        reference = load_json(PROJECT_ROOT / entry["reference_path"])
        rule = load_json(PROJECT_ROOT / entry["rule_path"])
        prior_verification = load_json(PROJECT_ROOT / entry["verification_path"])
        provisional = verification_event(question, prior_verification["checks"])
        provisional["event_id"] = f"far-verification-{question_id.removeprefix('far-q-')}-v002"
        provisional["recorded_at"] = STAMP
        provisional["input_evidence"][0]["path_or_id"] = (
            f"data/questions/{question_id}/versions/{question['version_id']}.json"
        )
        bundle = QuestionBundle(identity, reference, rule, question, provisional, None)
        results = run_checks(bundle)
        failures = [result for result in results if not result.passed]
        if failures:
            raise RuntimeError(
                f"{question_id} revision failed: "
                + "; ".join(f"{item.check_id}: {item.detail}" for item in failures)
            )
        provisional["checks"] = [
            dict(result.as_dict(), calibration_fixture_ids=[calibration_ids[result.check_id]])
            for result in results
        ]
        bundle.verification = provisional
        final_results = run_checks(bundle)
        readiness = derive_learner_ready(bundle, final_results)
        if any(not result.passed for result in final_results) or readiness.learner_ready:
            raise RuntimeError(f"{question_id} v002 did not remain a mechanically valid review candidate")

        question_path = (
            PROJECT_ROOT / "data" / "questions" / question_id / "versions" / f"{question['version_id']}.json"
        )
        verification_path = (
            PROJECT_ROOT / "data" / "events" / "verification" / f"{provisional['event_id']}.json"
        )
        if question_path.exists() or verification_path.exists():
            raise FileExistsError(f"refusing to overwrite immutable v002 artifacts for {question_id}")
        write_json(question_path, question)
        write_json(verification_path, provisional)
        revised_entry = copy.deepcopy(entry)
        revised_entry["question_path"] = question_path.relative_to(PROJECT_ROOT).as_posix()
        revised_entry["verification_path"] = verification_path.relative_to(PROJECT_ROOT).as_posix()
        revised_entries.append(revised_entry)

    revised_manifest = {
        "schema_version": "1.0.0",
        "sample_id": SAMPLE_ID,
        "generated_at": STAMP,
        "purpose": "Cross-area Gate G2 review sample revised to balance keyed answer positions; exact-version review state is derived separately and coverage remains zero until gate ratification.",
        "items": revised_entries,
    }
    write_json(manifest_path, revised_manifest)
    distribution = {letter: 0 for letter in "ABCD"}
    for entry in revised_entries:
        question = load_json(PROJECT_ROOT / entry["question_path"])
        distribution[question["content"]["solution"]["keyed_answer_option_id"]] += 1
    print(f"PASS issued answer-position-balanced {SAMPLE_ID}: {distribution}")


if __name__ == "__main__":
    build()
