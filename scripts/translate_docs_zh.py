#!/usr/bin/env python3
"""Create Markdown-preserving Simplified-Chinese drafts for the Verse book.

Only prose is sent for translation. Fenced code blocks, inline code, URLs and
Markdown link destinations are replaced with temporary tokens first and restored
afterwards, so examples and links remain byte-for-byte intact.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path


TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"
# Smaller requests are more reliable at retaining protected inline Markdown in
# dense lists and tables. The concurrency option keeps whole-book runs fast.
MAX_CHARS = 1_000
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
PROTECT_RE = re.compile(
    r"`[^`\n]+`"  # inline code
    r"|https?://[^\s)>]+"  # bare URLs
    r"|<https?://[^>]+>"  # autolinks
)
LINK_RE = re.compile(r"(!?\[)([^\]]*)(\]\()([^\)\n]+)(\))")
TOKEN_RE = re.compile(r"\[\[\[PRESERVEINLINE\d{5}\]\]\]")


def protect_markdown(text: str) -> tuple[str, dict[str, str]]:
    """Protect code and URL portions while allowing link labels to translate."""
    tokens: dict[str, str] = {}

    def save(value: str) -> str:
        token = f"[[[PRESERVEINLINE{len(tokens):05d}]]]"
        tokens[token] = value
        return token

    # Keep labels translatable, but protect link targets and image sources.
    text = LINK_RE.sub(lambda m: m.group(1) + m.group(2) + m.group(3) + save(m.group(4)) + m.group(5), text)

    def replace(match: re.Match[str]) -> str:
        value = match.group(0)
        # Link target has already become a token; all remaining matches can stay intact.
        return save(value)

    return PROTECT_RE.sub(replace, text), tokens


def restore_markdown(text: str, tokens: dict[str, str]) -> str:
    for token, value in tokens.items():
        text = text.replace(token, value)
    missing = [token for token in tokens if token not in text and tokens[token] not in text]
    if missing:
        raise RuntimeError(f"Translation altered protected tokens: {missing[:3]}")
    return text


def chunks(text: str) -> list[str]:
    """Split at paragraph boundaries, keeping requests below the endpoint limit."""
    result: list[str] = []
    current = ""
    for part in re.split(r"(\n\s*\n)", text):
        if len(part) > MAX_CHARS:
            remainder = part
            while len(remainder) > MAX_CHARS:
                cut = max(remainder.rfind("\n", 0, MAX_CHARS), remainder.rfind(" ", 0, MAX_CHARS))
                if cut <= 0:
                    cut = MAX_CHARS
                # Never divide a temporary token between two API requests.
                for match in TOKEN_RE.finditer(remainder):
                    if match.start() < cut < match.end():
                        cut = match.start()
                        break
                if cut <= 0:
                    cut = MAX_CHARS
                if current:
                    result.append(current)
                    current = ""
                result.append(remainder[:cut])
                remainder = remainder[cut:]
            if remainder:
                result.append(remainder)
            continue
        if current and len(current) + len(part) > MAX_CHARS:
            result.append(current)
            current = part
        else:
            current += part
    if current:
        result.append(current)
    return result


def translate(text: str) -> str:
    if not text.strip():
        return text
    params = urllib.parse.urlencode(
        [("client", "gtx"), ("sl", "en"), ("tl", "zh-CN"), ("dt", "t"), ("q", text)]
    )
    request = urllib.request.Request(
        f"{TRANSLATE_URL}?{params}", headers={"User-Agent": "VerseBookTranslation/1.0"}
    )
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return "".join(item[0] for item in payload[0])
        except Exception as error:  # Endpoint failures are transient in practice.
            last_error = error
            time.sleep(2**attempt)
    raise RuntimeError(f"Translation request failed: {last_error}")


def translate_prose(text: str) -> str:
    protected, tokens = protect_markdown(text)
    translated = "".join(translate(chunk) for chunk in chunks(protected))
    return restore_markdown(translated, tokens)


def translate_file(source: Path, destination: Path) -> None:
    lines = source.read_text(encoding="utf-8").splitlines(keepends=True)
    output: list[str] = []
    prose: list[str] = []
    in_fence = False

    def flush_prose() -> None:
        nonlocal prose
        if prose:
            output.append(translate_prose("".join(prose)))
            prose = []

    for line in lines:
        if FENCE_RE.match(line):
            flush_prose()
            output.append(line)
            in_fence = not in_fence
        elif in_fence:
            output.append(line)
        else:
            prose.append(line)
    flush_prose()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("".join(output), encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("docs"))
    parser.add_argument("--output", type=Path, default=Path("docs/zh"))
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    sources = sorted(path for path in args.source.glob("*.md") if path.parent != args.output)
    if not sources:
        raise SystemExit("No source Markdown files found.")
    jobs = [
        (source, args.output / source.name)
        for source in sources
        if args.overwrite or not (args.output / source.name).exists()
    ]
    skipped = len(sources) - len(jobs)
    if skipped:
        print(f"Skipping {skipped} existing translation draft(s).", flush=True)
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {
            executor.submit(translate_file, source, destination): source
            for source, destination in jobs
        }
        for number, future in enumerate(as_completed(futures), 1):
            source = futures[future]
            future.result()
            print(f"[{number}/{len(jobs)}] completed {source}", flush=True)
    print("Chinese translation drafts created.")


if __name__ == "__main__":
    main()
