#!/usr/bin/env python3
"""Create complete English and Simplified-Chinese PDF editions of the book.

The script deliberately builds one self-contained HTML document per language
before handing it to Chromium.  This keeps Markdown as the source of truth and
avoids platform-specific PDF layout behaviour from native document converters.
"""

from __future__ import annotations

import argparse
from datetime import date
import html
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Iterable

try:
    import markdown
except ImportError as error:  # A useful error when the script is run directly.
    raise SystemExit(
        "Missing Python package 'Markdown'. Run .\\scripts\\build_pdfs.ps1 first "
        "or install requirements-pdf.txt."
    ) from error


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
STYLE = ROOT / "styles" / "pdf-book.css"
TEMP = ROOT / "tmp" / "pdfs"
OUTPUT = ROOT / "output" / "pdf"

BOOK_FILES = (
    "index.md",
    "00_overview.md",
    "01_expressions.md",
    "02_primitives.md",
    "03_containers.md",
    "04_operators.md",
    "05_mutability.md",
    "06_functions.md",
    "07_control.md",
    "08_failure.md",
    "09_structs_enums.md",
    "10_classes_interfaces.md",
    "11_types.md",
    "12_access.md",
    "13_effects.md",
    "14_concurrency.md",
    "15_live_variables.md",
    "16_modules.md",
    "17_persistable.md",
    "18_evolution.md",
    "concept_index.md",
    "VerseSyntaxValidation.md",
)

EDITIONS = {
    "en": {
        "source": DOCS,
        "title": "Book of Verse",
        "subtitle": "Documentation for the Verse programming language",
        "toc": "Contents",
        "edition": "English edition",
        "filename": "Book-of-Verse-en.pdf",
    },
    "zh": {
        "source": DOCS / "zh",
        "title": "Verse 编程语言之书",
        "subtitle": "Verse 编程语言文档",
        "toc": "目录",
        "edition": "简体中文版",
        "filename": "Book-of-Verse-zh.pdf",
    },
    "zh-llm": {
        "source": DOCS / "zh-llm",
        "title": "Verse 编程语言之书",
        "subtitle": "Verse 编程语言文档",
        "toc": "目录",
        "edition": "简体中文 LLM 重译版",
        "filename": "Book-of-Verse-zh-llm.pdf",
    },
}

FALLBACK_TITLES = {
    "en": {"VerseSyntaxValidation.md": "Appendix: Verse Syntax Validation"},
    "zh": {"VerseSyntaxValidation.md": "附录：Verse 语法验证"},
    "zh-llm": {"VerseSyntaxValidation.md": "附录：Verse 语法验证"},
}

H1_RE = re.compile(r"^#\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
LINK_RE = re.compile(r"(?<!!)\]\((?P<target>[^)\s]+)(?P<suffix>\s+(?:\"[^\"]*\"|'[^']*'))?\)")
FRONT_MATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)


def chapter_id(filename: str) -> str:
    """Return a stable, PDF-local fragment for a source Markdown filename."""
    return "chapter-" + Path(filename).stem.lower().replace("_", "-")


def validate_sources(languages: Iterable[str]) -> None:
    """Fail before rendering if selected translated editions do not contain the same book."""
    english = {path.name for path in DOCS.glob("*.md")}
    absent = [filename for filename in BOOK_FILES if filename not in english]
    if absent:
        raise SystemExit("Book order references missing source file(s): " + ", ".join(absent))
    if set(BOOK_FILES) != english:
        omitted = english - set(BOOK_FILES)
        raise SystemExit("Book order omits source file(s): " + ", ".join(sorted(omitted)))
    for language in languages:
        if language == "en":
            continue
        edition = EDITIONS[language]
        translated = {path.name for path in edition["source"].glob("*.md")} - {"术语表.md"}
        missing = english - translated
        unexpected = translated - english
        if missing or unexpected:
            messages: list[str] = []
            label = edition["source"].relative_to(ROOT)
            if missing:
                messages.append(f"{label} translation missing: " + ", ".join(sorted(missing)))
            if unexpected:
                messages.append(f"Unexpected Markdown file in {label}: " + ", ".join(sorted(unexpected)))
            raise SystemExit("\n".join(messages))


def title_from_markdown(source: str, fallback: str) -> str:
    match = first_h1(source)
    if not match:
        return fallback
    title = re.sub(r"\s+#+$", "", match.group(1))
    return re.sub(r"`([^`]*)`", r"\1", title)


def first_h1(source: str) -> re.Match[str] | None:
    """Find the first document-level heading, never a comment inside code."""
    in_fence = False
    for line in source.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence and (match := H1_RE.match(line)):
            return match
    return None


