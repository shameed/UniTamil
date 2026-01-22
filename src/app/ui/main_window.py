import flet as ft
from pathlib import Path
import threading
import concurrent.futures
import os
import time
from .components import *
from ..core.pipeline import ProcessingPipeline
from ..utils.logger import logger

class FileProgressCard(ft.UserControl):
    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename
        self.progress_bar = ft.ProgressBar(value=0.0, color=COLOR_PRIMARY, bgcolor=ft.colors.GREY_200)
        self.status_text = ft.Text("Waiting...", size=12, color=COLOR_TEXT_SECONDARY)
        
    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.INSERT_DRIVE_FILE, size=20, color=COLOR_TEXT_SECONDARY),
                    ft.Text(self.filename, **TEXT_H2),
                ], spacing=10),
                self.progress_bar,
                ft.Row([ft.Container(), self.status_text], alignment=ft.MainAxisAlignment.END)
            ], spacing=5),
            bgcolor=COLOR_SURFACE,
            padding=15,
            border_radius=8,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=3, color=ft.colors.BLACK12)
        )

    def update_progress(self, value: float, msg: str):
        try:
            self.progress_bar.value = value
            self.status_text.value = msg
            # Force update - this will work from any thread in Flet
            self.progress_bar.update()
            self.status_text.update()
        except Exception:
            pass  # Ignore if control is not mounted

