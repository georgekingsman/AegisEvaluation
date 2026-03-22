#!/usr/bin/env python3
"""
将 Markdown 幻灯片转换为可在浏览器查看或打印为 PDF 的 HTML。
用法：python3 slides/convert_to_html.py
输出：slides/aegis_evaluation.html
"""

from __future__ import annotations

import html
import pathlib
import re


SRC = pathlib.Path(__file__).parent / "aegis_evaluation.md"
OUT = pathlib.Path(__file__).parent / "aegis_evaluation.html"


def inline(text: str) -> str:
        escaped = html.escape(text)
        escaped = re.sub(r'!\[(.*?)\]\((.+?)\)', r'<img src="\2" alt="\1">', escaped)
        escaped = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', escaped)
        escaped = re.sub(r'`(.+?)`', r'<code>\1</code>', escaped)
        escaped = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', escaped)
        escaped = re.sub(r'\*(.+?)\*', r'<em>\1</em>', escaped)
        return escaped


def md_to_html(text: str) -> str:
        lines = text.strip().splitlines()
        out: list[str] = []
        in_code = False
        code_lines: list[str] = []
        list_type: str | None = None
        in_table = False
        table_header_written = False

        def close_list() -> None:
                nonlocal list_type
                if list_type == "ul":
                        out.append("</ul>")
                elif list_type == "ol":
                        out.append("</ol>")
                list_type = None

        def close_table() -> None:
                nonlocal in_table, table_header_written
                if in_table:
                        out.append("</table>")
                in_table = False
                table_header_written = False

        for line in lines:
                stripped = line.strip()

                if stripped.startswith("```"):
                        close_list()
                        close_table()
                        if in_code:
                                out.append("<pre><code>{}</code></pre>".format(html.escape("\n".join(code_lines))))
                                in_code = False
                                code_lines = []
                        else:
                                in_code = True
                                code_lines = []
                        continue

                if in_code:
                        code_lines.append(line)
                        continue

                if stripped.startswith("<!--"):
                        continue

                if stripped.startswith("<") and not stripped.startswith("<!"):
                        close_list()
                        close_table()
                        out.append(line)
                        continue

                if not stripped:
                        close_list()
                        close_table()
                        out.append("<div class=\"spacer\"></div>")
                        continue

                if stripped.startswith("|") and stripped.endswith("|"):
                        close_list()
                        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
                        if all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells if cell):
                                continue
                        if not in_table:
                                out.append("<table>")
                                in_table = True
                                table_header_written = False
                        tag = "th" if not table_header_written else "td"
                        out.append("<tr>{}</tr>".format("".join(f"<{tag}>{inline(cell)}</{tag}>" for cell in cells)))
                        table_header_written = True
                        continue
                close_table()

                header_match = re.match(r'^(#{1,4})\s+(.*)', line)
                if header_match:
                        close_list()
                        level = len(header_match.group(1))
                        out.append(f"<h{level}>{inline(header_match.group(2))}</h{level}>")
                        continue

                unordered_match = re.match(r'^[-*]\s+(.*)', stripped)
                if unordered_match:
                        if list_type != "ul":
                                close_list()
                                out.append("<ul>")
                                list_type = "ul"
                        out.append(f"<li>{inline(unordered_match.group(1))}</li>")
                        continue

                ordered_match = re.match(r'^\d+\.\s+(.*)', stripped)
                if ordered_match:
                        if list_type != "ol":
                                close_list()
                                out.append("<ol>")
                                list_type = "ol"
                        out.append(f"<li>{inline(ordered_match.group(1))}</li>")
                        continue
                close_list()

                if stripped.startswith(">"):
                        out.append(f"<blockquote>{inline(stripped[1:].strip())}</blockquote>")
                        continue

                out.append(f"<p>{inline(line)}</p>")

        close_list()
        close_table()
        if in_code:
                out.append("<pre><code>{}</code></pre>".format(html.escape("\n".join(code_lines))))
        return "\n".join(out)


raw = SRC.read_text(encoding="utf-8")
raw = re.sub(r'^---\n.*?\n---\n', '', raw, count=1, flags=re.DOTALL)
slides_raw = re.split(r'^---\s*$', raw, flags=re.MULTILINE)

slide_divs = []
for index, slide in enumerate(slides_raw, start=1):
        stripped = slide.strip()
        if not stripped:
                continue
        slide_divs.append(f'<section class="slide" id="slide-{index}">\n{md_to_html(stripped)}\n</section>')

