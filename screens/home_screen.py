import flet as ft
from constants.config import *
from components.bottom_nav import bottom_nav
from services.firestore_service import get_user_profile, get_latest_sleep_session


def home_screen_view(page: ft.Page, show_screen):
    nav = bottom_nav(show_screen, 0)

    user_id = getattr(page, "session_user_id", None)
    user_name = getattr(page, "session_user_name", "Guest")

    session_data = None
    if user_id:
        session_data = get_latest_sleep_session(user_id)

    if session_data:
        score_text = f"{session_data.get('sleep_score', '--')} - {session_data.get('quality', '--').upper()}"
        detail_text = (
            f"Duration: {session_data.get('duration', '--')} | "
            f"Snore events: {session_data.get('snore_count', 0)}"
        )
    else:
        score_text = "No data yet"
        detail_text = "Start a sleep session to see your results here."

    return ft.Column(
        expand=True,
        controls=[
            ft.Container(
                expand=True,
                bgcolor=BG_COLOR,
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Text("Good morning,", size=13, color=TEXT_LIGHT),
                        ft.Text(f"{user_name} \U0001F44B", size=24, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                        ft.Container(height=20),
                        ft.Container(
                            bgcolor=WHITE,
                            border_radius=20,
                            padding=20,
                            content=ft.Column(
                                controls=[
                                    ft.Text("Last Night's Sleep Score", size=14, weight=ft.FontWeight.BOLD),
                                    ft.Text(score_text, size=22, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR),
                                    ft.Text(detail_text, size=12, color=TEXT_LIGHT),
                                ]
                            ),
                        ),
                    ]
                ),
            ),
            nav,
        ],
    )