# 팀장 에이전트의 분석, 검수, 위너/루저 판단 흐름을 관리한다.
from __future__ import annotations

import argparse
from typing import Any


BRANDS = ["someud", "kinda", "melliance", "paperback", "baren"]


def analyze_daily_inputs(date: str | None = None) -> dict[str, Any]:
    """광고 성과와 트렌드 데이터를 종합해 브랜드별 소재 방향을 만든다."""
    return {"status": "not_implemented", "step": "analyze", "date": date, "brands": BRANDS}


def review_storyboards(date: str | None = None) -> dict[str, Any]:
    """팀원 C의 텍스트 스토리보드를 승인하거나 반려한다."""
    return {"status": "not_implemented", "step": "storyboard_review", "date": date}


def review_images(date: str | None = None) -> dict[str, Any]:
    """생성 이미지의 품질을 검수하고 재생성 필요 여부를 판단한다."""
    return {"status": "not_implemented", "step": "image_review", "date": date}


def classify_winner_loser(date: str | None = None) -> dict[str, Any]:
    """광고 성과 기준으로 Winner, Loser, Pending을 분류한다."""
    return {"status": "not_implemented", "step": "classification", "date": date}


def main() -> None:
    """명령행 인자로 팀장 에이전트의 실행 단계를 선택한다."""
    parser = argparse.ArgumentParser(description="AIPR manager agent")
    parser.add_argument("--step", choices=["analyze", "storyboard", "review", "classify"], default="analyze")
    parser.add_argument("--date", default=None)
    args = parser.parse_args()

    handlers = {
        "analyze": analyze_daily_inputs,
        "storyboard": review_storyboards,
        "review": review_images,
        "classify": classify_winner_loser,
    }
    result = handlers[args.step](args.date)
    print(result)


if __name__ == "__main__":
    main()