#!/usr/bin/env python3
"""Fail when a Markdown relative link points to a missing path."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))(?:\s+['\"][^'\"]*['\"])?\)")
IGNORED_SCHEMES = {"http", "https", "mailto"}


def iter_relative_links(markdown: Path):
    text = markdown.read_text(encoding="utf-8")
    for match in MARKDOWN_LINK.finditer(text):
        target = match.group(1) or match.group(2)
        parsed = urlsplit(target)
        if parsed.scheme.lower() in IGNORED_SCHEMES or target.startswith("#"):
            continue
        path = unquote(parsed.path)
        if path:
            yield match, path


def main() -> int:
    failures: list[str] = []
    checked = 0
    markdown_files = sorted(
        path for path in ROOT.rglob("*.md") if ".git" not in path.parts
    )

    for markdown in markdown_files:
        text = markdown.read_text(encoding="utf-8")
        for match, raw_path in iter_relative_links(markdown):
            checked += 1
            target = (ROOT / raw_path.lstrip("/")) if raw_path.startswith("/") else (markdown.parent / raw_path)
            if not target.exists():
                line = text.count("\n", 0, match.start()) + 1
                failures.append(
                    f"{markdown.relative_to(ROOT)}:{line}: missing relative target: {raw_path}"
                )

    if failures:
        print("Broken relative Markdown links:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1

    print(f"Checked {checked} relative links across {len(markdown_files)} Markdown files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
