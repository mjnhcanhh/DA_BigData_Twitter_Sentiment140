import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def set_slide_background(slide, prs, bg_color_rgb):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = bg_color_rgb

def create_card(slide, left, top, width, height, bg_rgb, border_rgb=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_rgb
    if border_rgb:
        shape.line.color.rgb = border_rgb
        shape.line.width = Pt(1.5)
    else:
        shape.line.fill.background()
    return shape

def add_header(slide, title_text, category="ĐỒ ÁN MÔN: NHẬP MÔN BIG DATA — NHÓM 09"):
    # Category / Super-title
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.35))
    tf_c = cat_box.text_frame
    tf_c.word_wrap = True
    p_c = tf_c.paragraphs[0]
    p_c.text = category.upper()
    p_c.font.name = "Arial"
    p_c.font.size = Pt(10)
    p_c.font.bold = True
    p_c.font.color.rgb = RGBColor(0x2E, 0x75, 0xB6)

    # Main Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.7))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.name = "Arial"
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

def add_footer(slide, current_slide, total_slides=25):
    foot_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.7), Inches(0.3))
    tf = foot_box.text_frame
    p = tf.paragraphs[0]
    p.text = f"Phân tích Twitter với Apache Spark  |  Nhóm 9  |  Trang {current_slide}/{total_slides}"
    p.alignment = PP_ALIGN.RIGHT
    p.font.name = "Arial"
    p.font.size = Pt(9)
    p.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

def format_bullet_point(tf, title, desc, font_size=13, space_after=10):
    p = tf.add_paragraph() if len(tf.paragraphs[0].text) > 0 else tf.paragraphs[0]
    p.space_after = Pt(space_after)
    p.font.name = "Arial"
    p.font.size = Pt(font_size)
    r1 = p.add_run()
    r1.text = "• " + title + ": " if title else "• "
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    r2 = p.add_run()
    r2.text = desc
    r2.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

def style_table_cell(cell, text, bold=False, bg_rgb=None, text_rgb=None, font_size=11, align=PP_ALIGN.LEFT):
    cell.text = text
    if bg_rgb:
        cell.fill.solid()
        cell.fill.fore_color.rgb = bg_rgb
    p = cell.text_frame.paragraphs[0]
    p.alignment = align
    for r in p.runs:
        r.font.name = "Arial"
        r.font.size = Pt(font_size)
        r.font.bold = bold
        if text_rgb:
            r.font.color.rgb = text_rgb

