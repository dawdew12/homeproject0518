# 일별 실행 이력을 GitHub history 커밋으로 남기는 진입점을 제공한다.
from __future__ import annotations

import argparse
import json
from datetime import date as date_type
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HISTORY_DIR = PROJECT_ROOT / "history"
DEFAULT_DAILY_DIR = DEFAULT_HISTORY_DIR / "daily"
DEFAULT_WEEKLY_DIR = DEFAULT_HISTORY_DIR / "weekly"


def read_json(path: Path, default: Any) -> Any:
    """JSON 파일을 UTF-8 BOM까지 허용해 읽는다."""
    if not path.exists() or not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    """JSON payload를 보기 쉬운 포맷으로 저장한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def normalize_relative_path(path: Path) -> str:
    """프로젝트 기준 상대 경로를 슬래시 표기로 반환한다."""
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def resolve_daily_dir(history_path: Path) -> Path:
    """history 루트 또는 daily 폴더 입력을 daily 폴더로 정규화한다."""
    if history_path.name == "daily":
        return history_path
    if history_path.is_file():
        return history_path.parent
    return history_path / "daily"


def find_latest_date(daily_dir: Path) -> str | None:
    """daily 폴더에서 최신 날짜 문자열을 찾는다."""
    dates = sorted({path.name.split("_", 1)[0] for path in daily_dir.glob("*.json") if "_" in path.name})
    return dates[-1] if dates else None


def collect_daily_files(history_path: Path, run_date: str) -> list[Path]:
    """지정 날짜의 daily JSON 파일 목록을 수집한다."""
    if history_path.is_file():
        return [history_path]
    daily_dir = resolve_daily_dir(history_path)
    return sorted(daily_dir.glob(f"{run_date}_*.json"))


def suffix_from_daily_file(path: Path, run_date: str) -> str:
    """daily JSON 파일명에서 날짜 뒤 suffix를 추출한다."""
    return path.stem.removeprefix(f"{run_date}_")


def iso_week_key(run_date: str) -> str:
    """YYYY-MM-DD 날짜를 ISO 주차 키로 변환한다."""
    parsed = date_type.fromisoformat(run_date)
    year, week, _ = parsed.isocalendar()
    return f"{year}-W{week:02d}"


def merge_metrics(suffix: str, payload: dict[str, Any], metrics: dict[str, Any]) -> None:
    """daily 산출물별 핵심 수치를 metrics에 누적한다."""
    summary = payload.get("summary", {})
    if suffix == "ad_data":
        metrics["ad_record_count"] = summary.get("record_count", 0)
    elif suffix == "trend_data":
        metrics["trend_record_count"] = summary.get("record_count", 0)
    elif suffix == "manager_brief":
        metrics["manager_brand_count"] = summary.get("brand_count", 0)
    elif suffix == "prompts":
        metrics["storyboard_count"] = summary.get("storyboard_count", 0)
        metrics["prompt_count"] = summary.get("prompt_count", 0)
    elif suffix == "image_dry_run":
        metrics["image_request_count"] = summary.get("request_count", 0)
        metrics["estimated_cost_usd"] = summary.get("estimated_cost_usd", 0)
    elif suffix == "quality_review":
        metrics["approved_count"] = summary.get("approved_count", 0)
        metrics["regeneration_required_count"] = summary.get("regeneration_required_count", 0)
    elif suffix == "winner_loser":
        metrics["winner_count"] = summary.get("winner_count", 0)
        metrics["loser_count"] = summary.get("loser_count", 0)
        metrics["pending_count"] = summary.get("pending_count", 0)
    elif suffix == "gdrive_manifest":
        metrics["gdrive_planned_upload_count"] = summary.get("planned_upload_count", 0)
        metrics["gdrive_missing_file_count"] = summary.get("missing_file_count", 0)


def summarize_artifact(path: Path, run_date: str, payload: dict[str, Any]) -> dict[str, Any]:
    """daily 산출물 1개를 커밋 요약용으로 줄인다."""
    suffix = suffix_from_daily_file(path, run_date)
    summary = payload.get("summary", {})
    return {
        "suffix": suffix,
        "path": normalize_relative_path(path),
        "status": payload.get("status"),
        "record_count": summary.get("record_count", summary.get("request_count", summary.get("planned_upload_count", 0))),
    }


def summarize_daily_history(history_path: Path, date: str | None = None) -> dict[str, Any]:
    """일별 history 파일을 읽어 커밋 메시지에 필요한 요약을 만든다."""
    daily_dir = resolve_daily_dir(history_path)
    run_date = date or find_latest_date(daily_dir)
    if run_date is None:
        return {"status": "missing_daily_history", "history_path": normalize_relative_path(history_path)}

    files = collect_daily_files(history_path, run_date)
    artifacts = []
    metrics: dict[str, Any] = {
        "ad_record_count": 0,
        "trend_record_count": 0,
        "manager_brand_count": 0,
        "storyboard_count": 0,
        "prompt_count": 0,
        "image_request_count": 0,
        "estimated_cost_usd": 0,
        "approved_count": 0,
        "regeneration_required_count": 0,
        "winner_count": 0,
        "loser_count": 0,
        "pending_count": 0,
        "gdrive_planned_upload_count": 0,
        "gdrive_missing_file_count": 0,
    }

    for path in files:
        suffix = suffix_from_daily_file(path, run_date)
        payload = read_json(path, {})
        merge_metrics(suffix, payload, metrics)
        artifacts.append(summarize_artifact(path, run_date, payload))

    weekly_key = iso_week_key(run_date)
    commit_message = f"[HISTORY] {run_date} daily run summary"
    return {
        "date": run_date,
        "status": "github_history_summary_ready",
        "weekly_key": weekly_key,
        "summary": {
            "daily_file_count": len(files),
            "artifact_count": len(artifacts),
            "weekly_key": weekly_key,
            "commit_message": commit_message,
            "metrics": metrics,
        },
        "artifacts": artifacts,
        "planned_commit": {
            "message": commit_message,
            "paths": [
                "history/daily",
                "history/weekly",
                "history/winner_loser_patterns.json",
            ],
        },
    }


def build_weekly_history(daily_summary: dict[str, Any]) -> dict[str, Any]:
    """일별 요약 1건을 주간 history 요약으로 변환한다."""
    metrics = daily_summary.get("summary", {}).get("metrics", {})
    return {
        "week": daily_summary.get("weekly_key"),
        "status": "weekly_history_summary_ready",
        "summary": {
            "run_count": 1,
            "dates": [daily_summary.get("date")],
            "total_ad_records": metrics.get("ad_record_count", 0),
            "total_prompts": metrics.get("prompt_count", 0),
            "total_image_requests": metrics.get("image_request_count", 0),
            "total_approved": metrics.get("approved_count", 0),
            "total_winners": metrics.get("winner_count", 0),
            "total_losers": metrics.get("loser_count", 0),
            "total_pending": metrics.get("pending_count", 0),
            "total_planned_uploads": metrics.get("gdrive_planned_upload_count", 0),
            "estimated_cost_usd": metrics.get("estimated_cost_usd", 0),
        },
        "daily_summaries": [
            {
                "date": daily_summary.get("date"),
                "artifact_count": daily_summary.get("summary", {}).get("artifact_count", 0),
                "metrics": metrics,
            }
        ],
    }


def save_history_summary(daily_summary: dict[str, Any], output_root: Path = DEFAULT_HISTORY_DIR) -> Path:
    """daily GitHub history 요약을 저장한다."""
    return write_json(output_root / "daily" / f"{daily_summary['date']}_github_history_summary.json", daily_summary)


def save_weekly_history(weekly_summary: dict[str, Any], output_root: Path = DEFAULT_HISTORY_DIR) -> Path:
    """weekly GitHub history 요약을 저장한다."""
    return write_json(output_root / "weekly" / f"{weekly_summary['week']}.json", weekly_summary)


def commit_history(
    message: str | None = None,
    date: str | None = None,
    history_path: Path = DEFAULT_HISTORY_DIR,
    output_root: Path = DEFAULT_HISTORY_DIR,
    dry_run: bool = True,
) -> dict[str, Any]:
    """GitHub history 변경사항을 커밋하기 전 요약과 계획을 만든다."""
    daily_summary = summarize_daily_history(history_path, date)
    if daily_summary.get("status") != "github_history_summary_ready":
        return daily_summary

    if message:
        daily_summary["planned_commit"]["message"] = message
        daily_summary["summary"]["commit_message"] = message

    weekly_summary = build_weekly_history(daily_summary)
    daily_path = save_history_summary(daily_summary, output_root)
    weekly_path = save_weekly_history(weekly_summary, output_root)
    return {
        "date": daily_summary["date"],
        "status": "github_history_dry_run_ready" if dry_run else "github_history_commit_blocked",
        "dry_run": dry_run,
        "daily_summary_path": normalize_relative_path(daily_path),
        "weekly_summary_path": normalize_relative_path(weekly_path),
        "planned_commit": daily_summary["planned_commit"],
        "summary": daily_summary["summary"],
    }


def parse_args() -> argparse.Namespace:
    """명령행 인자를 파싱한다."""
    parser = argparse.ArgumentParser(description="Build GitHub history summaries for AIPR.")
    parser.add_argument("--date", default=None)
    parser.add_argument("--message", default=None)
    parser.add_argument("--dry-run", action="store_true", default=True)
    return parser.parse_args()


def main() -> None:
    """GitHub history 요약 생성 명령행 진입점."""
    args = parse_args()
    print(json.dumps(commit_history(message=args.message, date=args.date, dry_run=args.dry_run), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
