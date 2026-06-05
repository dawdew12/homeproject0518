# 운영 전 점검, 비용 리포트, 실패 로그를 관리한다.
from __future__ import annotations

import json
import tomllib
import traceback
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
KST = timezone(timedelta(hours=9))
DEFAULT_REQUIRED_BRAND_SECTIONS = ("brand", "style", "performance_targets", "image_config")
DEFAULT_REQUIRED_ENV_KEYS = (
    "OPENAI_API_KEY",
    "META_ACCESS_TOKEN",
    "NAVER_SA_API_KEY",
    "KAKAO_MOMENT_ACCESS_TOKEN",
    "GOOGLE_SERVICE_ACCOUNT_JSON",
    "SLACK_WEBHOOK_URL",
)
AGENT_MONTHLY_BUDGETS_USD = {
    "manager": 7.0,
    "data_collector": 2.0,
    "trend_collector": 1.0,
    "prompt_engineer": 5.0,
    "image_designer": 61.0,
    "history_analysis": 3.0,
}


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


def display_path(path: Path, project_root: Path = PROJECT_ROOT) -> str:
    """프로젝트 기준 상대 경로를 슬래시 표기로 반환한다."""
    try:
        return str(path.relative_to(project_root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def now_kst() -> str:
    """KST 현재 시각을 ISO 문자열로 반환한다."""
    return datetime.now(KST).isoformat(timespec="seconds")


def read_toml(path: Path) -> dict[str, Any]:
    """TOML 파일을 읽는다."""
    return tomllib.loads(path.read_text(encoding="utf-8-sig"))


def validate_brand_directory(brand_dir: Path, project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """브랜드 폴더 1개의 config와 context 준비 상태를 점검한다."""
    config_path = brand_dir / "config.toml"
    context_path = brand_dir / "brand_context.md"
    issues: list[str] = []
    config: dict[str, Any] = {}

    if not config_path.exists():
        issues.append("missing_config")
    else:
        try:
            config = read_toml(config_path)
        except tomllib.TOMLDecodeError:
            issues.append("invalid_config_toml")

    if not context_path.exists():
        issues.append("missing_brand_context")
    elif context_path.read_text(encoding="utf-8-sig").strip() == "":
        issues.append("empty_brand_context")

    for section in DEFAULT_REQUIRED_BRAND_SECTIONS:
        if section not in config:
            issues.append(f"missing_section:{section}")

    brand_section = config.get("brand", {})
    image_config = config.get("image_config", {})
    real_photo_count = int(image_config.get("real_photo_count", 0))
    illustration_count = int(image_config.get("illustration_count", 0))
    if real_photo_count + illustration_count <= 0:
        issues.append("missing_image_count")

    return {
        "brand_key": brand_dir.name,
        "display_name": brand_section.get("name", brand_dir.name),
        "active": bool(brand_section.get("active", False)),
        "config_path": display_path(config_path, project_root),
        "context_path": display_path(context_path, project_root),
        "real_photo_count": real_photo_count,
        "illustration_count": illustration_count,
        "status": "ready" if not issues else "needs_attention",
        "issues": issues,
    }


def build_brand_registry(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """전체 브랜드 폴더의 운영 준비 상태를 만든다."""
    brand_root = project_root / "brands"
    brands = [
        validate_brand_directory(path, project_root)
        for path in sorted(brand_root.iterdir())
        if path.is_dir()
    ]
    ready_count = sum(1 for brand in brands if brand["status"] == "ready")
    active_count = sum(1 for brand in brands if brand["active"])
    return {
        "status": "brand_registry_ready" if ready_count == len(brands) else "brand_registry_needs_attention",
        "brand_count": len(brands),
        "active_brand_count": active_count,
        "ready_brand_count": ready_count,
        "brands": brands,
        "new_brand_checklist": [
            "brands/{brand}/config.toml 생성",
            "brands/{brand}/brand_context.md 생성",
            "brand.name_en을 폴더명과 동일하게 설정",
            "performance_targets에 CTR, CVR, CPA, ROAS 목표 입력",
            "image_config에 실사와 일러스트 생산 수량 입력",
        ],
    }


def read_env_example_keys(path: Path) -> list[str]:
    """`.env.example`에서 환경변수 키 목록을 추출한다."""
    if not path.exists():
        return []
    keys = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        keys.append(stripped.split("=", 1)[0].strip())
    return keys


def build_credential_readiness(project_root: Path = PROJECT_ROOT, live: bool = False) -> dict[str, Any]:
    """live 전환 전에 필요한 환경변수 슬롯이 준비되어 있는지 점검한다."""
    env_example_keys = set(read_env_example_keys(project_root / ".env.example"))
    missing_slots = [key for key in DEFAULT_REQUIRED_ENV_KEYS if key not in env_example_keys]
    return {
        "status": "mock_safe" if not live else "live_requires_secret_review",
        "mode": "live" if live else "mock",
        "required_key_count": len(DEFAULT_REQUIRED_ENV_KEYS),
        "missing_slots": missing_slots,
        "ready_for_mock": True,
        "ready_for_live": False,
        "live_note": "실제 API 호출은 GitHub Secrets와 운영 승인 후에만 켠다.",
    }


def build_cost_report(
    runtime: dict[str, Any],
    estimated_cost_usd: float,
    daily_limit_usd: float,
    monthly_limit_usd: float,
) -> dict[str, Any]:
    """현재 runtime과 예상 비용으로 운영 비용 리포트를 만든다."""
    daily_cost = float(runtime.get("daily_cost_usd", 0))
    monthly_cost = float(runtime.get("monthly_cost_usd", 0))
    projected_daily = round(daily_cost + estimated_cost_usd, 4)
    projected_monthly = round(monthly_cost + estimated_cost_usd, 4)
    return {
        "status": "cost_within_limits" if projected_daily <= daily_limit_usd and projected_monthly <= monthly_limit_usd else "cost_limit_risk",
        "estimated_next_run_usd": estimated_cost_usd,
        "daily_cost_usd": daily_cost,
        "monthly_cost_usd": monthly_cost,
        "projected_daily_cost_usd": projected_daily,
        "projected_monthly_cost_usd": projected_monthly,
        "daily_limit_usd": daily_limit_usd,
        "monthly_limit_usd": monthly_limit_usd,
        "daily_remaining_usd": round(daily_limit_usd - projected_daily, 4),
        "monthly_remaining_usd": round(monthly_limit_usd - projected_monthly, 4),
        "agent_monthly_budgets_usd": AGENT_MONTHLY_BUDGETS_USD,
    }


def build_preflight_report(
    run_date: str,
    runtime: dict[str, Any],
    estimated_cost_usd: float,
    daily_limit_usd: float,
    monthly_limit_usd: float,
    project_root: Path = PROJECT_ROOT,
    live: bool = False,
) -> dict[str, Any]:
    """일일 실행 전 운영 준비 상태를 점검한다."""
    brand_registry = build_brand_registry(project_root)
    credential_readiness = build_credential_readiness(project_root, live=live)
    cost_report = build_cost_report(runtime, estimated_cost_usd, daily_limit_usd, monthly_limit_usd)
    checks = [
        {"name": "brand_registry", "status": brand_registry["status"]},
        {"name": "credential_readiness", "status": credential_readiness["status"]},
        {"name": "cost_report", "status": cost_report["status"]},
    ]
    blocking = [
        check for check in checks
        if check["status"] in {"brand_registry_needs_attention", "cost_limit_risk"}
    ]
    return {
        "date": run_date,
        "generated_at": now_kst(),
        "status": "preflight_passed" if not blocking else "preflight_blocked",
        "checks": checks,
        "brand_registry": brand_registry,
        "credential_readiness": credential_readiness,
        "cost_report": cost_report,
    }


def save_preflight_report(report: dict[str, Any], history_root: Path, run_date: str) -> Path:
    """preflight 리포트를 daily history에 저장한다."""
    return write_json(history_root / "daily" / f"{run_date}_preflight.json", report)


def build_error_record(error: BaseException, step: str, run_date: str) -> dict[str, Any]:
    """예외를 운영 로그 JSONL에 남길 구조로 변환한다."""
    return {
        "date": run_date,
        "timestamp": now_kst(),
        "step": step,
        "error_type": error.__class__.__name__,
        "message": str(error),
        "traceback": traceback.format_exception_only(error.__class__, error)[-1].strip(),
    }


def append_error_log(error: BaseException, step: str, run_date: str, log_path: Path) -> dict[str, Any]:
    """실패 원인을 JSONL 로그에 추가한다."""
    record = build_error_record(error, step, run_date)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record
