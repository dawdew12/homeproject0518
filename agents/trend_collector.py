# 팀원 B가 검색 트렌드, 뉴스, 시즌 이슈를 수집하는 진입점을 제공한다.
from __future__ import annotations

import argparse
import json
import os
from datetime import date as date_type
from pathlib import Path
from time import sleep
from typing import Any, Callable


BRANDS = ["someud", "kinda", "melliance", "paperback", "baren"]
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "history" / "daily"
MARKETING_SOURCE_DOC = PROJECT_ROOT / "docs" / "MARKETING_AD_TREND_SOURCES.md"
MAX_ATTEMPTS = 3

SOURCE_CONFIGS: dict[str, dict[str, Any]] = {
    "naver_trends": {
        "label": "네이버 트렌드 API",
        "required_env": ["NAVER_TRENDS_CLIENT_ID", "NAVER_TRENDS_CLIENT_SECRET"],
    },
    "google_trends": {
        "label": "Google Trends",
        "required_env": [],
    },
    "news": {
        "label": "네이버 뉴스 API",
        "required_env": ["NAVER_NEWS_CLIENT_ID", "NAVER_NEWS_CLIENT_SECRET"],
    },
    "competitor": {
        "label": "경쟁사 이슈 수집",
        "required_env": [],
    },
}

BRAND_KEYWORDS: dict[str, list[str]] = {
    "someud": ["황토침대", "어버이날 선물", "숙면"],
    "kinda": ["극손상 헤어팩", "비포애프터", "홈케어"],
    "melliance": ["뷰티 루틴", "봄 컬렉션", "피부결"],
    "paperback": ["라이프스타일", "독서 감성", "카페"],
    "baren": ["기능성 케어", "인포그래픽", "성분"],
}


def parse_marketing_source_catalog(markdown: str) -> list[dict[str, str]]:
    """시장조사 출처 문서의 Markdown 표를 구조화한다."""
    catalog = []
    category = ""
    category_label = ""

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if line.startswith("## ") and "(" in line and ")" in line:
            heading = line.removeprefix("## ").strip()
            category_label = heading.split("(")[0].strip()
            category = heading.rsplit("(", 1)[1].rstrip(")").strip()
            continue

        if not line.startswith("|") or line.startswith("|---") or line.startswith("| Priority"):
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 6 or not category:
            continue

        priority, cadence, source_name, url, use_case, codex_task = cells
        catalog.append(
            {
                "category": category,
                "category_label": category_label,
                "priority": priority,
                "cadence": cadence,
                "source_name": source_name,
                "url": url,
                "use_case": use_case,
                "codex_task": codex_task,
            }
        )

    return catalog


def load_marketing_source_catalog(path: Path = MARKETING_SOURCE_DOC) -> list[dict[str, str]]:
    """프로젝트 문서에 저장된 시장조사 출처 카탈로그를 읽는다."""
    if not path.exists():
        return []
    return parse_marketing_source_catalog(path.read_text(encoding="utf-8"))


def select_due_monitoring_sources(catalog: list[dict[str, str]], cadence: str) -> list[dict[str, str]]:
    """실행 주기에 맞는 시장조사 출처만 고른다."""
    normalized = cadence.lower()
    return [source for source in catalog if source["cadence"].lower() == normalized]


