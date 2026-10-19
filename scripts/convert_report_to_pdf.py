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
    is_first_h1 = True

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
        # Images: ![alt](url) - không lặp caption vì markdown đã có dòng in đậm caption bên dưới
        text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<div class="img-container"><img src="\2" alt="\1" /></div>', text)
        # Links: [text](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        # Bold: **text**
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        # Italic: *text*
        text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
        # Inline code: `code`
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        return text

    in_blockquote = False
    blockquote_lines = []

    def flush_blockquote():
        nonlocal in_blockquote, blockquote_lines
        if not blockquote_lines:
            in_blockquote = False
            return
        res = ["<div class='callout-box'>"]
        for bq_l in blockquote_lines:
            if bq_l.startswith("[!"):
                continue
            if bq_l.startswith("- ") or bq_l.startswith("* "):
                res.append(f"<ul><li>{inline_formatting(bq_l[2:])}</li></ul>")
            else:
                res.append(f"<p>{inline_formatting(bq_l)}</p>")
        res.append("</div>")
        full_bq = "\n".join(res)
        full_bq = re.sub(r'</ul>\s*<ul>', '', full_bq)
        html_lines.append(full_bq)
        blockquote_lines = []
        in_blockquote = False

    for line in lines:
        stripped = line.strip()

        # Blockquote lines
        if stripped.startswith(">"):
            if in_table:
                flush_table()
            in_blockquote = True
            bq_content = stripped[1:].strip()
            if bq_content:
                blockquote_lines.append(bq_content)
            continue
        elif in_blockquote:
            flush_blockquote()

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

        # Horizontal Rule - bỏ toàn bộ gạch ngang phân cách theo yêu cầu
        if stripped in ("---", "***", "___"):
            continue

        # Headings
        if stripped.startswith("# "):
            title_text = inline_formatting(stripped[2:])
            if is_first_h1:
                html_lines.append(f"<h1 class='title-main'>{title_text}</h1>")
                is_first_h1 = False
            else:
                html_lines.append(f"<h1 class='chapter-title'>{title_text}</h1>")
        elif stripped.startswith("## "):
            sec_title = stripped[3:].strip()
            if sec_title.upper() == "MỤC LỤC":
                html_lines.append(f"<h2 class='toc-break'>{inline_formatting(sec_title)}</h2>")
            else:
                html_lines.append(f"<h2>{inline_formatting(sec_title)}</h2>")
        elif stripped.startswith("### "):
            html_lines.append(f"<h3>{inline_formatting(stripped[4:])}</h3>")
        elif stripped.startswith("#### "):
            html_lines.append(f"<h4>{inline_formatting(stripped[5:])}</h4>")
        # Captions for images and tables
        elif stripped.startswith("**Hình ") or stripped.startswith("*Hình ") or stripped.startswith("**Bảng ") or stripped.startswith("*Bảng "):
            html_lines.append(f"<p class='caption'>{inline_formatting(stripped)}</p>")
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
    if in_blockquote:
        flush_blockquote()
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
        color: #000000;
        margin: 0;
        padding: 0;
        background: #fff;
    }}
    h1.title-main {{
        font-size: 18pt;
        text-align: center;
        color: #000000;
        text-transform: uppercase;
        margin-top: 10px;
        margin-bottom: 8px;
    }}
    h1.chapter-title {{
        font-size: 15pt;
        color: #000000;
        text-transform: uppercase;
        margin-top: 0;
        padding-top: 0;
        margin-bottom: 14px;
        page-break-before: always;
        break-before: page;
        page-break-after: avoid;
        break-after: avoid;
    }}
    h2 {{
        font-size: 13.5pt;
        color: #000000;
        margin-top: 20px;
        margin-bottom: 8px;
        page-break-after: avoid;
        break-after: avoid;
    }}
    h2.toc-break {{
        page-break-before: always;
        break-before: page;
        margin-top: 0;
        padding-top: 0;
    }}
    h3 {{
        font-size: 13pt;
        color: #000000;
        margin-top: 14px;
        margin-bottom: 6px;
        page-break-after: avoid;
        break-after: avoid;
    }}
    h4 {{
        font-size: 12pt;
        color: #000000;
        margin-top: 10px;
        margin-bottom: 4px;
        page-break-after: avoid;
        break-after: avoid;
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
        color: #000000;
    }}
    a {{
        color: #000000;
        text-decoration: underline;
    }}
    hr {{
        display: none;
    }}
    .table-wrapper {{
        margin: 12px 0;
        width: 100%;
        page-break-inside: auto;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 10pt;
        margin: auto;
        background-color: #ffffff;
        border: 1px solid #000000;
        page-break-inside: auto;
    }}
    thead {{
        display: table-header-group;
    }}
    tr {{
        page-break-inside: avoid;
    }}
    th, td {{
        border: 1px solid #000000;
        padding: 5px 8px;
        text-align: left;
        background-color: #ffffff;
        color: #000000;
    }}
    th {{
        background-color: #ffffff;
        color: #000000;
        font-weight: bold;
        text-align: center;
        border: 1px solid #000000;
    }}
    tr, tr:nth-child(even), tr:nth-child(odd) {{
        background-color: #ffffff;
    }}
    table code {{
        background-color: transparent;
        border: none;
        color: #000000;
        font-weight: bold;
    }}
    pre {{
        background-color: #ffffff;
        border: 1px solid #000000;
        border-left: 4px solid #000000;
        padding: 8px 12px;
        font-family: Consolas, 'Courier New', monospace;
        font-size: 9.5pt;
        line-height: 1.35;
        overflow-x: auto;
        white-space: pre-wrap;
        margin: 10px 0;
        page-break-inside: auto;
        color: #000000;
    }}
    code {{
        font-family: Consolas, 'Courier New', monospace;
        background-color: #ffffff;
        color: #000000;
        padding: 1px 3px;
        border: 1px solid #999999;
        border-radius: 2px;
        font-size: 10pt;
    }}
    .img-container {{
        text-align: center;
        margin: 12px auto 4px auto;
        page-break-inside: avoid;
    }}
    .img-container img {{
        max-width: 88%;
        max-height: 460px;
        height: auto;
        border: 1px solid #000000;
        border-radius: 2px;
        box-shadow: none;
    }}
    .callout-box {{
        border: 1px solid #000000;
        border-left: 5px solid #000000;
        background-color: #fafafa;
        padding: 8px 14px;
        margin: 12px 0;
        border-radius: 2px;
        page-break-inside: avoid;
    }}
    .callout-box p {{
        text-indent: 0;
        margin: 4px 0;
        font-size: 11pt;
    }}
    .callout-box ul {{
        margin: 4px 0;
        padding-left: 20px;
        font-size: 11pt;
    }}
    .callout-box li {{
        margin: 2px 0;
    }}
    p.caption {{
        text-align: center;
        font-weight: bold;
        font-size: 10.5pt;
        color: #000000;
        margin-top: 6px;
        margin-bottom: 10px;
        text-indent: 0;
        page-break-before: avoid;
        break-before: avoid;
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
    # Đồng bộ toàn bộ ảnh từ figures/ sang report/figures/
    report_fig_dir = PROJECT_ROOT / "report" / "figures"
    report_fig_dir.mkdir(parents=True, exist_ok=True)
    root_fig_dir = PROJECT_ROOT / "figures"
    if root_fig_dir.exists():
        import shutil
        for f in root_fig_dir.glob("*.png"):
            shutil.copy2(f, report_fig_dir / f.name)

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