def main():
    prs = Presentation()
    # 16:9 aspect ratio (13.333 x 7.5 inches)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    NAVY = RGBColor(0x1F, 0x4E, 0x79)
    ACCENT_BLUE = RGBColor(0x2E, 0x75, 0xB6)
    CARD_BG = RGBColor(0xF4, 0xF7, 0xFA)
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)
    DARK_TEXT = RGBColor(0x22, 0x22, 0x22)
    BORDER_COLOR = RGBColor(0xD0, 0xDC, 0xE5)
    CHARTS_DIR = Path("outputs/charts")

    # =========================================================================
    # SLIDE 1: TRANG TIÊU ĐỀ (TITLE SLIDE)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, prs, RGBColor(0x15, 0x2C, 0x4A))

    # Decorative banner card
    create_card(s1, Inches(1.0), Inches(1.2), Inches(11.333), Inches(5.1), RGBColor(0x1E, 0x3C, 0x64), RGBColor(0x2E, 0x75, 0xB6))

    tb = s1.shapes.add_textbox(Inches(1.5), Inches(1.5), Inches(10.333), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "BÁO CÁO ĐỒ ÁN HỌC PHẦN: NHẬP MÔN BIG DATA"
    p0.font.name = "Arial"
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = RGBColor(0x92, 0xC5, 0xDE)
    p0.space_after = Pt(14)

    p1 = tf.add_paragraph()
    p1.text = "PHÂN TÍCH HÀNH VI ĐĂNG BÀI VÀ CẢM XÚC\nCỦA NGƯỜI DÙNG TRÊN TWITTER BẰNG APACHE SPARK"
    p1.font.name = "Arial"
    p1.font.size = Pt(26)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.space_after = Pt(20)

    p2 = tf.add_paragraph()
    p2.text = "Nhóm thực hiện: Nhóm 09\n" \
              "• Sinh viên 1: Võ Minh Cảnh  —  MSSV: 2001230065\n" \
              "• Sinh viên 2: Hồ Thị Thanh Nhã  —  MSSV: 2001230592\n" \
              "Dữ liệu nghiên cứu: Sentiment140 Dataset (1.6 triệu tweet)  |  Môi trường: Apache Spark, HDFS Docker"
    p2.font.name = "Arial"
    p2.font.size = Pt(13)
    p2.font.color.rgb = RGBColor(0xE0, 0xE0, 0xE0)

    # =========================================================================
    # SLIDE 2: BỐI CẢNH & TÍNH CẤP THIẾT
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "1. Bối cảnh và Tính cấp thiết của Đề tài")
    add_footer(s2, 2)

    create_card(s2, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s2.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "TẦM QUAN TRỌNG CỦA DỮ LIỆU TWITTER"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = NAVY
    p.space_after = Pt(12)
    format_bullet_point(tf, "Nguồn ý kiến công chúng khổng lồ", "Mỗi ngày có hàng trăm triệu dòng tweet phản ánh ý kiến, thị hiếu và cảm xúc về sản phẩm, dịch vụ và sự kiện.")
    format_bullet_point(tf, "Ứng dụng doanh nghiệp", "Hỗ trợ chăm sóc khách hàng, quản trị thương hiệu, phát hiện khủng hoảng truyền thông và nghiên cứu thị trường.")
    format_bullet_point(tf, "Tính tức thời", "Dữ liệu được tạo ra liên tục đòi hỏi các giải pháp xử lý quy mô lớn và tốc độ cao.")

    create_card(s2, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s2.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "GIẢI PHÁP CÔNG NGHỆ: APACHE SPARK"
    p.font.bold = True
    p.font.size = Pt(15)
    p.font.color.rgb = NAVY
    p.space_after = Pt(12)
    format_bullet_point(tf, "Khắc phục giới hạn đơn máy", "Các công cụ truyền thống (Pandas, Excel, Scikit-learn) quá tải bộ nhớ RAM khi mở tệp hàng triệu bản ghi.")
    format_bullet_point(tf, "Xử lý In-Memory", "Apache Spark tính toán trực tiếp trên bộ nhớ đệm, nhanh hơn Hadoop MapReduce từ 10 đến 100 lần.")
    format_bullet_point(tf, "Hệ sinh thái toàn diện", "Tích hợp sẵn Spark SQL (truy vấn quan hệ) và Spark MLlib (học máy phân tán) trong một nền tảng duy nhất.")

    # =========================================================================
    # SLIDE 3: THÁCH THỨC ĐẶC TRƯNG BIG DATA (3V)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "2. Thách thức Big Data trong Đề tài (The 3V Challenges)")
    add_footer(s3, 3)

    cols_data = [
        ("VOLUME (Khối lượng lớn)", "1,600,000 Tweets", [
            ("Quy mô dòng", "1.6 triệu bản ghi văn bản lịch sử."),
            ("Bộ nhớ RAM", "Vượt ngưỡng xử lý an toàn của Pandas trên máy tính cá nhân."),
            ("Độ phức tạp I/O", "Đọc/ghi CSV thô tốn nhiều băng thông ổ đĩa nếu không tối ưu hóa.")
        ]),
        ("VARIETY (Độ biến thiên & Nhiễu)", "Dữ liệu văn bản phi cấu trúc", [
            ("Nhiễu văn bản", "Chứa nhiều liên kết URL, thẻ @mention, biểu tượng cảm xúc, ký tự HTML lỗi."),
            ("Định dạng ngày giờ", "Chuỗi ngày Twitter chứa múi giờ PDT/EST cần chuẩn hóa về UTC."),
            ("Trùng lặp & mâu thuẫn", "Xuất hiện tweet trùng ID và các câu trùng nội dung nhưng khác nhãn.")
        ]),
        ("VELOCITY (Tốc độ & Hiệu năng)", "Xử lý & Suy luận phân tán", [
            ("Huấn luyện phân tán", "Trích xuất 32,768 đặc trưng TF-IDF song song trên toàn bộ tập dữ liệu."),
            ("Tối ưu hóa Caching", "Cần cơ chế Spark Cache để tăng tốc các phép toán lặp lại."),
            ("Tốc độ truy vấn", "Yêu cầu định dạng lưu trữ cột (Parquet) để truy vấn tức thì.")
        ])
    ]

    for i, (title, sub, items) in enumerate(cols_data):
        c_left = Inches(0.8 + i * 4.0)
        create_card(s3, c_left, Inches(1.6), Inches(3.7), Inches(5.0), CARD_BG, BORDER_COLOR)
        tb = s3.shapes.add_textbox(c_left + Inches(0.2), Inches(1.8), Inches(3.3), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = NAVY
        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.bold = True
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = ACCENT_BLUE
        p_sub.space_after = Pt(12)
        for k, v in items:
            format_bullet_point(tf, k, v, font_size=11, space_after=8)

    # =========================================================================
    # SLIDE 4: MỤC TIÊU VÀ PHẠM VI NGHIÊN CỨU
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "3. Mục tiêu và Phạm vi Nghiên cứu")
    add_footer(s4, 4)

    goals = [
        ("Mục tiêu 1: Xây dựng Big Data Pipeline khép kín", 
         "Thiết kế luồng Batch Ingestion -> HDFS / Parquet -> Spark Engine -> Serving (SQL, ML, GUI) hoàn chỉnh, chạy ổn định từ đầu đến cuối."),
        ("Mục tiêu 2: Phân tích hành vi người dùng (EDA với Spark SQL)", 
         "Khám phá chu kỳ đăng bài theo ngày, mật độ theo 24 giờ UTC, phân bố người dùng tích cực và trích xuất từ khóa phân hóa cảm xúc."),
        ("Mục tiêu 3: Huấn luyện mô hình phân loại cảm xúc (Spark MLlib)", 
         "Xây dựng pipeline TF-IDF + Logistic Regression (có tuning siêu tham số), đối chứng với Naive Bayes và Majority Class Baseline."),
        ("Mục tiêu 4: Thực nghiệm đo lường hiệu năng hạ tầng Big Data", 
         "Đo đạc thực tế lợi ích của Spark Cache (so sánh 3 mức dữ liệu) và chứng minh ưu thế vượt trội của định dạng Parquet so với CSV."),
        ("Mục tiêu 5: Xây dựng Desktop GUI & Đảm bảo kiểm thử chất lượng", 
         "Phát triển giao diện tương tác chọn nguồn Local/HDFS, demo suy luận tweet trực tiếp và thiết lập bộ 13 Unit Tests hồi quy tự động.")
    ]
    for idx, (g_title, g_desc) in enumerate(goals):
        top_y = Inches(1.6 + idx * 1.0)
        card = create_card(s4, Inches(0.8), top_y, Inches(11.733), Inches(0.85), CARD_BG, BORDER_COLOR)
        tb = s4.shapes.add_textbox(Inches(1.0), top_y + Inches(0.08), Inches(11.3), Inches(0.7))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = g_title
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = NAVY
        p2 = tf.add_paragraph()
        p2.text = g_desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = DARK_TEXT

    # =========================================================================
    # SLIDE 5: KIẾN TRÚC TỔNG THỂ HỆ THỐNG
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "4. Kiến trúc Tổng thể Hệ thống (Big Data Pipeline)")
    add_footer(s5, 5)

    stages = [
        ("1. SOURCES", "Tệp CSV Sentiment140\n• 1.6 triệu bài đăng\n• 238 MB dữ liệu thô\n• Mã hóa ISO-8859-1"),
        ("2. INGESTION", "Batch Ingestion\n• Script PowerShell nạp tệp\n• Spark DataFrame Reader\n• Áp đặt Schema cố định"),
        ("3. STORAGE", "HDFS & Parquet\n• Cụm Hadoop 3.3.6 Docker\n• NameNode & DataNode\n• Parquet nén Snappy"),
        ("4. PROCESSING", "Spark Engine\n• Làm sạch văn bản (Regex)\n• Lọc trùng & chuẩn hóa UTC\n• MLlib TF-IDF & Tuning"),
        ("5. SERVING", "Đầu ra Ứng dụng\n• Bảng Spark SQL\n• 6 biểu đồ trực quan BI\n• Mô hình ML & Desktop GUI")
    ]
    for i, (st_name, st_desc) in enumerate(stages):
        box_left = Inches(0.8 + i * 2.4)
        create_card(s5, box_left, Inches(1.8), Inches(2.2), Inches(4.5), CARD_BG, NAVY)
        tb = s5.shapes.add_textbox(box_left + Inches(0.1), Inches(2.0), Inches(2.0), Inches(4.0))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = st_name
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = NAVY
        p.space_after = Pt(12)
        p2 = tf.add_paragraph()
        p2.text = st_desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = DARK_TEXT

    # Bottom Banner
    create_card(s5, Inches(0.8), Inches(6.4), Inches(11.733), Inches(0.6), RGBColor(0x1F, 0x4E, 0x79))
    tb_b = s5.shapes.add_textbox(Inches(1.0), Inches(6.45), Inches(11.3), Inches(0.5))
    p_b = tb_b.text_frame.paragraphs[0]
    p_b.text = "LƯU Ý THỰC NGHIỆM: Đồ án triển khai chuẩn theo luồng BATCH PATH (Files -> HDFS -> Spark Batch -> BI/ML/GUI)."
    p_b.font.bold = True
    p_b.font.size = Pt(11)
    p_b.font.color.rgb = WHITE
    p_b.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 6: BỘ DỮ LIỆU SENTIMENT140
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "5. Tổng quan Bộ dữ liệu Sentiment140")
    add_footer(s6, 6)

    create_card(s6, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s6.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "THÔNG TIN TỔNG QUÁT"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    format_bullet_point(tf, "Đơn vị phát triển", "Nhóm nghiên cứu thuộc Đại học Stanford (Go, Bhayani & Huang).")
    format_bullet_point(tf, "Cơ chế gán nhãn", "Gán nhãn tự động dựa trên biểu tượng cảm xúc (Emoticons) trong bài đăng (ví dụ :) và :().")
    format_bullet_point(tf, "Quy mô", "1,600,000 dòng dữ liệu văn bản tweet tiếng Anh.")
    format_bullet_point(tf, "Mã hóa ký tự", "ISO-8859-1 (cần xử lý chuẩn hóa sang UTF-8).")
    format_bullet_point(tf, "Cân bằng nhãn gốc", "800,000 mẫu tiêu cực (nhãn 0) và 800,000 mẫu tích cực (nhãn 4).")

    create_card(s6, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s6.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Ý NGHĨA KHOA HỌC & GIỚI HẠN DỮ LIỆU"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    format_bullet_point(tf, "Ưu điểm", "Quy mô dữ liệu chuẩn quốc tế cho bài toán phân tích cảm xúc Big Data; số lượng bài mẫu phong phú.")
    format_bullet_point(tf, "Đặc thù lịch sử", "Thu thập năm 2009, phản ánh các chủ đề mạng xã hội thời kỳ đầu.")
    format_bullet_point(tf, "Giới hạn quan trọng", "Bộ dữ liệu dùng nhãn vi mô dựa trên emoticon; kết quả mô hình phản ánh cấu trúc tập mẫu huấn luyện chứ không đại diện cho dư luận công chúng toàn cầu ở hiện tại.")

    # =========================================================================
    # SLIDE 7: CẤU TRÚC 6 TRƯỜNG DỮ LIỆU THÔ
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "6. Cấu trúc 6 Trường Dữ liệu Thô (Raw Schema)")
    add_footer(s7, 7)

    table_s7 = s7.shapes.add_table(7, 4, Inches(0.8), Inches(1.6), Inches(11.733), Inches(4.8)).table
    format_table_headers = ["STT", "Tên trường", "Kiểu dữ liệu", "Ý nghĩa nghiệp vụ & Dữ liệu mẫu"]
    for i, h in enumerate(format_table_headers):
        style_table_cell(table_s7.cell(0, i), h, bold=True, bg_rgb=NAVY, text_rgb=WHITE, font_size=12, align=PP_ALIGN.CENTER)

    raw_schema_data = [
        ("1", "target", "Integer", "Nhãn cảm xúc gốc: 0 = Tiêu cực, 4 = Tích cực."),
        ("2", "id", "Long", "Mã định danh duy nhất của bài đăng (Tweet ID, ví dụ: 1467810369)."),
        ("3", "date", "String", "Thời gian đăng bài của Twitter (Ví dụ: Mon Apr 06 22:19:45 PDT 2009)."),
        ("4", "flag", "String", "Cờ truy vấn dữ liệu từ API (Trong tập này luôn là NO_QUERY)."),
        ("5", "user", "String", "Tên người dùng đăng tweet (Ví dụ: _TheSpecialOne_)."),
        ("6", "text", "String", "Nội dung văn bản tweet gốc chứa ký tự đặc biệt, link, mention, HTML entity.")
    ]
    for r_idx, row_vals in enumerate(raw_schema_data, start=1):
        for c_idx, val in enumerate(row_vals):
            bg = CARD_BG if r_idx % 2 == 1 else WHITE
            align = PP_ALIGN.CENTER if c_idx < 3 else PP_ALIGN.LEFT
            style_table_cell(table_s7.cell(r_idx, c_idx), val, bold=(c_idx == 1), bg_rgb=bg, font_size=11, align=align)

    # =========================================================================
    # SLIDE 8: QUY TRÌNH TIỀN XỬ LÝ & LÀM SẠCH VĂN BẢN
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "7. Quy trình Tiền xử lý & Làm sạch Văn bản")
    add_footer(s8, 8)

    clean_steps = [
        ("1. Khử trùng lặp ID bài đăng", "Phát hiện và loại bỏ các dòng có Tweet ID trùng lặp (1,685 dòng trùng), đảm bảo tính toàn vẹn khóa chính."),
        ("2. Chuẩn hóa nhãn nhị phân (Binary Mapping)", "Chuyển nhãn 4 (Positive) thành 1, giữ nguyên nhãn 0 (Negative). Giúp thuận tiện cho hàm mất mát nhị phân trong Spark MLlib."),
        ("3. Giải mã thực thể HTML lỗi", "Chuyển đổi các ký tự mã hóa URL/HTML như &amp; -> &, &lt; -> <, &gt; -> > để khôi phục cấu trúc văn bản gốc."),
        ("4. Loại bỏ siêu liên kết (URLs)", "Sử dụng biểu thức chính quy (Regex) quét và loại bỏ http://..., https://... vì không mang ý nghĩa cảm xúc."),
        ("5. Loại bỏ thẻ người dùng (@user)", "Xóa các thẻ @username để mô hình tập trung vào nội dung biểu đạt thay vì phụ thuộc vào tên tài khoản người khác."),
        ("6. Chuẩn hóa thời gian sang UTC Timestamp", "Phân tích cú pháp ngày giờ định dạng Twitter và chuyển đổi chuẩn về múi giờ UTC để phân tích thời gian thống nhất.")
    ]
    for idx, (st_t, st_d) in enumerate(clean_steps):
        r = idx // 2
        c = idx % 2
        top_y = Inches(1.6 + r * 1.7)
        left_x = Inches(0.8 + c * 6.0)
        create_card(s8, left_x, top_y, Inches(5.7), Inches(1.5), CARD_BG, BORDER_COLOR)
        tb = s8.shapes.add_textbox(left_x + Inches(0.2), top_y + Inches(0.15), Inches(5.3), Inches(1.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = st_t
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = NAVY
        p2 = tf.add_paragraph()
        p2.text = st_d
        p2.font.size = Pt(11)
        p2.font.color.rgb = DARK_TEXT

    # =========================================================================
    # SLIDE 9: KẾT QUẢ KIỂM SOÁT CHẤT LƯỢNG (DATA QUALITY ASSURANCE)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "8. Kết quả Kiểm soát Chất lượng (Data Quality)")
    add_footer(s9, 9)

    cards_metrics = [
        ("1,600,000", "Tổng số dòng đầu vào", "Toàn bộ dữ liệu thô đọc từ Sentiment140"),
        ("1,595,145", "Dòng hợp lệ sau làm sạch", "Tỷ lệ giữ lại đạt mức ấn tượng 99.70%"),
        ("4,855", "Số dòng bị loại bỏ", "Bao gồm 1,685 dòng trùng ID và dòng lỗi"),
        ("100%", "Tỷ lệ chuẩn hóa thời gian", "Chuyển đổi thành công 100% ngày giờ sang UTC")
    ]
    for idx, (val, title, note) in enumerate(cards_metrics):
        c_left = Inches(0.8 + idx * 3.0)
        create_card(s9, c_left, Inches(1.6), Inches(2.7), Inches(2.2), CARD_BG, NAVY)
        tb = s9.shapes.add_textbox(c_left + Inches(0.1), Inches(1.8), Inches(2.5), Inches(1.8))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = val
        p.font.bold = True
        p.font.size = Pt(22)
        p.font.color.rgb = NAVY
        p.alignment = PP_ALIGN.CENTER
        p2 = tf.add_paragraph()
        p2.text = title
        p2.font.bold = True
        p2.font.size = Pt(11)
        p2.font.color.rgb = ACCENT_BLUE
        p2.alignment = PP_ALIGN.CENTER
        p3 = tf.add_paragraph()
        p3.text = note
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = DARK_TEXT
        p3.alignment = PP_ALIGN.CENTER

    # Quality Summary Box below
    create_card(s9, Inches(0.8), Inches(4.2), Inches(11.733), Inches(2.4), CARD_BG, BORDER_COLOR)
    tb_q = s9.shapes.add_textbox(Inches(1.0), Inches(4.4), Inches(11.3), Inches(2.0))
    tf_q = tb_q.text_frame
    tf_q.word_wrap = True
    p = tf_q.paragraphs[0]
    p.text = "PHÂN BỐ NHÃN DỮ LIỆU SAU KHI LÀM SẠCH:"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)
    format_bullet_point(tf_q, "Nhãn Tiêu cực (0)", "798,387 dòng, chiếm 50.05% tổng số dòng hợp lệ.")
    format_bullet_point(tf_q, "Nhãn Tích cực (1)", "796,758 dòng, chiếm 49.95% tổng số dòng hợp lệ.")
    format_bullet_point(tf_q, "Kết luận cân bằng", "Độ chênh lệch giữa hai lớp chỉ 0.1%, là điều kiện lý tưởng cho các thuật toán phân loại mà không cần kỹ thuật Oversampling hay Undersampling.")

    # =========================================================================
    # SLIDE 10: TẦNG LƯU TRỮ HDFS TRÊN DOCKER
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "9. Tầng Lưu trữ Phân tán: Hadoop HDFS trên Docker")
    add_footer(s10, 10)

    create_card(s10, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s10.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "KIẾN TRÚC CỤM HDFS MULTI-CONTAINER"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    format_bullet_point(tf, "Image chuẩn", "apache/hadoop:3.3.6 (Nền tảng Linux container).")
    format_bullet_point(tf, "NameNode (Master)", "Quản lý metadata, namespace; mở cổng 8020 (RPC cho Spark) và 9870 (Web UI theo dõi tình trạng cluster).")
    format_bullet_point(tf, "DataNode (Worker)", "Lưu trữ các khối block dữ liệu phân tán; mở cổng 9864 và 9866.")
    format_bullet_point(tf, "Volume Persistent", "Gắn kết namenode_data và datanode_data đảm bảo dữ liệu không bị mất khi khởi động lại container.")

    create_card(s10, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s10.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "TỰ ĐỘNG HÓA VẬN HÀNH & KẾT NỐI SPARK"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    format_bullet_point(tf, "Scripts tự động hóa", "Bộ script PowerShell quản lý vòng đời cụm: hdfs_start.ps1, hdfs_upload.ps1, hdfs_status.ps1, hdfs_stop.ps1.")
    format_bullet_point(tf, "Khắc phục lỗi Windows", "Loại bỏ hoàn toàn lỗi winutils.exe và thiếu thư viện native C++ thường gặp trên Windows bằng cách đóng gói trong Docker.")
    format_bullet_point(tf, "Đường dẫn URI kết nối", "Dữ liệu được nạp vào đường dẫn HDFS chuẩn: hdfs://localhost:8020/twitter/raw/sentiment140.csv.")

    # =========================================================================
    # SLIDE 11: SO SÁNH LƯU TRỮ: CSV VS APACHE PARQUET
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "10. So sánh Lưu trữ: CSV vs Apache Parquet")
    add_footer(s11, 11)

    table_s11 = s11.shapes.add_table(3, 4, Inches(0.8), Inches(1.6), Inches(11.733), Inches(2.2)).table
    headers_s11 = ["Định dạng tệp", "Thời gian đọc Spark", "Tỷ lệ tăng tốc", "Độ nén & Tối ưu I/O"]
    for i, h in enumerate(headers_s11):
        style_table_cell(table_s11.cell(0, i), h, bold=True, bg_rgb=NAVY, text_rgb=WHITE, font_size=12, align=PP_ALIGN.CENTER)

    st_rows_data = [
        ("Raw CSV (ISO-8859-1)", "11.461 giây", "1.0x (Chuẩn đối chứng)", "0% (Dữ liệu dạng dòng thuần túy)"),
        ("Cleaned Parquet (Snappy)", "0.303 giây", "37.80x (Nhanh hơn)", "Tối ưu nén dạng cột Snappy")
    ]
    for r_idx, row_vals in enumerate(st_rows_data, start=1):
        for c_idx, val in enumerate(row_vals):
            bg = RGBColor(0xEA, 0xF2, 0xF8) if r_idx == 2 else WHITE
            style_table_cell(table_s11.cell(r_idx, c_idx), val, bold=(r_idx == 2), bg_rgb=bg, font_size=11, align=PP_ALIGN.CENTER)

    create_card(s11, Inches(0.8), Inches(4.2), Inches(11.733), Inches(2.4), CARD_BG, BORDER_COLOR)
    tb_exp = s11.shapes.add_textbox(Inches(1.0), Inches(4.4), Inches(11.3), Inches(2.0))
    tf_exp = tb_exp.text_frame
    tf_exp.word_wrap = True
    p = tf_exp.paragraphs[0]
    p.text = "NGUYÊN NHÂN PARQUET ĐẠT HIỆU NĂNG VƯỢT TRỘI:"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = NAVY
    p.space_after = Pt(8)
    format_bullet_point(tf_exp, "Lưu trữ định dạng cột (Columnar Storage)", "Spark chỉ cần đọc đúng các cột được truy vấn (projection pushdown), bỏ qua các cột không cần thiết thay vì phải scan toàn bộ dòng như CSV.")
    format_bullet_point(tf_exp, "Nén khối thông minh (Snappy Compression)", "Các giá trị cùng kiểu dữ liệu đứng cạnh nhau giúp thuật toán nén đạt hiệu suất cao, giảm kích thước đĩa và giảm lượng dữ liệu truyền qua mạng.")
    format_bullet_point(tf_exp, "Metadata tích hợp sẵn", "Parquet lưu sẵn schema và số liệu thống kê (min, max per chunk), giúp bộ tối ưu Catalyst áp dụng Predicate Pushdown hiệu quả.")

    # =========================================================================
    # SLIDE 12: PHÂN TÍCH KHÁM PHÁ DỮ LIỆU VỚI SPARK SQL (EDA)
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "11. Phân tích Khám phá Dữ liệu với Spark SQL (EDA)")
    add_footer(s12, 12)

    rq_list = [
        ("RQ1: HÀNH VI THEO THỜI GIAN", "Khảo sát tần suất đăng bài theo chu kỳ ngày và theo 24 khung giờ UTC", [
            ("Phân tích ngày", "Xác định các ngày có lượng bài đăng đột biến và ngày có lưu lượng thấp nhất."),
            ("Phân tích giờ", "Khảo sát mật độ hoạt động của người dùng toàn cầu theo từng khung giờ trong ngày."),
            ("Tương quan nhãn", "So sánh tỷ lệ cảm xúc tích cực và tiêu cực biến động qua các mốc thời gian.")
        ]),
        ("RQ2: HÀNH VI NGƯỜI DÙNG", "Khảo sát mức độ tích cực của các tài khoản Twitter trong tập mẫu", [
            ("Tài khoản duy nhất", "Ghi nhận 659,775 tài khoản khác nhau trong tập dữ liệu nghiên cứu."),
            ("Hiện tượng đuôi dài", "Hầu hết người dùng chỉ đăng 1-2 bài tweet (Long-tail user distribution)."),
            ("Người dùng tích cực", "Nhóm người dùng đăng nhiều bài có xu hướng phân bổ cảm xúc ra sao?")
        ]),
        ("RQ3: KHÁM PHÁ TỪ VỰNG", "Trích xuất các từ khóa đặc trưng phân hóa cảm xúc mạnh mẽ nhất", [
            ("Tách từ phân tán", "Sử dụng Spark SQL explode(split(clean_text, ' ')) đếm tần suất từ song song."),
            ("Từ vựng tích cực", "Các từ mang sắc thái lạc quan, cảm ơn, khen ngợi (love, good, thank, great)."),
            ("Từ vựng tiêu cực", "Các từ mang sắc thái than phiền, bức xúc, phủ định (not, no, miss, sad, bad).")
        ])
    ]
    for i, (title, sub, items) in enumerate(rq_list):
        c_left = Inches(0.8 + i * 4.0)
        create_card(s12, c_left, Inches(1.6), Inches(3.7), Inches(5.0), CARD_BG, BORDER_COLOR)
        tb = s12.shapes.add_textbox(c_left + Inches(0.2), Inches(1.8), Inches(3.3), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = NAVY
        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.bold = True
        p_sub.font.size = Pt(10.5)
        p_sub.font.color.rgb = ACCENT_BLUE
        p_sub.space_after = Pt(12)
        for k, v in items:
            format_bullet_point(tf, k, v, font_size=11, space_after=8)

    # =========================================================================
    # SLIDE 13: RQ1 - PHÂN TÍCH THEO NGÀY (EMBED CHART)
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "12. RQ1 - Biến động Khối lượng Tweet theo Ngày")
    add_footer(s13, 13)

    img_day = CHARTS_DIR / "posts_by_day.png"
    if img_day.is_file():
        s13.shapes.add_picture(str(img_day), Inches(0.8), Inches(1.6), width=Inches(6.8))

    create_card(s13, Inches(7.8), Inches(1.6), Inches(4.7), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s13.shapes.add_textbox(Inches(8.0), Inches(1.8), Inches(4.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "NHẬN XÉT THỰC NGHIỆM"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    format_bullet_point(tf, "Thời gian khảo sát", "Kéo dài từ ngày 07/04/2009 đến 25/06/2009 (hơn 2.5 tháng).")
    format_bullet_point(tf, "Ngày cao điểm nhất", "Ngày 07/06/2009 ghi nhận lượng tweet tăng vọt (hơn 100,000 bài), phản ánh các sự kiện chính trị / thể thao lớn diễn ra.")
    format_bullet_point(tf, "Chu kỳ tuần hoàn", "Lưu lượng bài đăng có xu hướng tăng vào các ngày cuối tuần và các ngày diễn ra sự kiện nóng.")

    # =========================================================================
    # SLIDE 14: RQ1 - MẬT ĐỘ THEO 24 GIỜ UTC (EMBED CHART)
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    add_header(s14, "13. RQ1 - Mật độ Bài đăng theo 24 Khung giờ UTC")
    add_footer(s14, 14)

    img_hour = CHARTS_DIR / "posts_by_hour_utc.png"
    if img_hour.is_file():
        s14.shapes.add_picture(str(img_hour), Inches(0.8), Inches(1.6), width=Inches(6.8))

    create_card(s14, Inches(7.8), Inches(1.6), Inches(4.7), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s14.shapes.add_textbox(Inches(8.0), Inches(1.8), Inches(4.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "NHẬN XÉT THỰC NGHIỆM"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    format_bullet_point(tf, "Giờ cao điểm", "Khung giờ 12:00 - 15:00 UTC ghi nhận mật độ tweet cao nhất (trên 80,000 tweet/giờ).")
    format_bullet_point(tf, "Ý nghĩa địa lý", "Tương ứng với buổi sáng tại khu vực Bắc Mỹ và buổi chiều tối tại châu Âu, thời điểm người dùng bắt đầu các hoạt động trực tuyến tích cực.")
    format_bullet_point(tf, "Giờ trầm lắng", "Khung giờ 03:00 - 05:00 UTC có lưu lượng thấp nhất, tương ứng với nửa đêm tại bờ Tây và bờ Đông nước Mỹ.")

    # =========================================================================
    # SLIDE 15: RQ2 - PHÂN TÍCH HÀNH VI NGƯỜI DÙNG (USER BEHAVIOR)
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    add_header(s15, "14. RQ2 - Phân tích Mức độ Hoạt động của Người dùng")
    add_footer(s15, 15)

    img_user = CHARTS_DIR / "posts_per_user.png"
    if img_user.is_file():
        s15.shapes.add_picture(str(img_user), Inches(0.8), Inches(1.6), width=Inches(6.8))

    create_card(s15, Inches(7.8), Inches(1.6), Inches(4.7), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s15.shapes.add_textbox(Inches(8.0), Inches(1.8), Inches(4.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "HIỆN TƯỢNG ĐUÔI DÀI (LONG-TAIL)"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    format_bullet_point(tf, "Quy mô tài khoản", "659,775 tài khoản khác nhau trong tập mẫu.")
    format_bullet_point(tf, "Đại đa số người dùng", "Hơn 70% tài khoản chỉ xuất hiện đúng 1 lần trong tập dữ liệu.")
    format_bullet_point(tf, "Tài khoản tích cực", "Chỉ một tỷ lệ rất nhỏ tài khoản có trên 10 bài đăng.")
    format_bullet_point(tf, "Ý nghĩa học máy", "Không thể dùng ID người dùng làm đặc trưng phân loại vì sẽ gây Overfitting nghiêm trọng; mô hình chỉ được phép học từ nội dung văn bản (clean_text).")

    # =========================================================================
    # SLIDE 16: RQ3 - KHÁM PHÁ TỪ VỰNG THEO CẢM XÚC (EMBED CHART)
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    add_header(s16, "15. RQ3 - Top Từ vựng Phân hóa Cảm xúc Mạnh mẽ")
    add_footer(s16, 16)

    img_words = CHARTS_DIR / "top_words_by_label.png"
    if img_words.is_file():
        s16.shapes.add_picture(str(img_words), Inches(0.8), Inches(1.6), width=Inches(6.8))

    create_card(s16, Inches(7.8), Inches(1.6), Inches(4.7), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s16.shapes.add_textbox(Inches(8.0), Inches(1.8), Inches(4.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "ĐẶC TRƯNG TỪ VỰNG PHÂN HÓA"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    format_bullet_point(tf, "Nhóm Tích cực (Positive)", "Chi phối bởi các từ: 'good', 'love', 'day', 'thanks', 'happy', 'great'. Thể hiện sự hài lòng, niềm vui và sự ủng hộ.")
    format_bullet_point(tf, "Nhóm Tiêu cực (Negative)", "Chi phối bởi các từ phủ định và than phiền: 'not', 'no', 'work', 'miss', 'sad', 'hate'.")
    format_bullet_point(tf, "Cơ sở cho TF-IDF", "Sự phân hóa rõ rệt của các từ khóa này là tiền đề vững chắc để bộ trích xuất TF-IDF gán trọng số và giúp mô hình phân loại chính xác.")

    # =========================================================================
    # SLIDE 17: PIPELINE TRÍCH XUẤT ĐẶC TRƯNG NLP (SPARK MLLIB)
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    add_header(s17, "16. Pipeline Trích xuất Đặc trưng NLP (Spark MLlib)")
    add_footer(s17, 17)

    nlp_pipeline = [
        ("BƯỚC 1: RegexTokenizer", "Phân tách văn bản thành danh sách từ", [
            ("Biểu thức Regex", "pattern='\\w+' tách theo từ ngữ hợp lệ."),
            ("Chuyển chữ thường", "Đồng nhất toàn bộ ký tự về chữ thường."),
            ("Loại bỏ khoảng trắng", "Tự động khử các ký tự khoảng trắng dư thừa.")
        ]),
        ("BƯỚC 2: HashingTF", "Biến đổi chuỗi từ thành vector tần suất (TF)", [
            ("Không gian đặc trưng", "numFeatures = 32,768 chiều vector."),
            ("Hashing Trick", "Dùng hàm băm MurmurHash ánh xạ trực tiếp từ ngữ vào index vector."),
            ("Tiết kiệm RAM", "Không cần duy trì từ điển từ vựng (Vocabulary) khổng lồ trên driver.")
        ]),
        ("BƯỚC 3: IDF Estimator", "Tính trọng số nghịch đảo tài liệu (Inverse Doc Freq)", [
            ("Công thức IDF", "Giảm trọng số các từ xuất hiện phổ biến ở mọi tài liệu."),
            ("Tăng trọng số", "Khuếch đại các từ khóa đặc trưng có tính phân loại cao."),
            ("Đầu ra Pipeline", "Tạo cột 'features' vector sẵn sàng cho thuật toán phân loại.")
        ])
    ]
    for i, (title, sub, items) in enumerate(nlp_pipeline):
        c_left = Inches(0.8 + i * 4.0)
        create_card(s17, c_left, Inches(1.6), Inches(3.7), Inches(5.0), CARD_BG, BORDER_COLOR)
        tb = s17.shapes.add_textbox(c_left + Inches(0.2), Inches(1.8), Inches(3.3), Inches(4.5))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.bold = True
        p.font.size = Pt(13)
        p.font.color.rgb = NAVY
        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.bold = True
        p_sub.font.size = Pt(10.5)
        p_sub.font.color.rgb = ACCENT_BLUE
        p_sub.space_after = Pt(12)
        for k, v in items:
            format_bullet_point(tf, k, v, font_size=11, space_after=8)

    # =========================================================================
    # SLIDE 18: CHIẾN LƯỢC CHỐNG RÒ RỈ DỮ LIỆU (ANTI-DATA LEAKAGE)
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    add_header(s18, "17. Chiến lược Phân chia Dữ liệu & Chống Rò rỉ")
    add_footer(s18, 18)

    create_card(s18, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s18.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "NGUY CƠ RÒ RỈ DỮ LIỆU (DATA LEAKAGE)"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    format_bullet_point(tf, "Hiện tượng mâu thuẫn nhãn", "Trong 1.6M tweet, có 2,361 nhóm câu có nội dung giống hệt nhau nhưng bị gán nhãn trái ngược nhau (29,280 dòng).")
    format_bullet_point(tf, "Hậu quả nếu chia ngẫu nhiên", "Cùng một câu văn sẽ đồng thời rơi vào cả tập Train và tập Test, khiến mô hình 'học vẹt' và thổi phồng độ chính xác ảo.")
    format_bullet_point(tf, "Giải pháp triệt để", "Nhóm lọc bỏ hoàn toàn các nhóm bài viết mâu thuẫn nhãn trước khi tiến hành phân chia tập dữ liệu.")

    create_card(s18, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s18.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "CƠ CHẾ PHÂN CHIA XÁC ĐỊNH BẰNG HÀM BĂM"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    format_bullet_point(tf, "Quy tắc phân chia", "Sử dụng hàm băm phân tán: pmod(xxhash64(clean_text), 1000).")
    format_bullet_point(tf, "Tập Train (70%)", "Các mẫu có hash < 700 (106,209 dòng trên mẫu 10%).")
    format_bullet_point(tf, "Tập Validation (15%)", "Các mẫu có hash từ 700 đến 849 (22,826 dòng) dùng để tinh chỉnh siêu tham số.")
    format_bullet_point(tf, "Tập Test (15%)", "Các mẫu có hash >= 850 (22,812 dòng) dùng để đánh giá độc lập khách quan.")

    # =========================================================================
    # SLIDE 19: HUẤN LUYỆN VÀ TINH CHỈNH MÔ HÌNH (MODEL TUNING)
    # =========================================================================
    s19 = prs.slides.add_slide(blank_layout)
    add_header(s19, "18. Huấn luyện và Tinh chỉnh Siêu tham số (Model Tuning)")
    add_footer(s19, 19)

    create_card(s19, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s19.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "THUẬT TOÁN LOGISTIC REGRESSION"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    format_bullet_point(tf, "Ưu thế trên Big Data", "Khả năng mở rộng phân tán cực tốt, hội tụ nhanh với không gian đặc trưng lớn (32k chiều).")
    format_bullet_point(tf, "Hàm mất mát", "Cross-entropy kết hợp hàm kích hoạt Sigmoid đưa ra xác suất dự đoán P(Positive).")
    format_bullet_point(tf, "Chính quy hóa L2", "Áp dụng hệ số phạt Ridge (L2 penalty) để chống Overfitting khi số lượng đặc trưng lớn.")

    create_card(s19, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s19.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "KẾT QUẢ TUNING TRÊN TẬP VALIDATION"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    format_bullet_point(tf, "Thử nghiệm regParam = 0.01", "Validation Macro-F1: 0.7363 | Thời gian Fit: 12.22s.")
    format_bullet_point(tf, "Thử nghiệm regParam = 0.1", "Validation Macro-F1: 0.7522 | Thời gian Fit: 7.23s.")
    format_bullet_point(tf, "Đối chứng Naive Bayes", "Validation Macro-F1: 0.7244 | Thời gian Fit: 3.70s.")
    format_bullet_point(tf, "Mô hình được chọn", "Logistic Regression với regParam = 0.1 đạt F1 cao nhất và thời gian huấn luyện tối ưu nhất.")

    # =========================================================================
    # SLIDE 20: KẾT QUẢ ĐÁNH GIÁ MÔ HÌNH THỰC NGHIỆM (EMBED CONFUSION MATRIX)
    # =========================================================================
    s20 = prs.slides.add_slide(blank_layout)
    add_header(s20, "19. Kết quả Đánh giá Mô hình trên Tập Kiểm thử (Test Set)")
    add_footer(s20, 20)

    img_cm = CHARTS_DIR / "confusion_matrix.png"
    if img_cm.is_file():
        s20.shapes.add_picture(str(img_cm), Inches(0.8), Inches(1.6), width=Inches(5.5))

    create_card(s20, Inches(6.6), Inches(1.6), Inches(5.9), Inches(5.0), CARD_BG, BORDER_COLOR)
    table_eval = s20.shapes.add_table(4, 4, Inches(6.8), Inches(1.8), Inches(5.5), Inches(2.2)).table
    headers_eval = ["Mô hình", "Accuracy", "Macro-F1", "Nhận xét"]
    for i, h in enumerate(headers_eval):
        style_table_cell(table_eval.cell(0, i), h, bold=True, bg_rgb=NAVY, text_rgb=WHITE, font_size=11, align=PP_ALIGN.CENTER)

    eval_data = [
        ("Baseline (Đa số)", "50.49%", "0.3355", "Mức sàn ngẫu nhiên"),
        ("Naive Bayes", "72.44%", "0.7244", "Mô hình đối chứng"),
        ("Logistic Regression", "74.75%", "0.7475", "Tối ưu và cân bằng nhất")
    ]
    for r_idx, row_vals in enumerate(eval_data, start=1):
        for c_idx, val in enumerate(row_vals):
            bg = RGBColor(0xEA, 0xF2, 0xF8) if r_idx == 3 else WHITE
            style_table_cell(table_eval.cell(r_idx, c_idx), val, bold=(r_idx == 3), bg_rgb=bg, font_size=10, align=PP_ALIGN.CENTER)

    tb_cm = s20.shapes.add_textbox(Inches(6.8), Inches(4.3), Inches(5.5), Inches(2.2))
    tf_cm = tb_cm.text_frame
    tf_cm.word_wrap = True
    p = tf_cm.paragraphs[0]
    p.text = "PHÂN TÍCH MA TRẬN NHẦM LẪN:"
    p.font.bold = True
    p.font.size = Pt(12)
    p.font.color.rgb = NAVY
    p.space_after = Pt(6)
    format_bullet_point(tf_cm, "Độ chính xác cao", "Mô hình phân loại đúng 8,465 mẫu tiêu cực (TN) và 8,586 mẫu tích cực (TP).")
    format_bullet_point(tf_cm, "Cân bằng tuyệt đối", "Tỷ lệ dự đoán đúng hai lớp đồng đều nhau (~74.8%), chứng minh mô hình không bị thiên vị hay lệch lớp.")

    # =========================================================================
    # SLIDE 21: ĐO LƯỜNG HIỆU NĂNG SPARK CACHING (EMBED PERFORMANCE CHART)
    # =========================================================================
    s21 = prs.slides.add_slide(blank_layout)
    add_header(s21, "20. Đo lường Hiệu năng Bộ nhớ đệm (Spark Caching Benchmark)")
    add_footer(s21, 21)

    img_perf = CHARTS_DIR / "performance.png"
    if img_perf.is_file():
        s21.shapes.add_picture(str(img_perf), Inches(0.8), Inches(1.6), width=Inches(6.8))

    create_card(s21, Inches(7.8), Inches(1.6), Inches(4.7), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s21.shapes.add_textbox(Inches(8.0), Inches(1.8), Inches(4.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Ý NGHĨA CỦA SPARK CACHE()"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    format_bullet_point(tf, "Cơ chế In-memory", "Khi gọi .cache(), kết quả tính toán của DataFrame được lưu trữ trực tiếp trong bộ nhớ RAM của Worker nodes.")
    format_bullet_point(tf, "Tránh tính toán lại (Recompute)", "Các lượt truy vấn thứ 2 và thứ 3 đọc thẳng từ RAM, không cần quét lại từ đĩa hay lặp lại các phép biến đổi rườm rà.")
    format_bullet_point(tf, "Khuyến nghị vận hành", "Nên áp dụng Caching cho các DataFrame được tái sử dụng nhiều lần (như trong huấn luyện lặp ML) và giải phóng bằng unpersist() ngay khi hoàn tất.")

    # =========================================================================
    # SLIDE 22: GIAO DIỆN DESKTOP GUI & KIỂM THỬ MÃ NGUỒN
    # =========================================================================
    s22 = prs.slides.add_slide(blank_layout)
    add_header(s22, "21. Giao diện Desktop GUI & Đảm bảo Chất lượng Mã nguồn")
    add_footer(s22, 22)

    create_card(s22, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s22.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "GIAO DIỆN DESKTOP GUI (TKINTER)"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    format_bullet_point(tf, "Chuyển đổi nguồn linh hoạt", "Hỗ trợ chọn đọc dữ liệu từ Local File System hoặc Hadoop HDFS URI chỉ bằng 1 cú nhấp chuột.")
    format_bullet_point(tf, "Điều khiển Pipeline", "Các nút bấm chạy độc lập từng bước (Prepare, Analyze, Train, Benchmark) hoặc chạy toàn bộ (Run All).")
    format_bullet_point(tf, "Giám sát thời gian thực", "Tích hợp Console Log đa luồng (threading) không gây đóng băng giao diện khi Spark đang tính toán.")
    format_bullet_point(tf, "Demo suy luận cảm xúc", "Ô nhập câu tweet tiếng Anh bất kỳ và nhận kết quả dự đoán kèm xác suất %.")

    create_card(s22, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s22.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "KIỂM THỬ MÃ NGUỒN TỰ ĐỘNG (CI/UNIT TESTS)"
    p.font.bold = True
    p.font.size = Pt(14)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    format_bullet_point(tf, "Bộ 13 Unit Tests tự động", "Bảo vệ toàn diện các module: làm sạch (cleaning), trích xuất đặc trưng, huấn luyện ML, benchmark, GUI và sinh báo cáo.")
    format_bullet_point(tf, "Kiểm thử không phụ thuộc Spark nặng", "Sử dụng synthetic smoke-test data (400 dòng) giúp chạy kiểm thử toàn bộ hệ thống chỉ mất dưới 0.1 giây.")
    format_bullet_point(tf, "Kết quả thực tế", "13/13 tests PASSED 100%, đảm bảo hệ thống không phát sinh lỗi hồi quy (regression).")

    # =========================================================================
    # SLIDE 23: PHÂN CÔNG CÔNG VIỆC TRONG NHÓM (50/50 WORKLOAD)
    # =========================================================================
    s23 = prs.slides.add_slide(blank_layout)
    add_header(s23, "22. Phân công Công việc và Đóng góp của Thành viên")
    add_footer(s23, 23)

    create_card(s23, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s23.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "VÕ MINH CẢNH (MSSV: 2001230065)"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = NAVY
    p_role = tf.add_paragraph()
    p_role.text = "Nhóm trưởng  |  Phụ trách Xử lý & Học máy"
    p_role.font.bold = True
    p_role.font.size = Pt(11)
    p_role.font.color.rgb = ACCENT_BLUE
    p_role.space_after = Pt(10)
    format_bullet_point(tf, "Tuần 1", "Cài đặt môi trường Python, PySpark; thiết lập cấu trúc mã nguồn dự án.")
    format_bullet_point(tf, "Tuần 2", "Viết module làm sạch văn bản (cleaning.py), xử lý regex và chuẩn hóa Parquet.")
    format_bullet_point(tf, "Tuần 3", "Xây dựng Pipeline Spark MLlib (TF-IDF + Logistic Regression), tuning siêu tham số.")
    format_bullet_point(tf, "Tuần 4", "Lập trình giao diện Desktop GUI demo, viết bộ Unit Tests và kịch bản demo.")

    create_card(s23, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s23.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "HỒ THỊ THANH NHÃ (MSSV: 2001230592)"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = NAVY
    p_role = tf.add_paragraph()
    p_role.text = "Thành viên  |  Phụ trách Hạ tầng & Phân tích"
    p_role.font.bold = True
    p_role.font.size = Pt(11)
    p_role.font.color.rgb = ACCENT_BLUE
    p_role.space_after = Pt(10)
    format_bullet_point(tf, "Tuần 1", "Khảo sát kiến trúc Hadoop HDFS, cấu hình NameNode/DataNode Docker.")
    format_bullet_point(tf, "Tuần 2", "Nạp dữ liệu vào HDFS; viết các truy vấn Spark SQL thống kê hành vi (EDA).")
    format_bullet_point(tf, "Tuần 3", "Huấn luyện mô hình đối chứng Naive Bayes, thực hiện Benchmark Spark Cache.")
    format_bullet_point(tf, "Tuần 4", "Thực nghiệm so sánh lưu trữ CSV vs Parquet; hoàn thiện tài liệu báo cáo cuối kỳ.")

    # =========================================================================
    # SLIDE 24: KHÓ KHĂN KỸ THUẬT & HƯỚNG PHÁT TRIỂN
    # =========================================================================
    s24 = prs.slides.add_slide(blank_layout)
    add_header(s24, "23. Khó khăn Kỹ thuật Đã Giải quyết & Hướng Phát triển")
    add_footer(s24, 24)

    create_card(s24, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s24.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "CÁC KHÓ KHĂN KỸ THUẬT ĐÃ VƯỢT QUA"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    format_bullet_point(tf, "Lỗi Hadoop Native trên Windows", "Giải quyết triệt để bằng cách đóng gói cụm HDFS vào Docker Linux container chuẩn.")
    format_bullet_point(tf, "Rò rỉ dữ liệu (Data Leakage)", "Khử sạch 2,361 nhóm câu trùng văn bản khác nhãn và dùng hàm băm xác định để phân tách tập.")
    format_bullet_point(tf, "Tràn bộ nhớ đệm JVM", "Điều chỉnh cấu hình shuffle partitions và cấp phát heap RAM hợp lý.")

    create_card(s24, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.0), CARD_BG, BORDER_COLOR)
    tb = s24.shapes.add_textbox(Inches(7.0), Inches(1.8), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "CÁC ĐỊNH HƯỚNG PHÁT TRIỂN TIẾP THEO"
    p.font.bold = True
    p.font.size = Pt(13)
    p.font.color.rgb = NAVY
    p.space_after = Pt(10)
    format_bullet_point(tf, "Tích hợp Streaming Path", "Kết hợp Apache Kafka và Spark Structured Streaming để nhận và phân loại luồng tweet theo thời gian thực (đạt Lambda Architecture).")
    format_bullet_point(tf, "Bổ sung đặc trưng N-gram", "Tích hợp NGram(n=2) để phân biệt các cụm từ đảo ngữ như 'not good', 'never like'.")
    format_bullet_point(tf, "Nâng cấp Web Dashboard", "Chuyển đổi giao diện Tkinter sang nền tảng Web tương tác hiện đại bằng Streamlit / Plotly.")

    # =========================================================================
    # SLIDE 25: TỔNG KẾT VÀ HỎI ĐÁP (Q&A)
    # =========================================================================
    s25 = prs.slides.add_slide(blank_layout)
    set_slide_background(s25, prs, RGBColor(0x15, 0x2C, 0x4A))

    create_card(s25, Inches(1.0), Inches(1.2), Inches(11.333), Inches(5.1), RGBColor(0x1E, 0x3C, 0x64), RGBColor(0x2E, 0x75, 0xB6))
    tb = s25.shapes.add_textbox(Inches(1.5), Inches(1.5), Inches(10.333), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "KẾT LUẬN & ĐÁNH GIÁ ĐỒ ÁN"
    p0.font.bold = True
    p0.font.size = Pt(22)
    p0.font.color.rgb = WHITE
    p0.space_after = Pt(16)

    format_bullet_point(tf, "Hoàn thành 100% mục tiêu", "Xây dựng thành công Big Data Pipeline phân tán xử lý 1.6 triệu tweet từ đầu đến cuối.", font_size=13, space_after=8)
    format_bullet_point(tf, "Kết quả mô hình vượt trội", "Logistic Regression đạt Accuracy 74.75% và Macro-F1 0.7475, suy luận cực nhanh 1.06s cho 22k mẫu.", font_size=13, space_after=8)
    format_bullet_point(tf, "Chứng minh ưu thế Big Data", "Định dạng Parquet nhanh gấp 37.8 lần CSV thô; Spark Cache tối ưu hóa truy vấn lặp lại vượt bậc.", font_size=13, space_after=8)
    format_bullet_point(tf, "Sẵn sàng ứng dụng thực tế", "Giao diện Desktop GUI trực quan, bộ 13 Unit Tests bảo đảm an toàn hệ thống.", font_size=13, space_after=18)

    p_qa = tf.add_paragraph()
    p_qa.text = "XIN CHÂN THÀNH CẢM ƠN THẦY CÔ VÀ HỘI ĐỒNG ĐÃ LẮNG NGHE!\nCHÚNG EM XIN SẴN SÀNG BƯỚC VÀO PHẦN TRẢ LỜI CÂU HỎI & DEMO."
    p_qa.font.bold = True
    p_qa.font.size = Pt(15)
    p_qa.font.color.rgb = RGBColor(0x92, 0xC5, 0xDE)
    p_qa.alignment = PP_ALIGN.CENTER

    # Save
    out_dir = Path("report")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "Thuyet_Trinh_BigData_Nhom9.pptx"
    prs.save(str(out_file))
    print(f"Generated PPTX successfully at: {out_file.resolve()}")

if __name__ == "__main__":
    main()
