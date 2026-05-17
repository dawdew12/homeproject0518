# 팀원 B가 검색 트렌드, 뉴스, 시즌 이슈를 수집하는 진입점을 제공한다.
from __future__ import annotations

from typing import Any


BRANDS = ["someud", "kinda", "melliance", "paperback", "baren"]


def collect_naver_trends(date: str | None = None) -> dict[str, Any]:
    """네이버 트렌드에서 브랜드 관련 키워드를 수집한다."""
    return {"source": "naver_trends", "status": "not_implemented", "date": date, "brands": BRANDS}


def collect_google_trends(date: str | None = None) -> dict[str, Any]:
    """Google Trends에서 브랜드와 카테고리 키워드를 수집한다."""
    return {"source": "google_trends", "status": "not_implemented", "date": date, "brands": BRANDS}


def collect_news_issues(date: str | None = None) -> dict[str, Any]:
    """뉴스 API에서 시즌 이슈와 경쟁사 동향을 수집한다."""
    return {"source": "news", "status": "not_implemented", "date": date, "brands": BRANDS}


def collect_trend_data(date: str | None = None) -> dict[str, Any]:
    """트렌드와 뉴스 수집 결과를 하나의 일별 데이터로 묶는다."""
    return {
        "date": date,
        "sources": [
            collect_naver_trends(date),
            collect_google_trends(date),
            collect_news_issues(date),
        ],
    }


if __name__ == "__main__":
    print(collect_trend_data())