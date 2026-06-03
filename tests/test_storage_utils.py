# 저장소 연동 유틸의 dry-run manifest 생성을 검증한다.
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from utils.gdrive_upload import (
    DEFAULT_DAILY_DIR,
    PROJECT_ROOT,
    build_upload_manifest,
    read_json,
    upload_outputs,
)
from utils.github_history import commit_history, summarize_daily_history


class StorageUtilsTest(unittest.TestCase):
    def test_build_upload_manifest_groups_requests_by_brand_learning_label(self) -> None:
        image_payload = read_json(DEFAULT_DAILY_DIR / "2026-05-18_image_dry_run.json", {})
        winner_loser_payload = read_json(DEFAULT_DAILY_DIR / "2026-05-18_winner_loser.json", {})

        manifest = build_upload_manifest("2026-05-18", image_payload, winner_loser_payload)

        self.assertEqual(manifest["status"], "gdrive_upload_manifest_ready")
        self.assertEqual(manifest["summary"]["request_count"], 20)
        self.assertEqual(manifest["summary"]["planned_upload_count"], 20)
        self.assertEqual(manifest["summary"]["existing_file_count"], 0)
        self.assertEqual(manifest["summary"]["missing_file_count"], 20)
        self.assertEqual(manifest["summary"]["classification_counts"]["winner"], 16)
        self.assertEqual(manifest["summary"]["classification_counts"]["pending"], 4)
        self.assertTrue(manifest["items"][0]["drive_path"].startswith("AIPR_소재관리/someud/2026-05-18/pending/"))

    def test_upload_outputs_saves_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            manifest = upload_outputs(date="2026-05-18", output_dir=Path(tmp_dir))
            saved_path = Path(tmp_dir) / "2026-05-18_gdrive_manifest.json"
            saved = json.loads(saved_path.read_text(encoding="utf-8"))

        self.assertEqual(manifest["summary"]["planned_upload_count"], 20)
        self.assertEqual(saved["summary"]["classification_counts"]["winner"], 16)

    def test_summarize_daily_history_collects_phase_outputs(self) -> None:
        summary = summarize_daily_history(PROJECT_ROOT / "history", "2026-05-18")
        metrics = summary["summary"]["metrics"]

        self.assertEqual(summary["status"], "github_history_summary_ready")
        self.assertEqual(summary["weekly_key"], "2026-W21")
        self.assertGreaterEqual(summary["summary"]["daily_file_count"], 7)
        self.assertEqual(metrics["winner_count"], 12)
        self.assertEqual(metrics["pending_count"], 3)
        self.assertEqual(metrics["image_request_count"], 20)
        self.assertEqual(metrics["approved_count"], 20)

    def test_commit_history_dry_run_writes_daily_and_weekly_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = commit_history(date="2026-05-18", output_root=Path(tmp_dir), dry_run=True)
            daily_path = Path(tmp_dir) / "daily" / "2026-05-18_github_history_summary.json"
            weekly_path = Path(tmp_dir) / "weekly" / "2026-W21.json"

            self.assertTrue(daily_path.exists())
            self.assertTrue(weekly_path.exists())

        self.assertEqual(result["status"], "github_history_dry_run_ready")
        self.assertEqual(result["summary"]["metrics"]["prompt_count"], 20)
        self.assertEqual(result["planned_commit"]["message"], "[HISTORY] 2026-05-18 daily run summary")


if __name__ == "__main__":
    unittest.main()
