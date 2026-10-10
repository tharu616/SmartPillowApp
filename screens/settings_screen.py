import flet as ft
from constants.config import *
from components.bottom_nav import bottom_nav
from services.firestore_service import get_user_profile


def settings_screen_view(page: ft.Page, show_screen):
    nav = bottom_nav(show_screen, 3)
    user_id = getattr(page, "session_user_id", None)
    profile = get_user_profile(user_id) if user_id else None
    name = profile.get("name") if profile else "Guest"
    email = profile.get("email") if profile else "Not logged in"

    def handle_logout(e):
        page.session_user_id = None
        page.session_user_name = None
        show_screen("/login")

    return ft.Column(expand=True, controls=[
        ft.Container(expand=True, bgcolor=BG_COLOR, padding=20, content=ft.Column(controls=[
            ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
            ft.Container(bgcolor=WHITE, border_radius=16, padding=16, content=ft.Column(controls=[
                ft.Text(name, size=16, weight=ft.FontWeight.BOLD),
                ft.Text(email, size=12, color=TEXT_LIGHT),
            ])),
            ft.ListTile(title=ft.Text("Anti-Snore Vibration"),
                        trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                        on_click=lambda e: show_screen("/vibration")),
            ft.ListTile(title=ft.Text("Cleaning Maintenance Guide"),
                        trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                        on_click=lambda e: show_screen("/cleaning")),
            ft.ListTile(title=ft.Text("Pillow Height / Air Pump"),
                        trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                        on_click=lambda e: show_screen("/height")),
            ft.Button(content="Log Out", width=320, height=50,
                      bgcolor=ft.Colors.RED_400, color=WHITE, on_click=handle_logout),
        ])),
        nav,
    ])