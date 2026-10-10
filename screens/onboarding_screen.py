import flet as ft
from constants.config import *

def onboarding_screen_view(page: ft.Page, show_screen):
    return ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[PRIMARY_COLOR, PRIMARY_DARK],
        ),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=120,
                    height=80,
                    bgcolor=WHITE,
                    border_radius=40,
                ),
                ft.Text(
                    "Meet Your Smart Pillow",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=WHITE,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Track your sleep, reduce snoring, and fall asleep to calming sounds — all in one pillow.",
                    size=14,
                    color=ft.Colors.with_opacity(0.85, WHITE),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Button(
                    content="Get Started",
                    width=260,
                    height=50,
                    bgcolor=WHITE,
                    color=PRIMARY_DARK,
                    on_click=lambda e: show_screen("/login"),
                ),
                ft.Button(
                    content="I already have an account",
                    width=260,
                    height=50,
                    color=TEXT_DARK,
                    on_click=lambda e: show_screen("/login"),
                ),
            ],
            spacing=20,
        ),
        padding=30,
    )