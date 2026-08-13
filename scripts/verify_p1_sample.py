from __future__ import annotations

import argparse
import hashlib
import json
import re
from itertools import combinations
from pathlib import Path
from typing import Any

from validate_p1_records import PROJECT_ROOT, load_json
from verify_questions import QuestionBundle, derive_learner_ready, run_checks


MANIFEST_PATH = PROJECT_ROOT / "data" / "sample" / "p1" / "manifest.json"
REPORT_PATH = PROJECT_ROOT / "reports" / "p1-sample-verification.v002.json"


def load_review_history(question: dict[str, Any], project_root: Path = PROJECT_ROOT) -> list[dict[str, Any]]:
    review_dir = project_root / "data" / "events" / "review"
    if not review_dir.exists():
        return []
    events = []
    for path in review_dir.glob("*.json"):
        event = load_json(path)
        subject = event["subject"]
        if (
            subject["question_id"] == question["question_id"]
            and subject["version_id"] == question["version_id"]
            and subject["content_sha256"] == question["content_sha256"]
        ):
            events.append(event)
    return sorted(events, key=lambda event: (event["recorded_at"], event["event_id"]))


def latest_decisive_review(events: list[dict[str, Any]]) -> dict[str, Any] | None:
    decisive = [event for event in events if event["action"] != "comment"]
    return decisive[-1] if decisive else None


def load_bundles(manifest_path: Path = MANIFEST_PATH, *, include_reviews: bool = True) -> list[QuestionBundle]:
    manifest = load_json(manifest_path)
    bundles: list[QuestionBundle] = []
    for item in manifest["items"]:
        question = load_json(PROJECT_ROOT / item["question_path"])
        history = load_review_history(question) if include_reviews else []
        bundles.append(
            QuestionBundle(
                identity=load_json(PROJECT_ROOT / item["identity_path"]),
                reference=load_json(PROJECT_ROOT / item["reference_path"]),
                rule=load_json(PROJECT_ROOT / item["rule_path"]),
                question=question,
                verification=load_json(PROJECT_ROOT / item["verification_path"]),
                review=latest_decisive_review(history),
            )
        )
    return bundles


def normalized_words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.casefold())


def ngrams(text: str, size: int = 5) -> set[tuple[str, ...]]:
    words = normalized_words(text)
    return {tuple(words[index:index + size]) for index in range(max(0, len(words) - size + 1))}


def jaccard(left: set[Any], right: set[Any]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def build_report(manifest_path: Path = MANIFEST_PATH, *, include_reviews: bool = True) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    bundles = load_bundles(manifest_path, include_reviews=include_reviews)
    item_reports: list[dict[str, Any]] = []
    all_pass = True
    all_candidate_only = True

    for bundle in bundles:
        results = run_checks(bundle)
        readiness = derive_learner_ready(bundle, results)
        recorded = {item["check_id"]: item["outcome"] for item in bundle.verification["checks"]}
        observed = {item.check_id: "pass" if item.passed else "fail" for item in results}
        event_matches = recorded == observed
        candidate_only = not readiness.learner_ready and "required_reviewer_missing" in readiness.reasons
        all_pass = all_pass and all(item.passed for item in results) and event_matches
        all_candidate_only = all_candidate_only and candidate_only
        mapping = bundle.question["content"]["blueprint_mappings"][0]
        item_reports.append(
            {
                "question_id": bundle.question["question_id"],
                "version_id": bundle.question["version_id"],
                "content_sha256": bundle.question["content_sha256"],
                "area_id": mapping["area_id"],
                "skill_level": mapping["skill_level"],
                "challenge_tags": [entry["tag"] for entry in bundle.question["content"]["challenge_mechanics"]],
                "checks": [entry.as_dict() for entry in results],
                "verification_event_matches_observed_results": event_matches,
                "learner_ready": readiness.learner_ready,
                "readiness_hold_reasons": list(readiness.reasons),
            }
        )

    pairwise: list[dict[str, Any]] = []
    exact_duplicate_count = 0
    for left, right in combinations(bundles, 2):
        left_stem = left.question["content"]["stem"]
        right_stem = right.question["content"]["stem"]
        normalized_equal = normalized_words(left_stem) == normalized_words(right_stem)
        exact_duplicate_count += int(normalized_equal)
        pairwise.append(
            {
                "left_question_id": left.question["question_id"],
                "right_question_id": right.question["question_id"],
                "normalized_exact_match": normalized_equal,
                "word_5gram_jaccard": round(jaccard(ngrams(left_stem), ngrams(right_stem)), 6),
            }
        )

    areas = sorted({item["area_id"] for item in item_reports})
    skills = sorted({item["skill_level"] for item in item_reports})
    challenge_tags = sorted({tag for item in item_reports for tag in item["challenge_tags"]})
    maximum_similarity = max((item["word_5gram_jaccard"] for item in pairwise), default=0)
    review_dir = PROJECT_ROOT / "data" / "events" / "review"
    total_review_event_count = len(list(review_dir.glob("*.json"))) if include_reviews and review_dir.exists() else 0
    exact_review_event_count = sum(
        len(load_review_history(bundle.question)) for bundle in bundles
    ) if include_reviews else 0
    learner_ready_count = sum(item["learner_ready"] for item in item_reports)
    summary_pass = (
        len(bundles) == 6
        and areas == ["far.area.1", "far.area.2", "far.area.3"]
        and skills == ["analysis", "application", "remembering_and_understanding"]
        and all_pass
        and exact_duplicate_count == 0
    )
    return {
        "schema_version": "1.0.0",
        "sample_id": manifest["sample_id"],
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "summary": {
            "outcome": "pass" if summary_pass else "fail",
            "item_count": len(bundles),
            "area_ids": areas,
            "skill_levels": skills,
            "distinct_challenge_tags": challenge_tags,
            "all_checks_pass": all_pass,
            "all_items_candidate_only": all_candidate_only,
            "learner_ready_count": learner_ready_count,
            "pending_review_count": len(bundles) - learner_ready_count,
            "canonical_review_event_count": total_review_event_count,
            "exact_current_version_review_event_count": exact_review_event_count,
            "normalized_exact_stem_duplicate_count": exact_duplicate_count,
            "maximum_pairwise_word_5gram_jaccard": maximum_similarity,
            "claim_limit": "This is a bounded six-item within-bank comparison and candidate verification report, not human approval, learner readiness, external-corpus originality, or coverage-floor evidence.",
        },
        "items": item_reports,
        "within_bank_originality": pairwise,
    }


def report_bytes(report: dict[str, Any]) -> bytes:
    return (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the bounded candidate-only P1 FAR sample.")
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--output", type=Path, default=REPORT_PATH)
    args = parser.parse_args()
    report = build_report(args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(report_bytes(report))
    summary = report["summary"]
    print(
        f"{'PASS' if summary['outcome'] == 'pass' else 'FAIL'} P1 sample: "
        f"items={summary['item_count']} areas={len(summary['area_ids'])} "
        f"skills={len(summary['skill_levels'])} candidate_only={summary['all_items_candidate_only']}"
    )
    return 0 if summary["outcome"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
