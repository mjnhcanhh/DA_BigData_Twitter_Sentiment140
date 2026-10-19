"""
Script tự động đóng gói toàn bộ hồ sơ nghiệm thu Báo cáo Cuối kỳ Big Data - Nhóm 09
Thành viên: Võ Minh Cảnh — Trưởng nhóm (2001230065), Hồ Thị Thanh Nhã — Thành viên (2001230592)

Chức năng:
1. Thu thập báo cáo chính thức: PDF (33 trang), DOCX (3.3 MB), HTML, Slide PPTX, Báo cáo tiến độ DOCX & MD, README hướng dẫn.
2. Đóng gói TOÀN BỘ REPOSITORY MÃ NGUỒN (source_code/):
   - main.py, gui.py, requirements.txt, requirements-dev.txt
   - twitter_spark/, dags/, docker/, scripts/, tests/, models/, java/, data/demo/
3. Thu thập Video Demo MP4 chất lượng cao (video_demo/):
   - video_demo_gui_pipeline.mp4 (45 giây, HD 1280x720, 20 FPS)
   - README_VideoDemo.md (kịch bản demo theo mốc thời gian)
4. Thu thập toàn bộ 14 hình ảnh gốc (figures/):
   - Sơ đồ kiến trúc (Hình 3.1), Airflow UI (Hình 3.2), HDFS Web UI (Hình 3.3), Dashboard GUI (Hình 4.1), Spark Web UI (Hình 4.2), Prediction Demo (Hình 4.3), 7 biểu đồ RQ1-RQ5 (Hình 5.1-5.7), Gantt Chart (Hình C.1).
5. Thu thập toàn bộ 10 bảng dữ liệu định lượng CSV từ Spark SQL và MLlib (tables/).
6. Thu thập toàn bộ 7 biểu đồ phân tích thực nghiệm PNG (charts/).
7. Thu thập toàn bộ 8 tệp nhật ký thực thi (logs/):
   - hdfs_upload.log, hdfs_cluster_status.log, spark_execution.log (show(5) sample), airflow_dag_run.log, airflow_detailed_tasks.log, unittest_results.log (14/14 pass), git_commit_history.log, bang_loi_va_su_co.log.
8. Thu thập toàn bộ 4 tệp JSON tổng hợp định lượng (summary/).
9. Đóng gói thành tệp nén ZIP hoàn chỉnh:
   - report/Nhom09_BaoCaoCuoiKy_BigData_HoSoNghiemThu.zip
   - Nhom09_BaoCaoCuoiKy_BigData_HoSoNghiemThu.zip (tại thư mục gốc)
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SUBMISSION_DIR = PROJECT_ROOT / "submission_package"
EVIDENCE_DIR = SUBMISSION_DIR / "minh_chung_truc_quan"
SOURCE_CODE_DIR = SUBMISSION_DIR / "source_code"
ZIP_OUTPUT = PROJECT_ROOT / "report" / "Nhom09_BaoCaoCuoiKy_BigData_HoSoNghiemThu.zip"
ZIP_ROOT_COPY = PROJECT_ROOT / "Nhom09_BaoCaoCuoiKy_BigData_HoSoNghiemThu.zip"

try:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [PACKAGE] {msg}")


def copy_tree_filtered(src_dir: Path, dst_dir: Path, ignore_patterns=None):
    if ignore_patterns is None:
        ignore_patterns = shutil.ignore_patterns(
            "*.pyc", "__pycache__", ".pytest_cache", ".git", "*.tmp", ".venv", ".test-artifacts"
        )
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    shutil.copytree(src_dir, dst_dir, ignore=ignore_patterns)


def main():
    log("Bắt đầu chuẩn bị gói hồ sơ nộp bài nghiệm thu toàn diện Nhóm 09...")

    # Làm sạch thư mục tạm
    if SUBMISSION_DIR.exists():
        shutil.rmtree(SUBMISSION_DIR)
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    SOURCE_CODE_DIR.mkdir(parents=True, exist_ok=True)

    # Tạo các thư mục trực tiếp tại root của package VÀ bên trong minh_chung_truc_quan
    dirs_to_create = ["figures", "tables", "logs", "charts", "summary", "video_demo"]
    for dname in dirs_to_create:
        (SUBMISSION_DIR / dname).mkdir(parents=True, exist_ok=True)
        (EVIDENCE_DIR / dname).mkdir(parents=True, exist_ok=True)

    # 1. Sao chép tài liệu báo cáo chính
    log("1. Sao chép tài liệu báo cáo, slide thuyết trình và hướng dẫn...")
    report_files = [
        ("report/BaoCaoCuoiKy_BigData_Nhom9.pdf", "BaoCaoCuoiKy_BigData_Nhom9.pdf"),
        ("report/BaoCaoCuoiKy_BigData_Nhom9.docx", "BaoCaoCuoiKy_BigData_Nhom9.docx"),
        ("report/BaoCaoCuoiKy_BigData_Nhom9.html", "BaoCaoCuoiKy_BigData_Nhom9.html"),
        ("report/BaCaoTienDo_BigData_Nhom9.docx", "BaCaoTienDo_BigData_Nhom9.docx"),
        ("outputs/logs/bang_loi_va_nhat_ky_tien_do.md", "BaoCaoTienDo_Va_BangXuLyLoi.md"),
        ("report/Thuyet_Trinh_BigData_Nhom9.pptx", "Thuyet_Trinh_BigData_Nhom9.pptx"),
        ("report/ThuyetTrinh_BigData_Nhom9.pptx", "ThuyetTrinh_BigData_Nhom9.pptx"),
        ("README.md", "README_HuongDanCaiDat.md"),
        ("outputs/logs/git_commit_history.log", "git_commit_history.log"),
        ("outputs/logs/bang_loi_va_su_co.log", "bang_loi_va_su_co.log"),
    ]
    for rel_src, dst_name in report_files:
        src = PROJECT_ROOT / rel_src
        if src.is_file():
            shutil.copy2(src, SUBMISSION_DIR / dst_name)
            log(f"  [Tài liệu] {dst_name} ({src.stat().st_size / 1024:.1f} KB)")
        else:
            log(f"  CẢNH BÁO: Không tìm thấy {rel_src}")

    # 2. Đóng gói TOÀN BỘ REPOSITORY MÃ NGUỒN vào source_code/
    log("2. Đóng gói toàn bộ repository mã nguồn đầy đủ vào source_code/...")
    root_files = ["main.py", "gui.py", "requirements.txt", "requirements-dev.txt"]
    for rf in root_files:
        fpath = PROJECT_ROOT / rf
        if fpath.is_file():
            shutil.copy2(fpath, SOURCE_CODE_DIR / rf)
            # Đồng thời sao chép ra root package để chạy tiện lợi
            shutil.copy2(fpath, SUBMISSION_DIR / rf)
            log(f"  [Mã nguồn] Đã sao chép: {rf}")

    code_dirs = ["twitter_spark", "dags", "docker", "scripts", "tests", "models", "java"]
    for cd in code_dirs:
        src_d = PROJECT_ROOT / cd
        if src_d.is_dir():
            copy_tree_filtered(src_d, SOURCE_CODE_DIR / cd)
            log(f"  [Mã nguồn] Đã sao chép thư mục: {cd}/")

    # Sao chép dữ liệu demo
    demo_dir = PROJECT_ROOT / "data" / "demo"
    if demo_dir.is_dir():
        copy_tree_filtered(demo_dir, SOURCE_CODE_DIR / "data" / "demo")
        log("  [Mã nguồn] Đã sao chép data/demo/ phục vụ kiểm thử nhanh")

    # 3. Thu thập Video Demo MP4
    log("3. Thu thập Video Demo MP4 vào video_demo/...")
    video_src = PROJECT_ROOT / "outputs" / "video_demo"
    if video_src.is_dir():
        for vf in video_src.glob("*.*"):
            shutil.copy2(vf, SUBMISSION_DIR / "video_demo" / vf.name)
            shutil.copy2(vf, EVIDENCE_DIR / "video_demo" / vf.name)
            log(f"  [Video Demo] {vf.name} ({vf.stat().st_size / 1024:.1f} KB)")

    # 4. Thu thập 14 hình ảnh sơ đồ & UI vào figures/
    log("4. Thu thập toàn bộ 14 hình ảnh minh chứng vào figures/...")
    figures_src = PROJECT_ROOT / "report" / "figures"
    if not figures_src.is_dir():
        figures_src = PROJECT_ROOT / "outputs" / "charts"
    for img in figures_src.glob("*.png"):
        shutil.copy2(img, SUBMISSION_DIR / "figures" / img.name)
        shutil.copy2(img, EVIDENCE_DIR / "figures" / img.name)
        log(f"  [Hình ảnh] {img.name} ({img.stat().st_size / 1024:.1f} KB)")

    # 5. Thu thập 10 bảng dữ liệu định lượng CSV vào tables/
    log("5. Thu thập toàn bộ 10 bảng kết quả CSV vào tables/...")
    tables_dir = PROJECT_ROOT / "outputs" / "tables"
    if tables_dir.is_dir():
        for tbl in tables_dir.glob("*.csv"):
            shutil.copy2(tbl, SUBMISSION_DIR / "tables" / tbl.name)
            shutil.copy2(tbl, EVIDENCE_DIR / "tables" / tbl.name)
            log(f"  [Bảng CSV] {tbl.name} ({tbl.stat().st_size / 1024:.1f} KB)")

    # 6. Thu thập toàn bộ 7 biểu đồ PNG vào charts/
    log("6. Thu thập toàn bộ 7 biểu đồ phân tích thực nghiệm vào charts/...")
    charts_dir = PROJECT_ROOT / "outputs" / "charts"
    if charts_dir.is_dir():
        for ch in charts_dir.glob("*.png"):
            shutil.copy2(ch, SUBMISSION_DIR / "charts" / ch.name)
            shutil.copy2(ch, EVIDENCE_DIR / "charts" / ch.name)
            log(f"  [Biểu đồ] {ch.name} ({ch.stat().st_size / 1024:.1f} KB)")

    # 7. Thu thập toàn bộ 8 tệp log thực thi vào logs/
    log("7. Thu thập toàn bộ 8 tệp log thực thi thực tế vào logs/...")
    logs_dir = PROJECT_ROOT / "outputs" / "logs"
    if logs_dir.is_dir():
        for lg in logs_dir.glob("*.*"):
            shutil.copy2(lg, SUBMISSION_DIR / "logs" / lg.name)
            shutil.copy2(lg, EVIDENCE_DIR / "logs" / lg.name)
            log(f"  [Nhật ký Log] {lg.name} ({lg.stat().st_size / 1024:.1f} KB)")

    # 8. Thu thập 4 tệp JSON tổng hợp vào summary/
    log("8. Thu thập toàn bộ 4 tệp JSON tổng hợp vào summary/...")
    for json_name in ["data_quality.json", "evaluation.json", "performance.json", "run_manifest.json"]:
        json_file = PROJECT_ROOT / "outputs" / json_name
        if json_file.is_file():
            shutil.copy2(json_file, SUBMISSION_DIR / "summary" / json_name)
            shutil.copy2(json_file, EVIDENCE_DIR / "summary" / json_name)
            log(f"  [JSON] {json_name}")

    # 9. Nén toàn bộ thành tệp ZIP
    log("9. Đang nén toàn bộ gói hồ sơ thành tệp ZIP: Nhom09_BaoCaoCuoiKy_BigData_HoSoNghiemThu.zip ...")
    ZIP_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zip_f:
        for file_path in SUBMISSION_DIR.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(SUBMISSION_DIR)
                zip_f.write(file_path, arcname=str(rel_path))

    # Sao chép ra thư mục gốc để người dùng dễ dàng nộp bài
    shutil.copy2(ZIP_OUTPUT, ZIP_ROOT_COPY)

    log("=" * 70)
    log("HOÀN THÀNH ĐÓNG GÓI TOÀN DIỆN!")
    log(f"Tệp nộp bài nghiệm thu 1: {ZIP_OUTPUT.resolve()}")
    log(f"Tệp nộp bài nghiệm thu 2 (thư mục gốc): {ZIP_ROOT_COPY.resolve()}")
    log(f"Dung lượng tệp ZIP: {ZIP_OUTPUT.stat().st_size / (1024 * 1024):.2f} MB")
    log(f"Thư mục giải nén sẵn sàng kiểm chứng: {SUBMISSION_DIR.resolve()}")
    log("=" * 70)


if __name__ == "__main__":
    main()
