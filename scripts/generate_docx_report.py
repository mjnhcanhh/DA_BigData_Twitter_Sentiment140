import os
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

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

def add_callout(doc, text, title="LƯU Ý"):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)
    cell = table.cell(0, 0)
    set_cell_background(cell, "F0F4F8")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    # Left border only (thick blue)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="1F4E79"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    run_t = p.add_run(f"[{title}] ")
    run_t.bold = True
    run_t.font.name = "Arial"
    run_t.font.size = Pt(10)
    run_t.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    
    run_b = p.add_run(text)
    run_b.font.name = "Arial"
    run_b.font.size = Pt(10)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def format_table_headers(table, col_widths, headers):
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1F4E79")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=140, right=140)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.bold = True
            r.font.name = "Arial"
            r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            
    for row in table.rows:
        for i, w in enumerate(col_widths):
            row.cells[i].width = Inches(w)

def style_row_cells(row, bg_hex=None):
    for cell in row.cells:
        if bg_hex:
            set_cell_background(cell, bg_hex)
        set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        for p in cell.paragraphs:
            for r in p.runs:
                r.font.name = "Arial"
                r.font.size = Pt(9.5)

def main():
    doc = docx.Document()
    
    # Page Setup: Normal Margins (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = False
        
        # Header & Footer
        header = section.header
        hp = header.paragraphs[0]
        hp.text = "Báo cáo Cuối kỳ Đồ án Big Data — Nhóm 09"
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hp.runs[0].font.name = "Arial"
        hp.runs[0].font.size = Pt(8.5)
        hp.runs[0].font.color.rgb = RGBColor(0x88, 0x88, 0x88)
        
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.text = "Học phần: Nhập môn Big Data • Học kỳ I / 2026-2027"
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fp.runs[0].font.name = "Arial"
        fp.runs[0].font.size = Pt(8.5)
        fp.runs[0].font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    # Base style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Arial'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    normal_style.paragraph_format.line_spacing = 1.2
    normal_style.paragraph_format.space_after = Pt(6)

    # ------------------ COVER / HEADER TITLE ------------------
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("BỘ GIÁO DỤC VÀ ĐÀO TẠO — TRƯỜNG ĐẠI HỌC\nKHOA CÔNG NGHỆ THÔNG TIN")
    r_inst.bold = True
    r_inst.font.size = Pt(11)
    r_inst.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(18)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("BÁO CÁO CUỐI KỲ — ĐỒ ÁN MÔN NHẬP MÔN BIG DATA")
    r_title.bold = True
    r_title.font.size = Pt(18)
    r_title.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(16)
    r_sub = p_sub.add_run("ĐỀ TÀI: PHÂN TÍCH HÀNH VI ĐĂNG BÀI VÀ CẢM XÚC CỦA NGƯỜI DÙNG TRÊN TWITTER BẰNG APACHE SPARK")
    r_sub.bold = True
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = RGBColor(0x2E, 0x75, 0xB6)

    # Info Box Table
    info_table = doc.add_table(rows=5, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_data = [
        ("Học phần:", "Nhập môn Big Data"),
        ("Nhóm thực hiện:", "Nhóm 09"),
        ("Sinh viên thực hiện:", "1. Võ Minh Cảnh — MSSV: 2001230065\n2. Hồ Thị Thanh Nhã — MSSV: 2001230592"),
        ("Bộ dữ liệu nghiên cứu:", "Sentiment140 (1.6 triệu tweet gắn nhãn tự động từ Kaggle)"),
        ("Môi trường thực nghiệm:", "Apache Spark 3.5.7, Hadoop HDFS 3.3.6 (Docker), Python 3.10"),
    ]
    for row_idx, (k, v) in enumerate(info_data):
        row = info_table.rows[row_idx]
        row.cells[0].text = k
        row.cells[1].text = v
        row.cells[0].paragraphs[0].runs[0].bold = True
        set_cell_background(row.cells[0], "F2F2F2")
        style_row_cells(row)
        row.cells[0].width = Inches(2.2)
        row.cells[1].width = Inches(4.3)
    
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(10)
    p_div.paragraph_format.space_after = Pt(10)
    p_div.add_run("_________________________________________________________________________________").font.color.rgb = RGBColor(0xCC, 0xCC, 0xCC)

    # Helper for Headings
    def add_h1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.bold = True
        r.font.name = "Arial"
        r.font.size = Pt(14)
        r.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
        return h

    def add_h2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(3)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.bold = True
        r.font.name = "Arial"
        r.font.size = Pt(12)
        r.font.color.rgb = RGBColor(0x2E, 0x75, 0xB6)
        return h

    # ------------------ PHẦN 1 ------------------
    add_h1("1. MỤC TIÊU VÀ BÀI TOÁN CỦA ĐỒ ÁN")
    
    add_h2("1.1. Bối cảnh và bài toán đặt ra")
    doc.add_paragraph(
        "Mạng xã hội Twitter (hiện nay là X) là một trong những nền tảng giao tiếp trực tuyến hàng đầu, nơi người dùng liên tục "
        "chia sẻ trạng thái, suy nghĩ và cảm xúc theo thời gian thực. Việc khai phá dữ liệu Twitter lịch sử giúp các tổ chức nắm bắt "
        "được phản hồi của công chúng, dự báo xu hướng và phân tích tâm lý người tiêu dùng. "
        "Tuy nhiên, tập dữ liệu mạng xã hội đặt ra bài toán Big Data điển hình:"
    )
    p = doc.add_paragraph()
    p.add_run("• Về khối lượng (Volume): ").bold = True
    p.add_run("Tập dữ liệu Sentiment140 gồm 1,600,000 bài đăng dạng văn bản, gây quá tải bộ nhớ RAM đối với các công cụ đơn máy tính truyền thống như Pandas hay Scikit-learn.\n")
    p.add_run("• Về tính biến thiên và độ nhiễu (Variety): ").bold = True
    p.add_run("Văn bản tweet chứa lượng lớn teencode, hashtag, liên kết URL, thẻ nhắc @user, thực thể HTML lỗi và thời gian ghi nhận ở nhiều múi giờ khác nhau.\n")
    p.add_run("• Về tốc độ xử lý (Velocity / Efficiency): ").bold = True
    p.add_run("Đòi hỏi kiến trúc xử lý song song và tối ưu hóa bộ nhớ đệm (In-memory computing) để huấn luyện mô hình học máy nhanh chóng.")

    add_h2("1.2. Mục tiêu nghiên cứu cụ thể")
    doc.add_paragraph(
        "Đồ án hướng tới các mục tiêu cốt lõi sau:\n"
        "1. Xây dựng hoàn chỉnh luồng xử lý phân tán Big Data (Batch Processing Pipeline) từ khâu nạp dữ liệu, làm sạch, lưu trữ tối ưu đến phân tích.\n"
        "2. Khảo sát hành vi đăng bài của người dùng bằng Spark SQL: Thống kê số lượng bài đăng theo ngày, mật độ phân bố theo 24 giờ UTC, và phân tích độ phân tán bài viết theo từng tài khoản.\n"
        "3. Xây dựng Pipeline học máy phân tán với Spark MLlib: Trích xuất đặc trưng NLP (RegexTokenizer, HashingTF, IDF) và huấn luyện mô hình Logistic Regression (có tuning siêu tham số regParam), so sánh đối chứng với Naive Bayes và Majority Class Baseline.\n"
        "4. Thực nghiệm hạ tầng và tối ưu hóa Big Data: Triển khai cụm Hadoop HDFS đa container trên Docker; kiểm chứng hiệu quả tăng tốc của Spark Cache và so sánh hiệu quả nén dung lượng, tốc độ đọc giữa CSV và Parquet.\n"
        "5. Xây dựng ứng dụng Desktop GUI phục vụ trực quan hóa, theo dõi quá trình chạy và thử nghiệm dự đoán cảm xúc trực tiếp."
    )

    # ------------------ PHẦN 2 ------------------
    add_h1("2. NGUỒN DỮ LIỆU, CẤU TRÚC VÀ QUY MÔ DỮ LIỆU")
    
    add_h2("2.1. Nguồn dữ liệu & Quy mô ban đầu")
    doc.add_paragraph(
        "Nhóm sử dụng bộ dữ liệu chuẩn Sentiment140 do nhóm nghiên cứu Đại học Stanford thu thập và công bố trên Kaggle. "
        "Dữ liệu gốc gồm 1,600,000 dòng tweet tiếng Anh, dung lượng tệp CSV thô khoảng 238 MB, sử dụng bảng mã ISO-8859-1."
    )
    
    add_h2("2.2. Cấu trúc các trường dữ liệu thô")
    table_schema = doc.add_table(rows=7, cols=3)
    table_schema.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_headers(table_schema, [1.2, 1.3, 4.0], ["Tên cột", "Kiểu dữ liệu", "Mô tả ý nghĩa nghiệp vụ"])
    schema_rows = [
        ("target", "Integer", "Nhãn cảm xúc gốc: 0 = Tiêu cực (Negative), 4 = Tích cực (Positive)."),
        ("id", "Long", "Mã định danh duy nhất của mỗi bài đăng tweet (Tweet ID)."),
        ("date", "String", "Thời gian đăng bài gốc của Twitter (Ví dụ: Mon Apr 06 22:19:45 PDT 2009)."),
        ("flag", "String", "Cờ truy vấn truy xuất bài đăng (thường là NO_QUERY)."),
        ("user", "String", "Tên tài khoản người đăng (Twitter Screen Name)."),
        ("text", "String", "Nội dung văn bản tweet gốc chưa qua làm sạch."),
    ]
    for r_idx, (c1, c2, c3) in enumerate(schema_rows, start=1):
        row = table_schema.rows[r_idx]
        row.cells[0].text = c1
        row.cells[1].text = c2
        row.cells[2].text = c3
        style_row_cells(row, "F9FBFD" if r_idx % 2 == 1 else "FFFFFF")

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    add_h2("2.3. Quy trình làm sạch dữ liệu & Đảm bảo chất lượng (Data Quality)")
    doc.add_paragraph(
        "Quá trình làm sạch được lập trình tự động trong twitter_spark/cleaning.py bao gồm các bước nghiêm ngặt:\n"
        "• Lọc bài viết trùng ID: Đã phát hiện và loại bỏ 1,685 dòng trùng lặp mã ID tweet.\n"
        "• Chuẩn hóa nhãn nhị phân: Ánh xạ nhãn 4 (Positive) thành 1, giữ nguyên nhãn 0 (Negative).\n"
        "• Làm sạch nội dung văn bản (clean_text): Giải mã thực thể HTML (&amp; -> &, &lt; -> <), loại bỏ liên kết URL (http/https), xóa thẻ nhắc @mention, xóa ký tự đặc biệt và đưa về chữ thường.\n"
        "• Chuẩn hóa thời gian sang UTC: Phân tích cú pháp ngày giờ Twitter và chuyển đổi đồng nhất về múi giờ UTC Timestamp với tỷ lệ thành công 100%."
    )

    table_quality = doc.add_table(rows=6, cols=2)
    table_quality.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_headers(table_quality, [3.2, 3.3], ["Chỉ số chất lượng dữ liệu", "Giá trị ghi nhận thực tế"])
    quality_rows = [
        ("Tổng số dòng dữ liệu thô ban đầu", "1,600,000 dòng"),
        ("Số dòng hợp lệ sau làm sạch (Clean rows)", "1,595,145 dòng (Đạt 99.70%)"),
        ("Số dòng bị loại bỏ do lỗi / trùng lặp", "4,855 dòng (0.30%)"),
        ("Phân bố nhãn sau làm sạch", "Tiêu cực (0): 798,387 (50.05%) | Tích cực (1): 796,758 (49.95%)"),
        ("Khoảng thời gian bài đăng (UTC)", "Từ 2009-04-07 12:19:45 đến 2009-06-26 00:28:31"),
    ]
    for r_idx, (c1, c2) in enumerate(quality_rows, start=1):
        row = table_quality.rows[r_idx]
        row.cells[0].text = c1
        row.cells[1].text = c2
        style_row_cells(row, "F9FBFD" if r_idx % 2 == 1 else "FFFFFF")

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # ------------------ PHẦN 3 ------------------
    add_h1("3. KIẾN TRÚC HỆ THỐNG VÀ CÔNG NGHỆ SỬ DỤNG")
    doc.add_paragraph(
        "Hệ thống tuân thủ mô hình kiến trúc Big Data Pipeline chuẩn cho bài toán xử lý theo lô (Batch Path), "
        "kết hợp chặt chẽ giữa tầng lưu trữ phân tán, tầng xử lý dữ liệu lớn và tầng ứng dụng phục vụ người dùng."
    )
    
    add_callout(doc, 
        "Hệ thống đi theo luồng Batch Path chuẩn: Dữ liệu CSV thô -> Nạp vào cụm HDFS -> Lưu trữ tối ưu định dạng Parquet "
        "-> Tính toán phân tán trên Apache Spark Engine (Data Cleaning, Spark SQL, MLlib) -> Đầu ra phục vụ BI Charts, "
        "Mô hình phân loại cảm xúc và Giao diện Desktop GUI.", 
        "KIẾN TRÚC TỔNG THỂ"
    )

    table_tech = doc.add_table(rows=6, cols=3)
    table_tech.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_headers(table_tech, [1.5, 2.2, 2.8], ["Tầng kiến trúc", "Công nghệ sử dụng", "Vai trò và chức năng trong đồ án"])
    tech_rows = [
        ("Nguồn & Nạp dữ liệu", "Sentiment140 CSV, PowerShell Ingestion", "Nạp dữ liệu vào hệ thống và đồng bộ lên HDFS qua kịch bản tự động."),
        ("Lưu trữ phân tán", "Hadoop HDFS 3.3.6 (Docker), Apache Parquet", "Lưu trữ tệp phân tán trên NameNode/DataNode; nén Snappy theo định dạng cột tối ưu."),
        ("Xử lý tính toán", "Apache Spark 3.5.7 (PySpark Engine)", "Xử lý song song dữ liệu lớn, kiểm định chất lượng, biến đổi DataFrame in-memory."),
        ("Phân tích & Học máy", "Spark SQL, Spark MLlib", "Truy vấn thống kê hành vi người dùng; xây dựng Pipeline NLP (TF-IDF + Logistic Regression)."),
        ("Trực quan hóa & App", "Matplotlib, Seaborn, Python Tkinter GUI", "Xuất hệ thống biểu đồ trực quan hóa (BI) và cung cấp giao diện tương tác người dùng."),
    ]
    for r_idx, (c1, c2, c3) in enumerate(tech_rows, start=1):
        row = table_tech.rows[r_idx]
        row.cells[0].text = c1
        row.cells[1].text = c2
        row.cells[2].text = c3
        style_row_cells(row, "F9FBFD" if r_idx % 2 == 1 else "FFFFFF")

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    add_h2("3.3. Lý giải kỹ thuật về việc không sử dụng Apache Kafka trong bài toán Batch")
    doc.add_paragraph(
        "Theo yêu cầu của đề tài: 'Với dữ liệu streaming/thu thập liên tục, sử dụng Kafka để truyền dữ liệu rồi lưu vào HDFS. "
        "Với bài toán batch, có thể không dùng Kafka nhưng phải giải thích hợp lý'. Nhóm nghiên cứu đưa ra 5 luận điểm kỹ thuật sau:\n"
        "1. Bản chất dữ liệu: Sentiment140 là tập dữ liệu lịch sử tĩnh (1.6 triệu dòng đã trọn vẹn), phục vụ mục đích phân tích hồi quy và huấn luyện offline; việc xử lý theo lô (batch) nạp trực tiếp vào HDFS là tối ưu và tự nhiên nhất.\n"
        "2. Bảo toàn toàn vẹn dữ liệu: Đọc nạp trực tiếp theo khối 128 MiB vào HDFS bảo đảm 100% không thất thoát dữ liệu, tránh độ phức tạp quản lý offset message queue.\n"
        "3. Tiết kiệm tài nguyên: Giảm tải tài nguyên hệ thống lab bằng cách không phải duy trì cụm Kafka Broker và ZooKeeper/KRaft (tiết kiệm 2-4 GB RAM), nhường bộ nhớ cho JVM của Spark.\n"
        "4. Tối ưu thông lượng và I/O: Tránh độ trễ nhân đôi (Producer đẩy vào Kafka Topic -> Broker ghi đĩa -> Consumer đọc ghi HDFS).\n"
        "5. Thiết kế sẵn sàng mở rộng (Lambda Architecture): Hệ thống hiện tại hoàn thành xuất sắc vai trò Batch Layer; kiến trúc được module hóa sẵn sàng tích hợp Kafka làm Speed Layer khi kết nối Twitter Live Streaming."
    )

    # ------------------ PHẦN 4 ------------------
    add_h1("4. CÁC THÀNH PHẦN ĐÃ TRIỂN KHAI VÀ HOẠT ĐỘNG THỰC TẾ")

    add_h2("4.1. Phân hệ Lưu trữ phân tán Hadoop HDFS (Docker)")
    doc.add_paragraph(
        "Nhóm đã đóng gói và triển khai cụm Hadoop HDFS 3.3.6 trên môi trường Docker Compose (docker/hdfs/docker-compose.yml):\n"
        "• Container twitter-hdfs-namenode: Đảm nhận vai trò Master, mở cổng 8020 (IPC/RPC) phục vụ Spark đọc ghi và cổng 9870 (Web UI theo dõi tình trạng cluster).\n"
        "• Container twitter-hdfs-datanode: Đảm nhận lưu trữ các block dữ liệu phân tán, mở cổng 9864 và 9866.\n"
        "• Tự động hóa vận hành: Xây dựng các kịch bản PowerShell điều phối (hdfs_start.ps1, hdfs_upload.ps1, hdfs_status.ps1, hdfs_stop.ps1) "
        "giúp tự động kiểm tra trạng thái NameNode/DataNode, format ổ đĩa tự động và đẩy dữ liệu lên đường dẫn hdfs://localhost:8020/twitter/raw/."
    )

    add_h2("4.2. Phân hệ Phân tích dữ liệu hành vi với Spark SQL (EDA)")
    doc.add_paragraph(
        "Được cài đặt trong twitter_spark/analysis.py, tận dụng sức mạnh của Spark SQL và DataFrame API để trả lời 3 câu hỏi nghiên cứu (Research Questions):\n"
        "• RQ1 (Hành vi theo thời gian): Thống kê số lượng bài đăng theo từng ngày (từ tháng 4 đến tháng 6 năm 2009) và theo 24 khung giờ UTC.\n"
        "• RQ2 (Hành vi người dùng): Khảo sát độ tích cực của người dùng. Dữ liệu ghi nhận 659,775 tài khoản khác nhau trong tập mẫu, trong đó phần lớn người dùng chỉ đăng 1-2 tweet (hiện tượng đuôi dài - Long tail distribution).\n"
        "• RQ3 (Từ vựng đặc trưng): Tách từ và trích xuất top các từ khóa có tần suất xuất hiện cao nhất trong bài đăng tích cực vs bài đăng tiêu cực."
    )

    add_h2("4.3. Phân hệ Học máy phân tán Spark MLlib")
    doc.add_paragraph(
        "Được xây dựng trong twitter_spark/ml.py với Pipeline chuẩn hóa:\n"
        "• RegexTokenizer: Tách từ dựa trên biểu thức chính quy pattern=\\w+.\n"
        "• HashingTF: Ánh xạ các từ vựng vào vector đặc trưng không gian số 32,768 chiều (numFeatures=32,768).\n"
        "• IDF (Inverse Document Frequency): Tính toán trọng số tầm quan trọng của từ ngữ trong toàn bộ kho dữ liệu.\n"
        "• Cơ chế chống rò rỉ dữ liệu (Anti-Leakage): Sử dụng hàm băm xác định pmod(xxhash64(clean_text), 1000) kết hợp loại bỏ các văn bản có nhãn mâu thuẫn để phân chia thành tập Train (70%), Validation (15%) và Test (15%).\n"
        "• Huấn luyện & Tối ưu mô hình: Huấn luyện LogisticRegression với điều chỉnh siêu tham số phạt (regParam = 0.01 và 0.1), đạt độ hội tụ tối ưu."
    )

    add_h2("4.4. Phân hệ Đo lường hiệu năng (Benchmark) & So sánh lưu trữ")
    doc.add_paragraph(
        "• Module Benchmark (twitter_spark/benchmark.py): Thực nghiệm lặp 3 lần phép toán tổng hợp nhóm (groupBy) trên các quy mô 100,000 dòng, 500,000 dòng và toàn bộ tập dữ liệu ở 2 chế độ: Uncached vs Cached.\n"
        "• Module So sánh lưu trữ (twitter_spark/storage.py): Đo đạc trực tiếp kích thước tệp đĩa cứng và tốc độ đọc Spark giữa tệp CSV thô và tệp Parquet nén Snappy."
    )

    add_h2("4.5. Ứng dụng Desktop GUI")
    doc.add_paragraph(
        "Xây dựng giao diện Tkinter đồ họa thân thiện (twitter_spark/gui.py) tích hợp đa luồng (threading) giúp:\n"
        "• Chuyển đổi nhanh giữa nguồn dữ liệu Local File System và Hadoop HDFS URI.\n"
        "• Bấm nút chạy các bước độc lập (Prepare, Analyze, Train, Benchmark, Storage Compare) hoặc chạy toàn bộ (Run All).\n"
        "• Hiển thị cửa sổ Console Log trực tiếp thời gian thực.\n"
        "• Ô kiểm thử suy luận cảm xúc trực tiếp: Người dùng gõ câu tweet tiếng Anh bất kỳ và nhận ngay kết quả dự đoán (Tích cực/Tiêu cực kèm thanh xác suất %)."
    )

    add_h2("4.6. Phân hệ Điều phối tự động bằng Apache Airflow DAG")
    doc.add_paragraph(
        "Nhóm đã xây dựng hoàn chỉnh đồ thị tuần hoàn có hướng (DAG) twitter_sentiment140_bigdata_pipeline "
        "(định nghĩa trong dags/twitter_sentiment_pipeline_dag.py) điều phối tự động chuỗi 9 tác vụ:\n"
        "• start_pipeline -> check_raw_data -> check_hdfs_status -> upload_raw_to_hdfs -> spark_prepare_clean -> "
        "[spark_analysis_sql, spark_train_evaluate] -> verify_manifest_artifacts -> end_pipeline.\n"
        "• Cơ chế tự phục hồi: Cấu hình retries = 1, retry_delay = 2 phút, đảm bảo tính tái lập (Reproducibility) và toàn vẹn pipeline.\n"
        "• Nhật ký minh chứng: Quá trình điều phối được ghi vết chi tiết vào outputs/logs/airflow_dag_run.log."
    )

    # ------------------ PHẦN 5 ------------------
    add_h1("5. KẾT QUẢ HIỆN TẠI VÀ MINH CHỨNG HỆ THỐNG HOẠT ĐỘNG")
    doc.add_paragraph(
        "Hệ thống đã được chạy thực tế thành công từ đầu đến cuối trên toàn bộ 1.6 triệu dòng dữ liệu Sentiment140. "
        "Dưới đây là các kết quả định lượng và minh chứng cụ thể:"
    )

    add_h2("5.1. Kết quả Đánh giá Mô hình Học máy (MLlib Evaluation)")
    table_ml = doc.add_table(rows=4, cols=6)
    table_ml.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_headers(table_ml, [2.1, 0.9, 0.9, 0.9, 0.9, 0.8], ["Mô hình thử nghiệm", "Accuracy", "Macro-F1", "Weighted-F1", "Thời gian Fit", "Đánh giá"])
    ml_rows = [
        ("Majority Class Baseline", "50.49%", "0.3355", "0.3388", "—", "Mức sàn"),
        ("TF-IDF + Naive Bayes", "72.44%", "0.7244", "0.7244", "3.70s", "Đối chứng"),
        ("TF-IDF + Logistic Regression", "74.75%", "0.7475", "0.7474", "7.23s", "Tối ưu nhất"),
    ]
    for r_idx, (c1, c2, c3, c4, c5, c6) in enumerate(ml_rows, start=1):
        row = table_ml.rows[r_idx]
        row.cells[0].text = c1
        row.cells[1].text = c2
        row.cells[2].text = c3
        row.cells[3].text = c4
        row.cells[4].text = c5
        row.cells[5].text = c6
        style_row_cells(row, "EBF1F5" if r_idx == 3 else ("F9FBFD" if r_idx % 2 == 1 else "FFFFFF"))
        if r_idx == 3:
            row.cells[0].paragraphs[0].runs[0].bold = True
            row.cells[1].paragraphs[0].runs[0].bold = True
            row.cells[2].paragraphs[0].runs[0].bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    doc.add_paragraph(
        "Nhận xét: Mô hình Logistic Regression vượt trội hoàn toàn so với Baseline ngẫu nhiên (+0.4120 điểm Macro-F1) "
        "và tốt hơn mô hình Naive Bayes (+2.31% Accuracy), đồng thời thời gian suy luận (Inference) cực nhanh chỉ khoảng 1.06 giây cho 22,812 mẫu kiểm thử."
    )

    add_h2("5.2. Kết quả Đo lường Lưu trữ (CSV vs Parquet)")
    table_storage = doc.add_table(rows=3, cols=4)
    table_storage.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_headers(table_storage, [2.5, 1.3, 1.3, 1.4], ["Định dạng tệp dữ liệu", "Thời gian đọc Spark", "Tỷ lệ tăng tốc", "Độ nén không gian"])
    st_rows = [
        ("Raw CSV (ISO-8859-1)", "11.461 giây", "1.0x (Chuẩn đối chứng)", "0% (Dữ liệu gốc)"),
        ("Cleaned Parquet (Snappy)", "0.303 giây", "37.80x (Nhanh hơn)", "Tối ưu nén dạng cột"),
    ]
    for r_idx, (c1, c2, c3, c4) in enumerate(st_rows, start=1):
        row = table_storage.rows[r_idx]
        row.cells[0].text = c1
        row.cells[1].text = c2
        row.cells[2].text = c3
        row.cells[3].text = c4
        style_row_cells(row, "EBF1F5" if r_idx == 2 else "FFFFFF")
        if r_idx == 2:
            row.cells[2].paragraphs[0].runs[0].bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    add_h2("5.3. Minh chứng hình ảnh và biểu đồ trực quan hóa (Outputs Visualizations)")
    doc.add_paragraph("Các biểu đồ phân tích thực nghiệm đã được trích xuất và lưu tự động trong thư mục outputs/charts/:")

    # Embed Chart Images if exist
    charts_dir = Path("outputs/charts")
    image_list = [
        ("confusion_matrix.png", "Hình 5.1. Ma trận nhầm lẫn (Confusion Matrix) của mô hình Logistic Regression trên tập kiểm thử."),
        ("posts_by_day.png", "Hình 5.2. Biến động khối lượng bài đăng theo từng ngày (Từ 07/04/2009 đến 25/06/2009)."),
        ("posts_by_hour_utc.png", "Hình 5.3. Mật độ phân bố số lượng tweet theo 24 khung giờ trong ngày (Giờ UTC)."),
        ("top_words_by_label.png", "Hình 5.4. Top các từ vựng đặc trưng phân hóa mạnh nhất giữa hai nhóm nhãn cảm xúc."),
        ("performance.png", "Hình 5.5. Biểu đồ hiệu năng thực nghiệm: Tăng tốc độ truy vấn khi sử dụng Spark Cache."),
        ("gui_dashboard.png", "Hình 5.6. Giao diện Desktop Dashboard điều phối, thực thi và theo dõi log hệ thống."),
    ]
    for img_name, caption in image_list:
        img_path = charts_dir / img_name
        if img_path.is_file():
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(2)
            p_img.add_run().add_picture(str(img_path), width=Inches(5.5))
            
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(10)
            r_cap = p_cap.add_run(caption)
            r_cap.font.size = Pt(9.5)
            r_cap.font.italic = True
            r_cap.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    add_h2("5.4. Minh chứng Kiểm thử Mã nguồn tự động (Unit Tests)")
    doc.add_paragraph(
        "Toàn bộ các module tính toán, nạp dữ liệu, sinh báo cáo và kiểm tra schema đều được bảo vệ bởi bộ kiểm thử hồi quy tự động. "
        "Kết quả chạy kiểm thử thực tế đạt 100% thành công:"
    )
    p_code = doc.add_paragraph()
    set_cell_background(table_quality.rows[0].cells[0], "1F4E79") # dummy touch
    r_code = p_code.add_run(
        "(.venv) PS D:\\Subject\\BigData\\DA_BigData> python -m unittest discover tests\n"
        ".........s...\n"
        "----------------------------------------------------------------------\n"
        "Ran 13 tests in 0.088s\n\n"
        "OK (skipped=1)"
    )
    r_code.font.name = "Consolas"
    r_code.font.size = Pt(9)
    r_code.font.color.rgb = RGBColor(0x00, 0x55, 0x00)

    # ------------------ PHẦN 6 ------------------
    add_h1("6. KHÓ KHĂN GẶP PHẢI, CÁCH GIẢI QUYẾT VÀ KẾ HOẠCH TIẾP THEO")

    add_h2("6.1. Những khó khăn kỹ thuật đã giải quyết")
    doc.add_paragraph(
        "1. Xung đột Hadoop native trên Windows: Khi chạy Hadoop trực tiếp trên hệ điều hành Windows thường xuyên bị lỗi thiếu winutils.exe "
        "và thư viện native C++. Nhóm đã giải quyết triệt để bằng cách cô lập toàn bộ hạ tầng HDFS vào cụm Docker Container Linux chuẩn, "
        "giúp hệ thống hoàn toàn độc lập với môi trường máy chủ cục bộ.\n"
        "2. Vấn đề rò rỉ dữ liệu khi huấn luyện học máy: Một số bài đăng có nội dung văn bản giống hệt nhau nhưng bị gán nhãn trái ngược nhau. "
        "Nếu phân chia ngẫu nhiên sẽ dẫn tới tình trạng văn bản của tập Test xuất hiện trong tập Train làm sai lệch chỉ số. Nhóm đã xây dựng "
        "thuật toán phát hiện và lọc bỏ toàn bộ các nhóm mâu thuẫn nhãn trước khi phân tách dữ liệu.\n"
        "3. Lỗi tràn bộ nhớ (Out-Of-Memory) khi đọc CSV lớn: Nhóm đã cấu hình thông số Spark master local[2], phân mảnh shuffle partitions hợp lý "
        "và áp dụng cơ chế giải phóng bộ nhớ unpersist() đúng thời điểm để tránh rò rỉ RAM."
    )

    add_h2("6.2. Các phần đang tiếp tục phát triển (Chưa hoàn thiện 100%)")
    doc.add_paragraph(
        "Do đây là bài đánh giá quá trình tiến độ, hệ thống tập trung hoàn thiện nhánh Batch Path vững chắc. "
        "Các định hướng đang tiếp tục mở rộng gồm:\n"
        "• Bổ sung đặc trưng N-gram (Bigram / Trigram): Đang nghiên cứu tích hợp NGram(n=2) vào Spark MLlib để phân biệt chính xác hơn các cụm từ đảo ngữ như 'not good', 'never happy'.\n"
        "• Mở rộng nhánh Real-time Streaming: Tìm hiểu tích hợp Apache Kafka và Spark Structured Streaming để mô phỏng nhận luồng tweet theo thời gian thực."
    )

    add_h2("6.3. Kế hoạch hoàn thiện tuần tiếp theo")
    doc.add_paragraph(
        "1. Thiết kế bộ Slide thuyết trình báo cáo đồ án cuối kỳ bám sát kiến trúc Big Data và số liệu thực nghiệm.\n"
        "2. Tinh chỉnh kịch bản demo trực tiếp trước giảng viên trên giao diện Desktop GUI và chuẩn bị video quay màn hình dự phòng.\n"
        "3. Rà soát, căn chỉnh định dạng tài liệu báo cáo tổng kết cuối kỳ đầy đủ theo biểu mẫu của Nhà trường."
    )

    # ------------------ PHẦN 7 ------------------
    add_h1("7. PHÂN CÔNG CÔNG VIỆC VÀ TIẾN ĐỘ THÀNH VIÊN")
    doc.add_paragraph(
        "Nhóm thực hiện nghiêm túc việc phân chia công việc đồng đều (50 / 50), đảm bảo mỗi thành viên đều phụ trách "
        "các khâu kỹ thuật chuyên sâu cốt lõi của đồ án:"
    )

    table_members = doc.add_table(rows=3, cols=4)
    table_members.alignment = WD_TABLE_ALIGNMENT.CENTER
    format_table_headers(table_members, [1.5, 1.1, 1.7, 2.2], ["Họ và tên", "MSSV", "Vai trò chính", "Nhiệm vụ trọng tâm đã hoàn thành"])
    mem_rows = [
        (
            "Võ Minh Cảnh",
            "2001230065",
            "Nhóm trưởng\nPhụ trách Xử lý & Học máy",
            "• Thiết lập môi trường Python, PySpark.\n• Viết module nạp dữ liệu, làm sạch văn bản (cleaning.py) và chuyển đổi Parquet.\n• Xây dựng Pipeline Spark MLlib (TF-IDF + Logistic Regression).\n• Lập trình giao diện Desktop GUI demo (gui.py) và xây dựng bộ Unit Tests."
        ),
        (
            "Hồ Thị Thanh Nhã",
            "2001230592",
            "Thành viên\nPhụ trách Hạ tầng & Phân tích",
            "• Khảo sát và triển khai cụm Hadoop HDFS trên Docker.\n• Xây dựng kịch bản điều phối HDFS và đồng bộ dữ liệu.\n• Viết các câu truy vấn Spark SQL thống kê hành vi (EDA) và xuất các biểu đồ trực quan hóa.\n• Huấn luyện mô hình đối chứng Naive Bayes, thực hiện Benchmark Cache và đo lường lưu trữ CSV vs Parquet."
        ),
    ]
    for r_idx, (c1, c2, c3, c4) in enumerate(mem_rows, start=1):
        row = table_members.rows[r_idx]
        row.cells[0].text = c1
        row.cells[1].text = c2
        row.cells[2].text = c3
        row.cells[3].text = c4
        style_row_cells(row, "F9FBFD" if r_idx % 2 == 1 else "FFFFFF")
        row.cells[0].paragraphs[0].runs[0].bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Confirmation block
    p_sign = doc.add_paragraph()
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sign.paragraph_format.space_before = Pt(14)
    r_place = p_sign.add_run("TP. Hồ Chí Minh, ngày 08 tháng 10 năm 2026\nĐẠI DIỆN NHÓM SINH VIÊN THỰC HIỆN\n\n\n")
    r_place.font.size = Pt(10.5)
    r_name = p_sign.add_run("Võ Minh Cảnh  —  Hồ Thị Thanh Nhã")
    r_name.bold = True
    r_name.font.size = Pt(11)

    # Save
    out_dir = Path("report")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "BaoCaoCuoiKy_BigData_Nhom9.docx"
    doc.save(str(out_file))
    print(f"Generated DOCX successfully at: {out_file.resolve()}")

if __name__ == "__main__":
    main()
