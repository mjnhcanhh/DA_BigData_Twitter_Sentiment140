from __future__ import annotations

import argparse
import json
import os
import queue
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path
from typing import Any

import tkinter as tk
from tkinter import filedialog, messagebox, ttk


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = PROJECT_ROOT / "data" / "raw" / "training.1600000.processed.noemoticon.csv"


def validate_sample_fraction(value: str) -> float:
    try:
        fraction = float(value)
    except ValueError as exc:
        raise ValueError("Tỷ lệ mẫu phải là một số, ví dụ 0.10 hoặc 1.0.") from exc
    if not 0 < fraction <= 1:
        raise ValueError("Tỷ lệ mẫu phải lớn hơn 0 và không vượt quá 1.")
    return fraction


def powershell_command(script_name: str, *arguments: object) -> list[str]:
    return [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(PROJECT_ROOT / "scripts" / script_name),
        *[str(argument) for argument in arguments],
    ]


def load_result_summary(project_root: Path = PROJECT_ROOT) -> dict[str, str]:
    summary = {
        "source": "Chưa có kết quả",
        "raw_rows": "—",
        "clean_rows": "—",
        "macro_f1": "—",
        "result_type": "—",
    }
    quality_path = project_root / "outputs" / "data_quality.json"
    evaluation_path = project_root / "outputs" / "evaluation.json"

    try:
        quality = json.loads(quality_path.read_text(encoding="utf-8"))
        source = str(quality.get("source", "Không xác định"))
        summary["source"] = source
        summary["raw_rows"] = f"{int(quality.get('raw_rows', 0)):,}"
        summary["clean_rows"] = f"{int(quality.get('clean_rows', 0)):,}"
        summary["result_type"] = "Dữ liệu demo" if "data\\demo" in source or "data/demo" in source else "Dữ liệu thật"
    except (OSError, ValueError, TypeError):
        pass

    try:
        evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
        lr = evaluation["test_results"]["tfidf_logistic_regression"]
        summary["macro_f1"] = f"{float(lr['macro_f1']):.4f}"
    except (OSError, ValueError, TypeError, KeyError):
        pass
    return summary


