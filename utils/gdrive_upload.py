# 생성된 소재를 Google Drive 저장 구조로 업로드하는 진입점을 제공한다.
from __future__ import annotations

from pathlib import Path
from typing import Any


def upload_outputs(output_root: Path, dry_run: bool = True) -> dict[str, Any]:
    """outputs 폴더의 생성 소재를 Google Drive로 업로드한다."""
    return {"status": "dry_run" if dry_run else "not_implemented", "output_root": str(output_root)}


if __name__ == "__main__":
    print(upload_outputs(Path("outputs")))