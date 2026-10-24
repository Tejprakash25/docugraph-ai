"""Generate PDF fixtures from the repository's synthetic contract sources.

The script has no network access and only writes PDFs beneath the fixed
``data/sample_contracts`` directory. The Markdown files remain the source of
truth and contain fictional, non-legal test data.
"""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "sample_contracts"
PAGE_WIDTH = 595
PAGE_HEIGHT = 842
MARGIN_X = 58
TOP_Y = 58
BOTTOM_Y = 58
LINE_HEIGHT = 14


def _plain_text(line: str) -> str:
    return re.sub(r"[*`]", "", line).strip()


def _write_line(page: fitz.Page, text: str, y: float, *, size: float, bold: bool) -> float:
    # PyMuPDF's built-in Helvetica aliases are ``helv`` and ``hebo``.
    font = "hebo" if bold else "helv"
    page.insert_text((MARGIN_X, y), text, fontname=font, fontsize=size, color=(0.1, 0.1, 0.1))
    return y + (size + 5)


def render(source: Path, target: Path) -> None:
    document = fitz.open()
    page = document.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
    y = TOP_Y

    for raw_line in source.read_text(encoding="utf-8").splitlines():
        line = _plain_text(raw_line)
        if not line:
            y += 7
            continue

        if line.startswith("# "):
            size, bold, width = 15, True, 58
            content = line[2:]
        elif line.startswith("## "):
            size, bold, width = 11, True, 88
            content = line[3:]
        else:
            size, bold, width = 9, False, 108
            content = line

        for wrapped in textwrap.wrap(content, width=width, break_long_words=False, break_on_hyphens=False):
            if y > PAGE_HEIGHT - BOTTOM_Y - LINE_HEIGHT:
                page = document.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
                y = TOP_Y
            y = _write_line(page, wrapped, y, size=size, bold=bold)
        y += 4 if bold else 2

    document.save(target)
    document.close()


def main() -> None:
    for source in sorted(SOURCE_DIR.glob("contract_*.md")):
        target = source.with_suffix(".pdf")
        render(source, target)
        print(f"generated {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
