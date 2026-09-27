import flet as ft
from constants.config import *
from components.bottom_nav import bottom_nav
from services.firestore_service import get_height_preset, save_height_preset


def height_control_screen_view(page: ft.Page, show_screen):
    nav = bottom_nav(show_screen, 2)

    user_id = getattr(page, "session_user_id", None)
    current_value = get_height_preset(user_id) if user_id else 3

    status_text = ft.Text("", size=12, color=PRIMARY_COLOR)

    height_slider = ft.Slider(
        min=1,
        max=5,
        divisions=4,
        value=current_value,
        label="{value}",
    )

    def handle_inflate(e):
        if height_slider.value < 5:
            height_slider.value += 1
            page.update()

    def handle_deflate(e):
        if height_slider.value > 1:
            height_slider.value -= 1
            page.update()

    def handle_save(e):
        if not user_id:
            status_text.value = "Please log in first."
            page.update()
            return

        save_height_preset(user_id, height_slider.value)
        status_text.value = "Preset saved."
        page.update()

    return ft.Column(
        expand=True,
        controls=[
            ft.Container(
                expand=True,
                bgcolor=BG_COLOR,
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Text("Pillow Height Control", size=24, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                        ft.Text("Adjust air pump inflation to change pillow loft", size=12, color=TEXT_LIGHT),
                        ft.Container(height=20),
                        height_slider,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Button(content="Deflate", on_click=handle_deflate),
                                ft.Button(content="Save Preset", on_click=handle_save),
                                ft.Button(content="Inflate", on_click=handle_inflate),
                            ],
                        ),
                        ft.Container(height=10),
                        status_text,
                    ]
                ),
            ),
            nav,
        ],
    )