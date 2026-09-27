import flet as ft
from constants.config import *


def cleaning_screen_view(page: ft.Page, show_screen):
    return ft.Container(
        expand=True,
        bgcolor=BG_COLOR,
        padding=20,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: show_screen("/settings"),
                ),
                ft.Text("Cleaning & Maintenance", size=24, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Container(height=16),
                ft.Container(
                    bgcolor=WHITE,
                    border_radius=16,
                    padding=16,
                    content=ft.Column(
                        controls=[
                            ft.Text("1. Remove the pillow cover before washing.", size=14),
                            ft.Text("2. Do not submerge the sensor unit in water.", size=14),
                            ft.Text("3. Wipe the air pump housing with a damp cloth only.", size=14),
                            ft.Text("4. Air dry the cover completely before reattaching.", size=14),
                            ft.Text("5. Check sensor connections monthly for dust buildup.", size=14),
                        ],
                        spacing=10,
                    ),
                ),
            ],
        ),
    )