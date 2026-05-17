# 팀원 D가 이미지 생성 요청과 파일 저장 경로 생성을 담당한다.
from __future__ import annotations

from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAX_RETRY = 2
IMAGE_CONFIG = {
    "실사": {"size": "2048x2048", "quality": "high", "batch": True, "cost_per_image": 0.211},
    "일러스트": {"size": "2048x2048", "quality": "medium", "batch": True, "cost_per_image": 0.053},
}


def build_output_path(brand: str, date: str, filename: str) -> Path:
    """브랜드와 날짜 기준으로 이미지 저장 경로를 만든다."""
    return PROJECT_ROOT / "outputs" / brand / date / filename


def generate_images(brand: str, prompts: list[dict[str, Any]], dry_run: bool = True) -> dict[str, Any]:
    """브랜드별 프롬프트 묶음을 이미지 생성 요청으로 변환한다."""
    return {"brand": brand, "status": "dry_run" if dry_run else "not_implemented", "count": len(prompts)}


def request_regeneration(image_id: str, feedback: str, retry_count: int) -> dict[str, Any]:
    """재생성 제한을 확인하고 재생성 요청 상태를 반환한다."""
    if retry_count >= MAX_RETRY:
        return {"image_id": image_id, "status": "보류", "feedback": feedback}
    return {"image_id": image_id, "status": "regeneration_requested", "retry_count": retry_count + 1, "feedback": feedback}


if __name__ == "__main__":
    print(generate_images("someud", []))