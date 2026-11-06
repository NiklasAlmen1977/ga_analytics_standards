"""Make a PDF of a data product documentation file (docs/<semantic model name>.md).

Python, no installation. Builds an HTML page that renders the Markdown (marked) and the
Mermaid diagrams (mermaid) in the browser, and prints it with Microsoft Edge in headless mode.
Needs network access to cdn.jsdelivr.net for the two libraries.

Usage:
    python md_to_pdf.py "docs/<semantic model name>.md" [output.pdf]

Without an output path the PDF is written next to the Markdown file. The Markdown file is the
master; the PDF is a copy for business users and never goes into git (see the
ga-data-product-documentation skill for where to save it).
"""
import html
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

MARKED = "https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"
MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"
ATTEMPTS = 5
EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>
  @page {{ size: A4; margin: 16mm 14mm; }}
  body {{ font-family: Arial, sans-serif; font-size: 10pt; color: #252423; line-height: 1.4; }}
  h1 {{ color: #235A81; font-size: 20pt; }}
  h2 {{ color: #235A81; font-size: 15pt; border-bottom: 2px solid #235A81; padding-bottom: 2px; }}
  h3 {{ color: #235A81; font-size: 12pt; }}
  table {{ border-collapse: collapse; width: 100%; margin: 6px 0 12px; font-size: 8.5pt; }}
  th, td {{ border: 1px solid #C8C8C8; padding: 3px 5px; text-align: left; vertical-align: top; }}
  th {{ background: #EEF2F3; }}
  tr, img, .mermaid {{ page-break-inside: avoid; }}
  code {{ font-family: Consolas, monospace; font-size: 8.5pt; background: #F5F5F5; padding: 0 2px; }}
  pre code {{ display: block; padding: 6px; white-space: pre-wrap; }}
  .mermaid {{ text-align: center; margin: 8px 0 14px; }}
  .mermaid svg {{ max-width: 100%; height: auto; }}
</style>
<script src="{marked}"></script>
<script src="{mermaid}"></script>
</head><body>
<div id="content"></div>
<script>
  const source = {source};
  document.getElementById("content").innerHTML = marked.parse(source);
  // Code blocks marked as mermaid become diagrams
  document.querySelectorAll("pre code.language-mermaid").forEach(function (code) {{
    const div = document.createElement("div");
    div.className = "mermaid";
    div.textContent = code.textContent;
    code.parentElement.replaceWith(div);
  }});
  mermaid.initialize({{ startOnLoad: false, theme: "neutral", fontFamily: "Arial" }});
  mermaid.run();
</script>
</body></html>
"""


def find_edge():
    for path in EDGE_PATHS:
        if pathlib.Path(path).exists():
            return path
    return shutil.which("msedge")


def wait_for_pdf(pdf_path, seconds=30):
    """True when the PDF exists and its size has stopped changing."""
    last_size = -1
    for _ in range(seconds * 2):
        if pdf_path.exists():
            size = pdf_path.stat().st_size
            if size > 0 and size == last_size:
                return True
            last_size = size
        time.sleep(0.5)
    return pdf_path.exists() and pdf_path.stat().st_size > 0


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    md_path = pathlib.Path(sys.argv[1]).resolve()
    pdf_path = pathlib.Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else md_path.with_suffix(".pdf")
    edge = find_edge()
    if not edge:
        sys.exit("Microsoft Edge was not found; open the HTML file in a browser and print it to PDF instead.")

    source = md_path.read_text(encoding="utf-8")
    page = PAGE.format(
        title=html.escape(md_path.stem),
        marked=MARKED,
        mermaid=MERMAID,
        # JSON keeps the Markdown intact; escaping "</" keeps it from closing the script tag
        source=json.dumps(source).replace("</", "<\\/"),
    )

    if pdf_path.exists():
        try:
            pdf_path.unlink()  # so a PDF left from an earlier run is never taken for a new one
        except PermissionError:
            sys.exit(f"Close {pdf_path.name} first: it is open in another program.")

    # Edge can keep files in the profile folder open after it returns, so cleanup errors are ignored
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        html_path = pathlib.Path(tmp) / "document.html"
        html_path.write_text(page, encoding="utf-8")
        # Edge in headless mode sometimes exits without writing the PDF (seen 2026-11 with
        # --headless=new). The old headless mode works, but its launcher can return before the
        # PDF is written, so each attempt waits for the file; then it retries with a new profile.
        for attempt in range(1, ATTEMPTS + 1):
            subprocess.run(
                [
                    edge,
                    "--headless",
                    "--disable-gpu",
                    "--no-pdf-header-footer",
                    "--virtual-time-budget=15000",  # time for the libraries to load and draw
                    f"--user-data-dir={pathlib.Path(tmp) / f'profile{attempt}'}",
                    f"--print-to-pdf={pdf_path}",
                    html_path.as_uri(),
                ],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=120,
            )
            if wait_for_pdf(pdf_path):
                break
    if not pdf_path.exists():
        sys.exit(
            f"Edge did not write the PDF after {ATTEMPTS} attempts. Close the PDF if it is open, "
            "or open the Markdown in a browser and print it to PDF instead."
        )
    print(f"PDF written: {pdf_path}")


if __name__ == "__main__":
    main()
