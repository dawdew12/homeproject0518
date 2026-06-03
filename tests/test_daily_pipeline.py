# GitHub Actions 일일 파이프라인 runner와 workflow를 검증한다.
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.run_daily_pipeline import PROJECT_ROOT, run_daily_pipeline


class DailyPipelineTest(unittest.TestCase):
    def test_run_daily_pipeline_creates_expected_dry_run_outputs(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as tmp_dir:
            root = Path(tmp_dir)
            result = run_daily_pipeline(
                run_date="2026-05-18",
                history_root=root / "history",
                output_root=root / "outputs",
                runtime_path=root / "state" / "runtime.json",
                log_path=root / "logs" / "execution.log",
                pattern_path=root / "history" / "winner_loser_patterns.json",
                write_dashboard=False,
            )

            self.assertEqual(result["status"], "daily_pipeline_completed")
            self.assertEqual(result["cost_guard"]["status"], "cost_guard_passed")
            self.assertEqual(result["summary"]["ad_record_count"], 15)
            self.assertEqual(result["summary"]["prompt_count"], 20)
            self.assertEqual(result["summary"]["image_request_count"], 20)
            self.assertEqual(result["summary"]["approved_count"], 20)
            self.assertEqual(result["summary"]["planned_upload_count"], 20)
            self.assertTrue((root / "history" / "daily" / "2026-05-18_pipeline_run.json").exists())
            self.assertTrue((root / "history" / "weekly" / "2026-W21.json").exists())

    def test_run_daily_pipeline_stops_when_cost_limit_is_exceeded(self) -> None:
        with tempfile.TemporaryDirectory(dir=PROJECT_ROOT) as tmp_dir:
            root = Path(tmp_dir)
            result = run_daily_pipeline(
                run_date="2026-05-18",
                history_root=root / "history",
                output_root=root / "outputs",
                runtime_path=root / "state" / "runtime.json",
                log_path=root / "logs" / "execution.log",
                pattern_path=root / "history" / "winner_loser_patterns.json",
                write_dashboard=False,
                fail_on_cost_exceeded=False,
                daily_cost_limit_usd=1.0,
            )

            self.assertEqual(result["status"], "cost_limit_exceeded")
            self.assertEqual(result["cost_guard"]["estimated_cost_usd"], 2.64)
            self.assertFalse((root / "history" / "daily" / "2026-05-18_quality_review.json").exists())
            self.assertTrue((root / "history" / "daily" / "2026-05-18_pipeline_run.json").exists())

    def test_daily_workflow_contains_schedule_dispatch_commit_and_slack_steps(self) -> None:
        workflow = (PROJECT_ROOT / ".github" / "workflows" / "daily_run.yml").read_text(encoding="utf-8")

        self.assertIn('cron: "0 17 * * 0-4"', workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("contents: write", workflow)
        self.assertIn("python scripts/run_daily_pipeline.py", workflow)
        self.assertIn("git add history/daily history/weekly history/winner_loser_patterns.json state/runtime.json web/data web/api", workflow)
        self.assertIn("git push", workflow)
        self.assertIn("SLACK_WEBHOOK_URL", workflow)


if __name__ == "__main__":
    unittest.main()
