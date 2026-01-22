import flet as ft

# Design Tokens (from design-standards.md)
# Adapting to Flet constants
# Design Tokens (from design-standards.md)
COLOR_PRIMARY = ft.colors.BLUE
COLOR_SIDEBAR = ft.colors.BLUE_GREY_900
COLOR_SIDEBAR_TEXT = ft.colors.WHITE
COLOR_BACKGROUND = ft.colors.BLUE_GREY_50
COLOR_SURFACE = ft.colors.WHITE
COLOR_TEXT_PRIMARY = ft.colors.BLUE_GREY_900
COLOR_TEXT_SECONDARY = ft.colors.BLUE_GREY_500
COLOR_SUCCESS = ft.colors.GREEN_500

TEXT_SIDEBAR_HEADER = {"size": 24, "weight": ft.FontWeight.BOLD, "color": COLOR_SIDEBAR_TEXT}
TEXT_SIDEBAR_LABEL = {"size": 12, "weight": ft.FontWeight.BOLD, "color": COLOR_SIDEBAR_TEXT}
TEXT_H2 = {"size": 16, "weight": ft.FontWeight.W_600, "color": COLOR_TEXT_PRIMARY}
TEXT_BODY = {"size": 14, "weight": ft.FontWeight.NORMAL, "color": COLOR_TEXT_PRIMARY}
TEXT_META = {"size": 12, "weight": ft.FontWeight.NORMAL, "color": COLOR_SIDEBAR_TEXT}

def get_status_icon(is_ok: bool) -> ft.Icon:
    return ft.Icon(
        name=ft.icons.CHECK_CIRCLE if is_ok else ft.icons.ERROR_OUTLINE,
        color=COLOR_SUCCESS if is_ok else COLOR_ERROR,
        size=20
    )

def create_header() -> ft.Container:
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.icons.BOOK, size=30, color=COLOR_PRIMARY),
                ft.Text("UniTamil Converter", **TEXT_H1),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        padding=20,
        bgcolor=ft.colors.SURFACE_VARIANT,
        border_radius=10,
    )