html_out = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Aegis Security Evaluation</title>
<style>
    * {{ box-sizing: border-box; }}
    :root {{
        --paper: #f6f1e8;
        --paper-2: #fbf7f1;
        --ink: #16212f;
        --muted: #546173;
        --line: #d6c8b7;
        --navy: #18324a;
        --teal: #0f8b8d;
        --sand: #eadfcf;
        --red: #d95d39;
        --green: #2d8f5b;
        --amber: #c88a04;
    }}
    body {{
        margin: 0;
        background:
            radial-gradient(circle at top left, #efe3d2 0, #efe3d2 18%, transparent 18%),
            linear-gradient(180deg, #ece4d8 0%, #ddd2c2 100%);
        color: var(--ink);
        font-family: "Avenir Next", "Helvetica Neue", Helvetica, sans-serif;
        font-size: 24px;
    }}
    .slide {{
        width: 1365px;
        min-height: 768px;
        margin: 28px auto;
        padding: 52px 58px 62px;
        background: linear-gradient(180deg, var(--paper-2) 0%, var(--paper) 100%);
        border: 1px solid rgba(22, 33, 47, 0.08);
        box-shadow: 0 24px 60px rgba(22, 33, 47, 0.12);
        position: relative;
        overflow: hidden;
        page-break-after: always;
    }}
    .slide::before {{
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(24, 50, 74, 0.02), transparent 40%, rgba(15, 139, 141, 0.04));
        pointer-events: none;
    }}
    h1, h2, h3, p, ul, ol, table, blockquote, div {{ position: relative; z-index: 1; }}
    h1 {{
        margin: 0 0 18px;
        font-size: 2.4em;
        line-height: 1.02;
        letter-spacing: -0.04em;
        color: var(--navy);
    }}
    h2 {{
        margin: 0 0 14px;
        font-size: 1.45em;
        line-height: 1.1;
        color: var(--teal);
    }}
    h3 {{
        margin: 0 0 10px;
        font-size: 1em;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
    }}
    p {{ margin: 0 0 12px; line-height: 1.42; }}
    ul, ol {{ margin: 0; padding-left: 28px; }}
    li {{ margin: 8px 0; line-height: 1.4; }}
    blockquote {{
        margin: 16px 0;
        padding: 16px 20px;
        border-left: 6px solid var(--teal);
        background: rgba(15, 139, 141, 0.08);
        color: var(--navy);
        font-weight: 600;
    }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 0.74em; }}
    th, td {{ border: 1px solid var(--line); padding: 12px 14px; vertical-align: top; text-align: left; }}
    th {{ background: #e8dccd; color: var(--navy); font-size: 0.95em; }}
    td {{ background: rgba(255, 255, 255, 0.46); }}
    pre {{
        margin: 14px 0 0;
        padding: 18px 20px;
        border-radius: 18px;
        background: #1a2330;
        color: #ecf3ff;
        overflow-x: auto;
    }}
    code {{
        font-family: Menlo, Monaco, Consolas, monospace;
        font-size: 0.88em;
        background: rgba(24, 50, 74, 0.08);
        padding: 2px 6px;
        border-radius: 6px;
    }}
    pre code {{ background: transparent; padding: 0; color: inherit; }}
    a {{ color: var(--teal); text-decoration: none; }}
    .spacer {{ height: 10px; }}
    .eyebrow {{
        display: inline-block;
        margin-bottom: 18px;
        padding: 8px 12px;
        border-radius: 999px;
        background: rgba(24, 50, 74, 0.08);
        color: var(--navy);
        font-size: 0.68em;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}
    .hero-panel {{
        height: 100%;
        margin: -52px -58px -62px;
        padding: 62px 64px;
        background:
            radial-gradient(circle at 82% 18%, rgba(255,255,255,0.14), transparent 18%),
            linear-gradient(135deg, #19344c 0%, #0f4d63 52%, #0f8b8d 100%);
        color: #fffaf2;
        display: grid;
        grid-template-columns: 1.3fr 0.9fr;
        gap: 32px;
    }}
    .hero-panel h1, .hero-panel h2, .hero-panel h3, .hero-panel p {{ color: inherit; }}
    .hero-panel h1 {{ font-size: 3.2em; margin-bottom: 18px; }}
    .hero-panel h2 {{ font-size: 1.35em; color: #d7f5f2; margin-bottom: 18px; }}
    .hero-note {{ font-size: 0.84em; color: rgba(255,250,242,0.9); max-width: 780px; }}
    .hero-stats {{ display: grid; grid-template-columns: 1fr; gap: 14px; align-content: end; }}
    .stat-card {{
        padding: 18px 20px;
        border-radius: 22px;
        background: rgba(255,255,255,0.12);
        backdrop-filter: blur(6px);
        border: 1px solid rgba(255,255,255,0.18);
    }}
    .stat-card .label {{ font-size: 0.68em; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.82; }}
    .stat-card .value {{ font-size: 1.72em; font-weight: 800; line-height: 1.05; margin-top: 8px; }}
    .stat-card .sub {{ font-size: 0.72em; margin-top: 4px; opacity: 0.9; }}
    .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: start; }}
    .two-col.wide-left {{ grid-template-columns: 1.2fr 0.8fr; }}
    .two-col.wide-right {{ grid-template-columns: 0.82fr 1.18fr; }}
    .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }}
    .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }}
    .card {{
        padding: 18px 20px;
        border-radius: 22px;
        background: rgba(255,255,255,0.72);
        border: 1px solid rgba(24, 50, 74, 0.08);
    }}
    .card.tint {{ background: linear-gradient(180deg, rgba(15,139,141,0.12), rgba(255,255,255,0.72)); }}
    .card.warn {{ background: linear-gradient(180deg, rgba(217,93,57,0.12), rgba(255,255,255,0.74)); }}
    .card.soft {{ background: linear-gradient(180deg, rgba(24,50,74,0.06), rgba(255,255,255,0.72)); }}
    .card h3 {{ margin-bottom: 8px; }}
    .card p:last-child, .card ul:last-child {{ margin-bottom: 0; }}
    .mini {{ font-size: 0.74em; color: var(--muted); }}
    .code-note {{ margin-top: 10px; }}
    .code-note strong {{ color: var(--navy); }}
    .big-number {{ font-size: 2.4em; font-weight: 800; color: var(--navy); line-height: 1; }}
    .result-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 8px; }}
    .metric {{ padding: 20px; border-radius: 22px; background: #ffffffc9; border: 1px solid rgba(24, 50, 74, 0.08); }}
    .metric .value {{ font-size: 2em; font-weight: 800; color: var(--navy); }}
    .metric .label {{ font-size: 0.68em; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }}
    .metric.good .value {{ color: var(--green); }}
    .metric.bad .value {{ color: var(--red); }}
    .metric.warn .value {{ color: var(--amber); }}
    .bar-row {{ display: grid; grid-template-columns: 220px 1fr 78px; gap: 12px; align-items: center; margin: 12px 0; }}
    .bar-label {{ font-weight: 700; color: var(--navy); font-size: 0.78em; }}
    .bar-track {{ height: 18px; border-radius: 999px; background: #dfd2c1; overflow: hidden; position: relative; }}
    .bar-fill {{ height: 100%; border-radius: 999px; }}
    .fill-teal {{ background: linear-gradient(90deg, #0f8b8d, #30b4b7); }}
    .fill-red {{ background: linear-gradient(90deg, #d95d39, #eb8a63); }}
    .fill-amber {{ background: linear-gradient(90deg, #c88a04, #edbf52); }}
    .bar-value {{ font-weight: 800; color: var(--navy); font-size: 0.8em; text-align: right; }}
    .screenshot-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 12px; }}
    .shot-card {{
        background: rgba(255,255,255,0.84);
        border: 1px solid rgba(24, 50, 74, 0.08);
        border-radius: 22px;
        overflow: hidden;
    }}
    .shot-card img {{ width: 100%; height: 300px; object-fit: cover; object-position: top; display: block; }}
    .shot-caption {{ padding: 14px 16px 16px; }}
    .shot-caption strong {{ color: var(--navy); }}
    .pill-row {{ display: flex; gap: 10px; flex-wrap: wrap; margin: 12px 0 0; }}
    .pill {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 0.68em;
        font-weight: 700;
        letter-spacing: 0.04em;
        background: #ffffffa8;
        border: 1px solid rgba(24, 50, 74, 0.08);
        color: var(--navy);
    }}
    .pill.good {{ background: rgba(45, 143, 91, 0.14); color: #17633d; }}
    .pill.bad {{ background: rgba(217, 93, 57, 0.14); color: #8c2f14; }}
    .pill.warn {{ background: rgba(200, 138, 4, 0.16); color: #7b5200; }}
    .flow {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-top: 18px; }}
    .flow-step {{ padding: 18px; border-radius: 20px; background: rgba(255,255,255,0.78); border: 1px solid rgba(24, 50, 74, 0.08); }}
    .flow-step .n {{ font-size: 0.72em; color: var(--teal); font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; }}
    .flow-step .t {{ font-size: 1em; font-weight: 800; color: var(--navy); margin: 6px 0 8px; }}
    .footer-note {{ position: absolute; left: 58px; right: 58px; bottom: 24px; font-size: 0.63em; color: var(--muted); }}
    .slide-num {{ position: absolute; right: 28px; bottom: 20px; font-size: 0.64em; color: rgba(24, 50, 74, 0.42); z-index: 2; }}
    .summary-strip {{ display: grid; grid-template-columns: 1.2fr 0.9fr 0.9fr; gap: 18px; margin-top: 16px; }}
    .quote-box {{ padding: 24px; border-radius: 24px; background: #18324a; color: #fffaf2; }}
    .quote-box p {{ color: inherit; }}
    .quote-box .mini {{ color: rgba(255,250,242,0.82); }}
    @media print {{
        body {{ background: #ffffff; }}
        .slide {{ margin: 0; box-shadow: none; }}
    }}
    @page {{ size: 1365px 768px; margin: 0; }}
</style>
</head>
<body>
{''.join(slide_divs)}
<script>
    const slides = document.querySelectorAll('.slide');
    slides.forEach((slide, index) => {{
        const num = document.createElement('div');
        num.className = 'slide-num';
        num.textContent = `${{index + 1}} / ${{slides.length}}`;
        slide.appendChild(num);
    }});
</script>
</body>
</html>"""

OUT.write_text(html_out, encoding="utf-8")
print(f"Generated {OUT}")
print(f"Slides: {len(slide_divs)}")
