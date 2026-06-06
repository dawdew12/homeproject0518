# 포털 뉴스와 SNS 공개 검색 클리핑을 브랜드별 일간 요약으로 묶는다.
from __future__ import annotations

import argparse
import html
import json
import re
import xml.etree.ElementTree as ET
from datetime import date as date_type
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "history" / "daily"
KST = timezone(timedelta(hours=9))

BRAND_CLIP_CONFIGS: dict[str, dict[str, Any]] = {
    "someud": {
        "display_name": "소머드",
        "keywords": ["황토침대", "숙면", "부모님 선물"],
        "portal_queries": ["황토침대 숙면 부모님 선물", "흙침대 건강침대 숙면"],
        "sns_queries": ["황토침대 숙면 후기", "부모님 선물 흙침대"],
        "sns_angle": "후기형 콘텐츠, 부모님 선물 반응, 설치 전후 체감 포인트",
        "action": "부모님 선물형 후킹과 숙면 체감 후기를 소재 첫 문장에 배치한다.",
    },
    "kinda": {
        "display_name": "킨다",
        "keywords": ["극손상 헤어팩", "홈케어", "비포애프터"],
        "portal_queries": ["헤어팩 홈케어 트리트먼트", "손상모 헤어케어 홈케어", "헤어케어 비포애프터 트렌드"],
        "sns_queries": ["극손상 헤어팩 비포애프터", "홈살롱 헤어팩 후기"],
        "sns_angle": "비포애프터 컷, 손상모 회복 루틴, 홈살롱 사용 순서",
        "action": "비포애프터 증거 화면과 홈살롱 루틴을 짧은 영상 구조로 전환한다.",
    },
    "melliance": {
        "display_name": "멜리언스",
        "keywords": ["뷰티 루틴", "피부결", "스킨케어"],
        "portal_queries": ["뷰티 루틴 피부결 스킨케어", "맞춤형 루틴 피부과학 성분 데이터"],
        "sns_queries": ["피부결 루틴 스킨케어", "아침 저녁 뷰티 루틴"],
        "sns_angle": "루틴 공개형 콘텐츠, 피부결 근접 컷, 성분 기반 설명",
        "action": "피부결 개선 루틴을 단계별 카드와 근접 컷 조합으로 제안한다.",
    },
    "paperback": {
        "display_name": "페이퍼백",
        "keywords": ["독서 감성", "카페", "라이프스타일"],
        "portal_queries": ["독서 감성 카페 라이프스타일", "책갈피 독서 감성 라이프스타일"],
        "sns_queries": ["독서 감성 카페 브이로그", "책 읽는 카페 라이프스타일"],
        "sns_angle": "카페 브이로그, 북스타그램 감성, 취향 큐레이션",
        "action": "카페 공간과 독서 루틴을 묶어 저장하고 싶은 생활 장면으로 만든다.",
    },
    "baren": {
        "display_name": "바렌",
        "keywords": ["기능성 케어", "성분", "인포그래픽"],
        "portal_queries": ["기능성 케어 성분 스킨케어", "기능성 선케어 성분 출시"],
        "sns_queries": ["성분 인포그래픽 스킨케어", "기능성 케어 사용법"],
        "sns_angle": "성분 요약형 카드, 사용법 숏폼, 기능성 전후 비교",
        "action": "성분 근거와 사용법을 한 화면에서 이해되는 인포그래픽 소재로 정리한다.",
    },
}

SNS_PLATFORMS = [
    ("YouTube", "https://www.youtube.com/results?search_query={query}"),
    ("Instagram", "https://www.instagram.com/explore/search/keyword/?q={query}"),
    ("TikTok", "https://www.tiktok.com/search?q={query}"),
]


def resolve_date(value: str | None = None) -> str:
    """수집 기준 날짜를 YYYY-MM-DD 형식으로 반환한다."""
    return value or datetime.now(KST).date().isoformat()


def google_news_rss_url(query: str) -> str:
    """Google News RSS 검색 URL을 만든다."""
    return f"https://news.google.com/rss/search?q={quote(query)}&hl=ko&gl=KR&ceid=KR:ko"


