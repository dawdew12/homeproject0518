# GitHub Actions에서 일일 dry-run 파이프라인을 실행한다.
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.data_collector import collect_ad_data, save_ad_data
from agents.image_designer import generate_daily_image_dry_run
from agents.manager import analyze_daily_inputs, classify_winner_loser, review_images
from agents.prompt_engineer import generate_daily_prompts
from agents.trend_collector import collect_trend_data, save_trend_data
from scripts.build_dashboard_data import build_dashboard_payload, write_dashboard_api_payloads, write_dashboard_payload
from utils.gdrive_upload import upload_outputs
from utils.github_history import commit_history


KST = timezone(timedelta(hours=9))
DEFAULT_HISTORY_ROOT = PROJECT_ROOT / "history"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "outputs"
DEFAULT_RUNTIME_PATH = PROJECT_ROOT / "state" / "runtime.json"
DEFAULT_LOG_PATH = PROJECT_ROOT / "logs" / "execution.log"
DEFAULT_DAILY_COST_LIMIT_USD = 5.0
DEFAULT_MONTHLY_COST_LIMIT_USD = 79.0


def read_json(path: Path, default: Any) -> Any:
    """JSON 파일을 읽고 없으면 기본값을 반환한다."""
    if not path.exists() or not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    """JSON payload를 저장한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def resolve_run_date(value: str | None = None) -> str:
    """명령행, 환경변수, KST 오늘 날짜 순서로 실행 날짜를 정한다."""
    selected = value or os.getenv("AIPR_RUN_DATE")
    if selected:
        return selected
    return datetime.now(KST).date().isoformat()


def env_float(name: str, default: float) -> float:
    """환경변수의 숫자 값을 읽는다."""
    raw_value = os.getenv(name)
    if raw_value in (None, ""):
        return default
    return float(raw_value)


def display_path(path: Path) -> str:
    """프로젝트 기준 상대 경로를 슬래시 표기로 반환한다."""
    try:
        return str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def append_execution_log(message: str, log_path: Path = DEFAULT_LOG_PATH) -> None:
    """실행 로그에 한 줄을 추가한다."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S KST")
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")


def update_runtime(runtime_path: Path, updates: dict[str, Any]) -> dict[str, Any]:
    """runtime 상태 파일을 부분 갱신한다."""
    runtime = read_json(runtime_path, {})
    runtime.update(updates)
    write_json(runtime_path, runtime)
    return runtime


def build_cost_guard(
    image_payload: dict[str, Any],
    runtime: dict[str, Any],
    daily_limit_usd: float,
    monthly_limit_usd: float,
) -> dict[str, Any]:
    """예상 이미지 비용이 운영 한도 안에 있는지 판단한다."""
    estimated_cost = float(image_payload.get("summary", {}).get("estimated_cost_usd", 0))
    current_daily_cost = float(runtime.get("daily_cost_usd", 0))
    current_monthly_cost = float(runtime.get("monthly_cost_usd", 0))
    daily_allowed = current_daily_cost + estimated_cost <= daily_limit_usd
    monthly_allowed = current_monthly_cost + estimated_cost <= monthly_limit_usd
    return {
        "status": "cost_guard_passed" if daily_allowed and monthly_allowed else "cost_limit_exceeded",
        "estimated_cost_usd": estimated_cost,
        "daily_cost_usd": current_daily_cost,
        "monthly_cost_usd": current_monthly_cost,
        "daily_limit_usd": daily_limit_usd,
        "monthly_limit_usd": monthly_limit_usd,
        "daily_allowed": daily_allowed,
        "monthly_allowed": monthly_allowed,
    }


def write_pipeline_summary(
    run_date: str,
    history_root: Path,
    payload: dict[str, Any],
) -> Path:
    """일일 pipeline 실행 요약을 history에 저장한다."""
    return write_json(history_root / "daily" / f"{run_date}_pipeline_run.json", payload)


def build_artifact(path: Path, status: str) -> dict[str, str]:
    """파이프라인 산출물 정보를 표준 구조로 만든다."""
    return {"path": display_path(path), "status": status}


