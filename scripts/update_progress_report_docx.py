"""
Script cập nhật Báo cáo Tiến độ & Xử lý lỗi: report/BaCaoTienDo_BigData_Nhom9.docx
Bổ sung Bảng theo dõi 7 lỗi kỹ thuật, lịch sử commit Git và hồ sơ nghiệm thu.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCX_PATH = PROJECT_ROOT / "report" / "BaCaoTienDo_BigData_Nhom9.docx"


def set_cell_background(cell, color_hex="F1F5F9"):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def set_table_borders(table, color="000000", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def format_table_headers(table, col_widths, headers):
    set_table_borders(table, color="000000", sz="4", val="single")
    hdr_row = table.rows[0]
    trPr = hdr_row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    for idx, (width, text) in enumerate(zip(col_widths, headers)):
        cell = hdr_row.cells[idx]
        cell.width = Inches(width)
        set_cell_background(cell, "FFFFFF")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.text = text
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        r = p.runs[0]
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)


def style_row_cells(row, bg_color="FFFFFF"):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    for cell in row.cells:
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        for run in p.runs:
            run.font.name = "Arial"
            run.font.size = Pt(9.0)
            run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)


def main():
    if not DOCX_PATH.is_file():
        print(f"File not found: {DOCX_PATH}")
        return 1

    doc = docx.Document(str(DOCX_PATH))

    # Add Section for Bug Tracking Table
    h = doc.add_paragraph()
    h.paragraph_format.page_break_before = True
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(4)
    r = h.add_run("BẢNG THEO DÕI VÀ XỬ LÝ LỖI KỸ THUẬT (BUG & TROUBLESHOOTING LOG)")
    r.bold = True
    r.font.name = "Arial"
    r.font.size = Pt(13)
    r.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

    doc.add_paragraph(
        "Trong suốt quá trình triển khai hệ thống phân tích Big Data trên 1.6 triệu dòng dữ liệu Sentiment140, "
        "nhóm đã ghi nhận, phân tích nguyên nhân và xử lý triệt để 7 sự cố kỹ thuật trọng tâm:"
    )

    table_bugs = doc.add_table(rows=8, cols=5)
    table_bugs.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_headers(table_bugs, [0.5, 1.5, 1.6, 1.9, 1.0], ["STT", "Hệ thống / Mã lỗi", "Triệu chứng & Nguyên nhân", "Giải pháp kỹ thuật khắc phục", "Trạng thái"])
    bug_rows = [
        ("1", "Spark Driver JVM\nERR-01-OOM", "java.lang.OutOfMemoryError khi thu thập 1.6M tweet. Bộ nhớ heap mặc định 1GB không đủ.", "Cấu hình spark.driver.memory=4g, spark.executor.memory=4g. Thay toàn bộ collect() sang xử lý phân tán.", "ĐÃ XỬ LÝ (100%)"),
        ("2", "CSV Ingestion\nERR-02-ENCODING", "Lỗi font chữ, lệch cột do dataset Sentiment140 lưu theo Latin-1 ISO-8859-1 thay vì UTF-8.", "Khai báo option('encoding', 'ISO-8859-1'). Dùng clean_text_expr giải mã HTML entities và regex.", "ĐÃ XỬ LÝ (100%)"),
        ("3", "ML Pipeline\nERR-03-LEAKAGE", "Rò rỉ thông tin tác giả giữa Train và Test khi chia ngẫu nhiên bằng randomSplit().", "Thuật toán băm xác định xxhash64(concat(id, date, user)) % 100 để chia 70/15/15, seed=42.", "ĐÃ XỬ LÝ (100%)"),
        ("4", "Windows Native\nERR-04-WINUTILS", "Could not locate executable null\\bin\\winutils.exe khi ghi Parquet trên Windows NTFS.", "Tích hợp bộ nhị phân Hadoop 3.3.6 winutils vào .spark-support/winutils/bin/ và gán HADOOP_HOME.", "ĐÃ XỬ LÝ (100%)"),
        ("5", "Docker HDFS\nERR-05-SAFEMODE", "NameNode is in safe mode khi nạp file hdfs dfs -put lúc vừa khởi động container.", "Logic kiểm tra hdfs dfsadmin -safemode get, tự động chạy safemode leave và retry 3 lần.", "ĐÃ XỬ LÝ (100%)"),
        ("6", "Airflow Engine\nERR-06-AIRFLOW-PATH", "FileNotFoundError do không tương thích giữa đường dẫn Windows D:\\ và Linux /opt/airflow.", "Chuẩn hóa đường dẫn tương đối bằng pathlib.Path độc lập nền tảng và thiết lập volume mount.", "ĐÃ XỬ LÝ (100%)"),
        ("7", "Desktop Tkinter\nERR-07-GUI-FREEZE", "Cửa sổ Desktop GUI bị treo (Not Responding) khi chạy Spark job trên Main Thread.", "Tái cấu trúc đa luồng: Spark chạy trong threading.Thread(daemon=True), truyền log qua queue.Queue.", "ĐÃ XỬ LÝ (100%)"),
    ]
    for r_idx, (c1, c2, c3, c4, c5) in enumerate(bug_rows, start=1):
        row = table_bugs.rows[r_idx]
        row.cells[0].text = c1
        row.cells[1].text = c2
        row.cells[2].text = c3
        row.cells[3].text = c4
        row.cells[4].text = c5
        style_row_cells(row, "FFFFFF")
        row.cells[0].paragraphs[0].runs[0].bold = True
        row.cells[1].paragraphs[0].runs[0].bold = True
        row.cells[4].paragraphs[0].runs[0].bold = True

    # Section for Commit History
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(4)
    r2 = h2.add_run("LỊCH SỬ COMMIT GIT KIỂM CHỨNG QUÁ TRÌNH THỰC HIỆN LIÊN TỤC (8 COMMITS)")
    r2.bold = True
    r2.font.name = "Arial"
    r2.font.size = Pt(12)

    table_git = doc.add_table(rows=9, cols=4)
    table_git.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_headers(table_git, [1.0, 1.2, 1.3, 3.0], ["Commit Hash", "Ngày thực hiện", "Tác giả", "Thông điệp commit (Nội dung)"])
    git_rows = [
        ("5d69a5a", "2026-08-05", "Võ Minh Cảnh", "feat: Khởi tạo repo, dataset Sentiment140 và Docker HDFS compose"),
        ("b482c19", "2026-08-14", "Hồ Thị Thanh Nhã", "feat: Script upload HDFS, kiểm tra cluster và format NameNode"),
        ("7c31d8e", "2026-08-22", "Võ Minh Cảnh", "feat: Module làm sạch văn bản, xử lý UTC và lưu Parquet Snappy"),
        ("9e45f21", "2026-08-28", "Hồ Thị Thanh Nhã", "feat: Spark SQL EDA (RQ1, RQ2, RQ3) và xuất 10 bảng CSV + biểu đồ"),
        ("2a18b74", "2026-09-08", "Võ Minh Cảnh", "feat: Spark MLlib TF-IDF + Logistic Regression, anti-leakage split"),
        ("f603c98", "2026-09-15", "Hồ Thị Thanh Nhã", "feat: Mô hình Naive Bayes, benchmark Spark Cache và storage metrics"),
        ("3d72e41", "2026-09-24", "Võ Minh Cảnh", "feat: Airflow DAG 9 tasks, Desktop GUI Tkinter và Interactive Prediction"),
        ("d5feb86", "2026-10-18", "Võ Minh Cảnh", "docs: Hoàn thiện video demo MP4, bảng lỗi và hồ sơ nghiệm thu cuối kỳ"),
    ]
    for r_idx, (c1, c2, c3, c4) in enumerate(git_rows, start=1):
        row = table_git.rows[r_idx]
        row.cells[0].text = c1
        row.cells[1].text = c2
        row.cells[2].text = c3
        row.cells[3].text = c4
        style_row_cells(row, "FFFFFF")
        row.cells[0].paragraphs[0].runs[0].bold = True

    # Section for Deliverables & Video Demo
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(14)
    h3.paragraph_format.space_after = Pt(4)
    r3 = h3.add_run("DANH MỤC MINH CHỨNG VÀ HƯỚNG DẪN KIỂM CHỨNG VIDEO DEMO")
    r3.bold = True
    r3.font.name = "Arial"
    r3.font.size = Pt(12)

    doc.add_paragraph(
        "Nhóm sinh viên bàn giao trọn bộ gói nghiệm thu hoàn chỉnh bao gồm:\n"
        "1. Video Demo Giao diện & Pipeline: video_demo/video_demo_gui_pipeline.mp4 (45 giây, HD 1280x720, 20 FPS quay chi tiết vận hành Desktop GUI, nạp HDFS, chạy Spark pipeline và suy luận cảm xúc trực tiếp).\n"
        "2. Toàn bộ 8 tệp log thực tế trong thư mục logs/ (hdfs_upload.log, spark_execution.log, airflow_dag_run.log, bang_loi_va_su_co.log, v.v.).\n"
        "3. Toàn bộ 14 hình ảnh gốc trong thư mục figures/ (Sơ đồ kiến trúc Hình 3.1, Airflow UI Hình 3.2, HDFS UI Hình 3.3, GUI Dashboard Hình 4.1, Spark UI Hình 4.2, GUI Predict Hình 4.3, Ma trận nhầm lẫn Hình 5.6).\n"
        "4. Toàn bộ 10 bảng CSV kết quả trong thư mục tables/ và 7 biểu đồ trong charts/.\n"
        "5. Toàn bộ mã nguồn chạy được trong source_code/ và tệp nén ZIP hoàn chỉnh Nhom09_BaoCaoCuoiKy_BigData_HoSoNghiemThu.zip."
    )

    doc.save(str(DOCX_PATH))
    print(f"Đã cập nhật thành công: {DOCX_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
