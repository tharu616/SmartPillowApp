import threading
import flet as ft
from constants.config import *
from components.ui import fade_in


def onboarding_screen_view(page: ft.Page, show_screen):
    glow = ft.Container(
        width=170, height=170, border_radius=85,
        bgcolor=ft.Colors.with_opacity(0.14, WHITE),
        alignment=ft.Alignment.CENTER,
        scale=1,
        animate_scale=ft.Animation(1400, ft.AnimationCurve.EASE_IN_OUT),
        content=ft.Container(
            width=130, height=130, border_radius=65,
            bgcolor=ft.Colors.with_opacity(0.2, WHITE),
            alignment=ft.Alignment.CENTER,
            content=ft.Container(
                width=96, height=70, border_radius=35, bgcolor=WHITE,
                alignment=ft.Alignment.CENTER,
                shadow=ft.BoxShadow(blur_radius=30, color=ft.Colors.with_opacity(0.3, "#000000"),
                                    offset=ft.Offset(0, 10)),
                content=ft.Icon(ft.Icons.NIGHTS_STAY_ROUNDED, size=34, color=PRIMARY_COLOR),
            ),
        ),
    )

    def breathe(e=None):
        glow.scale = 1.12 if glow.scale == 1 else 1
        try:
            glow.update()
        except Exception:
            pass

    glow.on_animation_end = breathe
    threading.Timer(0.4, breathe).start()

    def feature(icon, text):
        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=12, vertical=8) if hasattr(ft, "Padding") else 8,
            border_radius=20,
            bgcolor=ft.Colors.with_opacity(0.16, WHITE),
            content=ft.Row(
                tight=True, spacing=6,
                controls=[ft.Icon(icon, size=16, color=WHITE),
                          ft.Text(text, size=12, color=WHITE, weight=ft.FontWeight.W_600)],
            ),
        )

    return ft.Container(
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[PRIMARY_COLOR, PRIMARY_DARK, NIGHT_BG2],
        ),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                glow,
                ft.Container(height=6),
                fade_in(ft.Text(
                    "Meet Your Smart Pillow", size=28, weight=ft.FontWeight.W_800,
                    color=WHITE, text_align=ft.TextAlign.CENTER), 0.2),
                fade_in(ft.Text(
                    "Track your sleep, reduce snoring, and fall asleep to calming sounds — all in one pillow.",
                    size=14, color=ft.Colors.with_opacity(0.85, WHITE),
                    text_align=ft.TextAlign.CENTER), 0.35),
                fade_in(ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER, wrap=True, spacing=8, run_spacing=8,
                    controls=[
                        feature(ft.Icons.QUERY_STATS_ROUNDED, "Sleep tracking"),
                        feature(ft.Icons.GRAPHIC_EQ_ROUNDED, "Anti-snore"),
                        feature(ft.Icons.MUSIC_NOTE_ROUNDED, "Calm sounds"),
                    ],
                ), 0.5),
                ft.Container(height=6),
                fade_in(ft.Button(
                    content="Get Started", icon=ft.Icons.ARROW_FORWARD_ROUNDED,
                    width=270, height=54,
                    style=ft.ButtonStyle(bgcolor=WHITE, color=PRIMARY_DARK,
                                         shape=ft.RoundedRectangleBorder(radius=27)),
                    on_click=lambda e: show_screen("/login"),
                ), 0.65),
                fade_in(ft.TextButton(
                    content="I already have an account",
                    style=ft.ButtonStyle(color=WHITE),
                    on_click=lambda e: show_screen("/login"),
                ), 0.8),
            ],
            spacing=20,
        ),
        padding=30,
    )