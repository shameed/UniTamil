import flet as ft
from ..core.dependency_checker import DependencyChecker
from .components import *

class DependencyScreen(ft.UserControl):
    def __init__(self, page: ft.Page, on_success: callable):
        super().__init__()
        self.page = page
        self.on_success = on_success
        self.checker = DependencyChecker()
        
    def did_mount(self):
        # Auto-proceed if ready
        if self.checker.get_status()["ready"]:
             # Small delay to let UI render if needed, or immediate
             # Using a timer to avoid immediate transition before UI is seen if we want that,
             # but user asked for "if dependencies are installed then show the Main processing screen"
             # which implies immediate or near-immediate.
             self.on_success()

    def build(self):
        # We wrap everything in a Centered container
        return ft.Container(
            content=self.build_card(),
            alignment=ft.alignment.center,
            expand=True, # Important to fill page
            bgcolor=COLOR_BACKGROUND
        )

    def build_card(self):
        status = self.checker.get_status()
        
        tess_row = ft.Row([
            get_status_icon(status["tesseract_found"]),
            ft.Text("Tesseract OCR", **TEXT_H2),
            ft.Text("Installed" if status['tesseract_found'] else "Not Found", color=COLOR_SUCCESS if status['tesseract_found'] else ft.colors.RED)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        lang_status = status["languages"]
        eng_row = ft.Row([
            get_status_icon(lang_status["eng"]),
            ft.Text("English Pack", **TEXT_H2),
            ft.Text("Installed" if lang_status['eng'] else "Missing", color=COLOR_SUCCESS if lang_status['eng'] else ft.colors.RED)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        tam_row = ft.Row([
            get_status_icon(lang_status["tam"]),
            ft.Text("Tamil Pack", **TEXT_H2),
            ft.Text("Installed" if lang_status['tam'] else "Missing", color=COLOR_SUCCESS if lang_status['tam'] else ft.colors.RED)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        action_btn = ft.ElevatedButton(
            "Continue",
            icon=ft.icons.CHECK,
            style=ft.ButtonStyle(bgcolor=COLOR_SUCCESS, color=ft.colors.WHITE),
            on_click=lambda _: self.on_success(),
            disabled=not status["ready"],
            width=200
        )
        
        refresh_btn = ft.IconButton(
            icon=ft.icons.REFRESH,
            tooltip="Refresh Checks",
            on_click=self.refresh_custom,
            icon_color=COLOR_PRIMARY
        )

        card_content = ft.Column(
            controls=[
                ft.Row([
                    ft.Text("System Check", size=24, weight=ft.FontWeight.BOLD),
                    refresh_btn
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Container(height=20),
                tess_row,
                eng_row,
                tam_row,
                ft.Container(height=40),
                ft.Divider(),
                ft.Row([action_btn], alignment=ft.MainAxisAlignment.CENTER)
            ],
            width=400,
            spacing=10
        )
        
        return ft.Container(
            content=card_content,
            padding=30,
            bgcolor=COLOR_SURFACE,
            border_radius=10,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.BLACK12)
        )

    def refresh_custom(self, e):
        # Trigger rebuild
        self.controls = [self.build()]
        self.update()
