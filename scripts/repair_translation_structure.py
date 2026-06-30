#!/usr/bin/env python3
"""Restore non-rendered Verse test code and Markdown fence boundaries.

Machine translation may remove a paragraph's trailing newline and may translate
the code held in ``<!--versetest ... -->`` comments. Both are structural data,
not prose, so restore them from the English source without changing translated
body text.
"""

from __future__ import annotations

import re
from pathlib import Path


HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
FENCE_NOT_AT_LINE_START_RE = re.compile(r"(?<!\n)(?=(```|~~~)[A-Za-z0-9_-]*\r?\n)")


def repair(source: Path, translated: Path) -> None:
    original = source.read_text(encoding="utf-8")
    chinese = translated.read_text(encoding="utf-8")
    # Documentation comments carry hidden test programs in several spellings
    # (for example ``versetest`` and ``NoCompile``). They are all source data.
    source_blocks = HTML_COMMENT_RE.findall(original)
    target_blocks = HTML_COMMENT_RE.findall(chinese)
    if len(source_blocks) != len(target_blocks):
        raise RuntimeError(
            f"{source.name}: HTML comment count differs ({len(source_blocks)} != {len(target_blocks)})"
        )
    block_index = 0

    def restore(_: re.Match[str]) -> str:
        nonlocal block_index
        value = source_blocks[block_index]
        block_index += 1
        return value

    chinese = HTML_COMMENT_RE.sub(restore, chinese)
    chinese = FENCE_NOT_AT_LINE_START_RE.sub("\n", chinese)
    translated.write_text(chinese, encoding="utf-8", newline="\n")


def main() -> None:
    source_dir = Path("docs")
    translated_dir = source_dir / "zh"
    for source in sorted(source_dir.glob("*.md")):
        translated = translated_dir / source.name
        if not translated.exists():
            raise RuntimeError(f"Missing translation: {translated}")
        repair(source, translated)
        print(f"repaired {translated}")


if __name__ == "__main__":
    main()