class MainWindow(ft.UserControl):
    def __init__(self, page: ft.Page, pipeline: ProcessingPipeline = None):
        super().__init__()
        self.page = page
        self.pipeline = pipeline if pipeline else ProcessingPipeline()
        self.selected_input_dir = None
        self.selected_output_dir = None
        self.file_cards = {} 
        self.executor = None # ThreadPool
        
        self.stop_event = threading.Event()
        self.is_processing = False
        self.reset_btn_ref = ft.Ref[ft.ElevatedButton]()
        
        # Refs
        self.process_btn_ref = ft.Ref[ft.ElevatedButton]()
        self.log_view_ref = ft.Ref[ft.ListView]()
        
        self.meta_total_files = ft.Text("Total Files: --", **TEXT_META)
        self.meta_last_mod = ft.Text("Status: Idle", **TEXT_META)

    def build(self):
        # -- Sidebar (30%) --
        self.input_dir_text = ft.TextField(
            hint_text="Select Input Folder", text_size=12, read_only=True, 
            bgcolor=ft.colors.WHITE, border_radius=5, height=40, content_padding=10, cursor_height=0
        )
        self.output_dir_text = ft.TextField(
            hint_text="Select Output Folder", text_size=12, read_only=True, 
            bgcolor=ft.colors.WHITE, border_radius=5, height=40, content_padding=10, cursor_height=0
        )
        
        sidebar_content = ft.Column(
            controls=[
                ft.Container(height=50),
                ft.Text("Input Folder", **TEXT_SIDEBAR_LABEL),
                ft.Stack([
                    self.input_dir_text,
                    ft.Container(
                        on_click=lambda _: self.get_directory_result.get_directory_path(),
                        expand=True,
                        opacity=0,
                        height=40,
                    )
                ]),
                
                ft.Container(height=20),
                ft.Text("Output Folder", **TEXT_SIDEBAR_LABEL),
                ft.Stack([
                    self.output_dir_text,
                    ft.Container(
                        on_click=lambda _: self.get_directory_result_out.get_directory_path(),
                        expand=True,
                        opacity=0,
                        height=40,
                    )
                ]),
                
                ft.Container(height=20),
                
                # moved Start Processing Button
                ft.ElevatedButton(
                    "Start Processing",
                    style=ft.ButtonStyle(bgcolor=COLOR_SUCCESS, color=ft.colors.WHITE, shape=ft.RoundedRectangleBorder(radius=5)),
                    height=45,
                    on_click=self.start_processing, disabled=True, ref=self.process_btn_ref
                ),
                
                ft.Container(height=5),
                
                # Dynamic Reset/Stop Button
                ft.ElevatedButton(
                    "Reset Application",
                    style=ft.ButtonStyle(bgcolor=ft.colors.GREY_500, color=ft.colors.WHITE, shape=ft.RoundedRectangleBorder(radius=5)),
                    height=35,
                    on_click=self.on_reset_stop_click,
                    ref=self.reset_btn_ref
                ),

                ft.Container(height=40),
                
                ft.Container(
                    content=ft.Column([
                        ft.Text("Metadata:", **TEXT_SIDEBAR_LABEL),
                        self.meta_total_files,
                        self.meta_last_mod,
                    ]), padding=10
                ),
                
                ft.Container(expand=True), # Spacer to push settings to bottom
                
                # Settings Drawer
                ft.ExpansionTile(
                    title=ft.Text("Settings", color=COLOR_SIDEBAR_TEXT),
                    icon_color=COLOR_SIDEBAR_TEXT,
                    collapsed_icon_color=COLOR_SIDEBAR_TEXT,
                    controls=[
                        ft.Container(
                            content=ft.Column([
                                ft.Checkbox(label="Skip Poor Quality", label_style=ft.TextStyle(color=COLOR_SIDEBAR_TEXT, size=12)),
                                ft.Checkbox(label="Force OCR", label_style=ft.TextStyle(color=COLOR_SIDEBAR_TEXT, size=12)),
                                ft.Row([
                                    ft.Text("DPI:", color=COLOR_SIDEBAR_TEXT, size=12, weight=ft.FontWeight.BOLD),
                                    ft.Dropdown(
                                        options=[
                                            ft.dropdown.Option("96"), 
                                            ft.dropdown.Option("150"), 
                                            ft.dropdown.Option("300")
                                        ],
                                        value="96",
                                        text_size=11,
                                        color=ft.colors.BLACK,
                                        bgcolor=ft.colors.WHITE,
                                        border_color=ft.colors.GREY_400,
                                        height=35,
                                        width=80,
                                        content_padding=5
                                    )
                                ], spacing=10, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                            ], spacing=10),
                            padding=10
                        )
                    ]
                )
            ],
            spacing=5,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH
        )
        
        sidebar = ft.Container(
            content=sidebar_content,
            bgcolor=COLOR_SIDEBAR,
            padding=20,
            border=ft.border.only(right=ft.BorderSide(1, ft.colors.BLACK12)),
            expand=3 # 30% flex relative to 7 (3+7=10)
        )
        
        # -- Right Content (70%) --
        
        # 1. Top List (80%)
        self.files_list = ft.ListView(expand=True, spacing=10, padding=20)
        
        # 2. Bottom Logs (20%)
        self.log_view = ft.ListView(expand=True, spacing=2, padding=10, auto_scroll=True, ref=self.log_view_ref)
        
        right_panel = ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text("Processing Queue", size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                    ft.Divider(color=ft.colors.BLACK12),
                    self.files_list
                ]),
                expand=8, # 80%
                bgcolor=COLOR_BACKGROUND,
                padding=20
            ),
            ft.Container(
                content=ft.Container(
                    content=self.log_view,
                    bgcolor=ft.colors.BLACK87,
                    border_radius=0
                ),
                expand=2, # 20%
                padding=0
            )
        ], spacing=0, expand=7) # 70% flex

        # -- File Pickers --
        self.get_directory_result = ft.FilePicker(on_result=self.on_input_dir_selected)
        self.get_directory_result_out = ft.FilePicker(on_result=self.on_output_dir_selected)
        self.page.overlay.extend([self.get_directory_result, self.get_directory_result_out])

        return ft.Row([sidebar, right_panel], spacing=0, expand=True)

    def on_input_dir_selected(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.selected_input_dir = e.path
            self.input_dir_text.value = e.path
            self._scan_files()
            self.check_ready()
            self.update()

    def on_output_dir_selected(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.selected_output_dir = e.path
            self.output_dir_text.value = e.path
            self.check_ready()
            self.update()
            
    def check_ready(self):
        is_ready = bool(self.selected_input_dir and self.selected_output_dir)
        if self.process_btn_ref.current:
            self.process_btn_ref.current.disabled = not is_ready
            self.process_btn_ref.current.update()

    def _scan_files(self):
        files = list(Path(self.selected_input_dir).glob("*.pdf"))
        self.meta_total_files.value = f"Total Files: {len(files)}"
        self.files_list.controls.clear()
        self.file_cards.clear()
        for f in files:
            card = FileProgressCard(f.name)
            self.files_list.controls.append(card)
            self.file_cards[str(f)] = card # Key by full path

    def log(self, msg):
        # Thread-safe logging to UI
        if self.log_view_ref.current:
            self.log_view_ref.current.controls.append(
                ft.Text(f"> {msg}", font_family="Consolas", color=ft.colors.GREEN_400, size=12)
            )
            self.log_view_ref.current.update()

    def on_reset_stop_click(self, e):
        if self.is_processing:
             self.confirm_dialog("Stop Processing?", "Are you sure you want to stop processing?", self.confirm_stop)
        else:
             self.confirm_dialog("Reset Application?", "This will clear all selections and logs. Continue?", self.confirm_reset)

    def confirm_dialog(self, title, msg, action):
        def close_dlg(e):
             self.page.dialog.open = False
             self.page.update()
             if e.control.text == "Yes":
                 action()
        
        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(msg),
            actions=[
                ft.TextButton("No", on_click=close_dlg),
                ft.TextButton("Yes", on_click=close_dlg, style=ft.ButtonStyle(color=ft.colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def confirm_stop(self):
        self.log("Stopping...")
        self.stop_event.set()

    def confirm_reset(self):
        self.selected_input_dir = None
        self.selected_output_dir = None
        self.input_dir_text.value = ""
        self.output_dir_text.value = ""
        self.files_list.controls.clear()
        self.file_cards.clear()
        if self.log_view_ref.current:
            self.log_view_ref.current.controls.clear()
        self.meta_total_files.value = "Total Files: --"
        self.meta_last_mod.value = "Status: Idle"
        self.check_ready()
        self.update()

    def _update_reset_stop_btn(self, processing):
        if self.reset_btn_ref.current:
            btn = self.reset_btn_ref.current
            if processing:
                btn.text = "Stop Processing"
                btn.style = ft.ButtonStyle(bgcolor=ft.colors.RED_500, color=ft.colors.WHITE, shape=ft.RoundedRectangleBorder(radius=5))
            else:
                btn.text = "Reset Application"
                btn.style = ft.ButtonStyle(bgcolor=ft.colors.GREY_500, color=ft.colors.WHITE, shape=ft.RoundedRectangleBorder(radius=5))
            btn.update()

    def start_processing(self, e):
        if self.process_btn_ref.current:
            self.process_btn_ref.current.disabled = True
            self.process_btn_ref.current.update()
        
        self.is_processing = True
        self.stop_event.clear()
        self._update_reset_stop_btn(True)
        
        self.meta_last_mod.value = "Status: Spawning Workers..."
        self.update()
        
        # Start Thread
        threading.Thread(target=self.run_parallel_pipeline, daemon=True).start()

    def run_parallel_pipeline(self):
        files = list(Path(self.selected_input_dir).glob("*.pdf"))
        # Use CPU count for workers
        max_workers = os.cpu_count() or 2
        self.log(f"Starting pipeline with {max_workers} workers.")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.process_single_file, f): f for f in files
            }
            
            for future in concurrent.futures.as_completed(futures):
                if self.stop_event.is_set():
                    self.log("Processing Aborted.")
                    break
                    
                f = futures[future]
                try:
                    success = future.result()
                    self.log(f"Finished: {f.name} [{'Success' if success else 'Failed'}]")
                except Exception as exc:
                    self.log(f"Exception for {f.name}: {exc}")
        
        self.meta_last_mod.value = "Status: " + ("Stopped" if self.stop_event.is_set() else "All Completed")
        self.update()
        
        self.is_processing = False
        self._update_reset_stop_btn(False)
        
        # Re-enable button
        if self.process_btn_ref.current:
            self.process_btn_ref.current.disabled = False
            self.process_btn_ref.current.update()

    def process_single_file(self, pdf_path: Path):
        # Double check stop logic inside worker if possible, 
        # but ThreadPool futures are hard to cancel once running.
        if self.stop_event.is_set():
            return False
            
        card = self.file_cards.get(str(pdf_path))
        
        def progress_cb(prog, msg):
             if card:
                card.update_progress(prog, msg)
        
        self.log(f"Started: {pdf_path.name}")
        success = self.pipeline.process_file(
            str(pdf_path),
            self.selected_output_dir,
            progress_callback=progress_cb,
            should_stop=lambda: self.stop_event.is_set()
        )
        
        if card:
            status = "Completed" if success else "Failed"
            card.update_progress(1.0 if success else 0.0, status)
            
        return success
