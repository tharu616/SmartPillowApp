import flet as ft
from constants.config import *
from services import esp_service


def connection_badge(page: ft.Page):
    dot = ft.Container(
        width=12, height=12, border_radius=6, bgcolor=ft.Colors.GREY,
        animate=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT),
        animate_scale=ft.Animation(900, ft.AnimationCurve.EASE_IN_OUT),
        scale=1,
    )
    icon = ft.Icon(ft.Icons.BLUETOOTH_SEARCHING_ROUNDED, size=18, color=TEXT_LIGHT)
    label = ft.Text("Checking pillow...", size=12, weight=ft.FontWeight.W_600, color=TEXT_LIGHT)
    box = ft.Container(
        border_radius=16, padding=12, bgcolor=WHITE,
        animate=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT),
    )

    def pulse(e=None):
        dot.scale = 1.5 if dot.scale == 1 else 1
        try:
            dot.update()
        except Exception:
            pass

    dot.on_animation_end = pulse

    def apply(connected: bool):
        if connected:
            dot.bgcolor = SUCCESS_COLOR
            icon.name = ft.Icons.SENSORS_ROUNDED
            icon.color = SUCCESS_COLOR
            label.value = f"Pillow connected ({esp_service.get_ip()})"
            label.color = SUCCESS_COLOR
            box.bgcolor = ft.Colors.with_opacity(0.10, SUCCESS_COLOR)
        else:
            dot.bgcolor = DANGER_COLOR
            icon.name = ft.Icons.SENSORS_OFF_ROUNDED
            icon.color = DANGER_COLOR
            label.value = "Pillow not connected"
            label.color = DANGER_COLOR
            box.bgcolor = ft.Colors.with_opacity(0.10, DANGER_COLOR)

    def on_update(connected, res):
        apply(connected)
        try:
            page.update()
        except Exception:
            pass

    apply(esp_service.is_connected())
    esp_service.set_listener(on_update)
    dot.scale = 1.5

    box.content = ft.Row(controls=[icon, label, ft.Container(expand=True), dot], spacing=10)
    return box