def normalize_source(filename: str, source: str, language: str) -> str:
    """Omit MkDocs-only metadata and give an untitled appendix a book heading."""
    source = source.removeprefix("\ufeff")
    source = FRONT_MATTER_RE.sub("", source, count=1)
    if first_h1(source):
        return source
    fallback = FALLBACK_TITLES.get(language, {}).get(filename, Path(filename).stem)
    return f"# {fallback}\n\n{source.lstrip()}"


def rewrite_internal_links(source: str) -> str:
    """Point cross-page Markdown links at the appropriate chapter in one PDF."""

    names = set(BOOK_FILES)

    def replace(match: re.Match[str]) -> str:
        target = match.group("target")
        plain_target, separator, _fragment = target.partition("#")
        filename = Path(plain_target).name
        if filename not in names:
            return match.group(0)
        suffix = match.group("suffix") or ""
        # Heading fragments may be translated differently in the Chinese source;
        # chapter anchors remain reliable in both PDFs.
        return f"](#{chapter_id(filename)}{suffix})"

    return LINK_RE.sub(replace, source)


def markdown_html(source: str) -> str:
    renderer = markdown.Markdown(
        extensions=(
            "admonition",
            "attr_list",
            "fenced_code",
            "footnotes",
            "sane_lists",
            "tables",
            "toc",
        ),
        output_format="html5",
    )
    return renderer.convert(rewrite_internal_links(source))


def toc_items(documents: Iterable[tuple[str, str]]) -> str:
    entries = []
    for filename, source in documents:
        label = html.escape(title_from_markdown(source, Path(filename).stem))
        entries.append(f'<li><a href="#{chapter_id(filename)}">{label}</a></li>')
    return "\n".join(entries)


def build_html(language: str) -> Path:
    edition = EDITIONS[language]
    source_root = edition["source"]
    documents = [
        (filename, normalize_source(filename, (source_root / filename).read_text(encoding="utf-8"), language))
        for filename in BOOK_FILES
    ]
    chapters = []
    for filename, source in documents:
        chapter = markdown_html(source)
        chapters.append(f'<section class="chapter" id="{chapter_id(filename)}">\n{chapter}\n</section>')

    today = date.today().isoformat()
    style = STYLE.read_text(encoding="utf-8")
    document_title = html.escape(edition["title"])
    page = f"""<!doctype html>
<html lang="{'zh-CN' if language.startswith('zh') else 'en'}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{document_title}</title>
  <style>{style}</style>
</head>
<body>
  <section class="cover">
    <p class="cover__eyebrow">{html.escape(edition['edition'])}</p>
    <h1>{document_title}</h1>
    <p class="cover__subtitle">{html.escape(edition['subtitle'])}</p>
    <p class="cover__meta">verselang.github.io/book - {today}</p>
  </section>
  <nav class="book-toc" aria-label="{html.escape(edition['toc'])}">
    <h1>{html.escape(edition['toc'])}</h1>
    <ol>
      {toc_items(documents)}
    </ol>
  </nav>
  {'\n'.join(chapters)}
</body>
</html>
"""
    TEMP.mkdir(parents=True, exist_ok=True)
    output = TEMP / f"book-{language}.html"
    output.write_text(page, encoding="utf-8", newline="\n")
    return output


def resolve_node(value: str | None) -> str:
    if value:
        return value
    if node := shutil.which("node"):
        return node
    raise SystemExit(
        "Node.js was not found. Supply --node or use .\\scripts\\build_pdfs.ps1, "
        "which locates the bundled runtime."
    )


def render_pdf(html_file: Path, pdf_file: Path, document_title: str, node: str) -> None:
    renderer = ROOT / "scripts" / "render_pdf.mjs"
    pdf_file.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [node, str(renderer), str(html_file), str(pdf_file), document_title],
        cwd=ROOT,
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build English and Chinese Book of Verse PDFs.")
    parser.add_argument("--lang", choices=("all", "en", "zh", "zh-llm"), default="all")
    parser.add_argument("--node", help="Path to the Node.js executable used for Chromium printing.")
    parser.add_argument("--html-only", action="store_true", help="Generate printable HTML without rendering PDFs.")
    args = parser.parse_args()

    languages = ("en", "zh") if args.lang == "all" else (args.lang,)
    validate_sources(languages)
    node = "" if args.html_only else resolve_node(args.node)
    for language in languages:
        html_file = build_html(language)
        if args.html_only:
            print(f"Generated {html_file.relative_to(ROOT)}")
            continue
        edition = EDITIONS[language]
        pdf_file = OUTPUT / edition["filename"]
        render_pdf(html_file, pdf_file, edition["title"], node)
        print(f"Generated {pdf_file.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
