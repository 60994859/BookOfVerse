#!/usr/bin/env python3
"""Restore commented-out Verse code and canonicalize Verse specifiers in comments."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path


SPEC = importlib.util.spec_from_file_location("editor", Path(__file__).with_name("editorial_review_zh.py"))
editor = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(editor)

FENCE = editor.FENCED_BLOCK_RE
SPECIFIER_MAP = {
    "<暂停>": "<suspends>",
    "<计算>": "<computes>",
    "<决定>": "<decides>",
    "<交易>": "<transacts>",
    "<读取>": "<reads>",
    "<写入>": "<writes>",
    "<覆盖>": "<override>",
    "<最终>": "<final>",
    "<内部>": "<internal>",
    "<唯一>": "<unique>",
}
COMMENTED_CODE_RE = re.compile(
    r"(?:\:=|\=>|\b(?:class|struct|interface|module)\b\s*[:{]|"
    r"^[\s]*(?:if|for|set|return|loop|defer|race|sync|spawn)\b|"
    r"^[\s]*[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)?\s*\(|"
    r"<\w+>\s*:\s*[A-Za-z_?])"
)


def normalize_comment(text: str) -> str:
    for before, after in SPECIFIER_MAP.items():
        text = text.replace(before, after)
    return text.replace("选项{", "option{").replace("否 <suspends>", "不含 <suspends>")


def repair_block(source_body: str, chinese_body: str) -> str:
    source_lines = source_body.splitlines(keepends=True)
    target_lines = chinese_body.splitlines(keepends=True)
    if len(source_lines) != len(target_lines):
        raise RuntimeError("Code block line count differs")
    result: list[str] = []
    for source_line, target_line in zip(source_lines, target_lines):
        marker = editor.comment_start(source_line)
        if marker is None:
            result.append(target_line)
            continue
        source_comment = source_line[marker + 1 :].rstrip("\r\n")
        if COMMENTED_CODE_RE.search(source_comment):
            result.append(source_line)
            continue
        target_marker = editor.comment_start(target_line)
        if target_marker is None:
            raise RuntimeError("Comment marker was lost")
        ending = "\n" if target_line.endswith("\n") else ""
        target_content = target_line[:-1] if ending else target_line
        result.append(target_content[: target_marker + 1] + normalize_comment(target_content[target_marker + 1 :]) + ending)
    return "".join(result)


def repair_document(source: Path, chinese: Path) -> None:
    source_text = source.read_text(encoding="utf-8")
    chinese_text = chinese.read_text(encoding="utf-8")
    source_blocks = list(FENCE.finditer(source_text))
    chinese_blocks = list(FENCE.finditer(chinese_text))
    if len(source_blocks) != len(chinese_blocks):
        raise RuntimeError(f"{source.name}: code block count differs")
    result: list[str] = []
    cursor = 0
    for original, translated in zip(source_blocks, chinese_blocks):
        result.append(chinese_text[cursor : translated.start()])
        result.append(translated.group("fence"))
        result.append(repair_block(original.group("body"), translated.group("body")))
        result.append(translated.group("close"))
        cursor = translated.end()
    result.append(chinese_text[cursor:])
    chinese.write_text("".join(result), encoding="utf-8", newline="\n")


def main() -> None:
    for source in sorted(Path("docs").glob("*.md")):
        chinese = Path("docs/zh") / source.name
        repair_document(source, chinese)
        print(f"repaired {chinese}")


if __name__ == "__main__":
    main()
