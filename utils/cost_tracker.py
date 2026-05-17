# 이미지 생성과 에이전트 실행 비용을 계산하고 한도를 확인한다.
from __future__ import annotations


DAILY_COST_LIMIT_USD = 5.00
MONTHLY_COST_LIMIT_USD = 79.00
IMAGE_COSTS = {
    "실사": 0.211,
    "일러스트": 0.053,
}


def calculate_image_cost(real_photo_count: int, illustration_count: int) -> float:
    """실사와 일러스트 생성 장수를 기준으로 이미지 비용을 계산한다."""
    return round((real_photo_count * IMAGE_COSTS["실사"]) + (illustration_count * IMAGE_COSTS["일러스트"]), 4)


def is_daily_cost_allowed(current_cost_usd: float, next_cost_usd: float) -> bool:
    """다음 작업 비용이 일일 한도 안에 있는지 확인한다."""
    return current_cost_usd + next_cost_usd <= DAILY_COST_LIMIT_USD


def is_monthly_cost_allowed(current_cost_usd: float, next_cost_usd: float) -> bool:
    """다음 작업 비용이 월간 한도 안에 있는지 확인한다."""
    return current_cost_usd + next_cost_usd <= MONTHLY_COST_LIMIT_USD