# 팀장 에이전트의 광고·트렌드 종합 분석과 다음 작업 전달안을 만든다.
from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DAILY_DIR = PROJECT_ROOT / "history" / "daily"
BRANDS = ["someud", "kinda", "melliance", "paperback", "baren"]
PRIORITY_ORDER = {"scale": 0, "high": 1, "test": 2, "watch": 3}
BRAND_VISUAL_CONCEPTS = {
    "someud": "따뜻한 침실에서 숙면과 가족 신뢰를 보여주는 실사",
    "kinda": "손상 모발 전후 차이가 선명한 욕실·파우더룸 실사",
    "melliance": "피부결과 루틴을 정돈된 뷰티 무드로 보여주는 클로즈업",
    "paperback": "취향 있는 카페와 독서 장면을 연결한 라이프스타일 컷",
    "baren": "성분과 기능을 깨끗하게 이해시키는 정보형 비주얼",
}
QUALITY_SCORE_THRESHOLD = 90
MAX_REGENERATION_RETRY = 2


def read_json(path: Path, default: Any | None = None) -> Any:
    """JSON 파일을 읽고 없으면 기본값을 반환한다."""
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    """JSON payload를 UTF-8로 저장한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def find_daily_file(date: str | None, suffix: str, daily_dir: Path = DEFAULT_DAILY_DIR) -> Path:
    """날짜가 있으면 해당 파일, 없으면 최신 daily 파일을 찾는다."""
    if date:
        path = daily_dir / f"{date}_{suffix}.json"
        if path.exists():
            return path
        raise FileNotFoundError(path)

    files = sorted(daily_dir.glob(f"*_{suffix}.json"))
    if not files:
        raise FileNotFoundError(f"*_{suffix}.json")
    return files[-1]


def load_brand_config(brand: str) -> dict[str, Any]:
    """브랜드별 TOML 설정을 읽는다."""
    config_path = PROJECT_ROOT / "brands" / brand / "config.toml"
    if not config_path.exists():
        return {"brand": {"name": brand, "name_en": brand}, "style": {}, "performance_targets": {}}
    return tomllib.loads(config_path.read_text(encoding="utf-8").lstrip("\ufeff"))


def average(values: list[float]) -> float:
    """숫자 목록 평균을 소수점 4자리로 반환한다."""
    if not values:
        return 0
    return round(sum(values) / len(values), 4)


def unique_ordered(values: list[str]) -> list[str]:
    """입력 순서를 유지하며 중복 문자열을 제거한다."""
    seen = set()
    result = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def build_ad_metrics(records: list[dict[str, Any]], targets: dict[str, Any]) -> dict[str, Any]:
    """브랜드 광고 mock 레코드를 분석 지표로 요약한다."""
    metrics = [record.get("metrics", {}) for record in records]
    avg_ctr = average([float(item.get("ctr", 0)) for item in metrics])
    avg_cvr = average([float(item.get("cvr", 0)) for item in metrics])
    avg_cpa = average([float(item.get("cpa", 0)) for item in metrics])
    avg_roas = average([float(item.get("roas", 0)) for item in metrics])
    ctr_target = float(targets.get("ctr_target", 2.0))
    roas_target = float(targets.get("roas_target", 250))

    return {
        "record_count": len(records),
        "source_count": len({record.get("source") for record in records}),
        "avg_ctr": avg_ctr,
        "avg_cvr": avg_cvr,
        "avg_cpa": avg_cpa,
        "avg_roas": avg_roas,
        "ctr_target": ctr_target,
        "roas_target": roas_target,
        "ctr_gap": round(avg_ctr - ctr_target, 4),
        "roas_gap": round(avg_roas - roas_target, 4),
        "total_impressions": sum(int(item.get("impressions", 0)) for item in metrics),
        "total_clicks": sum(int(item.get("clicks", 0)) for item in metrics),
        "total_conversions": sum(int(item.get("conversions", 0)) for item in metrics),
        "total_cost": round(sum(float(item.get("cost", 0)) for item in metrics), 4),
    }


def build_trend_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    """브랜드 트렌드 mock 레코드를 분석 지표로 요약한다."""
    keywords = []
    issues = []
    competitor_signal_count = 0

    for record in records:
        keywords.extend(record.get("keywords", []))
        issue = record.get("seasonal_issue", {})
        if issue.get("title"):
            issues.append(issue.get("title"))
        if record.get("competitor_signal", {}).get("detected"):
            competitor_signal_count += 1

    return {
        "record_count": len(records),
        "source_count": len({record.get("source") for record in records}),
        "avg_trend_score": average([float(record.get("trend_score", 0)) for record in records]),
        "avg_trend_change_pct": average([float(record.get("trend_change_pct", 0)) for record in records]),
        "top_keywords": unique_ordered(keywords)[:6],
        "issue_titles": unique_ordered(issues)[:4],
        "competitor_signal_count": competitor_signal_count,
    }


def decide_priority(ad_metrics: dict[str, Any], trend_metrics: dict[str, Any]) -> str:
    """성과와 관심도 기준으로 오늘의 소재 우선순위를 결정한다."""
    ctr_ratio = ad_metrics["avg_ctr"] / ad_metrics["ctr_target"] if ad_metrics["ctr_target"] else 0
    roas_ratio = ad_metrics["avg_roas"] / ad_metrics["roas_target"] if ad_metrics["roas_target"] else 0
    trend_score = trend_metrics["avg_trend_score"]

    if ctr_ratio >= 1 and roas_ratio >= 1 and trend_score >= 75:
        return "scale"
    if roas_ratio >= 0.9 and trend_score >= 80:
        return "high"
    if ctr_ratio < 0.8 or roas_ratio < 0.65:
        return "watch"
    return "test"


def build_recommended_actions(
    ad_metrics: dict[str, Any],
    trend_metrics: dict[str, Any],
    priority: str,
) -> list[str]:
    """팀장이 다음 제작자에게 줄 실행 액션을 만든다."""
    actions = []
    if priority in {"scale", "high"}:
        actions.append("성과가 받쳐주는 키워드를 첫 소재 묶음의 메인 각도로 배치한다.")
    if ad_metrics["ctr_gap"] < 0:
        actions.append("첫 화면 후킹 이미지를 더 명확하게 만들고 핵심 베네핏을 1개로 좁힌다.")
    if ad_metrics["roas_gap"] < 0:
        actions.append("신뢰 증거와 사용 맥락을 보강해 전환 설득력을 높인다.")
    if trend_metrics["competitor_signal_count"] > 0:
        actions.append("경쟁사 소재 변화가 감지된 채널은 카피보다 비주얼 차별점을 우선 검토한다.")
    if not actions:
        actions.append("현재 성과 구조를 유지하되 소재 포맷만 2개 이상 분산 테스트한다.")
    return actions[:4]


def build_brand_brief(
    brand: str,
    ad_records: list[dict[str, Any]],
    trend_records: list[dict[str, Any]],
) -> dict[str, Any]:
    """브랜드 1개의 팀장 분석 Brief를 만든다."""
    config = load_brand_config(brand)
    brand_config = config.get("brand", {})
    style = config.get("style", {})
    targets = config.get("performance_targets", {})
    ad_metrics = build_ad_metrics(ad_records, targets)
    trend_metrics = build_trend_metrics(trend_records)
    priority = decide_priority(ad_metrics, trend_metrics)
    top_keywords = trend_metrics["top_keywords"]
    main_keyword = top_keywords[0] if top_keywords else brand
    tone = style.get("tone", "브랜드 톤")
    visual_concept = BRAND_VISUAL_CONCEPTS.get(brand, f"{main_keyword} 중심의 브랜드 비주얼")

    return {
        "brand": brand,
        "display_name": brand_config.get("name", brand),
        "priority": priority,
        "score": round(ad_metrics["avg_roas"] * 0.4 + ad_metrics["avg_ctr"] * 10 + trend_metrics["avg_trend_score"] * 0.6, 4),
        "creative_direction": f"{main_keyword} 중심의 {tone} 소재",
        "visual_concept": visual_concept,
        "rationale": [
            f"평균 CTR {ad_metrics['avg_ctr']}%, 평균 ROAS {ad_metrics['avg_roas']}% 기준으로 판단했다.",
            f"평균 트렌드 점수 {trend_metrics['avg_trend_score']}와 변화율 {trend_metrics['avg_trend_change_pct']}%를 반영했다.",
        ],
        "ad_metrics": ad_metrics,
        "trend_metrics": trend_metrics,
        "recommended_actions": build_recommended_actions(ad_metrics, trend_metrics, priority),
        "prompt_keywords": top_keywords,
        "handoff": {
            "owner": "팀원 C",
            "storyboard_count": 4,
            "prompt_brief": f"{brand_config.get('name', brand)} 브랜드는 '{main_keyword}'를 메인 각도로 삼아 '{visual_concept}' 콘셉트를 만든다.",
            "constraints": ["텍스트 삽입 금지", "하단 카피 영역 확보", "경쟁사명 노출 금지"],
        },
    }


def build_manager_brief(
    date: str,
    ad_payload: dict[str, Any],
    trend_payload: dict[str, Any],
    input_files: dict[str, str] | None = None,
) -> dict[str, Any]:
    """광고와 트렌드 payload를 종합해 팀장 분석 결과를 만든다."""
    ad_records = ad_payload.get("records", [])
    trend_records = trend_payload.get("records", [])
    brand_briefs = []

    for brand in BRANDS:
        brand_briefs.append(
            build_brand_brief(
                brand,
                [record for record in ad_records if record.get("brand") == brand],
                [record for record in trend_records if record.get("brand") == brand],
            )
        )

    top_opportunities = sorted(
        brand_briefs,
        key=lambda item: (PRIORITY_ORDER.get(item["priority"], 9), -item["score"]),
    )[:3]

    return {
        "date": date,
        "status": "manager_brief_ready",
        "input_files": input_files or {},
        "summary": {
            "brand_count": len(brand_briefs),
            "high_priority_count": sum(1 for item in brand_briefs if item["priority"] in {"scale", "high"}),
            "avg_ctr": average([item["ad_metrics"]["avg_ctr"] for item in brand_briefs]),
            "avg_roas": average([item["ad_metrics"]["avg_roas"] for item in brand_briefs]),
            "avg_trend_score": average([item["trend_metrics"]["avg_trend_score"] for item in brand_briefs]),
            "top_opportunities": [
                {
                    "brand": item["brand"],
                    "priority": item["priority"],
                    "creative_direction": item["creative_direction"],
                }
                for item in top_opportunities
            ],
        },
        "brands": brand_briefs,
        "handoff_to_prompt_engineer": [
            {
                "brand": item["brand"],
                "priority": item["priority"],
                "prompt_brief": item["handoff"]["prompt_brief"],
                "keywords": item["prompt_keywords"],
                "actions": item["recommended_actions"],
            }
            for item in brand_briefs
        ],
    }


def save_manager_brief(payload: dict[str, Any], output_dir: Path = DEFAULT_DAILY_DIR) -> Path:
    """팀장 분석 Brief를 daily history에 저장한다."""
    return write_json(output_dir / f"{payload['date']}_manager_brief.json", payload)


def analyze_daily_inputs(
    date: str | None = None,
    daily_dir: Path = DEFAULT_DAILY_DIR,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """광고 성과와 트렌드 데이터를 종합해 브랜드별 소재 방향을 만든다."""
    ad_path = find_daily_file(date, "ad_data", daily_dir)
    ad_payload = read_json(ad_path)
    analysis_date = date or ad_payload.get("date")
    trend_path = find_daily_file(analysis_date, "trend_data", daily_dir)
    trend_payload = read_json(trend_path)
    payload = build_manager_brief(
        analysis_date,
        ad_payload,
        trend_payload,
        {
            "ad": str(ad_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "trend": str(trend_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        },
    )
    output_path = save_manager_brief(payload, output_dir or daily_dir)
    payload["output_path"] = str(output_path)
    return payload


def review_storyboards(date: str | None = None) -> dict[str, Any]:
    """팀원 C의 텍스트 스토리보드를 승인하거나 반려한다."""
    return {"status": "pending_prompt_engineer_output", "step": "storyboard_review", "date": date}


def build_quality_check(name: str, passed: bool, detail: str) -> dict[str, Any]:
    """품질 검수 항목 1개를 표준 구조로 만든다."""
    return {"name": name, "passed": passed, "detail": detail}


def build_quality_checks(request: dict[str, Any]) -> list[dict[str, Any]]:
    """이미지 생성 요청이 운영 품질 기준을 만족하는지 점검한다."""
    brand = str(request.get("brand", ""))
    output_path = str(request.get("output_path", ""))
    rules = [str(rule) for rule in request.get("rules", [])]
    negative_prompt = {str(item).lower() for item in request.get("negative_prompt", [])}
    image_type = request.get("image_type_label")
    expected_quality = "high" if image_type == "실사" else "medium" if image_type == "일러스트" else None

    return [
        build_quality_check(
            "status_ready",
            request.get("status") == "dry_run_ready",
            "이미지 요청이 dry-run 준비 상태여야 한다.",
        ),
        build_quality_check(
            "model",
            request.get("model") == "gpt-image-2",
            "이미지 생성 모델은 gpt-image-2여야 한다.",
        ),
        build_quality_check(
            "size",
            request.get("size") == "2048x2048",
            "이미지 사이즈는 2K 정사각형 규격이어야 한다.",
        ),
        build_quality_check(
            "quality_by_type",
            expected_quality is not None and request.get("quality") == expected_quality,
            "실사는 high, 일러스트는 medium 품질이어야 한다.",
        ),
        build_quality_check(
            "output_path",
            output_path.startswith(f"outputs/{brand}/") and output_path.endswith(".png"),
            "출력 경로는 브랜드별 outputs 폴더의 PNG 파일이어야 한다.",
        ),
        build_quality_check(
            "copy_space",
            request.get("copy_space") == "bottom_25_percent",
            "하단 25% 카피 여백이 예약되어야 한다.",
        ),
        build_quality_check(
            "no_text_rule",
            "NO text" in rules,
            "이미지 안에 텍스트를 넣지 않는 규칙이 필요하다.",
        ),
        build_quality_check(
            "negative_prompt",
            {"text", "watermark", "logo"}.issubset(negative_prompt),
            "negative prompt가 텍스트, 워터마크, 로고를 차단해야 한다.",
        ),
    ]


def review_image_request(request: dict[str, Any]) -> dict[str, Any]:
    """이미지 요청 1개의 품질 점수와 재생성 필요 여부를 만든다."""
    checks = build_quality_checks(request)
    failed_checks = [check for check in checks if not check["passed"]]
    score = max(0, 100 - len(failed_checks) * 15)
    regeneration_needed = score < QUALITY_SCORE_THRESHOLD
    reason = "all_checks_passed" if not failed_checks else ", ".join(check["name"] for check in failed_checks)

    return {
        "prompt_id": request.get("prompt_id"),
        "storyboard_id": request.get("storyboard_id"),
        "brand": request.get("brand"),
        "output_path": request.get("output_path"),
        "image_type_label": request.get("image_type_label"),
        "quality": request.get("quality"),
        "score": score,
        "status": "regeneration_required" if regeneration_needed else "approved",
        "checks": checks,
        "regeneration": {
            "needed": regeneration_needed,
            "reason": reason,
            "retry_count": 1 if regeneration_needed else 0,
            "max_retry": MAX_REGENERATION_RETRY,
        },
    }


def collect_image_requests(image_payload: dict[str, Any]) -> list[dict[str, Any]]:
    """이미지 dry-run payload에서 요청 목록을 모은다."""
    if image_payload.get("requests"):
        return image_payload.get("requests", [])
    requests = []
    for batch in image_payload.get("batches", []):
        requests.extend(batch.get("requests", []))
    return requests


def build_quality_review(
    date: str,
    image_payload: dict[str, Any],
    input_files: dict[str, str] | None = None,
) -> dict[str, Any]:
    """이미지 dry-run 요청 전체에 대한 품질 검수 결과를 만든다."""
    reviews = [review_image_request(request) for request in collect_image_requests(image_payload)]
    approved = [item for item in reviews if item["status"] == "approved"]
    regeneration_required = [item for item in reviews if item["status"] == "regeneration_required"]

    return {
        "date": date,
        "status": "quality_review_ready",
        "mode": image_payload.get("mode"),
        "input_files": input_files or {},
        "summary": {
            "brand_count": len({item.get("brand") for item in reviews}),
            "request_count": len(reviews),
            "approved_count": len(approved),
            "regeneration_required_count": len(regeneration_required),
            "blocked_count": 0,
            "avg_score": average([float(item["score"]) for item in reviews]),
            "no_text_rule_passed": all(
                check["passed"]
                for item in reviews
                for check in item["checks"]
                if check["name"] == "no_text_rule"
            ),
            "copy_space_passed": all(
                check["passed"]
                for item in reviews
                for check in item["checks"]
                if check["name"] == "copy_space"
            ),
            "max_retry": MAX_REGENERATION_RETRY,
        },
        "reviews": reviews,
        "handoff_to_prompt_engineer": [
            {
                "prompt_id": item["prompt_id"],
                "brand": item["brand"],
                "reason": item["regeneration"]["reason"],
                "retry_count": item["regeneration"]["retry_count"],
                "max_retry": item["regeneration"]["max_retry"],
            }
            for item in regeneration_required
        ],
    }


def save_quality_review(payload: dict[str, Any], output_dir: Path = DEFAULT_DAILY_DIR) -> Path:
    """품질 검수 결과를 daily history에 저장한다."""
    return write_json(output_dir / f"{payload['date']}_quality_review.json", payload)


def review_images(
    date: str | None = None,
    daily_dir: Path = DEFAULT_DAILY_DIR,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """생성 이미지의 품질을 검수하고 재생성 필요 여부를 판단한다."""
    image_path = find_daily_file(date, "image_dry_run", daily_dir)
    image_payload = read_json(image_path)
    review_date = date or image_payload.get("date")
    payload = build_quality_review(
        review_date,
        image_payload,
        {"image_dry_run": str(image_path.relative_to(PROJECT_ROOT)).replace("\\", "/")},
    )
    output_path = save_quality_review(payload, output_dir or daily_dir)
    payload["output_path"] = str(output_path)
    return payload


def classify_winner_loser(date: str | None = None) -> dict[str, Any]:
    """광고 성과 기준으로 Winner, Loser, Pending을 분류한다."""
    ad_path = find_daily_file(date, "ad_data")
    ad_payload = read_json(ad_path)
    classifications = []
    for record in ad_payload.get("records", []):
        brand = record.get("brand", "")
        config = load_brand_config(brand)
        targets = config.get("performance_targets", {})
        metrics = record.get("metrics", {})
        ctr = float(metrics.get("ctr", 0))
        roas = float(metrics.get("roas", 0))
        ctr_target = float(targets.get("ctr_target", 2.0))
        roas_target = float(targets.get("roas_target", 250))
        if ctr >= ctr_target and roas >= roas_target:
            label = "winner"
        elif ctr < ctr_target * 0.4 or roas < roas_target * 0.5:
            label = "loser"
        else:
            label = "pending"
        classifications.append({"brand": brand, "source": record.get("source"), "creative_id": record.get("creative_id"), "label": label})
    return {"status": "classified", "step": "classification", "date": ad_payload.get("date"), "records": classifications}


def main() -> None:
    """명령행 인자로 팀장 에이전트의 실행 단계를 선택한다."""
    parser = argparse.ArgumentParser(description="AIPR manager agent")
    parser.add_argument("--step", choices=["analyze", "storyboard", "review", "classify"], default="analyze")
    parser.add_argument("--date", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else None
    handlers = {
        "analyze": lambda selected_date: analyze_daily_inputs(selected_date, output_dir=output_dir),
        "storyboard": review_storyboards,
        "review": lambda selected_date: review_images(selected_date, output_dir=output_dir),
        "classify": classify_winner_loser,
    }
    result = handlers[args.step](args.date)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
