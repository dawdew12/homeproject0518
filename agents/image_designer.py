# 팀원 D가 이미지 생성 요청과 파일 저장 경로 생성을 담당한다.
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.cost_tracker import calculate_image_cost, is_daily_cost_allowed, is_monthly_cost_allowed

DEFAULT_DAILY_DIR = PROJECT_ROOT / "history" / "daily"
MAX_RETRY = 2
IMAGE_CONFIG = {
    "실사": {"size": "2048x2048", "quality": "high", "batch": True, "cost_per_image": 0.211},
    "일러스트": {"size": "2048x2048", "quality": "medium", "batch": True, "cost_per_image": 0.053},
}


def build_output_path(brand: str, date: str, filename: str) -> Path:
    """브랜드와 날짜 기준으로 이미지 저장 경로를 만든다."""
    return PROJECT_ROOT / "outputs" / brand / date / filename


def read_json(path: Path, default: Any | None = None) -> Any:
    """JSON 파일을 읽고 없으면 기본값을 반환한다."""
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8-sig"))


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


def compact_date(date: str) -> str:
    """YYYY-MM-DD 날짜를 파일명용 YYYYMMDD로 바꾼다."""
    return date.replace("-", "")


def get_image_config(prompt: dict[str, Any]) -> dict[str, Any]:
    """프롬프트의 이미지 유형에 맞는 생성 설정을 반환한다."""
    image_type_label = prompt.get("image_type_label", "일러스트")
    if image_type_label not in IMAGE_CONFIG:
        raise ValueError(f"지원하지 않는 이미지 유형입니다: {image_type_label}")
    return IMAGE_CONFIG[image_type_label]


def calculate_prompt_cost(prompt: dict[str, Any]) -> float:
    """프롬프트 1개의 예상 이미지 생성 비용을 계산한다."""
    return round(float(get_image_config(prompt)["cost_per_image"]), 4)


