"""
Script biên dịch Báo cáo cuối kỳ Markdown sang HTML và PDF chuẩn
Nhóm thực hiện: Nhóm 09 (Võ Minh Cảnh & Hồ Thị Thanh Nhã)
Sử dụng Microsoft Edge Headless engine để xuất PDF chất lượng cao.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

try:
    if sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MD_PATH = PROJECT_ROOT / "report" / "bao_cao_cuoi_ky.md"
HTML_PATH = PROJECT_ROOT / "report" / "BaoCaoCuoiKy_BigData_Nhom9.html"
PDF_PATH = PROJECT_ROOT / "report" / "BaoCaoCuoiKy_BigData_Nhom9.pdf"
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def markdown_to_html(md_text: str) -> str:
    lines = md_text.splitlines()
    html_lines = []
    in_code_block = False
    in_table = False
    table_lines = []

    def flush_table():
        nonlocal in_table, table_lines
        if not table_lines:
            in_table = False
            return
        
        # Build HTML table
        res = ["<div class='table-wrapper'><table>"]
        header_parsed = False
        
        for idx, line in enumerate(table_lines):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if idx == 1 and all(set(c).issubset({"-", ":", " "}) for c in cells):
                # separator line
                continue
            
            if not header_parsed:
                res.append("<thead><tr>")
                for c in cells:
                    res.append(f"<th>{inline_formatting(c)}</th>")
                res.append("</tr></thead><tbody>")
                header_parsed = True
            else:
                res.append("<tr>")
                for c in cells:
                    res.append(f"<td>{inline_formatting(c)}</td>")
                res.append("</tr>")
                
        if header_parsed:
            res.append("</tbody>")
        res.append("</table></div>")
        html_lines.append("\n".join(res))
        table_lines = []
        in_table = False

    def inline_formatting(text: str) -> str:
        # Images: ![alt](url)
        text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<div class="img-container"><img src="\2" alt="\1" /><p class="caption">\1</p></div>', text)
        # Links: [text](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        # Bold: **text**
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        # Italic: *text*
        text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
        # Inline code: `code`
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        return text

    for line in lines:
        stripped = line.strip()

        # Code block
        if stripped.startswith("```"):
            if in_table:
                flush_table()
            if in_code_block:
                html_lines.append("</code></pre>")
                in_code_block = False
            else:
                lang = stripped[3:].strip()
                html_lines.append(f"<pre><code class='language-{lang}'>")
                in_code_block = True
            continue

        if in_code_block:
            safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            html_lines.append(safe_line)
            continue

        # Tables
        if "|" in line and (line.strip().startswith("|") or line.strip().endswith("|")):
            in_table = True
            table_lines.append(line)
            continue
        elif in_table:
            flush_table()

        # Horizontal Rule
        if stripped in ("---", "***", "___"):
            html_lines.append("<hr />")
            continue

        # Headings
        if stripped.startswith("# "):
            html_lines.append(f"<h1 class='title-main'>{inline_formatting(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            html_lines.append(f"<h2>{inline_formatting(stripped[3:])}</h2>")
        elif stripped.startswith("### "):
            html_lines.append(f"<h3>{inline_formatting(stripped[4:])}</h3>")
        elif stripped.startswith("#### "):
            html_lines.append(f"<h4>{inline_formatting(stripped[5:])}</h4>")
        # Unordered list
        elif stripped.startswith("- ") or stripped.startswith("* "):
            content = stripped[2:]
            html_lines.append(f"<ul><li>{inline_formatting(content)}</li></ul>")
        # Ordered list
        elif re.match(r'^\d+\.\s', stripped):
            content = re.sub(r'^\d+\.\s', '', stripped)
            html_lines.append(f"<ol><li>{inline_formatting(content)}</li></ol>")
        # Empty line
        elif not stripped:
            html_lines.append("<p class='spacing'></p>")
        else:
            html_lines.append(f"<p>{inline_formatting(line)}</p>")

    if in_table:
        flush_table()
    if in_code_block:
        html_lines.append("</code></pre>")

    # Merge adjacent lists
    full_html = "\n".join(html_lines)
    full_html = re.sub(r'</ul>\s*<ul>', '', full_html)
    full_html = re.sub(r'</ol>\s*<ol>', '', full_html)
    return full_html


def build_complete_html(content_html: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Báo Cáo Cuối Kỳ — Nhóm 09 — Big Data</title>
<style>
    @page {{
        size: A4;
        margin: 20mm 18mm 20mm 18mm;
        @bottom-center {{
            content: counter(page);
        }}
    }}
    body {{
        font-family: 'Times New Roman', Times, serif, 'Segoe UI';
        font-size: 13pt;
        line-height: 1.45;
        color: #111827;
        margin: 0;
        padding: 0;
        background: #fff;
    }}
    h1.title-main {{
        font-size: 18pt;
        text-align: center;
        color: #1E3A8A;
        text-transform: uppercase;
        margin-top: 10px;
        margin-bottom: 8px;
    }}
    h2 {{
        font-size: 14pt;
        color: #1E40AF;
        border-bottom: 1.5px solid #CBD5E1;
        padding-bottom: 4px;
        margin-top: 24px;
        margin-bottom: 10px;
        page-break-after: avoid;
    }}
    h3 {{
        font-size: 13pt;
        color: #0F766E;
        margin-top: 16px;
        margin-bottom: 6px;
        page-break-after: avoid;
    }}
    h4 {{
        font-size: 12pt;
        color: #334155;
        margin-top: 12px;
        margin-bottom: 4px;
    }}
    p {{
        text-align: justify;
        margin: 6px 0;
        text-indent: 1.2cm;
    }}
    p.spacing {{
        margin: 4px 0;
    }}
    strong {{
        color: #0F172A;
    }}
    hr {{
        border: 0;
        border-top: 1px solid #CBD5E1;
        margin: 16px 0;
    }}
    .table-wrapper {{
        margin: 14px 0;
        width: 100%;
        page-break-inside: avoid;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 11pt;
        margin: auto;
    }}
    th, td {{
        border: 1px solid #94A3B8;
        padding: 6px 10px;
        text-align: left;
    }}
    th {{
        background-color: #F1F5F9;
        color: #1E293B;
        font-weight: bold;
        text-align: center;
    }}
    tr:nth-child(even) {{
        background-color: #F8FAFC;
    }}
    pre {{
        background-color: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-left: 4px solid #2563EB;
        padding: 10px 14px;
        font-family: Consolas, 'Courier New', monospace;
        font-size: 10pt;
        overflow-x: auto;
        white-space: pre-wrap;
        margin: 12px 0;
        page-break-inside: avoid;
    }}
    code {{
        font-family: Consolas, 'Courier New', monospace;
        background-color: #F1F5F9;
        padding: 2px 4px;
        border-radius: 3px;
        font-size: 10.5pt;
    }}
    .img-container {{
        text-align: center;
        margin: 16px auto;
        page-break-inside: avoid;
    }}
    .img-container img {{
        max-width: 92%;
        height: auto;
        border: 1px solid #E2E8F0;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
    }}
    p.caption {{
        text-align: center;
        font-style: italic;
        font-size: 11pt;
        color: #475569;
        margin-top: 4px;
        text-indent: 0;
    }}
    ul, ol {{
        margin: 6px 0;
        padding-left: 28px;
    }}
    li {{
        margin: 4px 0;
    }}
</style>
</head>
<body>
{content_html}
</body>
</html>"""


def generate_pdf():
    print(f"Đọc nội dung báo cáo từ: {MD_PATH}")
    md_text = MD_PATH.read_text(encoding="utf-8")
    
    html_content = markdown_to_html(md_text)
    full_html = build_complete_html(html_content)
    
    HTML_PATH.write_text(full_html, encoding="utf-8")
    print(f"Đã xuất tệp HTML trung gian tại: {HTML_PATH}")
    
    if os.path.exists(EDGE_EXE):
        print("Đang biên dịch tệp PDF bằng Microsoft Edge Headless Engine...")
        cmd = [
            EDGE_EXE,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={PDF_PATH}",
            str(HTML_PATH),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and PDF_PATH.exists():
            print(f"XUẤT BÁO CÁO PDF THÀNH CÔNG: {PDF_PATH} ({PDF_PATH.stat().st_size / (1024*1024):.2f} MB)")
            return 0
        else:
            print(f"Lỗi khi xuất PDF qua Edge: {res.stderr}")
            return 1
    else:
        print(f"Không tìm thấy Edge tại {EDGE_EXE}. Đã lưu tệp HTML sẵn sàng in ra PDF.")
        return 0


if __name__ == "__main__":
    sys.exit(generate_pdf())
