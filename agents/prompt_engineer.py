# 팀원 C가 브랜드별 스토리보드와 이미지 프롬프트를 작성한다.
from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DAILY_DIR = PROJECT_ROOT / "history" / "daily"
BRANDS = ["someud", "kinda", "melliance", "paperback", "baren"]
PROMPT_SECTIONS = ["브랜드 정체성", "오늘의 방향", "이미지 스펙", "카피 영역", "금지사항"]
REQUIRED_IMAGE_RULES = ["NO text", "NO watermark", "NO logo", "Leave 25% bottom space for copywriting"]
STORYBOARD_FRAMES = [
    {
        "name": "hero_context",
        "image_type": "real_photo",
        "image_type_label": "실사",
        "quality": "high",
        "scene_role": "첫 화면에서 타겟 고객이 상황을 바로 이해하는 메인 컷",
    },
    {
        "name": "use_moment",
        "image_type": "real_photo",
        "image_type_label": "실사",
        "quality": "high",
        "scene_role": "제품이 쓰이는 실제 순간과 생활 맥락을 보여주는 컷",
    },
    {
        "name": "benefit_diagram",
        "image_type": "illustration",
        "image_type_label": "일러스트",
        "quality": "medium",
        "scene_role": "핵심 베네핏을 과장 없이 정리하는 정보형 컷",
    },
    {
        "name": "variation_test",
        "image_type": "illustration",
        "image_type_label": "일러스트",
        "quality": "medium",
        "scene_role": "다른 후킹 각도를 테스트하는 확장 컷",
    },
]


