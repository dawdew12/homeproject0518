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
        self.assertEqual(payload["data"]["marketing_source_counts"]["daily"], 13)
        self.assertEqual(payload["next_step"]["phase"], "PHASE 4")

    def test_write_dashboard_payload_creates_json_file(self) -> None:
        payload = build_dashboard_payload()

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = write_dashboard_payload(payload, Path(tmp_dir) / "latest_status.json")
            saved = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(saved["project"]["github_repo"], "https://github.com/dawdew12/homeproject0518")
        self.assertEqual(saved["verification"]["test_count"], 9)
        self.assertTrue(output_path.name.endswith(".json"))


if __name__ == "__main__":
    unittest.main()
