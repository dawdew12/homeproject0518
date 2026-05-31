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
        self.assertEqual(payload["data"]["marketing_source_counts"]["daily"], 13)
        self.assertEqual(payload["architecture"]["overall_progress"]["total_phase_count"], 12)
        self.assertEqual(payload["architecture"]["overall_progress"]["completed_phase_count"], 5)
        self.assertEqual(payload["architecture"]["overall_progress"]["percent"], 42)
        self.assertGreaterEqual(len(payload["architecture"]["layers"]), 5)
        self.assertGreaterEqual(len(payload["architecture"]["flow"]), 8)
        self.assertGreaterEqual(len(payload["quality"]["phase_test_results"]), 6)
        self.assertEqual(len(payload["data"]["brand_snapshots"]), 5)
        self.assertEqual(len(payload["data"]["manager_preview"]), 5)
        self.assertGreaterEqual(len(payload["data"]["prompt_preview"]), 5)
        self.assertEqual(len(payload["operations"]["agent_status"]), 5)
        self.assertGreaterEqual(len(payload["operations"]["pipeline_steps"]), 9)
        self.assertGreaterEqual(len(payload["data"]["monitoring_preview"]["daily"]), 5)
        self.assertEqual(payload["next_step"]["phase"], "PHASE 6")

    def test_write_dashboard_payload_creates_json_file(self) -> None:
        payload = build_dashboard_payload()

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = write_dashboard_payload(payload, Path(tmp_dir) / "latest_status.json")
            saved = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(saved["project"]["github_repo"], "https://github.com/dawdew12/homeproject0518")
        self.assertEqual(saved["verification"]["test_count"], 16)
        self.assertIn("feature_status", saved["operations"])
        self.assertTrue(output_path.name.endswith(".json"))


if __name__ == "__main__":
    unittest.main()
