#!/usr/bin/env python3
"""
Render DEMO_AND_TEST_GUIDE.md → HTML (pandoc) → PDF (Chrome headless).

Requires: pandoc, Google Chrome. No WeasyPrint / LaTeX CJK packages needed.
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD_PATH = ROOT / "DEMO_AND_TEST_GUIDE.md"
PDF_PATH = ROOT / "DEMO_AND_TEST_GUIDE.pdf"
HEADER = Path(__file__).resolve().parent / "demo_guide_pdf_header.html"

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
]


def _chrome() -> str:
    for p in CHROME_CANDIDATES:
        if Path(p).is_file():
            return p
    raise SystemExit("Google Chrome or Chromium not found; install Chrome or set CHROME_PATH.")


def main() -> None:
    if not MD_PATH.is_file():
        raise SystemExit(f"Missing {MD_PATH}")
    if not HEADER.is_file():
        raise SystemExit(f"Missing {HEADER}")

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        html_path = Path(tmp.name)

    try:
        subprocess.run(
            [
                "pandoc",
                str(MD_PATH),
                "-o",
                str(html_path),
                "--standalone",
                "--toc",
                "--toc-depth=3",
                f"--include-in-header={HEADER}",
                "-M",
                "title=Aegis Demo & Test Guide",
            ],
            check=True,
            cwd=str(ROOT),
        )

        chrome = _chrome()
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--disable-gpu",
                f"--print-to-pdf={PDF_PATH}",
                "--no-pdf-header-footer",
                html_path.resolve().as_uri(),
            ],
            check=True,
        )
    finally:
        html_path.unlink(missing_ok=True)

    print(f"Wrote {PDF_PATH}")


if __name__ == "__main__":
    main()
