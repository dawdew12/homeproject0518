# 생성된 소재를 Google Drive 저장 구조로 업로드하는 진입점을 제공한다.
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DAILY_DIR = PROJECT_ROOT / "history" / "daily"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "outputs"
DRIVE_ROOT_NAME = "AIPR_소재관리"


def read_json(path: Path, default: Any) -> Any:
    """JSON 파일을 UTF-8 BOM까지 허용해 읽는다."""
    if not path.exists() or not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    """JSON payload를 보기 쉬운 포맷으로 저장한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def find_daily_file(date: str, suffix: str, daily_dir: Path = DEFAULT_DAILY_DIR) -> Path | None:
    """지정 날짜와 suffix에 맞는 daily JSON 파일을 찾는다."""
    path = daily_dir / f"{date}_{suffix}.json"
    return path if path.exists() else None


def find_latest_daily_file(suffix: str, daily_dir: Path = DEFAULT_DAILY_DIR) -> Path | None:
    """지정 suffix에 맞는 최신 daily JSON 파일을 찾는다."""
    files = sorted(daily_dir.glob(f"*_{suffix}.json"))
    return files[-1] if files else None


def derive_date_from_daily_file(path: Path) -> str:
    """daily JSON 파일명 앞부분에서 날짜를 추출한다."""
    return path.name.split("_", 1)[0]


def flatten_image_requests(image_payload: dict[str, Any]) -> list[dict[str, Any]]:
    """이미지 dry-run payload에서 요청 목록을 평탄화한다."""
    if image_payload.get("requests"):
        return list(image_payload.get("requests", []))

    requests: list[dict[str, Any]] = []
    for batch in image_payload.get("batches", []):
        requests.extend(batch.get("requests", []))
    return requests


def brand_labels_from_learning(winner_loser_payload: dict[str, Any]) -> dict[str, str]:
    """Winner/Loser 학습 결과에서 브랜드별 대표 라벨을 만든다."""
    labels: dict[str, str] = {}
    for item in winner_loser_payload.get("brand_summary", []):
        brand = item.get("brand")
        if brand:
            labels[brand] = item.get("top_label") or "pending"
    return labels


def normalize_relative_path(path_value: str) -> str:
    """Windows와 POSIX 경로 구분자를 대시보드용 슬래시로 통일한다."""
    return path_value.replace("\\", "/")


def display_path(path: Path) -> str:
    """프로젝트 안팎의 경로를 표시용 문자열로 변환한다."""
    try:
        return normalize_relative_path(str(path.relative_to(PROJECT_ROOT)))
    except ValueError:
        return normalize_relative_path(str(path))


def build_drive_path(request: dict[str, Any], date: str, label: str) -> str:
    """요청 1건의 Google Drive 저장 대상 경로를 만든다."""
    source_path = Path(request.get("output_path", ""))
    file_name = source_path.name or f"{request.get('prompt_id', 'unknown')}.png"
    brand = request.get("brand") or "unknown"
    return f"{DRIVE_ROOT_NAME}/{brand}/{date}/{label}/{file_name}"


def build_upload_manifest(
    date: str,
    image_payload: dict[str, Any],
    winner_loser_payload: dict[str, Any] | None = None,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    dry_run: bool = True,
) -> dict[str, Any]:
    """이미지 산출물을 Google Drive 저장 구조에 배치하는 manifest를 만든다."""
    requests = flatten_image_requests(image_payload)
    brand_labels = brand_labels_from_learning(winner_loser_payload or {})
    items = []
    classification_counts = {"winner": 0, "loser": 0, "pending": 0}
    existing_file_count = 0
    missing_file_count = 0

    for request in requests:
        brand = request.get("brand") or "unknown"
        label = brand_labels.get(brand, "pending")
        classification_counts[label] = classification_counts.get(label, 0) + 1
        source_path = Path(request.get("output_path", ""))
        absolute_source_path = source_path if source_path.is_absolute() else PROJECT_ROOT / source_path
        source_exists = absolute_source_path.exists()
        existing_file_count += 1 if source_exists else 0
        missing_file_count += 0 if source_exists else 1

        items.append(
            {
                "prompt_id": request.get("prompt_id"),
                "storyboard_id": request.get("storyboard_id"),
                "brand": brand,
                "classification": label,
                "source_path": normalize_relative_path(str(source_path)),
                "source_exists": source_exists,
                "drive_path": build_drive_path(request, date, label),
                "image_type_label": request.get("image_type_label"),
                "quality": request.get("quality"),
                "estimated_cost_usd": request.get("estimated_cost_usd", 0),
                "status": "ready_to_upload" if source_exists and not dry_run else "dry_run_planned",
            }
        )

    summary = {
        "brand_count": len({item["brand"] for item in items}),
        "request_count": len(items),
        "planned_upload_count": len(items),
        "existing_file_count": existing_file_count,
        "missing_file_count": missing_file_count,
        "classification_counts": classification_counts,
        "ready_to_upload": existing_file_count == len(items) and not dry_run,
        "dry_run": dry_run,
        "drive_root": DRIVE_ROOT_NAME,
        "output_root": normalize_relative_path(str(output_root)),
    }

    return {
        "date": date,
        "status": "gdrive_upload_manifest_ready" if dry_run else "gdrive_upload_blocked_missing_credentials",
        "mode": "dry_run" if dry_run else "blocked",
        "input_files": {
            "image_dry_run": f"history/daily/{date}_image_dry_run.json",
            "winner_loser": f"history/daily/{date}_winner_loser.json",
        },
        "summary": summary,
        "items": items,
    }


def save_upload_manifest(manifest: dict[str, Any], output_dir: Path = DEFAULT_DAILY_DIR) -> Path:
    """Google Drive upload manifest를 daily history에 저장한다."""
    date = manifest["date"]
    return write_json(output_dir / f"{date}_gdrive_manifest.json", manifest)


def upload_outputs(
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    date: str | None = None,
    daily_dir: Path = DEFAULT_DAILY_DIR,
    output_dir: Path | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """outputs 폴더의 생성 소재를 Google Drive 저장 계획으로 변환한다."""
    image_path = find_daily_file(date, "image_dry_run", daily_dir) if date else find_latest_daily_file("image_dry_run", daily_dir)
    if image_path is None:
        return {"status": "missing_image_dry_run", "output_root": str(output_root)}

    run_date = date or derive_date_from_daily_file(image_path)
    image_payload = read_json(image_path, {})
    winner_loser_path = find_daily_file(run_date, "winner_loser", daily_dir)
    winner_loser_payload = read_json(winner_loser_path, {}) if winner_loser_path else {}
    manifest = build_upload_manifest(
        run_date,
        image_payload,
        winner_loser_payload,
        output_root=output_root,
        dry_run=dry_run,
    )
    saved_path = save_upload_manifest(manifest, output_dir or daily_dir)
    manifest["output_path"] = display_path(saved_path)
    return manifest


def parse_args() -> argparse.Namespace:
    """명령행 인자를 파싱한다."""
    parser = argparse.ArgumentParser(description="Build Google Drive upload manifest for AIPR outputs.")
    parser.add_argument("--date", default=None)
    parser.add_argument("--dry-run", action="store_true", default=True)
    return parser.parse_args()


def main() -> None:
    """Google Drive upload manifest 생성 명령행 진입점."""
    args = parse_args()
    print(json.dumps(upload_outputs(date=args.date, dry_run=args.dry_run), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
