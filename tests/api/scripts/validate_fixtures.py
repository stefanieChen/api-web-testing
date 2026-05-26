#!/usr/bin/env python3
"""Validate recorded API fixture files under tests/api/fixtures/."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURES_DIR = REPO_ROOT / "tests" / "api" / "fixtures"

REQUIRED_FILES = {
    "recommend_words_success.json": {"success", "resp", "total"},
    "category_info_3wtshirt_success.json": {"success", "resp"},
    "product_listing_3wtshirt_success.json": {"success", "resp"},
    "shop_classification_pc.json": {"data"},
    "cms_config_sample.json": set(),
}


def validate_file(path: Path, required_top_keys: set[str]) -> list[str]:
    errors: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.name}: invalid JSON ({exc})"]

    if not isinstance(payload, dict):
        return [f"{path.name}: expected top-level object"]

    missing = required_top_keys - set(payload)
    if missing:
        errors.append(f"{path.name}: missing keys {sorted(missing)}")

    if path.name.endswith("_success.json") and payload.get("success") is not True:
        errors.append(f"{path.name}: success must be true")

    return errors


def main() -> int:
    if not FIXTURES_DIR.is_dir():
        print(f"Fixtures directory not found: {FIXTURES_DIR}", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    for filename, required_keys in REQUIRED_FILES.items():
        path = FIXTURES_DIR / filename
        if not path.is_file():
            all_errors.append(f"Missing fixture file: {filename}")
            continue
        all_errors.extend(validate_file(path, required_keys))

    if all_errors:
        print("Fixture validation failed:", file=sys.stderr)
        for error in all_errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"OK: validated {len(REQUIRED_FILES)} fixtures in {FIXTURES_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
