# 팀장 분석 엔진의 daily Brief 생성을 검증한다.
from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from agents.manager import (
    analyze_daily_inputs,
    build_manager_brief,
    build_quality_review,
    build_winner_loser_learning,
    classify_winner_loser,
    read_json,
    review_images,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ManagerAnalysisTest(unittest.TestCase):
    def test_build_manager_brief_creates_brand_analysis(self) -> None:
        ad_payload = read_json(PROJECT_ROOT / "history" / "daily" / "2026-05-18_ad_data.json")
        trend_payload = read_json(PROJECT_ROOT / "history" / "daily" / "2026-05-18_trend_data.json")

        payload = build_manager_brief("2026-05-18", ad_payload, trend_payload)

        self.assertEqual(payload["status"], "manager_brief_ready")
        self.assertEqual(payload["summary"]["brand_count"], 5)
        self.assertEqual(len(payload["brands"]), 5)
        self.assertEqual(len(payload["handoff_to_prompt_engineer"]), 5)
        self.assertTrue(all(brand["creative_direction"] for brand in payload["brands"]))

    def test_priority_marks_scalable_brands(self) -> None:
        ad_payload = read_json(PROJECT_ROOT / "history" / "daily" / "2026-05-18_ad_data.json")
        trend_payload = read_json(PROJECT_ROOT / "history" / "daily" / "2026-05-18_trend_data.json")

        payload = build_manager_brief("2026-05-18", ad_payload, trend_payload)
        priority_by_brand = {brand["brand"]: brand["priority"] for brand in payload["brands"]}

        self.assertEqual(priority_by_brand["baren"], "scale")
        self.assertEqual(priority_by_brand["melliance"], "scale")
        self.assertEqual(priority_by_brand["someud"], "test")

    def test_analyze_daily_inputs_saves_manager_brief(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            payload = analyze_daily_inputs("2026-05-18", output_dir=Path(tmp_dir))
            saved_path = Path(payload["output_path"])
            saved = json.loads(saved_path.read_text(encoding="utf-8"))

        self.assertEqual(saved["date"], "2026-05-18")
        self.assertGreaterEqual(saved["summary"]["high_priority_count"], 3)
        self.assertTrue(saved_path.name.endswith("_manager_brief.json"))

    def test_build_quality_review_approves_image_dry_run_requests(self) -> None:
        image_payload = read_json(PROJECT_ROOT / "history" / "daily" / "2026-05-18_image_dry_run.json")

        payload = build_quality_review("2026-05-18", image_payload)

        self.assertEqual(payload["status"], "quality_review_ready")
        self.assertEqual(payload["summary"]["request_count"], 20)
        self.assertEqual(payload["summary"]["approved_count"], 20)
        self.assertEqual(payload["summary"]["regeneration_required_count"], 0)
        self.assertEqual(payload["summary"]["avg_score"], 100)
        self.assertTrue(payload["summary"]["no_text_rule_passed"])
        self.assertTrue(payload["summary"]["copy_space_passed"])

    def test_build_quality_review_marks_regeneration_when_rules_fail(self) -> None:
        image_payload = read_json(PROJECT_ROOT / "history" / "daily" / "2026-05-18_image_dry_run.json")
        failing_payload = deepcopy(image_payload)
        failing_request = failing_payload["requests"][0]
        failing_request["copy_space"] = "none"
        failing_request["rules"] = ["NO logo"]

        payload = build_quality_review("2026-05-18", failing_payload)
        first_review = payload["reviews"][0]

        self.assertEqual(payload["summary"]["regeneration_required_count"], 1)
        self.assertEqual(first_review["status"], "regeneration_required")
        self.assertTrue(first_review["regeneration"]["needed"])
        self.assertIn("copy_space", first_review["regeneration"]["reason"])
        self.assertIn("no_text_rule", first_review["regeneration"]["reason"])

    def test_review_images_saves_quality_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            payload = review_images("2026-05-18", output_dir=Path(tmp_dir))
            saved_path = Path(payload["output_path"])
            saved = json.loads(saved_path.read_text(encoding="utf-8"))

        self.assertEqual(saved["date"], "2026-05-18")
        self.assertEqual(saved["summary"]["approved_count"], 20)
        self.assertTrue(saved_path.name.endswith("_quality_review.json"))

    def test_build_winner_loser_learning_classifies_mock_records(self) -> None:
        ad_payload = read_json(PROJECT_ROOT / "history" / "daily" / "2026-05-18_ad_data.json")

        payload = build_winner_loser_learning("2026-05-18", ad_payload)
        summary = payload["summary"]
        brand_summary = {item["brand"]: item for item in payload["brand_summary"]}

        self.assertEqual(payload["status"], "winner_loser_learning_ready")
        self.assertEqual(summary["record_count"], 15)
        self.assertEqual(summary["winner_count"], 12)
        self.assertEqual(summary["loser_count"], 0)
        self.assertEqual(summary["pending_count"], 3)
        self.assertEqual(summary["winner_rate"], 0.8)
        self.assertEqual(brand_summary["melliance"]["winner_count"], 3)
        self.assertEqual(brand_summary["baren"]["winner_count"], 3)
        self.assertEqual(brand_summary["kinda"]["winner_count"], 3)
        self.assertEqual(brand_summary["paperback"]["winner_count"], 3)
        self.assertEqual(brand_summary["someud"]["pending_count"], 3)

    def test_build_winner_loser_learning_marks_loser_when_cpa_spikes(self) -> None:
        ad_payload = read_json(PROJECT_ROOT / "history" / "daily" / "2026-05-18_ad_data.json")
        failing_payload = deepcopy(ad_payload)
        failing_payload["records"][0]["metrics"]["ctr"] = 0.4
        failing_payload["records"][0]["metrics"]["roas"] = 90
        failing_payload["records"][0]["metrics"]["cpa"] = 99

        payload = build_winner_loser_learning("2026-05-18", failing_payload)
        first_record = payload["records"][0]

        self.assertEqual(first_record["label"], "loser")
        self.assertEqual(first_record["reason"], "performance_drop_detected")
        self.assertGreaterEqual(payload["summary"]["loser_count"], 1)

    def test_classify_winner_loser_saves_daily_and_patterns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir)
            pattern_path = output_dir / "winner_loser_patterns.json"
            pattern_path.write_text('{"updated_at": null, "brands": {}}', encoding="utf-8-sig")
            payload = classify_winner_loser(
                "2026-05-18",
                output_dir=output_dir,
                pattern_path=pattern_path,
            )
            saved_path = Path(payload["output_path"])
            saved = json.loads(saved_path.read_text(encoding="utf-8"))
            patterns = json.loads(pattern_path.read_text(encoding="utf-8"))

        self.assertTrue(saved_path.name.endswith("_winner_loser.json"))
        self.assertEqual(saved["summary"]["winner_count"], 12)
        self.assertEqual(patterns["summary"]["winner_count"], 12)
        self.assertEqual(len(patterns["brands"]["baren"]["winners"]), 3)
        self.assertEqual(len(patterns["brands"]["someud"]["pending"]), 3)


if __name__ == "__main__":
    unittest.main()
