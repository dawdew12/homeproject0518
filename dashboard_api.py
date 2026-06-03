# 대시보드 실시간 API 계약을 FastAPI 엔드포인트로 제공한다.
from __future__ import annotations

from typing import Any

from scripts.build_dashboard_data import build_dashboard_api_payloads, build_dashboard_payload


try:
    from fastapi import FastAPI
except ModuleNotFoundError:
    FastAPI = None


def get_api_payloads() -> dict[str, Any]:
    """현재 프로젝트 상태를 API payload 묶음으로 반환한다."""
    return build_dashboard_api_payloads(build_dashboard_payload())


def get_status() -> dict[str, Any]:
    """현재 phase와 전체 진행도를 반환한다."""
    return get_api_payloads()["status"]


def get_agents() -> dict[str, Any]:
    """에이전트와 파이프라인 상태를 반환한다."""
    return get_api_payloads()["agents"]


def get_costs() -> dict[str, Any]:
    """비용과 runtime 상태를 반환한다."""
    return get_api_payloads()["costs"]


def get_brands() -> dict[str, Any]:
    """브랜드별 운영 지표 목록을 반환한다."""
    return get_api_payloads()["brands"]


def get_brand(brand: str) -> dict[str, Any]:
    """브랜드 1개의 상세 지표를 반환한다."""
    payloads = get_api_payloads()
    return payloads["brand_details"].get(
        brand,
        {"status": "brand_not_found", "brand": brand},
    )


def get_daily_history() -> dict[str, Any]:
    """daily history 산출물 요약을 반환한다."""
    return get_api_payloads()["history_daily"]


def get_winner_loser() -> dict[str, Any]:
    """Winner/Loser 학습 결과를 반환한다."""
    return get_api_payloads()["winner_loser"]


def get_logs() -> dict[str, Any]:
    """최근 실행 로그를 반환한다."""
    return get_api_payloads()["logs"]


if FastAPI is not None:
    app = FastAPI(title="AIPR Dashboard API", version="0.10.0")
    app.get("/api/status")(get_status)
    app.get("/api/agents")(get_agents)
    app.get("/api/costs")(get_costs)
    app.get("/api/brands")(get_brands)
    app.get("/api/brands/{brand}")(get_brand)
    app.get("/api/history/daily")(get_daily_history)
    app.get("/api/winner-loser")(get_winner_loser)
    app.get("/api/logs")(get_logs)
else:
    app = None
