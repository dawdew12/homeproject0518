# 트렌드 수집기의 mock 저장과 재시도 동작을 검증한다.
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agents.trend_collector import (
    BRANDS,
    collect_trend_data,
    load_marketing_source_catalog,
    retry_call,
    save_trend_data,
    select_due_monitoring_sources,
)


class TrendCollectorTest(unittest.TestCase):
    def test_collect_trend_data_returns_mock_records_for_all_sources_and_brands(self) -> None:
        payload = collect_trend_data("2026-05-18")

        self.assertEqual(payload["date"], "2026-05-18")
        self.assertEqual(payload["status"], "mock_collected")
        self.assertEqual(payload["summary"]["source_count"], 4)
        self.assertEqual(payload["summary"]["brand_count"], len(BRANDS))
        self.assertEqual(payload["summary"]["record_count"], 4 * len(BRANDS))
        self.assertEqual(len(payload["records"]), 4 * len(BRANDS))
        self.assertIn("top_keywords", payload["summary"])
        self.assertGreaterEqual(payload["summary"]["daily_monitoring_source_count"], 10)
        self.assertIn("monitoring_sources", payload)

    def test_save_trend_data_writes_daily_json(self) -> None:
        payload = collect_trend_data("2026-05-18")

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = save_trend_data(payload, Path(tmp_dir))
            saved = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(output_path.name, "2026-05-18_trend_data.json")
        self.assertEqual(saved["summary"]["record_count"], 20)
        self.assertIn("daily", saved["monitoring_sources"])

    def test_load_marketing_source_catalog_reads_attached_monitoring_sources(self) -> None:
        catalog = load_marketing_source_catalog()
        daily_sources = select_due_monitoring_sources(catalog, "daily")
        daily_source_names = {source["source_name"] for source in daily_sources}

        self.assertGreaterEqual(len(catalog), 30)
        self.assertIn("Meta Ad Library", daily_source_names)
        self.assertIn("오픈애즈", daily_source_names)
        self.assertIn("네이버 광고주센터 공지사항", daily_source_names)

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