def read_json(path: Path, default: Any | None = None) -> Any:
    """JSON 파일을 읽고 없으면 기본값을 반환한다."""
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    """JSON payload를 UTF-8로 저장한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def find_daily_file(date: str | None, suffix: str, daily_dir: Path = DEFAULT_DAILY_DIR) -> Path:
    """날짜가 있으면 해당 파일, 없으면 최신 daily 파일을 찾는다."""
    if date:
        path = daily_dir / f"{date}_{suffix}.json"
        if path.exists():
            return path
        raise FileNotFoundError(path)

    files = sorted(daily_dir.glob(f"*_{suffix}.json"))
    if not files:
        raise FileNotFoundError(f"*_{suffix}.json")
    return files[-1]


def load_brand_config(brand: str) -> dict[str, Any]:
    """브랜드별 TOML 설정을 읽는다."""
    config_path = PROJECT_ROOT / "brands" / brand / "config.toml"
    if not config_path.exists():
        return {"brand": {"name": brand}, "style": {}, "image_config": {}}
    return tomllib.loads(config_path.read_text(encoding="utf-8").lstrip("\ufeff"))


def load_brand_context(brand: str) -> str:
    """브랜드 컨텍스트 문서의 요약 문자열을 읽는다."""
    context_path = PROJECT_ROOT / "brands" / brand / "brand_context.md"
    if not context_path.exists():
        return ""
    return context_path.read_text(encoding="utf-8").lstrip("\ufeff").strip()


def compact_date(date: str) -> str:
    """YYYY-MM-DD 날짜를 파일명용 YYYYMMDD로 바꾼다."""
    return date.replace("-", "")


def slug_keyword(keyword: str) -> str:
    """파일명에 넣을 키워드를 간단히 정리한다."""
    return keyword.replace(" ", "-").replace("/", "-")[:24]


def get_brand_brief(manager_payload: dict[str, Any], brand: str) -> dict[str, Any]:
    """팀장 분석 payload에서 특정 브랜드 brief를 찾는다."""
    for item in manager_payload.get("brands", []):
        if item.get("brand") == brand:
            return item
    raise KeyError(brand)


def create_storyboard(
    brand: str,
    manager_direction: dict[str, Any] | None = None,
    sequence: int = 1,
    date: str | None = None,
) -> dict[str, Any]:
    """브랜드와 팀장 방향을 바탕으로 텍스트 스토리보드를 만든다."""
    direction = manager_direction or {}
    frame = STORYBOARD_FRAMES[(sequence - 1) % len(STORYBOARD_FRAMES)]
    config = load_brand_config(brand)
    brand_config = config.get("brand", {})
    style = config.get("style", {})
    image_config = config.get("image_config", {})
    keywords = direction.get("prompt_keywords") or direction.get("trend_metrics", {}).get("top_keywords", [])
    main_keyword = keywords[0] if keywords else brand
    storyboard_date = date or "0000-00-00"

    return {
        "storyboard_id": f"{brand}_{compact_date(storyboard_date)}_sb{sequence:02d}",
        "brand": brand,
        "display_name": direction.get("display_name") or brand_config.get("name", brand),
        "sequence": sequence,
        "status": "storyboard_ready",
        "priority": direction.get("priority", "test"),
        "frame": frame["name"],
        "image_type": frame["image_type"],
        "image_type_label": frame["image_type_label"],
        "quality": frame["quality"],
        "title": f"{main_keyword} {frame['scene_role']}",
        "objective": direction.get("creative_direction", f"{main_keyword} 중심 소재"),
        "visual_scene": direction.get("visual_concept", frame["scene_role"]),
        "opening_hook": f"{main_keyword}를 1초 안에 인지할 수 있는 명확한 화면.",
        "composition": f"중앙에는 주요 피사체를 두고 하단 {image_config.get('copy_area_bottom_pct', 25)}%는 깨끗한 카피 여백으로 비운다.",
        "tone": style.get("tone", "브랜드 톤 유지"),
        "required_elements": keywords[:4],
        "actions": direction.get("recommended_actions", [])[:3],
        "constraints": direction.get("handoff", {}).get("constraints", ["텍스트 삽입 금지", "하단 카피 영역 확보"]),
        "brand_context_excerpt": load_brand_context(brand)[:180],
    }


def build_prompt_text(storyboard: dict[str, Any]) -> str:
    """스토리보드를 gpt-image-2용 텍스트 프롬프트로 변환한다."""
    elements = ", ".join(storyboard.get("required_elements", [])) or storyboard["brand"]
    return (
        f"Create a {storyboard['image_type_label']} 2K advertising visual for {storyboard['display_name']}. "
        f"Scene: {storyboard['visual_scene']}. "
        f"Objective: {storyboard['objective']}. "
        f"Hook: {storyboard['opening_hook']} "
        f"Composition: {storyboard['composition']} "
        f"Tone: {storyboard['tone']}. "
        f"Include visual cues related to {elements}. "
        "Do not include any text, letters, numbers, logo, watermark, UI, price tag, or brand competitor name. "
        "Keep the bottom 25 percent clean and uncluttered for copywriting."
    )


def create_image_prompt(brand: str, storyboard: dict[str, Any]) -> dict[str, Any]:
    """승인된 스토리보드에서 이미지 생성 프롬프트를 만든다."""
    date = storyboard["storyboard_id"].split("_")[1]
    keywords = storyboard.get("required_elements", [])[:3] or [brand]
    keyword_slug = "-".join(slug_keyword(keyword) for keyword in keywords)
    prompt_id = storyboard["storyboard_id"].replace("_sb", "_prompt")
    sequence = int(storyboard.get("sequence", 1))

    return {
        "prompt_id": prompt_id,
        "brand": brand,
        "storyboard_id": storyboard["storyboard_id"],
        "status": "image_prompt_ready",
        "model": "gpt-image-2",
        "image_type": storyboard["image_type"],
        "image_type_label": storyboard["image_type_label"],
        "size": "2K",
        "quality": storyboard["quality"],
        "sections": PROMPT_SECTIONS,
        "rules": REQUIRED_IMAGE_RULES,
        "prompt": build_prompt_text(storyboard),
        "negative_prompt": ["text", "watermark", "logo", "competitor name", "crowded bottom area", "low quality composite"],
        "file_name_preview": f"{brand}_{date}_{storyboard['image_type_label']}_{keyword_slug}_v{sequence:02d}_{storyboard['quality']}.png",
        "copy_space": "bottom_25_percent",
        "batch_ready": True,
    }


def create_brand_prompt_pack(date: str, brand_brief: dict[str, Any]) -> dict[str, Any]:
    """브랜드 1개의 스토리보드와 이미지 프롬프트 묶음을 만든다."""
    brand = brand_brief["brand"]
    storyboard_count = int(brand_brief.get("handoff", {}).get("storyboard_count", 4))
    storyboards = [create_storyboard(brand, brand_brief, sequence + 1, date) for sequence in range(storyboard_count)]
    prompts = [create_image_prompt(brand, storyboard) for storyboard in storyboards]

    return {
        "brand": brand,
        "display_name": brand_brief.get("display_name", brand),
        "priority": brand_brief.get("priority", "test"),
        "status": "prompts_ready",
        "storyboards": storyboards,
        "prompts": prompts,
        "handoff_to_image_designer": {
            "owner": "팀원 D",
            "batch_size": len(prompts),
            "output_dir": f"outputs/{brand}/{date}/",
            "prompt_ids": [prompt["prompt_id"] for prompt in prompts],
        },
    }


def build_prompt_pack(
    date: str,
    manager_payload: dict[str, Any],
    input_files: dict[str, str] | None = None,
) -> dict[str, Any]:
    """팀장 분석 Brief를 입력으로 daily 프롬프트 생성 결과를 만든다."""
    brand_packs = [create_brand_prompt_pack(date, get_brand_brief(manager_payload, brand)) for brand in BRANDS]
    all_prompts = [prompt for pack in brand_packs for prompt in pack["prompts"]]
    all_storyboards = [storyboard for pack in brand_packs for storyboard in pack["storyboards"]]

    return {
        "date": date,
        "status": "prompts_ready",
        "input_files": input_files or {},
        "summary": {
            "brand_count": len(brand_packs),
            "storyboard_count": len(all_storyboards),
            "prompt_count": len(all_prompts),
            "real_photo_count": sum(1 for prompt in all_prompts if prompt["image_type"] == "real_photo"),
            "illustration_count": sum(1 for prompt in all_prompts if prompt["image_type"] == "illustration"),
            "no_text_rule_applied": all("NO text" in prompt["rules"] for prompt in all_prompts),
        },
        "brands": brand_packs,
        "prompts": all_prompts,
    }


def save_prompt_pack(payload: dict[str, Any], output_dir: Path = DEFAULT_DAILY_DIR) -> Path:
    """프롬프트 생성 결과를 daily history에 저장한다."""
    return write_json(output_dir / f"{payload['date']}_prompts.json", payload)


def generate_daily_prompts(
    date: str | None = None,
    daily_dir: Path = DEFAULT_DAILY_DIR,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """최신 또는 지정 날짜의 팀장 Brief를 읽어 프롬프트 pack을 저장한다."""
    manager_path = find_daily_file(date, "manager_brief", daily_dir)
    manager_payload = read_json(manager_path)
    prompt_date = date or manager_payload.get("date")
    payload = build_prompt_pack(
        prompt_date,
        manager_payload,
        {"manager": str(manager_path.relative_to(PROJECT_ROOT)).replace("\\", "/")},
    )
    output_path = save_prompt_pack(payload, output_dir or daily_dir)
    payload["output_path"] = str(output_path)
    return payload


def apply_review_feedback(prompt: dict[str, Any], feedback: str) -> dict[str, Any]:
    """팀장 검수 피드백을 반영해 재생성 프롬프트를 만든다."""
    updated_prompt = dict(prompt)
    updated_prompt["feedback"] = feedback
    updated_prompt["status"] = "feedback_applied"
    updated_prompt["revision"] = int(prompt.get("revision", 0)) + 1
    updated_prompt["prompt"] = f"{prompt.get('prompt', '')} Revision note: {feedback}"
    return updated_prompt


def main() -> None:
    """명령행 인자로 프롬프트 생성 작업을 실행한다."""
    parser = argparse.ArgumentParser(description="AIPR prompt engineer agent")
    parser.add_argument("--date", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else None
    result = generate_daily_prompts(args.date, output_dir=output_dir)
    print(
        json.dumps(
            {
                "status": result["status"],
                "date": result["date"],
                "summary": result["summary"],
                "output_path": result["output_path"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
