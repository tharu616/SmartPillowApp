from datetime import datetime

import flet as ft
from constants.config import *
from components.ui import fade_in
from services import esp_service


def alarm_screen_view(page: ft.Page, show_screen):
    time_text = datetime.now().strftime("%H:%M")
    status = ft.Text("", size=13, color=ft.Colors.with_opacity(0.8, WHITE))

    def go_back():
        if getattr(page, "session_user_id", None):
            show_screen("/home")
        else:
            show_screen("/login")

    def on_stop(e):
        status.value = "Stopping..."
        page.update()
        esp_service.run_async(esp_service.alarm_stop, on_done=lambda res: go_back())

    def on_snooze(e):
        status.value = "Snoozing for 5 minutes..."
        page.update()
        esp_service.run_async(esp_service.alarm_snooze, 5, on_done=lambda res: go_back())

    ring = ft.Container(
        width=130, height=130, border_radius=65,
        bgcolor=ft.Colors.with_opacity(0.15, WHITE),
        alignment=ft.Alignment.CENTER,
        scale=1,
        animate_scale=ft.Animation(700, ft.AnimationCurve.EASE_IN_OUT),
        content=ft.Container(
            width=92, height=92, border_radius=46,
            bgcolor=ft.Colors.with_opacity(0.25, WHITE),
            alignment=ft.Alignment.CENTER,
            content=ft.Icon(ft.Icons.ALARM_ROUNDED, size=54, color=WHITE),
        ),
    )

    def pulse(e=None):
        ring.scale = 1.18 if ring.scale == 1 else 1
        try:
            ring.update()
        except Exception:
            pass

    ring.on_animation_end = pulse
    import threading
    threading.Timer(0.3, pulse).start()

    return ft.Container(
        expand=True,
        padding=30,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,
            end=ft.Alignment.BOTTOM_CENTER,
            colors=[NIGHT_BG, NIGHT_BG2, PRIMARY_DARK],
        ),
        content=ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[
                ring,
                ft.Container(height=10),
                fade_in(ft.Text(time_text, size=76, weight=ft.FontWeight.W_900, color=WHITE), 0.1),
                fade_in(ft.Text("Time to wake up!", size=18, color=ft.Colors.with_opacity(0.85, WHITE)), 0.25),
                ft.Container(height=30),
                fade_in(ft.Button(
                    content="Snooze 5 min", icon=ft.Icons.SNOOZE_ROUNDED,
                    width=290, height=58, on_click=on_snooze,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.with_opacity(0.18, WHITE), color=WHITE,
                        shape=ft.RoundedRectangleBorder(radius=29)),
                ), 0.4),
                fade_in(ft.Button(
                    content="Stop alarm", icon=ft.Icons.ALARM_OFF_ROUNDED,
                    width=290, height=58, on_click=on_stop,
                    style=ft.ButtonStyle(
                        bgcolor=DANGER_COLOR, color=WHITE,
                        shape=ft.RoundedRectangleBorder(radius=29)),
                ), 0.55),
                status,
            ],
        ),
    )