def build_monitoring_source_plan(catalog: list[dict[str, str]]) -> dict[str, Any]:
    """팀원 B가 확인할 시장조사 출처를 주기별로 묶는다."""
    return {
        "catalog_path": str(MARKETING_SOURCE_DOC.relative_to(PROJECT_ROOT)),
        "daily": select_due_monitoring_sources(catalog, "daily"),
        "weekly": select_due_monitoring_sources(catalog, "weekly"),
        "monthly": select_due_monitoring_sources(catalog, "monthly"),
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
    """트렌드/뉴스 수집에 필요한 환경변수를 읽는다."""
    config = SOURCE_CONFIGS[source]
    values = {key: os.getenv(key, "") for key in config["required_env"]}
    missing = [key for key, value in values.items() if not value]
    if missing:
        raise RuntimeError(f"{source} API 환경변수가 없습니다: {', '.join(missing)}")
    return values


def build_mock_records(source: str, target_date: str, brands: list[str] | None = None) -> list[dict[str, Any]]:
    """브랜드별 트렌드 mock 데이터를 만든다."""
    selected_brands = brands or BRANDS
    source_offset = {"naver_trends": 0, "google_trends": 1, "news": 2, "competitor": 3}[source]
    records = []

    for index, brand in enumerate(selected_brands, start=1):
        keywords = BRAND_KEYWORDS[brand]
        score = 54 + (index * 6) + (source_offset * 4)
        change_pct = round(4.5 + (index * 1.7) + source_offset, 2)
        issue_level = "high" if score >= 78 else "medium"

        records.append(
            {
                "date": target_date,
                "source": source,
                "brand": brand,
                "keywords": keywords,
                "trend_score": score,
                "trend_change_pct": change_pct,
                "seasonal_issue": {
                    "title": f"{keywords[0]} 관심 증가",
                    "level": issue_level,
                    "summary": f"{brand} 관련 핵심 키워드가 전주 대비 {change_pct}% 상승했다.",
                },
                "competitor_signal": {
                    "detected": source in {"news", "competitor"},
                    "summary": "경쟁사 소재 변화는 mock 데이터 기준으로 관찰됨." if source in {"news", "competitor"} else "경쟁사 변화 없음.",
                },
            }
        )

    return records


def collect_source_trends(source: str, date: str | None = None, mock: bool = True) -> dict[str, Any]:
    """단일 트렌드 소스에서 데이터를 수집한다."""
    target_date = resolve_date(date)
    if source not in SOURCE_CONFIGS:
        raise ValueError(f"지원하지 않는 트렌드 소스입니다: {source}")

    if mock:
        records = build_mock_records(source, target_date)
        return {
            "source": source,
            "label": SOURCE_CONFIGS[source]["label"],
            "status": "mock_collected",
            "date": target_date,
            "records": records,
        }

    credentials = get_required_env(source)
    return {
        "source": source,
        "label": SOURCE_CONFIGS[source]["label"],
        "status": "credentials_ready",
        "date": target_date,
        "records": [],
        "credential_keys": sorted(credentials.keys()),
        "note": "실제 API 요청 매핑은 계정 권한과 응답 샘플 확인 후 연결한다.",
    }


def collect_naver_trends(date: str | None = None, mock: bool = True) -> dict[str, Any]:
    """네이버 트렌드에서 브랜드 관련 키워드를 수집한다."""
    return retry_call(lambda: collect_source_trends("naver_trends", date, mock=mock))


def collect_google_trends(date: str | None = None, mock: bool = True) -> dict[str, Any]:
    """Google Trends에서 브랜드와 카테고리 키워드를 수집한다."""
    return retry_call(lambda: collect_source_trends("google_trends", date, mock=mock))


def collect_news_issues(date: str | None = None, mock: bool = True) -> dict[str, Any]:
    """뉴스 API에서 시즌 이슈를 수집한다."""
    return retry_call(lambda: collect_source_trends("news", date, mock=mock))


def collect_competitor_issues(date: str | None = None, mock: bool = True) -> dict[str, Any]:
    """경쟁사 소재 변화와 시장 이슈를 수집한다."""
    return retry_call(lambda: collect_source_trends("competitor", date, mock=mock))


def collect_trend_data(date: str | None = None, mock: bool = True) -> dict[str, Any]:
    """트렌드와 뉴스 수집 결과를 하나의 일별 데이터로 묶는다."""
    target_date = resolve_date(date)
    marketing_source_catalog = load_marketing_source_catalog()
    monitoring_sources = build_monitoring_source_plan(marketing_source_catalog)
    sources = [
        collect_naver_trends(target_date, mock=mock),
        collect_google_trends(target_date, mock=mock),
        collect_news_issues(target_date, mock=mock),
        collect_competitor_issues(target_date, mock=mock),
    ]
    records = [record for source in sources for record in source["records"]]
    top_keywords = sorted({keyword for record in records for keyword in record["keywords"]})
    daily_categories = sorted({source["category"] for source in monitoring_sources["daily"]})

    return {
        "date": target_date,
        "status": "mock_collected" if mock else "credentials_ready",
        "sources": sources,
        "summary": {
            "source_count": len(sources),
            "brand_count": len(BRANDS),
            "record_count": len(records),
            "top_keywords": top_keywords[:10],
            "monitoring_source_count": len(marketing_source_catalog),
            "daily_monitoring_source_count": len(monitoring_sources["daily"]),
            "daily_monitoring_categories": daily_categories,
        },
        "monitoring_sources": monitoring_sources,
        "records": records,
    }


def save_trend_data(payload: dict[str, Any], output_dir: Path | None = None) -> Path:
    """일별 트렌드 데이터를 history/daily에 JSON으로 저장한다."""
    target_dir = output_dir or DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / f"{payload['date']}_trend_data.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def main() -> None:
    """명령행에서 트렌드 수집과 저장을 실행한다."""
    parser = argparse.ArgumentParser(description="AIPR trend collector")
    parser.add_argument("--date", default=None, help="수집 기준 날짜. 예: 2026-05-18")
    parser.add_argument("--live", action="store_true", help="환경변수 확인 후 실제 API 연결 모드로 실행한다.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="저장 폴더")
    args = parser.parse_args()

    payload = collect_trend_data(args.date, mock=not args.live)
    output_path = save_trend_data(payload, Path(args.output_dir))
    print(f"saved {output_path}")


if __name__ == "__main__":
    main()
