import flet as ft
from constants.config import *
from services import esp_service


def connection_badge(page: ft.Page):
    dot = ft.Icon(ft.Icons.CIRCLE, size=12, color=ft.Colors.GREY)
    label = ft.Text("Checking pillow...", size=12, color=TEXT_LIGHT)

    def apply(connected: bool):
        if connected:
            dot.color = ft.Colors.GREEN
            label.value = f"Pillow connected ({esp_service.get_ip()})"
            label.color = ft.Colors.GREEN_700
        else:
            dot.color = ft.Colors.RED_400
            label.value = "Pillow not connected"
            label.color = ft.Colors.RED_400

    def on_update(connected, res):
        apply(connected)
        try:
            page.update()
        except Exception:
            pass

    apply(esp_service.is_connected())
    esp_service.set_listener(on_update)

    return ft.Container(
        bgcolor=WHITE,
        border_radius=12,
        padding=10,
        content=ft.Row(controls=[dot, label], spacing=8),
    )