def build_image_request(prompt: dict[str, Any], date: str) -> dict[str, Any]:
    """프롬프트를 dry-run 이미지 생성 요청 1건으로 변환한다."""
    config = get_image_config(prompt)
    brand = prompt["brand"]
    filename = prompt["file_name_preview"]
    output_path = build_output_path(brand, date, filename)

    return {
        "prompt_id": prompt["prompt_id"],
        "storyboard_id": prompt.get("storyboard_id"),
        "brand": brand,
        "status": "dry_run_ready",
        "model": prompt.get("model", "gpt-image-2"),
        "image_type_label": prompt.get("image_type_label"),
        "size": config["size"],
        "quality": config["quality"],
        "batch": config["batch"],
        "estimated_cost_usd": calculate_prompt_cost(prompt),
        "output_path": str(output_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "copy_space": prompt.get("copy_space"),
        "rules": prompt.get("rules", []),
        "prompt": prompt.get("prompt", ""),
        "negative_prompt": prompt.get("negative_prompt", []),
    }


def build_brand_batch(date: str, brand: str, prompts: list[dict[str, Any]]) -> dict[str, Any]:
    """브랜드별 프롬프트 4개를 batch dry-run 묶음으로 만든다."""
    requests = [build_image_request(prompt, date) for prompt in prompts]
    real_photo_count = sum(1 for prompt in prompts if prompt.get("image_type_label") == "실사")
    illustration_count = sum(1 for prompt in prompts if prompt.get("image_type_label") == "일러스트")

    return {
        "batch_id": f"{brand}_{compact_date(date)}_image_batch01",
        "brand": brand,
        "status": "dry_run_ready",
        "request_count": len(requests),
        "real_photo_count": real_photo_count,
        "illustration_count": illustration_count,
        "estimated_cost_usd": calculate_image_cost(real_photo_count, illustration_count),
        "output_dir": f"outputs/{brand}/{date}/",
        "requests": requests,
    }


def generate_images(brand: str, prompts: list[dict[str, Any]], dry_run: bool = True) -> dict[str, Any]:
    """브랜드별 프롬프트 묶음을 이미지 생성 요청으로 변환한다."""
    if not dry_run:
        return {"brand": brand, "status": "not_implemented", "count": len(prompts)}
    return build_brand_batch("0000-00-00", brand, prompts)


def build_image_dry_run(
    prompt_payload: dict[str, Any],
    runtime_payload: dict[str, Any] | None = None,
    input_files: dict[str, str] | None = None,
) -> dict[str, Any]:
    """프롬프트 pack 전체를 이미지 생성 dry-run 결과로 변환한다."""
    date = prompt_payload["date"]
    batches = []
    for brand_pack in prompt_payload.get("brands", []):
        batches.append(build_brand_batch(date, brand_pack["brand"], brand_pack.get("prompts", [])))

    requests = [request for batch in batches for request in batch["requests"]]
    real_photo_count = sum(batch["real_photo_count"] for batch in batches)
    illustration_count = sum(batch["illustration_count"] for batch in batches)
    estimated_cost = calculate_image_cost(real_photo_count, illustration_count)
    runtime = runtime_payload or {}
    current_daily_cost = float(runtime.get("daily_cost_usd", 0))
    current_monthly_cost = float(runtime.get("monthly_cost_usd", 0))

    return {
        "date": date,
        "status": "image_dry_run_ready",
        "mode": "dry_run",
        "input_files": input_files or {},
        "summary": {
            "brand_count": len(batches),
            "batch_count": len(batches),
            "request_count": len(requests),
            "real_photo_count": real_photo_count,
            "illustration_count": illustration_count,
            "estimated_cost_usd": estimated_cost,
            "daily_cost_limit_usd": 5.0,
            "monthly_cost_limit_usd": 79.0,
            "daily_cost_allowed": is_daily_cost_allowed(current_daily_cost, estimated_cost),
            "monthly_cost_allowed": is_monthly_cost_allowed(current_monthly_cost, estimated_cost),
            "charged": False,
        },
        "batches": batches,
        "requests": requests,
    }


def save_image_dry_run(payload: dict[str, Any], output_dir: Path = DEFAULT_DAILY_DIR) -> Path:
    """이미지 dry-run 결과를 daily history에 저장한다."""
    return write_json(output_dir / f"{payload['date']}_image_dry_run.json", payload)


def generate_daily_image_dry_run(
    date: str | None = None,
    daily_dir: Path = DEFAULT_DAILY_DIR,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """최신 또는 지정 날짜의 프롬프트 pack을 읽어 이미지 dry-run 결과를 저장한다."""
    prompt_path = find_daily_file(date, "prompts", daily_dir)
    prompt_payload = read_json(prompt_path)
    runtime_payload = read_json(PROJECT_ROOT / "state" / "runtime.json", {})
    payload = build_image_dry_run(
        prompt_payload,
        runtime_payload,
        {"prompts": str(prompt_path.relative_to(PROJECT_ROOT)).replace("\\", "/")},
    )
    output_path = save_image_dry_run(payload, output_dir or daily_dir)
    payload["output_path"] = str(output_path)
    return payload


def request_regeneration(image_id: str, feedback: str, retry_count: int) -> dict[str, Any]:
    """재생성 제한을 확인하고 재생성 요청 상태를 반환한다."""
    if retry_count >= MAX_RETRY:
        return {"image_id": image_id, "status": "보류", "feedback": feedback}
    return {"image_id": image_id, "status": "regeneration_requested", "retry_count": retry_count + 1, "feedback": feedback}


def main() -> None:
    """명령행 인자로 이미지 dry-run 작업을 실행한다."""
    parser = argparse.ArgumentParser(description="AIPR image designer dry-run agent")
    parser.add_argument("--date", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir else None
    result = generate_daily_image_dry_run(args.date, output_dir=output_dir)
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
