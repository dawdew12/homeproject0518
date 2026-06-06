# 포털/SNS 클리핑 산출물이 브랜드별 3줄 요약으로 생성되는지 검증한다.
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from agents.portal_sns_clipper import (
    BRAND_CLIP_CONFIGS,
    collect_brand_clips,
    collect_daily_portal_sns_clips,
    save_portal_sns_clips,
)


class PortalSnsClipperTest(unittest.TestCase):
    def test_collect_daily_portal_sns_clips_returns_brand_summaries(self) -> None:
        payload = collect_daily_portal_sns_clips("2026-06-06")

        self.assertEqual(payload["date"], "2026-06-06")
        self.assertEqual(payload["summary"]["brand_count"], 5)
        self.assertEqual(payload["summary"]["summary_line_count"], 15)
        self.assertGreaterEqual(payload["summary"]["clip_count"], 25)
        self.assertEqual(len(payload["brands"]), 5)
        self.assertEqual(len(payload["brands"][0]["summary_3_lines"]), 3)
        self.assertIn("clips", payload["brands"][0])

    def test_collect_brand_clips_uses_live_fetcher_when_enabled(self) -> None:
        def fake_fetcher(query: str) -> list[dict[str, str]]:
            return [
                {
                    "source_type": "portal_news",
                    "source_name": "Google News RSS",
                    "source_site": "테스트뉴스",
                    "query": query,
                    "title": "테스트 포털 클립",
                    "url": "https://example.com/test",
                    "published_at": "Sat, 06 Jun 2026 00:00:00 GMT",
                    "snippet": "테스트 포털 클립",
                }
            ]

        payload = collect_brand_clips(
            "someud",
            BRAND_CLIP_CONFIGS["someud"],
            "2026-06-06",
            live=True,
            portal_fetcher=fake_fetcher,
        )

        self.assertEqual(payload["portal_clip_count"], 1)
        self.assertEqual(payload["sns_clip_count"], 3)
        self.assertEqual(payload["clips"][0]["title"], "테스트 포털 클립")
        self.assertIn("YouTube", payload["summary_3_lines"][1])

    def test_save_portal_sns_clips_writes_daily_json(self) -> None:
        payload = collect_daily_portal_sns_clips("2026-06-06")

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = save_portal_sns_clips(payload, Path(tmp_dir))
            saved = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(output_path.name, "2026-06-06_portal_sns_clips.json")
        self.assertEqual(saved["summary"]["brand_count"], 5)
        self.assertEqual(len(saved["brands"][0]["summary_3_lines"]), 3)


if __name__ == "__main__":
    unittest.main()
