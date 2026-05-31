# Vercel 대시보드에 표시할 최신 진행 상태 JSON을 생성한다.
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "web" / "data"
OUTPUT_PATH = OUTPUT_DIR / "latest_status.json"
KST = timezone(timedelta(hours=9))


def read_json(path: Path, default: Any) -> Any:
    """JSON 파일이 있으면 읽고, 없으면 기본값을 반환한다."""
    if not path.exists() or not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


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


def build_dashboard_payload() -> dict[str, Any]:
    """프로젝트 진행 상태를 하나의 대시보드 JSON으로 묶는다."""
    current_phase = read_json(PROJECT_ROOT / "state" / "current_phase.json", {})
    ad_summary = summarize_daily_file(find_latest_file("*_ad_data.json"))
    trend_summary = summarize_daily_file(find_latest_file("*_trend_data.json"))
    source_counts = count_marketing_sources()
    recent_commits = get_recent_commits()

    return {
        "generated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "project": {
            "name": "AIPR",
            "github_repo": "https://github.com/dawdew12/homeproject0518",
            "vercel_project_id": "prj_Pe7nqm93OZ6yPog5DJVGJwS0h3Ce",
            "vercel_team": "raw22226-9071s-projects",
            "custom_domain_enabled": False,
        },
        "current_phase": current_phase,
        "phase_progress": [
            {"phase": "PHASE 1", "title": "프로젝트 기반 세팅", "status": "completed"},
            {"phase": "PHASE 2", "title": "광고 데이터 수집 mock", "status": "completed"},
            {"phase": "PHASE 3", "title": "트렌드 수집 및 시장조사 출처", "status": "completed"},
            {"phase": "PHASE 3.5", "title": "Vercel 대시보드 배포 기반", "status": "completed"},
            {"phase": "PHASE 4", "title": "팀장 분석 엔진", "status": "next"},
        ],
        "data": {
            "ad": ad_summary,
            "trend": trend_summary,
            "marketing_source_counts": source_counts,
        },
        "verification": {
            "last_command": "python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_build_dashboard_data",
            "last_result": "passed",
            "test_count": 9,
        },
        "git": {
            "branch": run_git(["branch", "--show-current"]) or "main",
            "recent_commits": recent_commits,
        },
        "next_step": {
            "phase": "PHASE 4",
            "title": "팀장 분석 엔진",
            "summary": "광고 데이터와 트렌드 데이터를 종합해 브랜드별 소재 방향과 개선안을 생성한다.",
        },
        "risks": [
            "광고 API와 트렌드 API는 아직 mock 수집 단계다.",
            "Vercel 초기 버전은 push 이후 반영되는 정적 JSON 대시보드다.",
            "초 단위 실행 로그 실시간화는 PHASE 10 API 연동에서 확장한다.",
        ],
    }


def write_dashboard_payload(payload: dict[str, Any], output_path: Path = OUTPUT_PATH) -> Path:
    """대시보드 JSON 파일을 저장한다."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def main() -> None:
    """대시보드 JSON 생성 명령행 진입점."""
    output_path = write_dashboard_payload(build_dashboard_payload())
    print(f"saved {output_path}")


if __name__ == "__main__":
    main()
