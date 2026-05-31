# 팀원 D의 이미지 생성 dry-run 요청 생성을 검증한다.
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agents.image_designer import (
    build_image_dry_run,
    generate_daily_image_dry_run,
    read_json,
    request_regeneration,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ImageDesignerTest(unittest.TestCase):
    def test_build_image_dry_run_creates_batch_requests_and_costs(self) -> None:
        prompt_payload = read_json(PROJECT_ROOT / "history" / "daily" / "2026-05-18_prompts.json")

        payload = build_image_dry_run(prompt_payload, {"daily_cost_usd": 0, "monthly_cost_usd": 0})

        self.assertEqual(payload["status"], "image_dry_run_ready")
        self.assertEqual(payload["summary"]["brand_count"], 5)
        self.assertEqual(payload["summary"]["batch_count"], 5)
        self.assertEqual(payload["summary"]["request_count"], 20)
        self.assertEqual(payload["summary"]["real_photo_count"], 10)
        self.assertEqual(payload["summary"]["illustration_count"], 10)
        self.assertEqual(payload["summary"]["estimated_cost_usd"], 2.64)
        self.assertTrue(payload["summary"]["daily_cost_allowed"])
        self.assertFalse(payload["summary"]["charged"])

    def test_image_requests_keep_output_paths_and_generation_rules(self) -> None:
        prompt_payload = read_json(PROJECT_ROOT / "history" / "daily" / "2026-05-18_prompts.json")

        payload = build_image_dry_run(prompt_payload)
        first_request = payload["requests"][0]

        self.assertEqual(first_request["status"], "dry_run_ready")
        self.assertEqual(first_request["size"], "2048x2048")
        self.assertEqual(first_request["quality"], "high")
        self.assertTrue(first_request["output_path"].startswith("outputs/someud/2026-05-18/"))
        self.assertTrue(first_request["output_path"].endswith(".png"))
        self.assertIn("NO text", first_request["rules"])

    def test_generate_daily_image_dry_run_saves_history_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            payload = generate_daily_image_dry_run("2026-05-18", output_dir=Path(tmp_dir))
            saved_path = Path(payload["output_path"])
            saved = json.loads(saved_path.read_text(encoding="utf-8"))

        self.assertEqual(saved["date"], "2026-05-18")
        self.assertEqual(saved["summary"]["request_count"], 20)
        self.assertTrue(saved_path.name.endswith("_image_dry_run.json"))

    def test_request_regeneration_respects_retry_limit(self) -> None:
        requested = request_regeneration("someud_001", "배경을 더 밝게 조정한다.", 1)
        blocked = request_regeneration("someud_001", "배경을 더 밝게 조정한다.", 2)

        self.assertEqual(requested["status"], "regeneration_requested")
        self.assertEqual(requested["retry_count"], 2)
        self.assertEqual(blocked["status"], "보류")


if __name__ == "__main__":
    unittest.main()
