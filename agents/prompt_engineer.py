# 팀원 C가 브랜드별 스토리보드와 이미지 프롬프트를 작성한다.
from __future__ import annotations

from typing import Any


PROMPT_SECTIONS = ["브랜드 정체성", "오늘의 방향", "이미지 스펙", "카피 영역", "금지사항"]
REQUIRED_IMAGE_RULES = ["NO text", "NO watermark", "NO logo", "Leave 25% bottom space for copywriting"]


def create_storyboard(brand: str, manager_direction: dict[str, Any] | None = None) -> dict[str, Any]:
    """브랜드와 팀장 방향을 바탕으로 텍스트 스토리보드를 만든다."""
    return {"brand": brand, "status": "not_implemented", "manager_direction": manager_direction or {}}


def create_image_prompt(brand: str, storyboard: dict[str, Any]) -> dict[str, Any]:
    """승인된 스토리보드에서 이미지 생성 프롬프트를 만든다."""
    return {"brand": brand, "status": "not_implemented", "sections": PROMPT_SECTIONS, "rules": REQUIRED_IMAGE_RULES}


def apply_review_feedback(prompt: dict[str, Any], feedback: str) -> dict[str, Any]:
    """팀장 검수 피드백을 반영해 재생성 프롬프트를 만든다."""
    updated_prompt = dict(prompt)
    updated_prompt["feedback"] = feedback
    updated_prompt["status"] = "not_implemented"
    return updated_prompt


if __name__ == "__main__":
    print(create_image_prompt("someud", create_storyboard("someud")))