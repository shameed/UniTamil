import flet as ft
from app.ui.dependency_screen import DependencyScreen
from app.ui.main_window import MainWindow

def main(page: ft.Page):
    page.title = "UniTamil - PDF to Markdown Converter"
    page.window.width = 800
    page.window.height = 700
    page.window.resizable = False
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Load Fonts
    page.fonts = {
        "NotoSansTamil": "https://github.com/google/fonts/raw/main/ofl/notosanstamil/NotoSansTamil-Regular.ttf",
        "NotoSansTamilBold": "https://github.com/google/fonts/raw/main/ofl/notosanstamil/NotoSansTamil-Bold.ttf"
    }
    page.theme = ft.Theme(font_family="NotoSansTamil")
    
    def on_dependency_success():
        # Clear dependency screen and show main
        page.clean()
        page.padding = 0
        page.spacing = 0
        page.add(ft.Container(content=MainWindow(page), expand=True))
        page.update()

    # Initial Screen: Dependency Check
    # In a real build, we check this first.
    dep_screen = DependencyScreen(page, on_success=on_dependency_success)
    page.add(dep_screen)

if __name__ == "__main__":
    import sys
    import multiprocessing
    
    # Check for worker flag
    if len(sys.argv) > 1 and sys.argv[1] == "--ocr-worker":
        # We are in the subprocess! Run OCR worker logic.
        from app.core import ocr_worker
        ocr_worker.main()
        sys.exit(0)

    multiprocessing.freeze_support()
    ft.app(target=main)
