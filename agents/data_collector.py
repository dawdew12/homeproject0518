# 팀원 A가 광고 매체별 성과 데이터를 수집하는 진입점을 제공한다.
from __future__ import annotations

from typing import Any


METRICS = ["ctr", "cvr", "cpa", "roas", "impressions", "clicks", "cost", "conversions"]


def collect_meta_performance(date: str | None = None) -> dict[str, Any]:
    """Meta Marketing API에서 전일 광고 성과를 수집한다."""
    return {"source": "meta", "status": "not_implemented", "date": date, "metrics": METRICS}


def collect_naver_sa_performance(date: str | None = None) -> dict[str, Any]:
    """네이버 검색광고 API에서 전일 광고 성과를 수집한다."""
    return {"source": "naver_sa", "status": "not_implemented", "date": date, "metrics": METRICS}


def collect_kakao_moment_performance(date: str | None = None) -> dict[str, Any]:
    """카카오모먼트 API에서 전일 광고 성과를 수집한다."""
    return {"source": "kakao_moment", "status": "not_implemented", "date": date, "metrics": METRICS}


def collect_ad_data(date: str | None = None) -> dict[str, Any]:
    """매체별 수집 결과를 하나의 일별 광고 데이터로 묶는다."""
    return {
        "date": date,
        "sources": [
            collect_meta_performance(date),
            collect_naver_sa_performance(date),
            collect_kakao_moment_performance(date),
        ],
    }


if __name__ == "__main__":
    print(collect_ad_data())