def clean_text(value: str | None) -> str:
    """RSS에서 가져온 텍스트를 대시보드 표시용으로 정리한다."""
    text = html.unescape(value or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_google_news_clips(query: str, limit: int = 3, timeout_seconds: int = 10) -> list[dict[str, Any]]:
    """Google News RSS에서 포털 뉴스 클립을 가져온다."""
    request = Request(
        google_news_rss_url(query),
        headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "ko-KR,ko;q=0.9"},
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = response.read()
    except (OSError, URLError):
        return []

    root = ET.fromstring(payload)
    clips = []
    for item in root.findall("./channel/item")[:limit]:
        source_node = item.find("source")
        source_site = clean_text(source_node.text if source_node is not None else "")
        title = clean_text(item.findtext("title"))
        clips.append(
            {
                "source_type": "portal_news",
                "source_name": "Google News RSS",
                "source_site": source_site,
                "query": query,
                "title": title,
                "url": clean_text(item.findtext("link")),
                "published_at": clean_text(item.findtext("pubDate")),
                "snippet": title,
            }
        )
    return clips


def fallback_portal_clips(config: dict[str, Any]) -> list[dict[str, Any]]:
    """네트워크 결과가 없을 때 검색 링크 기반 클립을 만든다."""
    clips = []
    for query in config["portal_queries"][:2]:
        clips.append(
            {
                "source_type": "portal_news",
                "source_name": "Google News RSS",
                "source_site": "public_search",
                "query": query,
                "title": f"포털 뉴스 공개 검색: {query}",
                "url": google_news_rss_url(query),
                "published_at": "",
                "snippet": f"{query} 관련 최신 기사와 포털 노출 소재를 확인하는 검색 링크다.",
            }
        )
    return clips


def build_sns_search_clips(config: dict[str, Any]) -> list[dict[str, Any]]:
    """SNS 플랫폼별 공개 검색 확인 링크를 클리핑 형태로 만든다."""
    clips = []
    primary_query = config["sns_queries"][0]
    for platform, template in SNS_PLATFORMS:
        clips.append(
            {
                "source_type": "sns_search",
                "source_name": platform,
                "source_site": platform,
                "query": primary_query,
                "title": f"{platform} 공개 검색: {primary_query}",
                "url": template.format(query=quote(primary_query)),
                "published_at": "",
                "snippet": config["sns_angle"],
            }
        )
    return clips


def unique_clips(clips: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    """URL 기준 중복 클립을 제거한다."""
    seen = set()
    unique = []
    for clip in clips:
        key = clip.get("url") or f"{clip.get('source_name')}:{clip.get('title')}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(clip)
        if len(unique) >= limit:
            break
    return unique


def summarize_brand(config: dict[str, Any], portal_clips: list[dict[str, Any]], sns_clips: list[dict[str, Any]]) -> list[str]:
    """브랜드별 3줄 요약을 만든다."""
    keywords = ", ".join(config["keywords"][:3])
    first_title = portal_clips[0]["title"] if portal_clips else f"{keywords} 공개 검색 결과"
    platforms = ", ".join(clip["source_name"] for clip in sns_clips[:3])
    return [
        f"포털 신호는 {keywords} 중심으로 확인했고, 대표 클립은 {first_title}이다.",
        f"SNS 확인은 {platforms} 공개 검색 링크로 묶었고, 관찰 포인트는 {config['sns_angle']}이다.",
        f"오늘 소재 액션은 {config['action']}",
    ]


def collect_brand_clips(
    brand: str,
    config: dict[str, Any],
    target_date: str,
    live: bool,
    portal_fetcher: Callable[[str], list[dict[str, Any]]] = fetch_google_news_clips,
) -> dict[str, Any]:
    """한 브랜드의 포털/SNS 클립과 3줄 요약을 만든다."""
    portal_clips: list[dict[str, Any]] = []
    if live:
        for query in config["portal_queries"]:
            portal_clips.extend(portal_fetcher(query))
            if len(portal_clips) >= 3:
                break

    portal_clips = unique_clips(portal_clips, 3)
    if not portal_clips:
        portal_clips = fallback_portal_clips(config)

    sns_clips = build_sns_search_clips(config)
    summary_3_lines = summarize_brand(config, portal_clips, sns_clips)
    clips = portal_clips + sns_clips

    return {
        "date": target_date,
        "brand": brand,
        "display_name": config["display_name"],
        "keywords": config["keywords"],
        "summary_3_lines": summary_3_lines,
        "portal_clip_count": len(portal_clips),
        "sns_clip_count": len(sns_clips),
        "clips": clips,
    }


def build_article_links(brands: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """브랜드별 포털 뉴스 클립만 전체 기사 링크 목록으로 펼친다."""
    article_links = []
    for brand_item in brands:
        for clip in brand_item.get("clips", []):
            if clip.get("source_type") != "portal_news":
                continue
            article_links.append(
                {
                    "sequence": len(article_links) + 1,
                    "date": brand_item.get("date"),
                    "brand": brand_item.get("brand"),
                    "display_name": brand_item.get("display_name"),
                    "source_site": clip.get("source_site") or clip.get("source_name"),
                    "title": clip.get("title"),
                    "url": clip.get("url"),
                    "query": clip.get("query"),
                    "published_at": clip.get("published_at"),
                }
            )
    return article_links


def build_overall_article_implication(brands: list[dict[str, Any]], article_links: list[dict[str, Any]]) -> str:
    """수집 기사 전체가 시사하는 공통 소재 방향을 한 줄로 만든다."""
    keyword_groups = []
    for brand_item in brands:
        keywords = brand_item.get("keywords", [])
        if keywords:
            keyword_groups.append(", ".join(keywords[:2]))
    keyword_text = " / ".join(keyword_groups[:5])
    if not article_links:
        return "오늘 포털 기사 신호는 아직 부족하므로 SNS 검색 링크와 기존 트렌드 점수를 함께 확인해야 한다."
    return (
        f"수집 기사 {len(article_links)}건은 {keyword_text} 전반에서 "
        "개인 루틴, 체감 증거, 사용 장면을 짧게 보여주는 소재가 공통 기회임을 시사한다."
    )


def collect_daily_portal_sns_clips(date: str | None = None, live: bool = False) -> dict[str, Any]:
    """전체 브랜드의 일간 포털/SNS 클리핑 산출물을 만든다."""
    target_date = resolve_date(date)
    brands = [
        collect_brand_clips(brand, config, target_date, live=live)
        for brand, config in BRAND_CLIP_CONFIGS.items()
    ]
    article_links = build_article_links(brands)
    overall_implication = build_overall_article_implication(brands, article_links)
    portal_count = sum(item["portal_clip_count"] for item in brands)
    sns_count = sum(item["sns_clip_count"] for item in brands)

    return {
        "date": target_date,
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "status": "live_collected" if live else "fallback_collected",
        "collection_note": "SNS 내부 게시물 본문 수집은 플랫폼 로그인 또는 공식 API 권한 연결 후 확장한다.",
        "overall_implication": overall_implication,
        "summary": {
            "brand_count": len(brands),
            "portal_clip_count": portal_count,
            "sns_clip_count": sns_count,
            "clip_count": portal_count + sns_count,
            "article_link_count": len(article_links),
            "summary_line_count": len(brands) * 3,
        },
        "article_links": article_links,
        "brands": brands,
    }


def save_portal_sns_clips(payload: dict[str, Any], output_dir: Path | None = None) -> Path:
    """일간 포털/SNS 클립 JSON을 history/daily에 저장한다."""
    target_dir = output_dir or DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / f"{payload['date']}_portal_sns_clips.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def main() -> None:
    """명령행에서 일간 포털/SNS 클리핑을 실행한다."""
    parser = argparse.ArgumentParser(description="AIPR portal and SNS trend clipper")
    parser.add_argument("--date", default=None, help="수집 기준 날짜. 예: 2026-06-06")
    parser.add_argument("--live", action="store_true", help="공개 Google News RSS를 실제로 조회한다.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="저장 폴더")
    args = parser.parse_args()

    payload = collect_daily_portal_sns_clips(args.date, live=args.live)
    output_path = save_portal_sns_clips(payload, Path(args.output_dir))
    print(f"saved {output_path}")


if __name__ == "__main__":
    main()
