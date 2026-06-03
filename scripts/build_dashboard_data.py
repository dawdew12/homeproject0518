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
    return json.loads(path.read_text(encoding="utf-8-sig"))


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


def build_agent_status() -> list[dict[str, Any]]:
    """에이전트별 구현 범위와 다음 작업을 정리한다."""
    return [
        {
            "agent": "팀장",
            "file": "agents/manager.py",
            "status": "learning_ready",
            "implemented": ["광고/트렌드 종합", "브랜드별 우선순위", "소재 방향", "프롬프트 handoff", "품질 검수", "Winner/Loser 학습"],
            "output": "history/daily/{date}_winner_loser.json",
            "next": "PHASE 9에서 Google Drive와 GitHub 저장소 연동",
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
            "next": "실제 gpt-image-2 API 호출 연결",
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
        {"step": "08", "title": "저장소 연동", "owner": "utils", "status": "next"},
        {"step": "09", "title": "대시보드 실시간화", "owner": "dashboard", "status": "static_ready"},
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
            "name": "품질 검수와 재생성 판단",
            "status": "quality_review_ready",
            "details": ["20개 요청 승인", "평균 점수 100", "재생성 필요 0개", "no-text 검수", "카피 여백 검수"],
        },
        {
            "name": "Winner/Loser 학습",
            "status": "learning_ready",
            "details": ["15개 성과 분류", "Winner 12개", "Loser 0개", "Pending 3개", "패턴 저장"],
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
        {"phase": "PHASE 9", "title": "저장소 연동", "status": "next", "progress": 0},
        {"phase": "PHASE 10", "title": "Dashboard 실시간화", "status": "planned", "progress": 0},
        {"phase": "PHASE 11", "title": "GitHub Actions 자동화", "status": "planned", "progress": 0},
        {"phase": "PHASE 12", "title": "안정화", "status": "planned", "progress": 0},
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
        "current_phase": "PHASE 8",
        "next_phase": next_items[0]["phase"] if next_items else None,
        "dashboard_milestones_completed": 2,
        "latest_test_count": 26,
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
                {"id": "history", "label": "history/daily", "status": "ready", "metric": "6 daily JSON"},
                {"id": "dashboard", "label": "Vercel Dashboard", "status": "static_ready", "metric": "READY"},
                {"id": "automation", "label": "GitHub Actions", "status": "planned", "metric": "PHASE 11"},
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
        {"from": "history/state/git", "to": "Vercel Dashboard", "artifact": "latest_status.json", "status": "ready"},
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
        {"path": "outputs/{brand}/{date}/", "producer": "팀원 D", "consumer": "팀장 검수", "status": "dry_run_ready"},
        {"path": "web/data/latest_status.json", "producer": "scripts/build_dashboard_data.py", "consumer": "Vercel Dashboard", "status": "ready"},
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
            "check": "예정: Google Drive/GitHub 저장 유틸 검증",
            "result": "next",
            "test_count": 0,
            "artifact": "utils/gdrive_upload.py, utils/github_history.py",
        },
    ]


def build_dashboard_payload() -> dict[str, Any]:
    """프로젝트 진행 상태를 하나의 대시보드 JSON으로 묶는다."""
    current_phase = read_json(PROJECT_ROOT / "state" / "current_phase.json", {})
    latest_ad_file = find_latest_file("*_ad_data.json")
    latest_trend_file = find_latest_file("*_trend_data.json")
    latest_manager_file = find_latest_file("*_manager_brief.json")
    latest_prompt_file = find_latest_file("*_prompts.json")
    latest_image_file = find_latest_file("*_image_dry_run.json")
    latest_quality_file = find_latest_file("*_quality_review.json")
    latest_learning_file = find_latest_file("*_winner_loser.json")
    ad_payload = load_latest_daily_payload("*_ad_data.json")
    trend_payload = load_latest_daily_payload("*_trend_data.json")
    manager_payload = load_latest_daily_payload("*_manager_brief.json")
    prompt_payload = load_latest_daily_payload("*_prompts.json")
    image_payload = load_latest_daily_payload("*_image_dry_run.json")
    quality_payload = load_latest_daily_payload("*_quality_review.json")
    learning_payload = load_latest_daily_payload("*_winner_loser.json")
    ad_summary = summarize_daily_file(latest_ad_file)
    trend_summary = summarize_daily_file(latest_trend_file)
    manager_summary = summarize_manager_brief(latest_manager_file)
    prompt_summary = summarize_prompt_pack(latest_prompt_file)
    image_summary = summarize_image_dry_run(latest_image_file)
    quality_summary = summarize_quality_review(latest_quality_file)
    learning_summary = summarize_winner_loser(latest_learning_file)
    pattern_summary = summarize_winner_loser_patterns(PROJECT_ROOT / "history" / "winner_loser_patterns.json")
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
            {"phase": "PHASE 9", "title": "저장소 연동", "status": "next"},
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
            "quality_review": quality_summary,
            "winner_loser": learning_summary,
            "winner_loser_patterns": pattern_summary,
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
        },
        "verification": {
            "last_command": "python -m unittest tests.test_trend_collector tests.test_data_collector tests.test_manager tests.test_prompt_engineer tests.test_image_designer tests.test_build_dashboard_data",
            "last_result": "passed",
            "test_count": 26,
        },
        "git": {
            "branch": run_git(["branch", "--show-current"]) or "main",
            "recent_commits": recent_commits,
        },
        "next_step": {
            "phase": "PHASE 9",
            "title": "저장소 연동",
            "summary": "Google Drive와 GitHub 저장 유틸을 실제 운영 산출물 흐름에 연결하고 실패 시 로그를 남긴다.",
        },
        "risks": [
            "광고 API와 트렌드 API는 아직 mock 수집 단계다.",
            "팀장 분석은 deterministic rule 기반이며 실제 LLM 판단은 후속 API 연결 단계에서 붙인다.",
            "프롬프트 생성도 rule 기반이며 실제 OpenAI API 호출은 아직 수행하지 않는다.",
            "이미지 생성은 dry-run 단계이며 실제 gpt-image-2 API 호출은 아직 수행하지 않는다.",
            "품질 검수는 dry-run 요청 메타데이터 기준이며 실제 이미지 픽셀 검수는 이미지 API 연결 후 확장한다.",
            "Winner/Loser 학습은 mock 광고 성과 기준이며 실제 캠페인 집행 일수는 API 연결 후 교체한다.",
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
