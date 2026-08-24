import re, os

md_path = r"d:\ff\explainer\theory_explainer.md"
html_path = r"d:\ff\explainer\theory_explainer.html"

with open(md_path, "r", encoding="utf-8") as f:
    text = f.read()

# ── very small Markdown → HTML converter ──────────────────────────────────────
def md_to_html(md):
    lines = md.split("\n")
    html_lines = []
    in_table = False
    in_ul = False
    in_code = False
    code_buf = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Fenced code block
        if line.strip().startswith("```"):
            if not in_code:
                in_code = True
                code_buf = []
            else:
                in_code = False
                code_content = "\n".join(code_buf)
                html_lines.append(f'<pre><code>{code_content}</code></pre>')
            i += 1
            continue
        if in_code:
            code_buf.append(line.replace("<", "&lt;").replace(">", "&gt;"))
            i += 1
            continue

        # Table row
        if line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            # Skip separator rows
            if all(re.match(r"^[-:]+$", c) for c in cells if c):
                i += 1
                continue
            if not in_table:
                in_table = True
                html_lines.append('<table>')
                row_tag = "th"
            else:
                row_tag = "td"
            row_html = "".join(f"<{row_tag}>{c}</{row_tag}>" for c in cells)
            html_lines.append(f"<tr>{row_html}</tr>")
            i += 1
            continue
        else:
            if in_table:
                html_lines.append('</table>')
                in_table = False

        # Headings
        if line.startswith("#### "):
            html_lines.append(f"<h4>{inline(line[5:])}</h4>"); i += 1; continue
        if line.startswith("### "):
            html_lines.append(f"<h3>{inline(line[4:])}</h3>"); i += 1; continue
        if line.startswith("## "):
            html_lines.append(f"<h2>{inline(line[3:])}</h2>"); i += 1; continue
        if line.startswith("# "):
            html_lines.append(f"<h1>{inline(line[2:])}</h1>"); i += 1; continue

        # Horizontal rule
        if line.strip() in ("---", "***", "___"):
            html_lines.append("<hr>"); i += 1; continue

        # Blockquote
        if line.startswith("> "):
            html_lines.append(f"<blockquote>{inline(line[2:])}</blockquote>"); i += 1; continue

        # Bullet list
        if re.match(r"^[\*\-] ", line):
            if not in_ul:
                in_ul = True
                html_lines.append("<ul>")
            html_lines.append(f"<li>{inline(line[2:])}</li>")
            i += 1
            continue
        else:
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False

        # Empty line
        if line.strip() == "":
            html_lines.append("<br>"); i += 1; continue

        # Paragraph
        html_lines.append(f"<p>{inline(line)}</p>")
        i += 1

    if in_table: html_lines.append("</table>")
    if in_ul:    html_lines.append("</ul>")
    return "\n".join(html_lines)


def inline(text):
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    # Links
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    return text


body = md_to_html(text)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AI-Native LEO Satellite Network — Theory Explainer</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono&display=swap');

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    line-height: 1.7;
    color: #1a1a2e;
    background: #ffffff;
    padding: 48px 60px;
    max-width: 860px;
    margin: auto;
  }}

  h1 {{
    font-size: 24px;
    font-weight: 700;
    color: #0d0d2b;
    border-bottom: 3px solid #00b4d8;
    padding-bottom: 10px;
    margin-bottom: 20px;
    margin-top: 30px;
  }}

  h2 {{
    font-size: 17px;
    font-weight: 700;
    color: #0077b6;
    margin-top: 28px;
    margin-bottom: 8px;
    border-left: 4px solid #00b4d8;
    padding-left: 10px;
  }}

  h3 {{
    font-size: 14px;
    font-weight: 600;
    color: #023e8a;
    margin-top: 18px;
    margin-bottom: 6px;
  }}

  h4 {{
    font-size: 13px;
    font-weight: 600;
    color: #0077b6;
    margin-top: 12px;
  }}

  p {{
    margin: 6px 0;
    color: #2d2d2d;
  }}

  strong {{ color: #0d0d2b; }}

  code {{
    font-family: 'JetBrains Mono', monospace;
    background: #eef6fb;
    color: #023e8a;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
  }}

  pre {{
    background: #0d1b2a;
    color: #64ffda;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px;
    padding: 16px 20px;
    border-radius: 8px;
    margin: 14px 0;
    overflow-x: auto;
    border-left: 4px solid #00b4d8;
  }}

  pre code {{
    background: none;
    color: inherit;
    padding: 0;
    font-size: inherit;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 12px;
  }}

  th {{
    background: #0077b6;
    color: white;
    padding: 8px 12px;
    text-align: left;
    font-weight: 600;
  }}

  td {{
    padding: 7px 12px;
    border-bottom: 1px solid #dee2e6;
    color: #2d2d2d;
  }}

  tr:nth-child(even) td {{ background: #f0f8ff; }}

  blockquote {{
    border-left: 4px solid #00b4d8;
    background: #e8f7fc;
    padding: 10px 16px;
    margin: 14px 0;
    border-radius: 0 6px 6px 0;
    font-style: italic;
    color: #023e8a;
  }}

  ul {{
    padding-left: 22px;
    margin: 8px 0;
  }}

  li {{
    margin: 4px 0;
    color: #2d2d2d;
  }}

  hr {{
    border: none;
    border-top: 2px solid #bee9f5;
    margin: 28px 0;
  }}

  br {{ display: block; margin: 4px 0; content: ""; }}

  a {{ color: #0077b6; text-decoration: none; }}

  @media print {{
    body {{ padding: 20px 30px; }}
    h1 {{ page-break-before: auto; }}
    pre, table, blockquote {{ page-break-inside: avoid; }}
  }}
</style>
</head>
<body>
{body}
<div style="margin-top:48px; border-top:2px solid #bee9f5; padding-top:12px; font-size:11px; color:#888; text-align:center;">
  AI-Native LEO Satellite Digital Twin · Intent-Aware Cognitive Swarm Q-Routing Simulation
</div>
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"HTML written to: {html_path}")