def run_daily_pipeline(
    run_date: str | None = None,
    history_root: Path = DEFAULT_HISTORY_ROOT,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    runtime_path: Path = DEFAULT_RUNTIME_PATH,
    log_path: Path = DEFAULT_LOG_PATH,
    pattern_path: Path | None = None,
    mock: bool = True,
    dry_run: bool = True,
    write_dashboard: bool = True,
    update_runtime_file: bool = True,
    fail_on_cost_exceeded: bool = True,
    daily_cost_limit_usd: float = DEFAULT_DAILY_COST_LIMIT_USD,
    monthly_cost_limit_usd: float = DEFAULT_MONTHLY_COST_LIMIT_USD,
) -> dict[str, Any]:
    """일일 운영 파이프라인을 순서대로 실행한다."""
    selected_date = resolve_run_date(run_date)
    daily_dir = history_root / "daily"
    pattern_output_path = pattern_path or history_root / "winner_loser_patterns.json"
    artifacts: list[dict[str, str]] = []
    started_at = datetime.now(KST).isoformat(timespec="seconds")
    runtime = read_json(runtime_path, {})

    append_execution_log(f"PHASE 11 daily pipeline started for {selected_date}.", log_path)
    if update_runtime_file:
        runtime = update_runtime(
            runtime_path,
            {
                "execution_start": started_at,
                "execution_end": None,
                "last_run_date": selected_date,
                "last_status": "running",
            },
        )

    ad_payload = collect_ad_data(selected_date, mock=mock)
    ad_path = save_ad_data(ad_payload, daily_dir)
    artifacts.append(build_artifact(ad_path, ad_payload["status"]))

    trend_payload = collect_trend_data(selected_date, mock=mock)
    trend_path = save_trend_data(trend_payload, daily_dir)
    artifacts.append(build_artifact(trend_path, trend_payload["status"]))

    manager_payload = analyze_daily_inputs(selected_date, daily_dir=daily_dir, output_dir=daily_dir)
    artifacts.append(build_artifact(Path(manager_payload["output_path"]), manager_payload["status"]))

    prompt_payload = generate_daily_prompts(selected_date, daily_dir=daily_dir, output_dir=daily_dir)
    artifacts.append(build_artifact(Path(prompt_payload["output_path"]), prompt_payload["status"]))

    image_payload = generate_daily_image_dry_run(selected_date, daily_dir=daily_dir, output_dir=daily_dir)
    artifacts.append(build_artifact(Path(image_payload["output_path"]), image_payload["status"]))

    cost_guard = build_cost_guard(image_payload, runtime, daily_cost_limit_usd, monthly_cost_limit_usd)
    if cost_guard["status"] != "cost_guard_passed":
        finished_at = datetime.now(KST).isoformat(timespec="seconds")
        summary = {
            "date": selected_date,
            "status": "cost_limit_exceeded",
            "mode": "dry_run" if dry_run else "live",
            "started_at": started_at,
            "finished_at": finished_at,
            "cost_guard": cost_guard,
            "artifacts": artifacts,
        }
        summary_path = write_pipeline_summary(selected_date, history_root, summary)
        summary["output_path"] = display_path(summary_path)
        append_execution_log(f"PHASE 11 daily pipeline blocked by cost guard for {selected_date}.", log_path)
        if update_runtime_file:
            update_runtime(
                runtime_path,
                {
                    "execution_end": finished_at,
                    "last_status": "cost_limit_exceeded",
                    "last_error": "cost_limit_exceeded",
                    "last_estimated_cost_usd": cost_guard["estimated_cost_usd"],
                },
            )
        if fail_on_cost_exceeded:
            raise RuntimeError("cost_limit_exceeded")
        return summary

    quality_payload = review_images(selected_date, daily_dir=daily_dir, output_dir=daily_dir)
    artifacts.append(build_artifact(Path(quality_payload["output_path"]), quality_payload["status"]))

    learning_payload = classify_winner_loser(
        selected_date,
        daily_dir=daily_dir,
        output_dir=daily_dir,
        pattern_path=pattern_output_path,
    )
    artifacts.append(build_artifact(Path(learning_payload["output_path"]), learning_payload["status"]))
    artifacts.append(build_artifact(pattern_output_path, "winner_loser_patterns_ready"))

    gdrive_payload = upload_outputs(output_root=output_root, date=selected_date, daily_dir=daily_dir, output_dir=daily_dir, dry_run=dry_run)
    artifacts.append(build_artifact(Path(gdrive_payload["output_path"]), gdrive_payload["status"]))

    history_payload = commit_history(date=selected_date, history_path=history_root, output_root=history_root, dry_run=True)
    artifacts.append(build_artifact(history_root / "daily" / f"{selected_date}_github_history_summary.json", history_payload["status"]))
    artifacts.append(build_artifact(history_root / "weekly" / f"{history_payload['summary']['weekly_key']}.json", "weekly_history_summary_ready"))

    finished_at = datetime.now(KST).isoformat(timespec="seconds")
    dashboard_paths: list[str] = []
    summary = {
        "date": selected_date,
        "status": "daily_pipeline_completed",
        "mode": "dry_run" if dry_run else "live",
        "mock": mock,
        "started_at": started_at,
        "finished_at": finished_at,
        "cost_guard": cost_guard,
        "summary": {
            "artifact_count": len(artifacts),
            "ad_record_count": ad_payload["summary"]["record_count"],
            "trend_record_count": trend_payload["summary"]["record_count"],
            "prompt_count": prompt_payload["summary"]["prompt_count"],
            "image_request_count": image_payload["summary"]["request_count"],
            "approved_count": quality_payload["summary"]["approved_count"],
            "winner_count": learning_payload["summary"]["winner_count"],
            "planned_upload_count": gdrive_payload["summary"]["planned_upload_count"],
            "dashboard_file_count": len(dashboard_paths),
        },
        "artifacts": artifacts,
        "dashboard_paths": dashboard_paths,
        "planned_commit": history_payload["planned_commit"],
    }
    summary_path = write_pipeline_summary(selected_date, history_root, summary)
    summary["output_path"] = display_path(summary_path)

    if write_dashboard:
        dashboard_payload = build_dashboard_payload()
        dashboard_path = write_dashboard_payload(dashboard_payload)
        api_paths = write_dashboard_api_payloads(dashboard_payload)
        dashboard_paths = [display_path(dashboard_path), *[display_path(path) for path in api_paths]]
        summary["dashboard_paths"] = dashboard_paths
        summary["summary"]["dashboard_file_count"] = len(dashboard_paths)
        write_pipeline_summary(selected_date, history_root, summary)
        dashboard_payload = build_dashboard_payload()
        write_dashboard_payload(dashboard_payload)
        write_dashboard_api_payloads(dashboard_payload)

    if update_runtime_file:
        update_runtime(
            runtime_path,
            {
                "execution_end": finished_at,
                "last_status": "daily_pipeline_completed",
                "last_error": None,
                "last_estimated_cost_usd": cost_guard["estimated_cost_usd"],
                "images_generated": 0,
                "images_approved": quality_payload["summary"]["approved_count"],
                "retry_count": quality_payload["summary"]["regeneration_required_count"],
            },
        )

    append_execution_log(f"PHASE 11 daily pipeline completed for {selected_date}.", log_path)
    return summary


