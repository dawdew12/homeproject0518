# 대시보드 상태 JSON 생성 결과를 검증한다.
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_dashboard_data import build_dashboard_payload, write_dashboard_payload


class BuildDashboardDataTest(unittest.TestCase):
    def test_build_dashboard_payload_contains_phase_and_data_summaries(self) -> None:
        payload = build_dashboard_payload()

        self.assertEqual(payload["project"]["name"], "AIPR")
        self.assertEqual(payload["current_phase"]["status"], "completed")
        self.assertEqual(payload["data"]["ad"]["record_count"], 15)
        self.assertEqual(payload["data"]["trend"]["record_count"], 20)
        self.assertEqual(payload["data"]["manager"]["brand_count"], 5)
        self.assertEqual(payload["data"]["manager"]["high_priority_count"], 3)
        self.assertEqual(payload["data"]["prompts"]["prompt_count"], 20)
        self.assertEqual(payload["data"]["prompts"]["storyboard_count"], 20)
        self.assertEqual(payload["data"]["images"]["request_count"], 20)
        self.assertEqual(payload["data"]["images"]["estimated_cost_usd"], 2.64)
        self.assertEqual(payload["data"]["quality_review"]["approved_count"], 20)
        self.assertEqual(payload["data"]["quality_review"]["regeneration_required_count"], 0)
        self.assertEqual(payload["data"]["quality_review"]["avg_score"], 100.0)
        self.assertEqual(payload["data"]["winner_loser"]["winner_count"], 12)
        self.assertEqual(payload["data"]["winner_loser"]["loser_count"], 0)
        self.assertEqual(payload["data"]["winner_loser"]["pending_count"], 3)
        self.assertEqual(payload["data"]["winner_loser_patterns"]["winner_count"], 12)
        self.assertEqual(payload["data"]["storage"]["gdrive"]["planned_upload_count"], 20)
        self.assertEqual(payload["data"]["storage"]["gdrive"]["missing_file_count"], 20)
        self.assertEqual(payload["data"]["storage"]["gdrive"]["winner_upload_count"], 16)
        self.assertRegex(payload["data"]["storage"]["github_history"]["weekly_key"], r"^2026-W\d{2}$")
        self.assertEqual(payload["api"]["mode"], "static_json_rewrite")
        self.assertEqual(len(payload["api"]["endpoints"]), 8)
        self.assertEqual(payload["data"]["marketing_source_counts"]["daily"], 13)
        self.assertEqual(payload["architecture"]["overall_progress"]["total_phase_count"], 12)
        self.assertEqual(payload["architecture"]["overall_progress"]["completed_phase_count"], 12)
        self.assertEqual(payload["architecture"]["overall_progress"]["percent"], 100)
        self.assertGreaterEqual(len(payload["architecture"]["layers"]), 5)
        self.assertGreaterEqual(len(payload["architecture"]["flow"]), 8)
        self.assertGreaterEqual(len(payload["quality"]["phase_test_results"]), 7)
        self.assertEqual(len(payload["data"]["brand_snapshots"]), 5)
        self.assertEqual(len(payload["data"]["manager_preview"]), 5)
        self.assertGreaterEqual(len(payload["data"]["prompt_preview"]), 5)
        self.assertGreaterEqual(len(payload["data"]["image_preview"]), 5)
        self.assertGreaterEqual(len(payload["data"]["quality_preview"]), 5)
        self.assertGreaterEqual(len(payload["data"]["learning_preview"]), 5)
        self.assertGreaterEqual(len(payload["data"]["storage"]["gdrive_preview"]), 5)
        self.assertEqual(len(payload["operations"]["agent_status"]), 5)
        self.assertGreaterEqual(len(payload["operations"]["pipeline_steps"]), 11)
        self.assertIn("automation", payload["operations"])
        self.assertEqual(payload["operations"]["stability"]["status"], "stabilized")
        self.assertEqual(payload["operations"]["stability"]["brand_registry"]["ready_brand_count"], 5)
        self.assertGreaterEqual(len(payload["data"]["monitoring_preview"]["daily"]), 5)
        self.assertEqual(payload["next_step"]["phase"], "운영 전환")

    def test_write_dashboard_payload_creates_json_file(self) -> None:
        payload = build_dashboard_payload()

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = write_dashboard_payload(payload, Path(tmp_dir) / "latest_status.json")
            saved = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(saved["project"]["github_repo"], "https://github.com/dawdew12/homeproject0518")
        self.assertEqual(saved["verification"]["test_count"], 41)
        self.assertIn("feature_status", saved["operations"])
        self.assertTrue(output_path.name.endswith(".json"))


if __name__ == "__main__":
    unittest.main()
