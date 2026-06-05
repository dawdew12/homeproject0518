# 운영 안정화 유틸의 preflight, 비용, 브랜드 검증을 테스트한다.
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from utils.operation_guard import (
    PROJECT_ROOT,
    append_error_log,
    build_brand_registry,
    build_cost_report,
    build_preflight_report,
    save_preflight_report,
)


class OperationGuardTest(unittest.TestCase):
    def test_build_brand_registry_validates_current_brand_folders(self) -> None:
        registry = build_brand_registry(PROJECT_ROOT)

        self.assertEqual(registry["status"], "brand_registry_ready")
        self.assertEqual(registry["brand_count"], 5)
        self.assertEqual(registry["ready_brand_count"], 5)
        self.assertIn("brands/{brand}/config.toml 생성", registry["new_brand_checklist"])

    def test_build_cost_report_calculates_remaining_budget(self) -> None:
        report = build_cost_report(
            {"daily_cost_usd": 1.0, "monthly_cost_usd": 10.0},
            estimated_cost_usd=2.64,
            daily_limit_usd=5.0,
            monthly_limit_usd=79.0,
        )

        self.assertEqual(report["status"], "cost_within_limits")
        self.assertEqual(report["projected_daily_cost_usd"], 3.64)
        self.assertEqual(report["daily_remaining_usd"], 1.36)

    def test_build_preflight_report_can_be_saved(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as tmp_dir:
            root = Path(tmp_dir)
            report = build_preflight_report(
                "2026-05-18",
                {"daily_cost_usd": 0, "monthly_cost_usd": 0},
                estimated_cost_usd=2.64,
                daily_limit_usd=5.0,
                monthly_limit_usd=79.0,
                project_root=PROJECT_ROOT,
            )
            saved_path = save_preflight_report(report, root / "history", "2026-05-18")
            saved = json.loads(saved_path.read_text(encoding="utf-8"))

        self.assertEqual(saved["status"], "preflight_passed")
        self.assertEqual(saved["cost_report"]["status"], "cost_within_limits")
        self.assertEqual(saved["brand_registry"]["ready_brand_count"], 5)

    def test_append_error_log_writes_jsonl_record(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as tmp_dir:
            log_path = Path(tmp_dir) / "history" / "daily" / "2026-05-18_errors.log"
            record = append_error_log(RuntimeError("boom"), "unit_test", "2026-05-18", log_path)
            saved = json.loads(log_path.read_text(encoding="utf-8").strip())

        self.assertEqual(record["error_type"], "RuntimeError")
        self.assertEqual(saved["step"], "unit_test")
        self.assertEqual(saved["message"], "boom")


if __name__ == "__main__":
    unittest.main()
