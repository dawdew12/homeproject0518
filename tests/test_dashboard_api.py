# 대시보드 실시간 API payload 계약을 검증한다.
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import dashboard_api
from scripts.build_dashboard_data import build_dashboard_api_payloads, build_dashboard_payload, write_dashboard_api_payloads


class DashboardApiTest(unittest.TestCase):
    def test_build_dashboard_api_payloads_contains_expected_endpoints(self) -> None:
        payload = build_dashboard_payload()
        api_payloads = build_dashboard_api_payloads(payload)

        self.assertEqual(api_payloads["status"]["status"], "dashboard_status_api_ready")
        self.assertEqual(api_payloads["status"]["current_phase"]["current_phase"], 11)
        self.assertEqual(api_payloads["status"]["overall_progress"]["percent"], 92)
        self.assertEqual(api_payloads["agents"]["status"], "agents_api_ready")
        self.assertEqual(api_payloads["brands"]["brand_count"], 5)
        self.assertIn("someud", api_payloads["brand_details"])
        self.assertEqual(api_payloads["winner_loser"]["summary"]["winner_count"], 12)
        self.assertEqual(api_payloads["logs"]["status"], "logs_api_ready")

    def test_write_dashboard_api_payloads_creates_static_api_files(self) -> None:
        payload = build_dashboard_payload()

        with tempfile.TemporaryDirectory() as tmp_dir:
            written_paths = write_dashboard_api_payloads(payload, Path(tmp_dir))
            status = json.loads((Path(tmp_dir) / "status.json").read_text(encoding="utf-8"))
            someud = json.loads((Path(tmp_dir) / "brands" / "someud.json").read_text(encoding="utf-8"))
            daily_history = json.loads((Path(tmp_dir) / "history" / "daily.json").read_text(encoding="utf-8"))

        self.assertGreaterEqual(len(written_paths), 12)
        self.assertEqual(status["overall_progress"]["current_phase"], "PHASE 11")
        self.assertEqual(someud["brand"], "someud")
        self.assertEqual(daily_history["summary"]["weekly_key"], "2026-W21")

    def test_dashboard_api_functions_return_payloads_without_fastapi_dependency(self) -> None:
        status = dashboard_api.get_status()
        brand = dashboard_api.get_brand("kinda")
        missing = dashboard_api.get_brand("unknown")

        self.assertEqual(status["current_phase"]["current_phase"], 11)
        self.assertEqual(brand["status"], "brand_detail_api_ready")
        self.assertEqual(missing["status"], "brand_not_found")


if __name__ == "__main__":
    unittest.main()
