#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(message)


def check_frontmatter() -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter delimited by ---")
    end = text.find("\n---\n", 4)
    if end == -1:
        fail("SKILL.md frontmatter must close with ---")

    data = yaml.safe_load(text[4:end])
    if not isinstance(data, dict):
        fail("SKILL.md frontmatter must be a YAML mapping")
    for field in ("name", "description"):
        if not str(data.get(field, "")).strip():
            fail(f"SKILL.md frontmatter requires non-empty {field!r}")
    if data["name"] != "mentor":
        fail("SKILL.md frontmatter name must be 'mentor'")


def check_json_fences() -> None:
    fence = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE)
    for rel in ("SKILL.md", "README.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        for index, block in enumerate(fence.findall(text), start=1):
            try:
                json.loads(block)
            except json.JSONDecodeError as exc:
                fail(f"{rel} json fence #{index} is invalid: {exc}")


def check_readme_references() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    targets: set[str] = set()

    for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).split("#", 1)[0].strip()
        if target and not re.match(r"[a-z][a-z0-9+.-]*:|/|~", target, re.I):
            targets.add(target)

    for match in re.finditer(r"`([^`]+)`", text):
        token = match.group(1).strip()
        if re.fullmatch(r"[A-Za-z0-9_.-]+\.(?:md|txt|json|jsonl|ya?ml|toml|license)|LICENSE", token, re.I):
            targets.add(token)

    missing = sorted(target for target in targets if not (ROOT / target).is_file())
    if missing:
        fail("README.md references missing files: " + ", ".join(missing))


def main() -> None:
    check_frontmatter()
    check_json_fences()
    check_readme_references()
    print("All checks passed.")


if __name__ == "__main__":
    main()
