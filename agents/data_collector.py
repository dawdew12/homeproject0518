# 팀원 A가 광고 매체별 성과 데이터를 수집하는 진입점을 제공한다.
from __future__ import annotations

import argparse
import json
import os
from datetime import date as date_type
from pathlib import Path
from time import sleep
from typing import Any, Callable


METRICS = ["ctr", "cvr", "cpa", "roas", "impressions", "clicks", "cost", "conversions"]
BRANDS = ["someud", "kinda", "melliance", "paperback", "baren"]
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "history" / "daily"
MAX_ATTEMPTS = 3

SOURCE_CONFIGS: dict[str, dict[str, Any]] = {
    "meta": {
        "label": "Meta Marketing API",
        "required_env": ["META_ACCESS_TOKEN", "META_AD_ACCOUNT_ID"],
    },
    "naver_sa": {
        "label": "네이버 검색광고 API",
        "required_env": ["NAVER_SA_API_KEY", "NAVER_SA_SECRET_KEY", "NAVER_SA_CUSTOMER_ID"],
    },
    "kakao_moment": {
        "label": "카카오모먼트 API",
        "required_env": ["KAKAO_MOMENT_ACCESS_TOKEN"],
    },
}


def resolve_date(value: str | None = None) -> str:
    """명시된 날짜가 없으면 오늘 날짜를 YYYY-MM-DD 형식으로 반환한다."""
    return value or date_type.today().isoformat()


def retry_call(callback: Callable[[], Any], max_attempts: int = MAX_ATTEMPTS, delay_seconds: float = 0) -> Any:
    """일시 실패 가능성이 있는 수집 함수를 최대 3회까지 재시도한다."""
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return callback()
        except Exception as exc:
            last_error = exc
            if attempt < max_attempts and delay_seconds > 0:
                sleep(delay_seconds)
    raise RuntimeError(f"{max_attempts}회 재시도 후 실패: {last_error}") from last_error


def get_required_env(source: str) -> dict[str, str]:
    """매체별 실제 API 호출에 필요한 환경변수를 읽는다."""
    config = SOURCE_CONFIGS[source]
    values = {key: os.getenv(key, "") for key in config["required_env"]}
    missing = [key for key, value in values.items() if not value]
    if missing:
        raise RuntimeError(f"{source} API 환경변수가 없습니다: {', '.join(missing)}")
    return values


def build_mock_records(source: str, target_date: str, brands: list[str] | None = None) -> list[dict[str, Any]]:
    """브랜드별 광고 성과 mock 데이터를 만든다."""
    selected_brands = brands or BRANDS
    source_offset = {"meta": 0, "naver_sa": 1, "kakao_moment": 2}[source]
    records = []

    for index, brand in enumerate(selected_brands, start=1):
        impressions = 1200 + (index * 180) + (source_offset * 90)
        clicks = 28 + (index * 5) + source_offset
        conversions = 3 + (index % 3) + source_offset
        cost = round(18.5 + (index * 4.25) + (source_offset * 2.1), 4)
        revenue = round(cost * (2.35 + (index * 0.12)), 4)
        ctr = round((clicks / impressions) * 100, 4)
        cvr = round((conversions / clicks) * 100, 4)
        cpa = round(cost / conversions, 4)
        roas = round((revenue / cost) * 100, 4)

        records.append(
            {
                "date": target_date,
                "source": source,
                "brand": brand,
                "campaign_id": f"{source}_{brand}_{target_date.replace('-', '')}",
                "creative_id": f"{brand}_{source}_mock_001",
                "metrics": {
                    "ctr": ctr,
                    "cvr": cvr,
                    "cpa": cpa,
                    "roas": roas,
                    "impressions": impressions,
                    "clicks": clicks,
                    "cost": cost,
                    "conversions": conversions,
                },
            }
        )

    return records


def collect_source_performance(source: str, date: str | None = None, mock: bool = True) -> dict[str, Any]:
    """단일 광고 매체의 성과 데이터를 수집한다."""
    target_date = resolve_date(date)
    if source not in SOURCE_CONFIGS:
        raise ValueError(f"지원하지 않는 광고 매체입니다: {source}")

    if mock:
        records = build_mock_records(source, target_date)
        return {
            "source": source,
            "label": SOURCE_CONFIGS[source]["label"],
            "status": "mock_collected",
            "date": target_date,
            "metrics": METRICS,
            "records": records,
        }

    credentials = get_required_env(source)
    return {
        "source": source,
        "label": SOURCE_CONFIGS[source]["label"],
        "status": "credentials_ready",
        "date": target_date,
        "metrics": METRICS,
        "records": [],
        "credential_keys": sorted(credentials.keys()),
        "note": "실제 API 요청 매핑은 매체 계정 권한과 응답 샘플 확인 후 연결한다.",
    }


def collect_meta_performance(date: str | None = None, mock: bool = True) -> dict[str, Any]:
    """Meta Marketing API에서 전일 광고 성과를 수집한다."""
    return retry_call(lambda: collect_source_performance("meta", date, mock=mock))


def collect_naver_sa_performance(date: str | None = None, mock: bool = True) -> dict[str, Any]:
    """네이버 검색광고 API에서 전일 광고 성과를 수집한다."""
    return retry_call(lambda: collect_source_performance("naver_sa", date, mock=mock))


def collect_kakao_moment_performance(date: str | None = None, mock: bool = True) -> dict[str, Any]:
    """카카오모먼트 API에서 전일 광고 성과를 수집한다."""
    return retry_call(lambda: collect_source_performance("kakao_moment", date, mock=mock))


def collect_ad_data(date: str | None = None, mock: bool = True) -> dict[str, Any]:
    """매체별 수집 결과를 하나의 일별 광고 데이터로 묶는다."""
    target_date = resolve_date(date)
    sources = [
        collect_meta_performance(target_date, mock=mock),
        collect_naver_sa_performance(target_date, mock=mock),
        collect_kakao_moment_performance(target_date, mock=mock),
    ]
    records = [record for source in sources for record in source["records"]]

    return {
        "date": target_date,
        "status": "mock_collected" if mock else "credentials_ready",
        "sources": sources,
        "summary": {
            "source_count": len(sources),
            "brand_count": len(BRANDS),
            "record_count": len(records),
            "metrics": METRICS,
        },
        "records": records,
    }


def save_ad_data(payload: dict[str, Any], output_dir: Path | None = None) -> Path:
    """일별 광고 성과 데이터를 history/daily에 JSON으로 저장한다."""
    target_dir = output_dir or DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / f"{payload['date']}_ad_data.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def main() -> None:
    """명령행에서 광고 데이터 수집과 저장을 실행한다."""
    parser = argparse.ArgumentParser(description="AIPR ad data collector")
    parser.add_argument("--date", default=None, help="수집 기준 날짜. 예: 2026-05-18")
    parser.add_argument("--live", action="store_true", help="환경변수 확인 후 실제 API 연결 모드로 실행한다.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="저장 폴더")
    args = parser.parse_args()

    payload = collect_ad_data(args.date, mock=not args.live)
    output_path = save_ad_data(payload, Path(args.output_dir))
    print(f"saved {output_path}")


if __name__ == "__main__":
    main()
