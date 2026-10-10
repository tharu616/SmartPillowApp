import flet as ft
from constants.config import *
from components.bottom_nav import bottom_nav
from components.connection_badge import connection_badge
from components.pillow_card import pillow_card
from components.alarm_card import alarm_card
from components.ui import card, icon_badge, fade_in, bg_gradient
from services.firestore_service import get_user_profile, get_latest_sleep_session
from services import esp_service
from services import vibration_prefs


def home_screen_view(page: ft.Page, show_screen):
    nav = bottom_nav(show_screen, 0)

    user_id = getattr(page, "session_user_id", None)
    user_name = getattr(page, "session_user_name", "Guest")

    esp_service.set_user_id(user_id)
    esp_service.run_async(vibration_prefs.apply_saved, user_id)

    session_data = None
    if user_id:
        session_data = get_latest_sleep_session(user_id)

    if session_data:
        score_text = f"{session_data.get('sleep_score', '--')} - {str(session_data.get('quality', '--')).upper()}"
        detail_text = (
            f"Duration: {session_data.get('duration', '--')} | "
            f"Snore events: {session_data.get('snore_count', 0)}"
        )
    else:
        score_text = "No data yet"
        detail_text = "Start a sleep session to see your results here."

    header = fade_in(ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Column(spacing=2, controls=[
                ft.Text("Good morning,", size=13, color=TEXT_LIGHT),
                ft.Text(f"{user_name} \U0001F44B", size=26, weight=ft.FontWeight.W_800, color=TEXT_DARK),
            ]),
            ft.Container(
                width=46, height=46, border_radius=23,
                gradient=ft.LinearGradient(colors=[ACCENT_COLOR, PRIMARY_COLOR]),
                alignment=ft.Alignment.CENTER,
                content=ft.Icon(ft.Icons.PERSON_ROUNDED, color=WHITE),
            ),
        ],
    ), 0.0)

    score_card = ft.Container(
        border_radius=26, padding=22,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT,
            colors=[PRIMARY_COLOR, PRIMARY_DARK, NIGHT_BG2]),
        shadow=ft.BoxShadow(blur_radius=30, color=ft.Colors.with_opacity(0.35, PRIMARY_COLOR),
                            offset=ft.Offset(0, 12)),
        content=ft.Row(
            spacing=16,
            controls=[
                ft.Container(
                    content=ft.Icon(ft.Icons.NIGHTS_STAY_ROUNDED, size=34, color=WHITE),
                    padding=14, border_radius=20,
                    bgcolor=ft.Colors.with_opacity(0.18, WHITE),
                ),
                ft.Column(
                    spacing=3, expand=True,
                    controls=[
                        ft.Text("Last Night's Sleep Score", size=13,
                                color=ft.Colors.with_opacity(0.85, WHITE), weight=ft.FontWeight.W_600),
                        ft.Text(score_text, size=24, weight=ft.FontWeight.W_800, color=WHITE),
                        ft.Text(detail_text, size=12, color=ft.Colors.with_opacity(0.75, WHITE)),
                    ],
                ),
            ],
        ),
    )
    fade_in(score_card, 0.15)

    return ft.Column(
        expand=True,
        controls=[
            ft.Container(
                expand=True,
                gradient=bg_gradient(),
                padding=20,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=[
                        header,
                        ft.Container(height=6),
                        connection_badge(page),
                        ft.Container(height=6),
                        score_card,
                        ft.Container(height=6),
                        pillow_card(page),
                        ft.Container(height=6),
                        alarm_card(page),
                        ft.Container(height=20),
                    ],
                ),
            ),
            nav,
        ],
    )