# 광고 데이터 수집기의 mock 저장과 재시도 동작을 검증한다.
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agents.data_collector import BRANDS, collect_ad_data, retry_call, save_ad_data


class DataCollectorTest(unittest.TestCase):
    def test_collect_ad_data_returns_mock_records_for_all_sources_and_brands(self) -> None:
        payload = collect_ad_data("2026-05-18")

        self.assertEqual(payload["date"], "2026-05-18")
        self.assertEqual(payload["status"], "mock_collected")
        self.assertEqual(payload["summary"]["source_count"], 3)
        self.assertEqual(payload["summary"]["brand_count"], len(BRANDS))
        self.assertEqual(payload["summary"]["record_count"], 3 * len(BRANDS))
        self.assertEqual(len(payload["records"]), 3 * len(BRANDS))
        self.assertIn("ctr", payload["records"][0]["metrics"])

    def test_save_ad_data_writes_daily_json(self) -> None:
        payload = collect_ad_data("2026-05-18")

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = save_ad_data(payload, Path(tmp_dir))
            saved = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(output_path.name, "2026-05-18_ad_data.json")
        self.assertEqual(saved["summary"]["record_count"], 15)

    def test_retry_call_retries_until_success(self) -> None:
        attempts = {"count": 0}

        def flaky_call() -> str:
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise ValueError("temporary failure")
            return "ok"

        self.assertEqual(retry_call(flaky_call), "ok")
        self.assertEqual(attempts["count"], 3)


if __name__ == "__main__":
    unittest.main()
