import flet as ft
from constants.config import *
from components.bottom_nav import bottom_nav
from services.firestore_service import get_recent_sleep_sessions


def trends_screen_view(page: ft.Page, show_screen):
    nav = bottom_nav(show_screen, 1)

    user_id = getattr(page, "session_user_id", None)
    sessions = get_recent_sleep_sessions(user_id) if user_id else []

    if sessions:
        session_rows = [
            ft.Container(
                bgcolor=WHITE,
                border_radius=14,
                padding=14,
                content=ft.Column(
                    controls=[
                        ft.Text(
                            f"Score: {s.get('sleep_score', '--')} - {s.get('quality', '--').upper()}",
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            f"Duration: {s.get('duration', '--')} | Snore events: {s.get('snore_count', 0)}",
                            size=12,
                            color=TEXT_LIGHT,
                        ),
                    ]
                ),
            )
            for s in sessions
        ]
    else:
        session_rows = [
            ft.Container(
                bgcolor=WHITE,
                border_radius=14,
                padding=20,
                content=ft.Text("No sleep sessions recorded yet.", color=TEXT_LIGHT),
            )
        ]

    return ft.Column(
        expand=True,
        controls=[
            ft.Container(
                expand=True,
                bgcolor=BG_COLOR,
                padding=20,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Text("Sleep Trends", size=24, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                        ft.Container(height=20),
                        *session_rows,
                    ],
                ),
            ),
            nav,
        ],
    )