class ProjectGui:
    BG = "#F1F5F9"
    PANEL = "#FFFFFF"
    INK = "#0F172A"
    MUTED = "#64748B"
    BLUE = "#2563EB"
    TEAL = "#0F766E"
    ORANGE = "#C2410C"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.events: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.process: subprocess.Popen[str] | None = None
        self.action_buttons: list[ttk.Button] = []

        self.data_path = tk.StringVar(value=str(DEFAULT_DATA))
        self.sample_fraction = tk.StringVar(value="0.10")
        self.task_status = tk.StringVar(value="Sẵn sàng")
        self.source_value = tk.StringVar(value="Chưa có kết quả")
        self.raw_value = tk.StringVar(value="—")
        self.clean_value = tk.StringVar(value="—")
        self.f1_value = tk.StringVar(value="—")
        self.result_type_value = tk.StringVar(value="—")

        self._configure_window()
        self._configure_styles()
        self._build_layout()
        self.refresh_results()
        self.root.after(100, self._poll_events)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _configure_window(self) -> None:
        self.root.title("Twitter Sentiment140 • Spark & HDFS")
        self.root.geometry("1180x780")
        self.root.minsize(980, 680)
        self.root.configure(bg=self.BG)

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TFrame", background=self.BG)
        style.configure("Panel.TFrame", background=self.PANEL)
        style.configure("TLabel", background=self.BG, foreground=self.INK, font=("Segoe UI", 10))
        style.configure("Panel.TLabel", background=self.PANEL, foreground=self.INK, font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=self.PANEL, foreground=self.INK, font=("Segoe UI Semibold", 12))
        style.configure("CardTitle.TLabel", background=self.PANEL, foreground=self.MUTED, font=("Segoe UI", 9))
        style.configure("CardValue.TLabel", background=self.PANEL, foreground=self.INK, font=("Segoe UI Semibold", 16))
        style.configure("Primary.TButton", font=("Segoe UI Semibold", 10), padding=(12, 7))
        style.configure("Secondary.TButton", font=("Segoe UI", 10), padding=(10, 6))
        style.configure("Danger.TButton", font=("Segoe UI", 10), padding=(10, 6))
        style.configure("TEntry", padding=7)
        style.configure("TCombobox", padding=6)

    def _build_layout(self) -> None:
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_flow()

        content = ttk.Frame(self.root, padding=(16, 6, 16, 12))
        content.grid(row=2, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=0, minsize=390)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        controls = ttk.Frame(content, style="Panel.TFrame", padding=14)
        controls.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        controls.grid_columnconfigure(0, weight=1)
        self._build_controls(controls)

        right = ttk.Frame(content)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)
        self._build_results(right)
        self._build_log(right)

    def _build_header(self) -> None:
        header = tk.Frame(self.root, bg=self.INK, padx=22, pady=11)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        tk.Label(
            header,
            text="TWITTER SENTIMENT140",
            bg=self.INK,
            fg="#93C5FD",
            font=("Segoe UI Semibold", 10),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            header,
            text="Apache Spark & HDFS Control Center",
            bg=self.INK,
            fg="white",
            font=("Segoe UI Semibold", 19),
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))
        tk.Label(
            header,
            textvariable=self.task_status,
            bg="#1E293B",
            fg="#E2E8F0",
            padx=14,
            pady=7,
            font=("Segoe UI", 10),
        ).grid(row=0, column=1, rowspan=2, sticky="e")

    def _build_flow(self) -> None:
        flow = tk.Frame(self.root, bg="#DBEAFE", padx=20, pady=7)
        flow.grid(row=1, column=0, sticky="ew")
        items = [
            ("1", "CSV Sentiment140"),
            ("2", "Local hoặc HDFS"),
            ("3", "Spark xử lý & ML"),
            ("4", "Bảng, biểu đồ, mô hình"),
        ]
        for index, (number, label) in enumerate(items):
            block = tk.Frame(flow, bg="#DBEAFE")
            block.pack(side="left", expand=True)
            tk.Label(block, text=number, bg=self.BLUE, fg="white", width=2, font=("Segoe UI Semibold", 10)).pack(side="left")
            tk.Label(block, text=label, bg="#DBEAFE", fg=self.INK, font=("Segoe UI Semibold", 10), padx=7).pack(side="left")
            if index < len(items) - 1:
                tk.Label(flow, text="→", bg="#DBEAFE", fg=self.BLUE, font=("Segoe UI", 16)).pack(side="left")

    def _build_controls(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="Dữ liệu và cấu hình", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(parent, text="File CSV Sentiment140", style="CardTitle.TLabel").grid(row=1, column=0, sticky="w", pady=(12, 4))

        data_row = ttk.Frame(parent, style="Panel.TFrame")
        data_row.grid(row=2, column=0, sticky="ew")
        data_row.grid_columnconfigure(0, weight=1)
        ttk.Entry(data_row, textvariable=self.data_path).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(data_row, text="Chọn…", command=self._choose_data, style="Secondary.TButton").grid(row=0, column=1)

        ttk.Label(parent, text="Tỷ lệ mẫu dùng để huấn luyện", style="CardTitle.TLabel").grid(row=3, column=0, sticky="w", pady=(12, 4))
        fraction = ttk.Combobox(parent, textvariable=self.sample_fraction, values=("0.01", "0.05", "0.10", "0.25", "0.50", "1.0"), state="normal")
        fraction.grid(row=4, column=0, sticky="ew")

        ttk.Separator(parent).grid(row=5, column=0, sticky="ew", pady=16)
        ttk.Label(parent, text="1. Chuẩn bị và kiểm tra", style="Section.TLabel").grid(row=6, column=0, sticky="w")
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.grid(row=7, column=0, sticky="ew", pady=(8, 0))
        for column in (0, 1):
            row.grid_columnconfigure(column, weight=1)
        self._task_button(row, "Cài môi trường", lambda: self._run_script("Cài môi trường", "setup.ps1"), 0, 0)
        self._task_button(row, "Chạy kiểm thử", lambda: self._run_script("Kiểm thử", "test.ps1"), 0, 1)

        ttk.Label(parent, text="2. Chạy Apache Spark local", style="Section.TLabel").grid(row=8, column=0, sticky="w", pady=(16, 0))
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.grid(row=9, column=0, sticky="ew", pady=(8, 0))
        for column in (0, 1):
            row.grid_columnconfigure(column, weight=1)
        self._task_button(row, "Demo nhanh", lambda: self._run_script("Demo nhanh", "demo.ps1"), 0, 0, primary=True)
        self._task_button(row, "Chạy dữ liệu thật", self._run_local, 0, 1, primary=True)

        ttk.Label(parent, text="3. Hadoop/HDFS bằng Docker", style="Section.TLabel").grid(row=10, column=0, sticky="w", pady=(16, 0))
        hdfs = ttk.Frame(parent, style="Panel.TFrame")
        hdfs.grid(row=11, column=0, sticky="ew", pady=(8, 0))
        for column in (0, 1):
            hdfs.grid_columnconfigure(column, weight=1)
        self._task_button(hdfs, "Khởi động HDFS", lambda: self._run_script("Khởi động HDFS", "hdfs_start.ps1"), 0, 0)
        self._task_button(hdfs, "Upload CSV", self._upload_hdfs, 0, 1)
        self._task_button(hdfs, "Chạy Spark + HDFS", self._run_hdfs, 1, 0)
        self._task_button(hdfs, "Chạy tất cả HDFS", self._run_all_hdfs, 1, 1, primary=True)
        self._task_button(hdfs, "Xem trạng thái", lambda: self._run_script("Trạng thái HDFS", "hdfs_status.ps1"), 2, 0)
        self._task_button(hdfs, "Dừng HDFS", lambda: self._run_script("Dừng HDFS", "hdfs_stop.ps1"), 2, 1)

        stop = ttk.Button(parent, text="Dừng tác vụ đang chạy", command=self._stop_task, style="Danger.TButton", state="disabled")
        stop.grid(row=12, column=0, sticky="ew", pady=(16, 0))
        self.stop_button = stop

    def _task_button(self, parent: ttk.Frame, text: str, command, row: int, column: int, primary: bool = False) -> None:
        button = ttk.Button(parent, text=text, command=command, style="Primary.TButton" if primary else "Secondary.TButton")
        button.grid(row=row, column=column, sticky="ew", padx=(0 if column == 0 else 4, 4 if column == 0 else 0), pady=3)
        self.action_buttons.append(button)

    def _build_results(self, parent: ttk.Frame) -> None:
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=16)
        panel.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        for column in range(4):
            panel.grid_columnconfigure(column, weight=1)
        ttk.Label(panel, text="Kết quả gần nhất", style="Section.TLabel").grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Label(panel, textvariable=self.source_value, style="CardTitle.TLabel", wraplength=650).grid(row=1, column=0, columnspan=4, sticky="w", pady=(3, 10))
        self._metric_card(panel, "Dữ liệu gốc", self.raw_value, 0)
        self._metric_card(panel, "Sau làm sạch", self.clean_value, 1)
        self._metric_card(panel, "Macro-F1 (LR)", self.f1_value, 2)
        self._metric_card(panel, "Loại kết quả", self.result_type_value, 3)

        links = ttk.Frame(panel, style="Panel.TFrame")
        links.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(12, 0))
        ttk.Button(links, text="Mở biểu đồ", command=lambda: self._open_path(PROJECT_ROOT / "outputs" / "charts")).pack(side="left", padx=(0, 4))
        ttk.Button(links, text="Mở bảng kết quả", command=lambda: self._open_path(PROJECT_ROOT / "outputs" / "tables")).pack(side="left", padx=4)
        ttk.Button(links, text="Spark UI (4040)", command=lambda: webbrowser.open("http://localhost:4040")).pack(side="left", padx=4)
        ttk.Button(links, text="NameNode UI (9870)", command=lambda: webbrowser.open("http://localhost:9870")).pack(side="left", padx=4)
        ttk.Button(links, text="Cập nhật báo cáo", command=self._populate_report_action).pack(side="left", padx=4)
        ttk.Button(links, text="Mở báo cáo", command=lambda: self._open_path(PROJECT_ROOT / "report" / "bao_cao_cuoi_ky.md")).pack(side="left", padx=4)
        ttk.Button(links, text="Làm mới", command=self.refresh_results).pack(side="right")

    def _metric_card(self, parent: ttk.Frame, title: str, variable: tk.StringVar, column: int) -> None:
        card = ttk.Frame(parent, style="Panel.TFrame")
        card.grid(row=2, column=column, sticky="nsew", padx=(0 if column == 0 else 10, 0))
        ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(card, textvariable=variable, style="CardValue.TLabel").pack(anchor="w", pady=(3, 0))

    def _build_log(self, parent: ttk.Frame) -> None:
        panel = ttk.Frame(parent, style="Panel.TFrame", padding=14)
        panel.grid(row=1, column=0, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(2, weight=1)
        ttk.Label(panel, text="Nhật ký chạy chương trình", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        self.progress = ttk.Progressbar(panel, mode="indeterminate")
        self.progress.grid(row=1, column=0, sticky="ew", pady=(8, 8))

        log_frame = tk.Frame(panel, bg="#020617")
        log_frame.grid(row=2, column=0, sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        self.log = tk.Text(
            log_frame,
            bg="#020617",
            fg="#CBD5E1",
            insertbackground="white",
            font=("Cascadia Mono", 9),
            relief="flat",
            padx=10,
            pady=10,
            height=8,
            wrap="word",
            state="disabled",
        )
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=scrollbar.set)
        self.log.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        ttk.Button(panel, text="Xóa nhật ký", command=self._clear_log).grid(row=3, column=0, sticky="e", pady=(8, 0))

    def _choose_data(self) -> None:
        selected = filedialog.askopenfilename(
            title="Chọn file Sentiment140 CSV",
            initialdir=str(DEFAULT_DATA.parent),
            filetypes=(("CSV", "*.csv"), ("Tất cả file", "*.*")),
        )
        if selected:
            self.data_path.set(selected)

    def _selected_data(self) -> str:
        value = self.data_path.get().strip()
        path = Path(value)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        if not path.is_file():
            raise ValueError(f"Không tìm thấy CSV:\n{path}")
        return str(path.resolve())

    def _fraction(self) -> str:
        return str(validate_sample_fraction(self.sample_fraction.get().strip()))

    def _run_local(self) -> None:
        try:
            data = self._selected_data()
            fraction = self._fraction()
        except ValueError as exc:
            messagebox.showerror("Cấu hình chưa hợp lệ", str(exc))
            return
        self._run_script("Spark local với dữ liệu thật", "run_full.ps1", "-DataPath", data, "-SampleFraction", fraction)

    def _upload_hdfs(self) -> None:
        try:
            data = self._selected_data()
        except ValueError as exc:
            messagebox.showerror("Chưa chọn dữ liệu", str(exc))
            return
        self._run_script("Upload CSV lên HDFS", "hdfs_upload.ps1", "-DataPath", data)

    def _run_hdfs(self) -> None:
        try:
            fraction = self._fraction()
        except ValueError as exc:
            messagebox.showerror("Cấu hình chưa hợp lệ", str(exc))
            return
        self._run_script("Spark đọc/ghi HDFS", "hdfs_run.ps1", "-SampleFraction", fraction)

    def _run_all_hdfs(self) -> None:
        try:
            data = self._selected_data()
            fraction = self._fraction()
        except ValueError as exc:
            messagebox.showerror("Cấu hình chưa hợp lệ", str(exc))
            return
        self._run_script("Toàn bộ luồng HDFS", "hdfs_all.ps1", "-DataPath", data, "-SampleFraction", fraction)

    def _run_script(self, title: str, script: str, *arguments: object) -> None:
        if self.process is not None and self.process.poll() is None:
            messagebox.showinfo("Đang chạy", "Hãy chờ tác vụ hiện tại hoàn tất hoặc bấm Dừng tác vụ.")
            return
        command = powershell_command(script, *arguments)
        self._append_log(f"\n▶ {title}\n$ {subprocess.list2cmdline(command)}\n\n")
        self.task_status.set(f"Đang chạy: {title}")
        self._set_running(True)
        threading.Thread(target=self._worker, args=(title, command), daemon=True).start()

    def _worker(self, title: str, command: list[str]) -> None:
        environment = os.environ.copy()
        environment["PYTHONIOENCODING"] = "utf-8"
        environment["PYTHONUNBUFFERED"] = "1"
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            self.process = subprocess.Popen(
                command,
                cwd=PROJECT_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                env=environment,
                creationflags=flags,
            )
            assert self.process.stdout is not None
            for line in self.process.stdout:
                self.events.put(("log", line))
            code = self.process.wait()
            self.events.put(("done", (title, code)))
        except OSError as exc:
            self.events.put(("error", (title, str(exc))))

    def _poll_events(self) -> None:
        try:
            while True:
                event, payload = self.events.get_nowait()
                if event == "log":
                    self._append_log(str(payload))
                elif event == "done":
                    title, code = payload
                    self._append_log(f"\n■ Kết thúc với mã {code}.\n")
                    self.task_status.set("Hoàn tất" if code == 0 else f"Lỗi: {title}")
                    self._set_running(False)
                    self.refresh_results()
                    if code != 0:
                        messagebox.showerror("Tác vụ thất bại", f"{title} kết thúc với mã {code}. Xem nhật ký để biết chi tiết.")
                elif event == "error":
                    title, detail = payload
                    self._append_log(f"\nLỖI: {detail}\n")
                    self.task_status.set(f"Lỗi: {title}")
                    self._set_running(False)
                    messagebox.showerror("Không thể chạy", detail)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_events)

    def _set_running(self, running: bool) -> None:
        for button in self.action_buttons:
            button.configure(state="disabled" if running else "normal")
        self.stop_button.configure(state="normal" if running else "disabled")
        if running:
            self.progress.start(12)
        else:
            self.progress.stop()

    def _stop_task(self) -> None:
        if self.process is not None and self.process.poll() is None:
            self._append_log("\nĐang gửi yêu cầu dừng tác vụ…\n")
            self.process.terminate()

    def _append_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self) -> None:
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def refresh_results(self) -> None:
        summary = load_result_summary()
        self.source_value.set(f"Nguồn: {summary['source']}")
        self.raw_value.set(summary["raw_rows"])
        self.clean_value.set(summary["clean_rows"])
        self.f1_value.set(summary["macro_f1"])
        self.result_type_value.set(summary["result_type"])

    def _populate_report_action(self) -> None:
        from .report_filler import populate_report
        template = PROJECT_ROOT / "report" / "bao_cao_cuoi_ky_template.md"
        output = PROJECT_ROOT / "report" / "bao_cao_cuoi_ky.md"
        outputs = PROJECT_ROOT / "outputs"
        try:
            filled, missing = populate_report(template, output, outputs)
            self._append_log(f"\n[Báo cáo] Đã cập nhật thành công {filled} chỉ số vào {output.name}\n")
            messagebox.showinfo("Thành công", f"Đã cập nhật thành công {filled} chỉ số vào báo cáo!")
        except Exception as exc:
            self._append_log(f"\n[Lỗi] Không thể cập nhật báo cáo: {exc}\n")
            messagebox.showerror("Lỗi", f"Không thể cập nhật báo cáo:\n{exc}")

    def _open_path(self, path: Path) -> None:
        try:
            if path.is_file():
                os.startfile(path)  # type: ignore[attr-defined]
                return
            path.mkdir(parents=True, exist_ok=True)
            os.startfile(path)  # type: ignore[attr-defined]
        except OSError as exc:
            messagebox.showerror("Không thể mở", str(exc))

    def _on_close(self) -> None:
        if self.process is not None and self.process.poll() is None:
            if not messagebox.askyesno("Tác vụ đang chạy", "Dừng tác vụ và đóng giao diện?"):
                return
            self.process.terminate()
        self.root.destroy()


def check_gui() -> int:
    print(f"Tk version: {tk.TkVersion}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Default CSV exists: {DEFAULT_DATA.is_file()}")
    print("GUI check: OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Desktop interface for the Twitter Spark project")
    parser.add_argument("--check", action="store_true", help="check dependencies without opening a window")
    args = parser.parse_args(argv)
    if args.check:
        return check_gui()
    root = tk.Tk()
    ProjectGui(root)
    root.mainloop()
    return 0
