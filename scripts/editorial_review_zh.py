#!/usr/bin/env python3
"""Apply terminology corrections and translate English comments in fenced code.

The Verse source itself is never modified: only prose outside code fences and
the natural-language portion following a Verse ``#`` comment marker change.
"""

from __future__ import annotations

import importlib.util
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


MODULE_SPEC = importlib.util.spec_from_file_location("translator", Path(__file__).with_name("translate_docs_zh.py"))
translator = importlib.util.module_from_spec(MODULE_SPEC)
assert MODULE_SPEC.loader is not None
MODULE_SPEC.loader.exec_module(translator)

FENCED_BLOCK_RE = re.compile(r"(?ms)^(?P<fence>\s*(?:`{3,}|~{3,})[^\n]*\n)(?P<body>.*?)(?P<close>^\s*(?:`{3,}|~{3,})\s*$)")
ENGLISH_RE = re.compile(r"[A-Za-z]{2}")
MARKER_RE = re.compile(r"\[\[\[C(?P<id>\d{5})\]\]\]\s*(?P<text>.*?)(?=\[\[\[C\d{5}\]\]\]|\Z)", re.S)

# Applied longest-first. The language name is intentionally never translated.
GLOSSARY = {
    "《诗经》": "《Verse 之书》",
    "诗篇": "Verse",
    "诗歌": "Verse",
    "诗句": "Verse",
    "韵文": "Verse",
    "诗允许": "Verse 允许",
    "诗中的": "Verse 中的",
    "诗中": "Verse 中",
    "诗的": "Verse 的",
    "诗：": "Verse：",
    "诗，": "Verse，",
    "诗。": "Verse。",
    "诗 ": "Verse ",
    "交易效果": "事务效果",
    "交易函数": "事务函数",
}


def apply_glossary(text: str) -> str:
    for before, after in sorted(GLOSSARY.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(before, after)
    return text


def comment_start(line: str) -> int | None:
    """Find a Verse # comment marker outside ordinary quoted strings."""
    quote: str | None = None
    escaped = False
    for index, char in enumerate(line):
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in ("'", '"'):
            quote = char
        elif char == "#":
            return index
    return None


def collect_comments(text: str) -> list[str]:
    comments: list[str] = []
    for match in FENCED_BLOCK_RE.finditer(text):
        for line in match.group("body").splitlines():
            marker = comment_start(line)
            if marker is not None:
                comment = line[marker + 1 :].strip()
                if comment and ENGLISH_RE.search(comment):
                    comments.append(comment)
    return list(dict.fromkeys(comments))


def translate_batch(entries: list[tuple[int, str]]) -> dict[int, str]:
    request = "".join(f"[[[C{number:05d}]]]\n{text}\n" for number, text in entries)
    output = translator.translate(request)
    translated: dict[int, str] = {}
    for match in MARKER_RE.finditer(output):
        translated[int(match.group("id"))] = match.group("text").strip()
    if len(translated) != len(entries):
        # A short retry is more reliable for a malformed batch response.
        translated = {}
        for number, text in entries:
            translated[number] = translator.translate(text).strip()
    return translated


def batches(comments: list[str], limit: int = 850) -> list[list[tuple[int, str]]]:
    result: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    size = 0
    for number, comment in enumerate(comments):
        entry_size = len(comment) + 28
        if current and size + entry_size > limit:
            result.append(current)
            current, size = [], 0
        current.append((number, comment))
        size += entry_size
    if current:
        result.append(current)
    return result


def translate_comments(comments: list[str]) -> dict[str, str]:
    result: dict[int, str] = {}
    grouped = batches(comments)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(translate_batch, group) for group in grouped]
        for future in as_completed(futures):
            result.update(future.result())
    return {comment: apply_glossary(result[number]) for number, comment in enumerate(comments)}


def edit_code_comments(body: str, translations: dict[str, str]) -> str:
    result: list[str] = []
    for line in body.splitlines(keepends=True):
        marker = comment_start(line)
        if marker is None:
            result.append(line)
            continue
        newline = "\n" if line.endswith("\n") else ""
        content = line[:-1] if newline else line
        comment = content[marker + 1 :].strip()
        translated = translations.get(comment)
        if translated is None:
            result.append(line)
            continue
        leading = content[marker + 1 :]
        whitespace = leading[: len(leading) - len(leading.lstrip())]
        result.append(content[: marker + 1] + whitespace + translated + newline)
    return "".join(result)


def edit_document(path: Path, translations: dict[str, str]) -> None:
    text = path.read_text(encoding="utf-8")
    pieces: list[str] = []
    cursor = 0
    for match in FENCED_BLOCK_RE.finditer(text):
        pieces.append(apply_glossary(text[cursor : match.start()]))
        pieces.append(match.group("fence"))
        pieces.append(edit_code_comments(match.group("body"), translations))
        pieces.append(match.group("close"))
        cursor = match.end()
    pieces.append(apply_glossary(text[cursor:]))
    path.write_text("".join(pieces), encoding="utf-8", newline="\n")


def main() -> None:
    documents = sorted(Path("docs/zh").glob("*.md"))
    comments = []
    for document in documents:
        comments.extend(collect_comments(document.read_text(encoding="utf-8")))
    comments = list(dict.fromkeys(comments))
    print(f"Translating {len(comments)} distinct code comments.", flush=True)
    translations = translate_comments(comments)
    for document in documents:
        edit_document(document, translations)
        print(f"reviewed {document}", flush=True)


if __name__ == "__main__":
    main()
