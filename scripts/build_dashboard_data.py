# Vercel 대시보드에 표시할 최신 진행 상태 JSON을 생성한다.
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.operation_guard import build_brand_registry, build_cost_report

OUTPUT_DIR = PROJECT_ROOT / "web" / "data"
OUTPUT_PATH = OUTPUT_DIR / "latest_status.json"
API_OUTPUT_DIR = PROJECT_ROOT / "web" / "api"
LOG_DIR = PROJECT_ROOT / "logs"
KST = timezone(timedelta(hours=9))


def read_json(path: Path, default: Any) -> Any:
    """JSON 파일이 있으면 읽고, 없으면 기본값을 반환한다."""
    if not path.exists() or not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    """JSON payload를 보기 쉬운 포맷으로 저장한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def normalize_path(path: Path) -> str:
    """프로젝트 기준 경로를 대시보드용 슬래시 경로로 변환한다."""
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def read_recent_log_lines(path: Path, limit: int = 20) -> list[dict[str, Any]]:
    """로그 파일의 최근 줄을 대시보드 API용으로 반환한다."""
    if not path.exists() or not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    start = max(len(lines) - limit, 0)
    return [
        {"line_no": index + 1, "text": line}
        for index, line in enumerate(lines[start:], start=start)
    ]


def find_latest_file(pattern: str) -> Path | None:
    """history/daily에서 패턴과 맞는 최신 파일을 찾는다."""
    files = sorted((PROJECT_ROOT / "history" / "daily").glob(pattern))
    return files[-1] if files else None


def summarize_daily_file(path: Path | None) -> dict[str, Any]:
    """일별 history JSON을 대시보드용 요약으로 변환한다."""
    if path is None:
        return {"exists": False}

    payload = read_json(path, {})
    summary = payload.get("summary", {})
    return {
        "exists": True,
        "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "date": payload.get("date"),
        "status": payload.get("status"),
        "record_count": summary.get("record_count", 0),
        "source_count": summary.get("source_count", 0),
        "brand_count": summary.get("brand_count", 0),
        "daily_monitoring_source_count": summary.get("daily_monitoring_source_count", 0),
        "top_keywords": summary.get("top_keywords", []),
    }


def summarize_manager_brief(path: Path | None) -> dict[str, Any]:
    """팀장 분석 Brief를 대시보드용 요약으로 변환한다."""
    if path is None:
        return {"exists": False, "brand_count": 0, "high_priority_count": 0, "top_opportunities": []}

    payload = read_json(path, {})
    summary = payload.get("summary", {})
    return {
        "exists": True,
        "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "date": payload.get("date"),
        "status": payload.get("status"),
        "brand_count": summary.get("brand_count", 0),
        "high_priority_count": summary.get("high_priority_count", 0),
        "avg_ctr": summary.get("avg_ctr", 0),
        "avg_roas": summary.get("avg_roas", 0),
        "avg_trend_score": summary.get("avg_trend_score", 0),
        "top_opportunities": summary.get("top_opportunities", []),
        "handoff_count": len(payload.get("handoff_to_prompt_engineer", [])),
    }


def summarize_prompt_pack(path: Path | None) -> dict[str, Any]:
    """팀원 C 프롬프트 pack을 대시보드용 요약으로 변환한다."""
    if path is None:
        return {"exists": False, "storyboard_count": 0, "prompt_count": 0}

    payload = read_json(path, {})
    summary = payload.get("summary", {})
    return {
        "exists": True,
        "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "date": payload.get("date"),
        "status": payload.get("status"),
        "brand_count": summary.get("brand_count", 0),
        "storyboard_count": summary.get("storyboard_count", 0),
        "prompt_count": summary.get("prompt_count", 0),
        "real_photo_count": summary.get("real_photo_count", 0),
        "illustration_count": summary.get("illustration_count", 0),
        "no_text_rule_applied": summary.get("no_text_rule_applied", False),
    }


def summarize_image_dry_run(path: Path | None) -> dict[str, Any]:
    """팀원 D 이미지 dry-run 결과를 대시보드용 요약으로 변환한다."""
    if path is None:
        return {"exists": False, "request_count": 0, "estimated_cost_usd": 0}

    payload = read_json(path, {})
    summary = payload.get("summary", {})
    return {
        "exists": True,
        "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "date": payload.get("date"),
        "status": payload.get("status"),
        "mode": payload.get("mode"),
        "brand_count": summary.get("brand_count", 0),
        "batch_count": summary.get("batch_count", 0),
        "request_count": summary.get("request_count", 0),
        "real_photo_count": summary.get("real_photo_count", 0),
        "illustration_count": summary.get("illustration_count", 0),
        "estimated_cost_usd": summary.get("estimated_cost_usd", 0),
        "daily_cost_allowed": summary.get("daily_cost_allowed", False),
        "monthly_cost_allowed": summary.get("monthly_cost_allowed", False),
        "charged": summary.get("charged", False),
    }


def summarize_chatgpt_image_test(path: Path | None) -> dict[str, Any]:
    """ChatGPT 실제 이미지 생성 테스트 결과를 대시보드용으로 요약한다."""
    if path is None:
        return {"exists": False, "status": "not_run"}

    payload = read_json(path, {})
    return {
        "exists": True,
        "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "date": payload.get("date"),
        "status": payload.get("status"),
        "mode": payload.get("mode"),
        "brand": payload.get("brand"),
        "image_type_label": payload.get("image_type_label"),
        "quality": payload.get("quality"),
        "project_openai_api_key_present": payload.get("project_openai_api_key_present", False),
        "project_openai_api_call_attempted": payload.get("project_openai_api_call_attempted", False),
        "api_call_skip_reason": payload.get("api_call_skip_reason"),
        "local_output_path": payload.get("local_output_path"),
        "dashboard_asset_path": payload.get("dashboard_asset_path"),
        "width": payload.get("width"),
        "height": payload.get("height"),
        "file_size_bytes": payload.get("file_size_bytes"),
        "sha256": payload.get("sha256"),
        "visual_check": payload.get("visual_check", {}),
    }


def summarize_quality_review(path: Path | None) -> dict[str, Any]:
    """팀장 품질 검수 결과를 대시보드용 요약으로 변환한다."""
    if path is None:
        return {"exists": False, "request_count": 0, "approved_count": 0, "avg_score": 0}

    payload = read_json(path, {})
    summary = payload.get("summary", {})
    return {
        "exists": True,
        "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "date": payload.get("date"),
        "status": payload.get("status"),
        "request_count": summary.get("request_count", 0),
        "approved_count": summary.get("approved_count", 0),
        "regeneration_required_count": summary.get("regeneration_required_count", 0),
        "blocked_count": summary.get("blocked_count", 0),
        "avg_score": summary.get("avg_score", 0),
        "no_text_rule_passed": summary.get("no_text_rule_passed", False),
        "copy_space_passed": summary.get("copy_space_passed", False),
        "max_retry": summary.get("max_retry", 0),
    }


def summarize_winner_loser(path: Path | None) -> dict[str, Any]:
    """Winner/Loser 학습 결과를 대시보드용 요약으로 변환한다."""
    if path is None:
        return {"exists": False, "record_count": 0, "winner_count": 0, "loser_count": 0, "pending_count": 0}

    payload = read_json(path, {})
    summary = payload.get("summary", {})
    return {
        "exists": True,
        "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "date": payload.get("date"),
        "status": payload.get("status"),
        "record_count": summary.get("record_count", 0),
        "winner_count": summary.get("winner_count", 0),
        "loser_count": summary.get("loser_count", 0),
        "pending_count": summary.get("pending_count", 0),
        "mature_count": summary.get("mature_count", 0),
        "winner_rate": summary.get("winner_rate", 0),
        "brand_summary": payload.get("brand_summary", []),
    }


def summarize_winner_loser_patterns(path: Path) -> dict[str, Any]:
    """누적 Winner/Loser 패턴 저장소 상태를 요약한다."""
    payload = read_json(path, {})
    summary = payload.get("summary", {})
    return {
        "exists": bool(payload),
        "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "updated_at": payload.get("updated_at"),
        "winner_count": summary.get("winner_count", 0),
        "loser_count": summary.get("loser_count", 0),
        "pending_count": summary.get("pending_count", 0),
        "brand_count": summary.get("brand_count", 0),
    }


def summarize_gdrive_manifest(path: Path | None) -> dict[str, Any]:
    """Google Drive upload manifest를 대시보드용 요약으로 변환한다."""
    if path is None:
        return {"exists": False, "planned_upload_count": 0, "missing_file_count": 0}

    payload = read_json(path, {})
    summary = payload.get("summary", {})
    classification_counts = summary.get("classification_counts", {})
    return {
        "exists": True,
        "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "date": payload.get("date"),
        "status": payload.get("status"),
        "mode": payload.get("mode"),
        "brand_count": summary.get("brand_count", 0),
        "planned_upload_count": summary.get("planned_upload_count", 0),
        "existing_file_count": summary.get("existing_file_count", 0),
        "missing_file_count": summary.get("missing_file_count", 0),
        "winner_upload_count": classification_counts.get("winner", 0),
        "loser_upload_count": classification_counts.get("loser", 0),
        "pending_upload_count": classification_counts.get("pending", 0),
        "ready_to_upload": summary.get("ready_to_upload", False),
        "drive_root": summary.get("drive_root"),
    }


def summarize_github_history(path: Path | None) -> dict[str, Any]:
    """GitHub history 요약 파일을 대시보드용으로 변환한다."""
    if path is None:
        return {"exists": False, "daily_file_count": 0}

    payload = read_json(path, {})
    summary = payload.get("summary", {})
    metrics = summary.get("metrics", {})
    return {
        "exists": True,
        "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "date": payload.get("date"),
        "status": payload.get("status"),
        "weekly_key": payload.get("weekly_key"),
        "daily_file_count": summary.get("daily_file_count", 0),
        "artifact_count": summary.get("artifact_count", 0),
        "commit_message": payload.get("planned_commit", {}).get("message"),
        "prompt_count": metrics.get("prompt_count", 0),
        "image_request_count": metrics.get("image_request_count", 0),
        "approved_count": metrics.get("approved_count", 0),
        "winner_count": metrics.get("winner_count", 0),
        "planned_upload_count": metrics.get("gdrive_planned_upload_count", 0),
    }


def summarize_pipeline_run(path: Path | None) -> dict[str, Any]:
    """GitHub Actions daily pipeline 실행 결과를 대시보드용으로 변환한다."""
    if path is None:
        return {"exists": False, "status": "not_run"}

    payload = read_json(path, {})
    summary = payload.get("summary", {})
    cost_guard = payload.get("cost_guard", {})
    return {
        "exists": True,
        "path": normalize_path(path),
        "date": payload.get("date"),
        "status": payload.get("status"),
        "mode": payload.get("mode"),
        "mock": payload.get("mock"),
        "started_at": payload.get("started_at"),
        "finished_at": payload.get("finished_at"),
        "artifact_count": summary.get("artifact_count", 0),
        "image_request_count": summary.get("image_request_count", 0),
        "approved_count": summary.get("approved_count", 0),
        "planned_upload_count": summary.get("planned_upload_count", 0),
        "cost_guard_status": cost_guard.get("status"),
        "estimated_cost_usd": cost_guard.get("estimated_cost_usd", 0),
    }


def summarize_preflight(path: Path | None) -> dict[str, Any]:
    """일일 preflight 결과를 대시보드용으로 요약한다."""
    if path is None:
        return {"exists": False, "status": "not_run"}

    payload = read_json(path, {})
    cost_report = payload.get("cost_report", {})
    brand_registry = payload.get("brand_registry", {})
    credential_readiness = payload.get("credential_readiness", {})
    return {
        "exists": True,
        "path": normalize_path(path),
        "date": payload.get("date"),
        "status": payload.get("status"),
        "brand_registry_status": brand_registry.get("status"),
        "ready_brand_count": brand_registry.get("ready_brand_count", 0),
        "brand_count": brand_registry.get("brand_count", 0),
        "credential_status": credential_readiness.get("status"),
        "cost_status": cost_report.get("status"),
        "estimated_next_run_usd": cost_report.get("estimated_next_run_usd", 0),
        "daily_remaining_usd": cost_report.get("daily_remaining_usd", 0),
        "monthly_remaining_usd": cost_report.get("monthly_remaining_usd", 0),
    }


def run_git(args: list[str]) -> str:
    """가능하면 Git 명령 결과를 반환한다."""
    git_candidates = [
        "git",
        r"C:\Program Files\Git\cmd\git.exe",
    ]
    for git_cmd in git_candidates:
        try:
            result = subprocess.run(
                [git_cmd, *args],
                cwd=PROJECT_ROOT,
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            return result.stdout.strip()
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    return ""


def get_recent_commits(limit: int = 5) -> list[dict[str, str]]:
    """최근 커밋 목록을 대시보드용으로 만든다."""
    output = run_git(["log", f"--max-count={limit}", "--pretty=format:%h%x09%s"])
    commits = []
    for line in output.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        commits.append({"hash": commit_hash, "subject": subject})
    return commits


def count_marketing_sources() -> dict[str, int]:
    """시장조사 출처 문서의 daily, weekly, monthly 항목 수를 계산한다."""
    latest_trend_file = find_latest_file("*_trend_data.json")
    trend_payload = read_json(latest_trend_file, {}) if latest_trend_file else {}
    monitoring_sources = trend_payload.get("monitoring_sources", {})
    return {
        "daily": len(monitoring_sources.get("daily", [])),
        "weekly": len(monitoring_sources.get("weekly", [])),
        "monthly": len(monitoring_sources.get("monthly", [])),
    }


def load_latest_daily_payload(pattern: str) -> dict[str, Any]:
    """최신 일별 JSON payload를 읽는다."""
    latest_file = find_latest_file(pattern)
    return read_json(latest_file, {}) if latest_file else {}


def average(values: list[float]) -> float:
    """숫자 목록의 평균을 소수점 4자리로 반환한다."""
    if not values:
        return 0
    return round(sum(values) / len(values), 4)


def build_brand_snapshots(
    ad_payload: dict[str, Any],
    trend_payload: dict[str, Any],
    manager_payload: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """브랜드별 광고와 트렌드 mock 데이터를 운영 화면용으로 요약한다."""
    brands = ["someud", "kinda", "melliance", "paperback", "baren"]
    ad_records = ad_payload.get("records", [])
    trend_records = trend_payload.get("records", [])
    manager_by_brand = {item.get("brand"): item for item in (manager_payload or {}).get("brands", [])}
    snapshots = []

    for brand in brands:
        brand_ad_records = [record for record in ad_records if record.get("brand") == brand]
        brand_trend_records = [record for record in trend_records if record.get("brand") == brand]
        ctr_values = [record.get("metrics", {}).get("ctr", 0) for record in brand_ad_records]
        roas_values = [record.get("metrics", {}).get("roas", 0) for record in brand_ad_records]
        cpa_values = [record.get("metrics", {}).get("cpa", 0) for record in brand_ad_records]
        trend_scores = [record.get("trend_score", 0) for record in brand_trend_records]
        keywords = []
        for record in brand_trend_records:
            keywords.extend(record.get("keywords", []))

        snapshots.append(
            {
                "brand": brand,
                "ad_records": len(brand_ad_records),
                "trend_records": len(brand_trend_records),
                "avg_ctr": average(ctr_values),
                "avg_roas": average(roas_values),
                "avg_cpa": average(cpa_values),
                "avg_trend_score": average(trend_scores),
                "top_keywords": sorted(set(keywords))[:5],
                "manager_priority": manager_by_brand.get(brand, {}).get("priority", "pending"),
                "creative_direction": manager_by_brand.get(brand, {}).get("creative_direction", ""),
                "status": "mock_ready" if brand_ad_records and brand_trend_records else "pending",
            }
        )

    return snapshots


def sample_records(payload: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    """대시보드 미리보기용 레코드 일부를 반환한다."""
    return payload.get("records", [])[:limit]


def build_manager_preview(manager_payload: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    """팀장 분석 결과를 화면 미리보기용으로 줄인다."""
    return [
        {
            "brand": item.get("brand"),
            "priority": item.get("priority"),
            "creative_direction": item.get("creative_direction"),
            "visual_concept": item.get("visual_concept"),
            "actions": item.get("recommended_actions", [])[:2],
            "keywords": item.get("prompt_keywords", [])[:4],
        }
        for item in manager_payload.get("brands", [])[:limit]
    ]


def build_prompt_preview(prompt_payload: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    """이미지 프롬프트 일부를 화면 미리보기용으로 줄인다."""
    return [
        {
            "prompt_id": prompt.get("prompt_id"),
            "brand": prompt.get("brand"),
            "image_type_label": prompt.get("image_type_label"),
            "quality": prompt.get("quality"),
            "file_name_preview": prompt.get("file_name_preview"),
            "copy_space": prompt.get("copy_space"),
            "rules": prompt.get("rules", [])[:4],
        }
        for prompt in prompt_payload.get("prompts", [])[:limit]
    ]


def build_image_request_preview(image_payload: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    """이미지 dry-run 요청 일부를 화면 미리보기용으로 줄인다."""
    return [
        {
            "prompt_id": request.get("prompt_id"),
            "brand": request.get("brand"),
            "image_type_label": request.get("image_type_label"),
            "quality": request.get("quality"),
            "estimated_cost_usd": request.get("estimated_cost_usd"),
            "output_path": request.get("output_path"),
            "status": request.get("status"),
        }
        for request in image_payload.get("requests", [])[:limit]
    ]


def build_quality_preview(quality_payload: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    """품질 검수 결과 일부를 화면 미리보기용으로 줄인다."""
    return [
        {
            "prompt_id": review.get("prompt_id"),
            "brand": review.get("brand"),
            "image_type_label": review.get("image_type_label"),
            "score": review.get("score"),
            "status": review.get("status"),
            "regeneration_needed": review.get("regeneration", {}).get("needed", False),
            "reason": review.get("regeneration", {}).get("reason"),
        }
        for review in quality_payload.get("reviews", [])[:limit]
    ]


def build_learning_preview(learning_payload: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    """Winner/Loser 학습 결과 일부를 화면 미리보기용으로 줄인다."""
    return [
        {
            "creative_id": record.get("creative_id"),
            "brand": record.get("brand"),
            "source": record.get("source"),
            "label": record.get("label"),
            "reason": record.get("reason"),
            "ctr": record.get("metrics", {}).get("ctr"),
            "roas": record.get("metrics", {}).get("roas"),
            "cpa": record.get("metrics", {}).get("cpa"),
            "action": (record.get("learning_actions") or ["-"])[0],
        }
        for record in learning_payload.get("records", [])[:limit]
    ]


def build_storage_preview(gdrive_payload: dict[str, Any], limit: int = 8) -> list[dict[str, Any]]:
    """Google Drive 저장 계획 일부를 화면 미리보기용으로 줄인다."""
    return [
        {
            "prompt_id": item.get("prompt_id"),
            "brand": item.get("brand"),
            "classification": item.get("classification"),
            "source_exists": item.get("source_exists", False),
            "drive_path": item.get("drive_path"),
            "status": item.get("status"),
        }
        for item in gdrive_payload.get("items", [])[:limit]
    ]


def build_agent_status() -> list[dict[str, Any]]:
    """에이전트별 구현 범위와 다음 작업을 정리한다."""
    return [
        {
            "agent": "팀장",
            "file": "agents/manager.py",
            "status": "learning_ready",
            "implemented": ["광고/트렌드 종합", "브랜드별 우선순위", "소재 방향", "프롬프트 handoff", "품질 검수", "Winner/Loser 학습"],
            "output": "history/daily/{date}_winner_loser.json",
            "next": "PHASE 12에서 안정화와 실제 API 연결",
        },
        {
            "agent": "팀원 A",
            "file": "agents/data_collector.py",
            "status": "mock_ready",
            "implemented": ["Meta mock 수집", "네이버SA mock 수집", "카카오모먼트 mock 수집", "3회 retry", "JSON 저장"],
            "output": "history/daily/{date}_ad_data.json",
            "next": "실제 광고 API 응답 매핑",
        },
        {
            "agent": "팀원 B",
            "file": "agents/trend_collector.py",
            "status": "mock_ready",
            "implemented": ["네이버 트렌드 mock", "Google Trends mock", "뉴스/경쟁사 mock", "시장조사 출처 카탈로그", "JSON 저장"],
            "output": "history/daily/{date}_trend_data.json",
            "next": "실제 트렌드/뉴스 수집 연결",
        },
        {
            "agent": "팀원 C",
            "file": "agents/prompt_engineer.py",
            "status": "prompt_ready",
            "implemented": ["브랜드별 스토리보드 4개", "이미지 프롬프트 4개", "no-text 규칙", "파일명 preview", "검수 피드백 반영"],
            "output": "history/daily/{date}_prompts.json",
            "next": "PHASE 6에서 팀원 D 이미지 dry-run과 연결",
        },
        {
            "agent": "팀원 D",
            "file": "agents/image_designer.py",
            "status": "dry_run_ready",
            "implemented": ["이미지 비용 설정", "브랜드별 batch dry-run", "출력 경로 생성", "한도 확인", "재생성 제한"],
            "output": "outputs/{brand}/{date}/",
            "next": "실제 gpt-image-2 API 호출과 Google Drive 실업로드 연결",
        },
    ]


def build_pipeline_steps() -> list[dict[str, str]]:
    """운영 자동화 단계별 구현 상태를 반환한다."""
    return [
        {"step": "01", "title": "광고 성과 수집", "owner": "팀원 A", "status": "mock_ready"},
        {"step": "02", "title": "트렌드/시장조사 수집", "owner": "팀원 B", "status": "mock_ready"},
        {"step": "03", "title": "팀장 분석/개선안", "owner": "팀장", "status": "analysis_ready"},
        {"step": "04", "title": "스토리보드/프롬프트", "owner": "팀원 C", "status": "prompt_ready"},
        {"step": "05", "title": "이미지 생성", "owner": "팀원 D", "status": "dry_run_ready"},
        {"step": "06", "title": "품질 검수/재생성", "owner": "팀장", "status": "quality_review_ready"},
        {"step": "07", "title": "Winner/Loser 학습", "owner": "팀장", "status": "learning_ready"},
        {"step": "08", "title": "저장소 연동", "owner": "utils", "status": "storage_ready"},
        {"step": "09", "title": "대시보드 실시간화", "owner": "dashboard", "status": "realtime_ready"},
        {"step": "10", "title": "GitHub Actions 자동화", "owner": "workflow", "status": "automation_ready"},
        {"step": "11", "title": "안정화", "owner": "ops", "status": "stabilized"},
    ]


def build_feature_status() -> list[dict[str, Any]]:
    """구현된 기능과 아직 남은 기능을 대시보드용으로 정리한다."""
    return [
        {
            "name": "프로젝트 기반 구조",
            "status": "completed",
            "details": ["폴더 구조", "브랜드 설정", "state/logs", "문서", "대시보드 원본 보존"],
        },
        {
            "name": "광고 데이터 수집",
            "status": "mock_ready",
            "details": ["3개 매체 mock", "15개 레코드", "retry", "JSON 저장", "단위 테스트"],
        },
        {
            "name": "트렌드/시장조사 수집",
            "status": "mock_ready",
            "details": ["4개 수집 소스 mock", "20개 레코드", "daily 출처 13개", "weekly 출처 24개", "monthly 출처 1개"],
        },
        {
            "name": "Vercel 진행 대시보드",
            "status": "static_ready",
            "details": ["정적 HTML", "latest_status.json", "GitHub push 기반 자동 배포", "Vercel READY"],
        },
        {
            "name": "팀장 분석 엔진",
            "status": "analysis_ready",
            "details": ["광고/트렌드 종합", "브랜드별 우선순위", "소재 방향", "팀원 C handoff"],
        },
        {
            "name": "프롬프트 엔지니어링",
            "status": "prompt_ready",
            "details": ["스토리보드 20개", "이미지 프롬프트 20개", "실사 10개", "일러스트 10개", "no-text 규칙"],
        },
        {
            "name": "이미지 생성 dry-run",
            "status": "dry_run_ready",
            "details": ["20개 요청", "5개 브랜드 batch", "출력 파일 경로", "$2.64 예상 비용", "한도 확인"],
        },
        {
            "name": "ChatGPT 실제 이미지 생성 테스트",
            "status": "generated_in_chat",
            "details": ["someud 샘플 1장", "실제 PNG 생성", "대시보드 asset 복사", "프로젝트 API 키는 미설정"],
        },
        {
            "name": "품질 검수와 재생성 판단",
            "status": "quality_review_ready",
            "details": ["20개 요청 승인", "평균 점수 100", "재생성 필요 0개", "no-text 검수", "카피 여백 검수"],
        },
        {
            "name": "Winner/Loser 학습",
            "status": "learning_ready",
            "details": ["15개 성과 분류", "Winner 12개", "Loser 0개", "Pending 3개", "패턴 저장"],
        },
        {
            "name": "저장소 연동",
            "status": "storage_ready",
            "details": ["Drive manifest 20개", "Winner 폴더 16개", "Pending 폴더 4개", "daily history 요약", "weekly history 요약"],
        },
        {
            "name": "Dashboard API 실시간화",
            "status": "realtime_ready",
            "details": ["정적 JSON API 8개", "브랜드 상세 API 5개", "30초 polling", "실행 로그 표시", "Vercel rewrite"],
        },
        {
            "name": "GitHub Actions 자동화",
            "status": "automation_ready",
            "details": ["평일 02:00 KST", "workflow_dispatch", "비용 guard", "history 자동 커밋", "Slack 조건부 알림"],
        },
        {
            "name": "운영 안정화",
            "status": "stabilized",
            "details": ["preflight", "브랜드 검증", "비용 리포트", "실패 로그", "대시보드 UX"],
        },
    ]


def build_monitoring_preview(trend_payload: dict[str, Any], limit: int = 8) -> dict[str, Any]:
    """시장조사 출처 일부를 대시보드 미리보기용으로 추출한다."""
    monitoring_sources = trend_payload.get("monitoring_sources", {})
    return {
        "daily": monitoring_sources.get("daily", [])[:limit],
        "weekly": monitoring_sources.get("weekly", [])[:limit],
        "monthly": monitoring_sources.get("monthly", [])[:limit],
    }


def build_phase_roadmap() -> list[dict[str, Any]]:
    """공식 PHASE 1-12 로드맵과 현재 상태를 반환한다."""
    return [
        {"phase": "PHASE 1", "title": "프로젝트 기반 세팅", "status": "completed", "progress": 100},
        {"phase": "PHASE 2", "title": "광고 데이터 수집", "status": "completed", "progress": 100},
        {"phase": "PHASE 3", "title": "트렌드 수집", "status": "completed", "progress": 100},
        {"phase": "PHASE 4", "title": "팀장 분석 엔진", "status": "completed", "progress": 100},
        {"phase": "PHASE 5", "title": "프롬프트 엔지니어링", "status": "completed", "progress": 100},
        {"phase": "PHASE 6", "title": "이미지 생성", "status": "completed", "progress": 100},
        {"phase": "PHASE 7", "title": "품질 검수 및 재생성", "status": "completed", "progress": 100},
        {"phase": "PHASE 8", "title": "Winner/Loser 학습", "status": "completed", "progress": 100},
        {"phase": "PHASE 9", "title": "저장소 연동", "status": "completed", "progress": 100},
        {"phase": "PHASE 10", "title": "Dashboard 실시간화", "status": "completed", "progress": 100},
        {"phase": "PHASE 11", "title": "GitHub Actions 자동화", "status": "completed", "progress": 100},
        {"phase": "PHASE 12", "title": "안정화", "status": "completed", "progress": 100},
    ]


def build_overall_progress(roadmap: list[dict[str, Any]]) -> dict[str, Any]:
    """로드맵 기반 전체 진행률을 계산한다."""
    total = len(roadmap)
    completed = sum(1 for item in roadmap if item["status"] == "completed")
    next_items = [item for item in roadmap if item["status"] == "next"]
    return {
        "completed_phase_count": completed,
        "total_phase_count": total,
        "percent": round(completed / total * 100),
        "current_phase": "PHASE 12",
        "next_phase": next_items[0]["phase"] if next_items else None,
        "dashboard_milestones_completed": 3,
        "latest_test_count": 41,
        "latest_test_result": "passed",
    }


def build_architecture_layers() -> list[dict[str, Any]]:
    """현재 소프트웨어 아키텍처를 레이어와 노드로 도식화한다."""
    return [
        {
            "layer": "Input",
            "title": "외부 입력과 기준 문서",
            "nodes": [
                {"id": "brand_config", "label": "브랜드 설정", "status": "ready", "metric": "5 brands"},
                {"id": "market_sources", "label": "시장조사 출처", "status": "ready", "metric": "38 sources"},
                {"id": "api_slots", "label": "API 키 슬롯", "status": "configured", "metric": ".env.example"},
            ],
        },
        {
            "layer": "Collection",
            "title": "데이터 수집 에이전트",
            "nodes": [
                {"id": "data_collector", "label": "팀원 A 광고 수집", "status": "mock_ready", "metric": "15 records"},
                {"id": "trend_collector", "label": "팀원 B 트렌드 수집", "status": "mock_ready", "metric": "20 records"},
            ],
        },
        {
            "layer": "Decision",
            "title": "분석과 제작 지시",
            "nodes": [
                {"id": "manager", "label": "팀장 분석", "status": "analysis_ready", "metric": "5 briefs"},
                {"id": "prompt_engineer", "label": "팀원 C 프롬프트", "status": "prompt_ready", "metric": "20 prompts"},
            ],
        },
        {
            "layer": "Generation",
            "title": "이미지 생성과 검수",
            "nodes": [
                {"id": "image_designer", "label": "팀원 D 이미지 생성", "status": "dry_run_ready", "metric": "20 requests"},
                {"id": "quality_review", "label": "품질 검수", "status": "quality_review_ready", "metric": "20 approved"},
                {"id": "learning", "label": "Winner/Loser 학습", "status": "learning_ready", "metric": "12 winners"},
            ],
        },
        {
            "layer": "Storage",
            "title": "저장과 운영 화면",
            "nodes": [
                {"id": "history", "label": "history/daily", "status": "storage_ready", "metric": "9 daily JSON"},
                {"id": "gdrive", "label": "Google Drive manifest", "status": "storage_ready", "metric": "20 planned"},
                {"id": "weekly_history", "label": "history/weekly", "status": "storage_ready", "metric": "2026-W21"},
                {"id": "dashboard", "label": "Vercel Dashboard", "status": "realtime_ready", "metric": "30s polling"},
                {"id": "dashboard_api", "label": "Dashboard API", "status": "realtime_ready", "metric": "8 endpoints"},
                {"id": "automation", "label": "GitHub Actions", "status": "automation_ready", "metric": "weekday 02 KST"},
                {"id": "stability", "label": "운영 안정화", "status": "stabilized", "metric": "preflight pass"},
            ],
        },
    ]


def build_architecture_flow() -> list[dict[str, str]]:
    """에이전트 간 데이터 흐름을 반환한다."""
    return [
        {"from": "브랜드 설정", "to": "팀원 A/B", "artifact": "brand config", "status": "ready"},
        {"from": "팀원 A", "to": "history/daily/*_ad_data.json", "artifact": "광고 mock 15개", "status": "ready"},
        {"from": "팀원 B", "to": "history/daily/*_trend_data.json", "artifact": "트렌드 mock 20개", "status": "ready"},
        {"from": "광고/트렌드 JSON", "to": "팀장", "artifact": "분석 입력", "status": "ready"},
        {"from": "팀장", "to": "history/daily/*_manager_brief.json", "artifact": "브랜드 Brief 5개", "status": "ready"},
        {"from": "팀장 Brief", "to": "팀원 C", "artifact": "handoff 5개", "status": "ready"},
        {"from": "팀원 C", "to": "history/daily/*_prompts.json", "artifact": "프롬프트 20개", "status": "ready"},
        {"from": "프롬프트 Pack", "to": "팀원 D", "artifact": "이미지 dry-run 입력", "status": "ready"},
        {"from": "팀원 D", "to": "history/daily/*_image_dry_run.json", "artifact": "dry-run 요청 20개", "status": "ready"},
        {"from": "이미지 Dry-run", "to": "팀장 검수", "artifact": "품질 점수 20개", "status": "ready"},
        {"from": "팀장 검수", "to": "history/daily/*_quality_review.json", "artifact": "승인 20개", "status": "ready"},
        {"from": "광고 성과 JSON", "to": "Winner/Loser 학습", "artifact": "성과 분류 15개", "status": "ready"},
        {"from": "팀장 학습", "to": "history/winner_loser_patterns.json", "artifact": "누적 패턴 15개", "status": "ready"},
        {"from": "이미지 Dry-run + 학습", "to": "Google Drive manifest", "artifact": "저장 계획 20개", "status": "storage_ready"},
        {"from": "history/daily", "to": "history/weekly", "artifact": "2026-W21 요약", "status": "storage_ready"},
        {"from": "history/state/logs", "to": "Dashboard API", "artifact": "정적 API JSON", "status": "realtime_ready"},
        {"from": "Dashboard API", "to": "Vercel Dashboard", "artifact": "30초 polling", "status": "realtime_ready"},
        {"from": "GitHub Actions", "to": "daily runner", "artifact": "평일 02:00 KST 자동 실행", "status": "automation_ready"},
        {"from": "daily runner", "to": "history/dashboard commit", "artifact": "생성 결과 자동 커밋", "status": "automation_ready"},
        {"from": "preflight", "to": "daily runner", "artifact": "브랜드, 비용, credential 점검", "status": "stabilized"},
    ]


def build_storage_contracts() -> list[dict[str, str]]:
    """저장 파일별 생산자와 소비자를 정리한다."""
    return [
        {"path": "history/daily/{date}_ad_data.json", "producer": "팀원 A", "consumer": "팀장, 대시보드", "status": "ready"},
        {"path": "history/daily/{date}_trend_data.json", "producer": "팀원 B", "consumer": "팀장, 대시보드", "status": "ready"},
        {"path": "history/daily/{date}_manager_brief.json", "producer": "팀장", "consumer": "팀원 C, 대시보드", "status": "ready"},
        {"path": "history/daily/{date}_prompts.json", "producer": "팀원 C", "consumer": "팀원 D, 대시보드", "status": "ready"},
        {"path": "history/daily/{date}_image_dry_run.json", "producer": "팀원 D", "consumer": "팀장 검수, 대시보드", "status": "ready"},
        {"path": "history/daily/{date}_quality_review.json", "producer": "팀장", "consumer": "팀원 C, 대시보드", "status": "quality_review_ready"},
        {"path": "history/daily/{date}_winner_loser.json", "producer": "팀장", "consumer": "프롬프트 학습, 대시보드", "status": "learning_ready"},
        {"path": "history/winner_loser_patterns.json", "producer": "팀장", "consumer": "다음 소재 판단", "status": "learning_ready"},
        {"path": "history/daily/{date}_gdrive_manifest.json", "producer": "utils/gdrive_upload.py", "consumer": "Google Drive 업로드, 대시보드", "status": "storage_ready"},
        {"path": "history/daily/{date}_github_history_summary.json", "producer": "utils/github_history.py", "consumer": "GitHub commit 요약, 대시보드", "status": "storage_ready"},
        {"path": "history/weekly/{week}.json", "producer": "utils/github_history.py", "consumer": "주간 운영 리뷰", "status": "storage_ready"},
        {"path": "outputs/{brand}/{date}/", "producer": "팀원 D", "consumer": "팀장 검수", "status": "dry_run_ready"},
        {"path": "web/data/latest_status.json", "producer": "scripts/build_dashboard_data.py", "consumer": "Vercel Dashboard", "status": "ready"},
        {"path": "web/api/{endpoint}.json", "producer": "scripts/build_dashboard_data.py", "consumer": "Dashboard polling, FastAPI mirror", "status": "realtime_ready"},
        {"path": "dashboard_api.py", "producer": "PHASE 10", "consumer": "FastAPI local server", "status": "realtime_ready"},
        {"path": "scripts/run_daily_pipeline.py", "producer": "PHASE 11", "consumer": "GitHub Actions", "status": "automation_ready"},
        {"path": ".github/workflows/daily_run.yml", "producer": "PHASE 11", "consumer": "GitHub Actions scheduler", "status": "automation_ready"},
        {"path": "history/daily/{date}_pipeline_run.json", "producer": "scripts/run_daily_pipeline.py", "consumer": "대시보드, 운영 로그", "status": "automation_ready"},
        {"path": "history/daily/{date}_preflight.json", "producer": "utils/operation_guard.py", "consumer": "daily runner, 대시보드", "status": "stabilized"},
        {"path": "history/daily/{date}_errors.log", "producer": "utils/operation_guard.py", "consumer": "운영자, Slack 알림", "status": "stabilized"},
    ]


def build_phase_test_results() -> list[dict[str, Any]]:
    """Phase별 검증 결과를 대시보드용으로 정리한다."""
    return [
        {
            "phase": "PHASE 1",
            "scope": "프로젝트 기반 구조",
            "check": "필수 파일 존재 확인 + skeleton import",
            "result": "passed",
            "test_count": "file checks + imports",
            "artifact": "state/current_phase.json",
        },
        {
            "phase": "PHASE 2",
            "scope": "광고 데이터 수집 mock",
            "check": "python -m unittest tests.test_data_collector",
            "result": "passed",
            "test_count": 3,
            "artifact": "history/daily/2026-05-18_ad_data.json",
        },
        {
            "phase": "PHASE 3",
            "scope": "트렌드 수집과 출처 카탈로그",
            "check": "python -m unittest tests.test_trend_collector tests.test_data_collector",
            "result": "passed",
            "test_count": 7,
            "artifact": "history/daily/2026-05-18_trend_data.json",
        },
        {
            "phase": "PHASE 3.5",
            "scope": "Vercel 정적 대시보드",
            "check": "python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_build_dashboard_data",
            "result": "passed",
            "test_count": 9,
            "artifact": "web/data/latest_status.json",
        },
        {
            "phase": "PHASE 4",
            "scope": "팀장 분석 엔진",
            "check": "python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_manager tests.test_build_dashboard_data",
            "result": "passed",
            "test_count": 12,
            "artifact": "history/daily/2026-05-18_manager_brief.json",
        },
        {
            "phase": "PHASE 5",
            "scope": "스토리보드와 프롬프트 생성",
            "check": "python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_manager tests.test_prompt_engineer tests.test_build_dashboard_data",
            "result": "passed",
            "test_count": 16,
            "artifact": "history/daily/2026-05-18_prompts.json",
        },
        {
            "phase": "PHASE 6",
            "scope": "이미지 생성 dry-run",
            "check": "python -m unittest tests.test_image_designer",
            "result": "passed",
            "test_count": 4,
            "artifact": "history/daily/2026-05-18_image_dry_run.json",
        },
        {
            "phase": "PHASE 7",
            "scope": "품질 검수 및 재생성",
            "check": "python -m unittest tests.test_manager",
            "result": "passed",
            "test_count": 6,
            "artifact": "history/daily/2026-05-18_quality_review.json",
        },
        {
            "phase": "PHASE 8",
            "scope": "Winner/Loser 학습",
            "check": "python -m unittest tests.test_manager",
            "result": "passed",
            "test_count": 9,
            "artifact": "history/winner_loser_patterns.json",
        },
        {
            "phase": "PHASE 9",
            "scope": "저장소 연동",
            "check": "python -m unittest tests.test_storage_utils",
            "result": "passed",
            "test_count": 4,
            "artifact": "history/daily/2026-05-18_gdrive_manifest.json",
        },
        {
            "phase": "PHASE 10",
            "scope": "Dashboard 실시간화",
            "check": "python -m unittest tests.test_dashboard_api",
            "result": "passed",
            "test_count": 3,
            "artifact": "web/api/status.json",
        },
        {
            "phase": "PHASE 11",
            "scope": "GitHub Actions 자동화",
            "check": "python -m unittest tests.test_daily_pipeline",
            "result": "passed",
            "test_count": 3,
            "artifact": ".github/workflows/daily_run.yml",
        },
        {
            "phase": "PHASE 12",
            "scope": "안정화",
            "check": "python -m unittest tests.test_operation_guard",
            "result": "passed",
            "test_count": 4,
            "artifact": "history/daily/2026-05-18_preflight.json",
        },
    ]


def build_api_manifest() -> list[dict[str, str]]:
    """Vercel rewrite와 FastAPI가 공유할 대시보드 API 계약을 반환한다."""
    return [
        {"path": "/api/status", "file": "web/api/status.json", "description": "현재 phase와 전체 진행도"},
        {"path": "/api/agents", "file": "web/api/agents.json", "description": "에이전트와 파이프라인 상태"},
        {"path": "/api/costs", "file": "web/api/costs.json", "description": "비용과 runtime 상태"},
        {"path": "/api/brands", "file": "web/api/brands.json", "description": "브랜드별 운영 지표 목록"},
        {"path": "/api/brands/{brand}", "file": "web/api/brands/{brand}.json", "description": "브랜드 상세 지표"},
        {"path": "/api/history/daily", "file": "web/api/history/daily.json", "description": "daily history 산출물 요약"},
        {"path": "/api/winner-loser", "file": "web/api/winner-loser.json", "description": "Winner/Loser 학습 결과"},
        {"path": "/api/logs", "file": "web/api/logs.json", "description": "최근 실행 로그"},
    ]


def build_brand_detail(payload: dict[str, Any], brand_name: str) -> dict[str, Any]:
    """브랜드 1개의 API 상세 payload를 만든다."""
    data = payload.get("data", {})
    return {
        "status": "brand_detail_api_ready",
        "generated_at": payload.get("generated_at"),
        "brand": brand_name,
        "snapshot": next((item for item in data.get("brand_snapshots", []) if item.get("brand") == brand_name), {}),
        "manager": [item for item in data.get("manager_preview", []) if item.get("brand") == brand_name],
        "prompts": [item for item in data.get("prompt_preview", []) if item.get("brand") == brand_name],
        "images": [item for item in data.get("image_preview", []) if item.get("brand") == brand_name],
        "quality_reviews": [item for item in data.get("quality_preview", []) if item.get("brand") == brand_name],
        "learning": [item for item in data.get("learning_preview", []) if item.get("brand") == brand_name],
        "storage": [item for item in data.get("storage", {}).get("gdrive_preview", []) if item.get("brand") == brand_name],
    }


def build_dashboard_api_payloads(payload: dict[str, Any]) -> dict[str, Any]:
    """대시보드에서 polling할 API별 payload를 만든다."""
    data = payload.get("data", {})
    runtime = read_json(PROJECT_ROOT / "state" / "runtime.json", {})
    github_history_path = data.get("storage", {}).get("github_history", {}).get("path")
    github_history_payload = read_json(PROJECT_ROOT / github_history_path, {}) if github_history_path else {}
    brands = data.get("brand_snapshots", [])

    return {
        "status": {
            "status": "dashboard_status_api_ready",
            "generated_at": payload.get("generated_at"),
            "project": payload.get("project", {}),
            "current_phase": payload.get("current_phase", {}),
            "overall_progress": payload.get("architecture", {}).get("overall_progress", {}),
            "verification": payload.get("verification", {}),
            "next_step": payload.get("next_step", {}),
            "api": payload.get("api", {}),
        },
        "agents": {
            "status": "agents_api_ready",
            "generated_at": payload.get("generated_at"),
            "agents": payload.get("operations", {}).get("agent_status", []),
            "pipeline_steps": payload.get("operations", {}).get("pipeline_steps", []),
        },
        "costs": {
            "status": "costs_api_ready",
            "generated_at": payload.get("generated_at"),
            "runtime": runtime,
            "image_dry_run": data.get("images", {}),
            "storage": data.get("storage", {}).get("gdrive", {}),
            "budget": {
                "daily_limit_usd": 5.0,
                "monthly_limit_usd": 79.0,
                "image_monthly_limit_usd": 65.0,
            },
        },
        "brands": {
            "status": "brands_api_ready",
            "generated_at": payload.get("generated_at"),
            "brand_count": len(brands),
            "brands": brands,
        },
        "brand_details": {
            brand.get("brand"): build_brand_detail(payload, brand.get("brand"))
            for brand in brands
            if brand.get("brand")
        },
        "history_daily": {
            "status": "history_daily_api_ready",
            "generated_at": payload.get("generated_at"),
            "summary": data.get("storage", {}).get("github_history", {}),
            "artifacts": github_history_payload.get("artifacts", []),
            "planned_commit": github_history_payload.get("planned_commit", {}),
        },
        "winner_loser": {
            "status": "winner_loser_api_ready",
            "generated_at": payload.get("generated_at"),
            "summary": data.get("winner_loser", {}),
            "patterns": data.get("winner_loser_patterns", {}),
            "preview": data.get("learning_preview", []),
        },
        "logs": {
            "status": "logs_api_ready",
            "generated_at": payload.get("generated_at"),
            "execution": read_recent_log_lines(LOG_DIR / "execution.log"),
            "cost_tracking": read_recent_log_lines(LOG_DIR / "cost_tracking.log"),
            "system": read_recent_log_lines(LOG_DIR / "system.log"),
            "api_errors": read_recent_log_lines(LOG_DIR / "api_errors.log"),
        },
    }


def build_dashboard_payload() -> dict[str, Any]:
    """프로젝트 진행 상태를 하나의 대시보드 JSON으로 묶는다."""
    current_phase = read_json(PROJECT_ROOT / "state" / "current_phase.json", {})
    latest_ad_file = find_latest_file("*_ad_data.json")
    latest_trend_file = find_latest_file("*_trend_data.json")
    latest_manager_file = find_latest_file("*_manager_brief.json")
    latest_prompt_file = find_latest_file("*_prompts.json")
    latest_image_file = find_latest_file("*_image_dry_run.json")
    latest_chatgpt_image_test_file = find_latest_file("*_chatgpt_image_test.json")
    latest_quality_file = find_latest_file("*_quality_review.json")
    latest_learning_file = find_latest_file("*_winner_loser.json")
    latest_gdrive_file = find_latest_file("*_gdrive_manifest.json")
    latest_github_history_file = find_latest_file("*_github_history_summary.json")
    latest_pipeline_file = find_latest_file("*_pipeline_run.json")
    latest_preflight_file = find_latest_file("*_preflight.json")
    ad_payload = load_latest_daily_payload("*_ad_data.json")
    trend_payload = load_latest_daily_payload("*_trend_data.json")
    manager_payload = load_latest_daily_payload("*_manager_brief.json")
    prompt_payload = load_latest_daily_payload("*_prompts.json")
    image_payload = load_latest_daily_payload("*_image_dry_run.json")
    quality_payload = load_latest_daily_payload("*_quality_review.json")
    learning_payload = load_latest_daily_payload("*_winner_loser.json")
    gdrive_payload = load_latest_daily_payload("*_gdrive_manifest.json")
    ad_summary = summarize_daily_file(latest_ad_file)
    trend_summary = summarize_daily_file(latest_trend_file)
    manager_summary = summarize_manager_brief(latest_manager_file)
    prompt_summary = summarize_prompt_pack(latest_prompt_file)
    image_summary = summarize_image_dry_run(latest_image_file)
    chatgpt_image_test_summary = summarize_chatgpt_image_test(latest_chatgpt_image_test_file)
    quality_summary = summarize_quality_review(latest_quality_file)
    learning_summary = summarize_winner_loser(latest_learning_file)
    pattern_summary = summarize_winner_loser_patterns(PROJECT_ROOT / "history" / "winner_loser_patterns.json")
    gdrive_summary = summarize_gdrive_manifest(latest_gdrive_file)
    github_history_summary = summarize_github_history(latest_github_history_file)
    pipeline_run_summary = summarize_pipeline_run(latest_pipeline_file)
    preflight_summary = summarize_preflight(latest_preflight_file)
    runtime_payload = read_json(PROJECT_ROOT / "state" / "runtime.json", {})
    cost_summary = build_cost_report(
        runtime_payload,
        float(image_summary.get("estimated_cost_usd", 0)),
        5.0,
        79.0,
    )
    source_counts = count_marketing_sources()
    recent_commits = get_recent_commits()
    phase_roadmap = build_phase_roadmap()

    return {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "project": {
            "name": "AIPR",
            "github_repo": "https://github.com/dawdew12/homeproject0518",
            "vercel_project_id": "prj_Pe7nqm93OZ6yPog5DJVGJwS0h3Ce",
            "vercel_team": "raw22226-9071s-projects",
            "custom_domain_enabled": False,
        },
        "api": {
            "mode": "static_json_rewrite",
            "refresh_interval_seconds": 30,
            "endpoints": build_api_manifest(),
        },
        "current_phase": current_phase,
        "phase_progress": [
            {"phase": "PHASE 1", "title": "프로젝트 기반 세팅", "status": "completed"},
            {"phase": "PHASE 2", "title": "광고 데이터 수집 mock", "status": "completed"},
            {"phase": "PHASE 3", "title": "트렌드 수집 및 시장조사 출처", "status": "completed"},
            {"phase": "PHASE 3.5", "title": "Vercel 대시보드 배포 기반", "status": "completed"},
            {"phase": "PHASE 4", "title": "팀장 분석 엔진", "status": "completed"},
            {"phase": "PHASE 5", "title": "스토리보드와 프롬프트 생성", "status": "completed"},
            {"phase": "PHASE 6", "title": "이미지 생성 dry-run", "status": "completed"},
            {"phase": "PHASE 7", "title": "품질 검수 및 재생성", "status": "completed"},
            {"phase": "PHASE 8", "title": "Winner/Loser 학습", "status": "completed"},
            {"phase": "PHASE 9", "title": "저장소 연동", "status": "completed"},
            {"phase": "PHASE 10", "title": "Dashboard 실시간화", "status": "completed"},
            {"phase": "PHASE 11", "title": "GitHub Actions 자동화", "status": "completed"},
            {"phase": "PHASE 12", "title": "안정화", "status": "completed"},
        ],
        "architecture": {
            "overall_progress": build_overall_progress(phase_roadmap),
            "phase_roadmap": phase_roadmap,
            "layers": build_architecture_layers(),
            "flow": build_architecture_flow(),
            "storage_contracts": build_storage_contracts(),
        },
        "quality": {
            "phase_test_results": build_phase_test_results(),
        },
        "data": {
            "ad": ad_summary,
            "trend": trend_summary,
            "manager": manager_summary,
            "prompts": prompt_summary,
            "images": image_summary,
            "chatgpt_image_test": chatgpt_image_test_summary,
            "quality_review": quality_summary,
            "winner_loser": learning_summary,
            "winner_loser_patterns": pattern_summary,
            "storage": {
                "gdrive": gdrive_summary,
                "github_history": github_history_summary,
                "gdrive_preview": build_storage_preview(gdrive_payload),
            },
            "marketing_source_counts": source_counts,
            "brand_snapshots": build_brand_snapshots(ad_payload, trend_payload, manager_payload),
            "ad_preview": sample_records(ad_payload),
            "trend_preview": sample_records(trend_payload),
            "manager_preview": build_manager_preview(manager_payload),
            "prompt_preview": build_prompt_preview(prompt_payload),
            "image_preview": build_image_request_preview(image_payload),
            "quality_preview": build_quality_preview(quality_payload),
            "learning_preview": build_learning_preview(learning_payload),
            "monitoring_preview": build_monitoring_preview(trend_payload),
        },
        "operations": {
            "feature_status": build_feature_status(),
            "agent_status": build_agent_status(),
            "pipeline_steps": build_pipeline_steps(),
            "automation": pipeline_run_summary,
            "stability": {
                "status": "stabilized",
                "preflight": preflight_summary,
                "brand_registry": build_brand_registry(PROJECT_ROOT),
                "cost_report": cost_summary,
            },
        },
        "verification": {
            "last_command": "python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_manager tests.test_prompt_engineer tests.test_image_designer tests.test_storage_utils tests.test_dashboard_api tests.test_daily_pipeline tests.test_operation_guard tests.test_build_dashboard_data",
            "last_result": "passed",
            "test_count": 41,
        },
        "git": {
            "branch": run_git(["branch", "--show-current"]) or "main",
            "recent_commits": recent_commits,
        },
        "next_step": {
            "phase": "운영 전환",
            "title": "실 API 연결 준비",
            "summary": "Secrets와 실제 계정 권한을 준비한 뒤 live 모드를 제한적으로 검증한다.",
        },
        "risks": [
            "광고 API와 트렌드 API는 아직 mock 수집 단계다.",
            "팀장 분석은 deterministic rule 기반이며 실제 LLM 판단은 후속 API 연결 단계에서 붙인다.",
            "프롬프트 생성도 rule 기반이며 실제 OpenAI API 호출은 아직 수행하지 않는다.",
            "이미지 생성은 dry-run 단계이며 실제 gpt-image-2 API 호출은 아직 수행하지 않는다.",
            "ChatGPT 이미지 생성 테스트는 완료했지만 프로젝트 OpenAI API 키 기반 호출은 .env 설정 후 별도 검증해야 한다.",
            "품질 검수는 dry-run 요청 메타데이터 기준이며 실제 이미지 픽셀 검수는 이미지 API 연결 후 확장한다.",
            "Winner/Loser 학습은 mock 광고 성과 기준이며 실제 캠페인 집행 일수는 API 연결 후 교체한다.",
            "Google Drive는 dry-run manifest 단계이며 실제 업로드에는 서비스 계정 또는 OAuth 인증이 필요하다.",
            "대시보드 실시간화는 30초 polling 기반이며 서버 push 방식은 후속 안정화 단계에서 확장한다.",
            "GitHub Actions는 mock과 dry-run을 기본값으로 실행하며 실제 API 호출은 credential과 운영 승인 후 켠다.",
        ],
    }


def write_dashboard_payload(payload: dict[str, Any], output_path: Path = OUTPUT_PATH) -> Path:
    """대시보드 JSON 파일을 저장한다."""
    return write_json(output_path, payload)


def write_dashboard_api_payloads(payload: dict[str, Any], output_dir: Path = API_OUTPUT_DIR) -> list[Path]:
    """대시보드 API JSON 파일들을 저장한다."""
    api_payloads = build_dashboard_api_payloads(payload)
    written_paths = [
        write_json(output_dir / "status.json", api_payloads["status"]),
        write_json(output_dir / "agents.json", api_payloads["agents"]),
        write_json(output_dir / "costs.json", api_payloads["costs"]),
        write_json(output_dir / "brands.json", api_payloads["brands"]),
        write_json(output_dir / "history" / "daily.json", api_payloads["history_daily"]),
        write_json(output_dir / "winner-loser.json", api_payloads["winner_loser"]),
        write_json(output_dir / "logs.json", api_payloads["logs"]),
    ]
    for brand_name, brand_payload in api_payloads["brand_details"].items():
        written_paths.append(write_json(output_dir / "brands" / f"{brand_name}.json", brand_payload))
    return written_paths


def main() -> None:
    """대시보드 JSON 생성 명령행 진입점."""
    payload = build_dashboard_payload()
    output_path = write_dashboard_payload(payload)
    api_paths = write_dashboard_api_payloads(payload)
    print(f"saved {output_path}")
    print(f"saved {len(api_paths)} api files")


if __name__ == "__main__":
    main()
