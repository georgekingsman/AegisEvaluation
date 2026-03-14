#!/usr/bin/env python3
"""
将 Marp Markdown slides 转为可在浏览器打印成 PDF 的 HTML 演示文稿。
用法：python3 slides/convert_to_html.py
输出：slides/aegis_evaluation.html  （浏览器打开 → Cmd+P → 另存为 PDF）
"""
import re
import pathlib

SRC = pathlib.Path(__file__).parent / "aegis_evaluation.md"
OUT = pathlib.Path(__file__).parent / "aegis_evaluation.html"

raw = SRC.read_text(encoding="utf-8")

# 去掉 front-matter
raw = re.sub(r'^---\n.*?---\n', '', raw, count=1, flags=re.DOTALL)

# 按幻灯片分隔符拆分（--- 单独一行 或 <!-- comment -->）
slides_raw = re.split(r'\n---\n', raw)

def md_to_html(text: str) -> str:
    """极简 Markdown → HTML（适用于幻灯片内容）"""
    lines = text.strip().splitlines()
    out = []
    in_code = False
    in_table = False
    in_ul = False

    for line in lines:
        # 代码块
        if line.startswith("```"):
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                if in_ul: out.append("</ul>"); in_ul = False
                if in_table: out.append("</table>"); in_table = False
                lang = line[3:].strip()
                out.append(f'<pre><code class="language-{lang}">')
                in_code = True
            continue
        if in_code:
            import html
            out.append(html.escape(line))
            continue

        # 表格
        if '|' in line and line.strip().startswith('|'):
            if in_ul: out.append("</ul>"); in_ul = False
            if not in_table:
                out.append('<table>')
                in_table = True
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            # 判断是否为分隔行
            if all(re.match(r'^[-:]+$', c.replace(' ','')) for c in cells if c):
                continue
            # 判断是否为表头：前一行之后紧接分隔行
            tag = 'th' if not any('<td>' in o or '<th>' in o for o in out[-3:]) else 'td'
            # 简单：首行用 th，后续用 td
            row = "".join(f'<{tag}>{inline(c)}</{tag}>' for c in cells)
            out.append(f"<tr>{row}</tr>")
            continue
        else:
            if in_table: out.append("</table>"); in_table = False

        # 列表
        if re.match(r'^[\-\*] ', line):
            if in_ul is False:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline(line[2:])}</li>")
            continue
        elif re.match(r'^\d+\. ', line):
            if in_ul: out.append("</ul>"); in_ul = False
            out.append(f"<li>{inline(re.sub(r'^\d+\. ','',line))}</li>")
            continue
        else:
            if in_ul: out.append("</ul>"); in_ul = False

        # 标题
        m = re.match(r'^(#{1,4})\s+(.*)', line)
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            continue

        # blockquote
        if line.startswith('>'):
            out.append(f"<blockquote>{inline(line[1:].strip())}</blockquote>")
            continue

        # 注释行（<!-- ... -->）
        if line.strip().startswith('<!--'):
            continue

        # 空行
        if not line.strip():
            out.append("<br>")
            continue

        out.append(f"<p>{inline(line)}</p>")

    if in_code: out.append("</code></pre>")
    if in_table: out.append("</table>")
    if in_ul: out.append("</ul>")
    return "\n".join(out)


def inline(text: str) -> str:
    """处理行内元素: bold, italic, code, link"""
    import html as htmllib
    text = htmllib.escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    return text


# 构建完整 HTML
slide_divs = []
for i, s in enumerate(slides_raw):
    s = s.strip()
    if not s:
        continue
    content = md_to_html(s)
    slide_divs.append(f'<section class="slide" id="slide-{i+1}">\n{content}\n</section>')

html_out = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Aegis Security Evaluation</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #060c16;
    color: #e8e8e8;
    font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
    font-size: 14px;
  }}
  .slide {{
    width: 1280px;
    min-height: 720px;
    margin: 20px auto;
    padding: 50px 70px;
    background: #0f1117;
    border: 1px solid #1e2a3a;
    border-radius: 4px;
    page-break-after: always;
    position: relative;
  }}
  h1 {{ color: #4fc3f7; font-size: 1.9em; border-bottom: 2px solid #4fc3f7; padding-bottom: 10px; margin-bottom: 20px; }}
  h2 {{ color: #81d4fa; font-size: 1.3em; margin: 16px 0 8px; }}
  h3 {{ color: #b3e5fc; font-size: 1.1em; margin: 12px 0 6px; }}
  p {{ margin: 8px 0; line-height: 1.6; }}
  br {{ display: block; margin: 4px 0; }}
  code {{ background: #1e2a3a; color: #a5d6a7; padding: 2px 6px; border-radius: 3px; font-family: 'Fira Code', monospace; font-size: 0.88em; }}
  pre {{ background: #1a2333; border: 1px solid #2a3a4a; border-radius: 4px; padding: 16px; margin: 12px 0; overflow-x: auto; }}
  pre code {{ background: none; padding: 0; color: #a5d6a7; font-size: 0.82em; white-space: pre; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.75em; margin: 12px 0; }}
  th {{ background: #1a3a5c; color: #4fc3f7; padding: 8px 10px; text-align: left; }}
  td {{ padding: 6px 10px; border: 1px solid #2a3a4a; vertical-align: top; }}
  tr:nth-child(even) {{ background: #141d2e; }}
  ul {{ padding-left: 20px; margin: 8px 0; }}
  li {{ margin: 4px 0; line-height: 1.5; }}
  blockquote {{ border-left: 4px solid #4fc3f7; padding: 8px 16px; color: #9e9e9e; font-style: italic; margin: 12px 0; background: #0d1520; }}
  a {{ color: #4fc3f7; }}
  strong {{ color: #fff; }}
  .slide-num {{ position: absolute; bottom: 16px; right: 24px; color: #444; font-size: 0.75em; }}

  /* 打印样式 */
  @media print {{
    body {{ background: #060c16; }}
    .slide {{
      width: 100%;
      min-height: 0;
      margin: 0;
      border: none;
      border-radius: 0;
      page-break-after: always;
    }}
  }}
  @page {{ size: 1280px 720px; margin: 0; }}
</style>
</head>
<body>
{''.join(slide_divs)}
<script>
  // 给每张幻灯片加页码
  document.querySelectorAll('.slide').forEach((s, i) => {{
    const total = document.querySelectorAll('.slide').length;
    const n = document.createElement('div');
    n.className = 'slide-num';
    n.textContent = (i+1) + ' / ' + total;
    s.appendChild(n);
  }});
</script>
</body>
</html>"""

OUT.write_text(html_out, encoding="utf-8")
print(f"✅ 已生成: {OUT}")
print(f"   幻灯片数量: {len(slide_divs)}")
print(f"   在浏览器打开后 Cmd+P → 另存为 PDF")
