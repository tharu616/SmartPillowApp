from datetime import datetime

import flet as ft
from constants.config import *
from services import esp_service


def alarm_screen_view(page: ft.Page, show_screen):
    time_text = datetime.now().strftime("%H:%M")
    status = ft.Text("", size=13, color=ft.Colors.WHITE)

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

    return ft.Container(
        expand=True,
        bgcolor="#1B1E33",
        padding=30,
        content=ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            controls=[
                ft.Icon(ft.Icons.ALARM, size=64, color=ft.Colors.WHITE),
                ft.Text(time_text, size=64, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text("Time to wake up!", size=18, color=ft.Colors.WHITE),
                ft.Container(height=30),
                ft.Button(
                    content="Snooze 5 min",
                    width=280,
                    height=56,
                    on_click=on_snooze,
                ),
                ft.Button(
                    content="Stop alarm",
                    width=280,
                    height=56,
                    bgcolor=ft.Colors.RED_400,
                    color=ft.Colors.WHITE,
                    on_click=on_stop,
                ),
                status,
            ],
        ),
    )