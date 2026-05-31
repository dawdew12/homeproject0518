# 팀원 C의 스토리보드와 이미지 프롬프트 생성을 검증한다.
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agents.prompt_engineer import (
    apply_review_feedback,
    build_prompt_pack,
    generate_daily_prompts,
    read_json,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PromptEngineerTest(unittest.TestCase):
    def test_build_prompt_pack_creates_storyboards_and_prompts(self) -> None:
        manager_payload = read_json(PROJECT_ROOT / "history" / "daily" / "2026-05-18_manager_brief.json")

        payload = build_prompt_pack("2026-05-18", manager_payload)

        self.assertEqual(payload["status"], "prompts_ready")
        self.assertEqual(payload["summary"]["brand_count"], 5)
        self.assertEqual(payload["summary"]["storyboard_count"], 20)
        self.assertEqual(payload["summary"]["prompt_count"], 20)
        self.assertEqual(payload["summary"]["real_photo_count"], 10)
        self.assertEqual(payload["summary"]["illustration_count"], 10)
        self.assertTrue(payload["summary"]["no_text_rule_applied"])

    def test_generated_prompts_include_required_image_rules(self) -> None:
        manager_payload = read_json(PROJECT_ROOT / "history" / "daily" / "2026-05-18_manager_brief.json")

        payload = build_prompt_pack("2026-05-18", manager_payload)
        first_prompt = payload["prompts"][0]

        self.assertIn("NO text", first_prompt["rules"])
        self.assertIn("bottom 25 percent", first_prompt["prompt"])
        self.assertTrue(first_prompt["file_name_preview"].endswith(".png"))
        self.assertEqual(first_prompt["model"], "gpt-image-2")
        self.assertEqual(len({prompt["file_name_preview"] for prompt in payload["prompts"]}), 20)

    def test_generate_daily_prompts_saves_prompt_pack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            payload = generate_daily_prompts("2026-05-18", output_dir=Path(tmp_dir))
            saved_path = Path(payload["output_path"])
            saved = json.loads(saved_path.read_text(encoding="utf-8"))

        self.assertEqual(saved["date"], "2026-05-18")
        self.assertEqual(saved["summary"]["prompt_count"], 20)
        self.assertTrue(saved_path.name.endswith("_prompts.json"))

    def test_apply_review_feedback_marks_revision(self) -> None:
        prompt = {"prompt_id": "someud_20260518_prompt01", "prompt": "base prompt", "revision": 0}

        updated = apply_review_feedback(prompt, "카피 영역을 더 넓힌다.")

        self.assertEqual(updated["status"], "feedback_applied")
        self.assertEqual(updated["revision"], 1)
        self.assertIn("카피 영역", updated["prompt"])


if __name__ == "__main__":
    unittest.main()