def parse_args() -> argparse.Namespace:
    """명령행 인자를 파싱한다."""
    parser = argparse.ArgumentParser(description="Run AIPR daily dry-run pipeline.")
    parser.add_argument("--date", default=None, help="실행 기준 날짜. 예: 2026-05-18")
    parser.add_argument("--live", action="store_true", help="mock 수집 대신 실제 API credential 확인 모드로 실행한다.")
    parser.add_argument("--history-root", default=str(DEFAULT_HISTORY_ROOT), help="history 루트 폴더")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="outputs 루트 폴더")
    parser.add_argument("--no-dashboard", action="store_true", help="대시보드 JSON 재생성을 건너뛴다.")
    parser.add_argument("--daily-cost-limit-usd", type=float, default=env_float("AIPR_DAILY_COST_LIMIT_USD", DEFAULT_DAILY_COST_LIMIT_USD))
    parser.add_argument("--monthly-cost-limit-usd", type=float, default=env_float("AIPR_MONTHLY_COST_LIMIT_USD", DEFAULT_MONTHLY_COST_LIMIT_USD))
    return parser.parse_args()


def main() -> int:
    """명령행 실행 진입점."""
    args = parse_args()
    result = run_daily_pipeline(
        run_date=args.date,
        history_root=Path(args.history_root),
        output_root=Path(args.output_root),
        mock=not args.live,
        write_dashboard=not args.no_dashboard,
        fail_on_cost_exceeded=False,
        daily_cost_limit_usd=args.daily_cost_limit_usd,
        monthly_cost_limit_usd=args.monthly_cost_limit_usd,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result["status"] == "cost_limit_exceeded" else 0


if __name__ == "__main__":
    raise SystemExit(main())
