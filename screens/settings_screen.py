import flet as ft
from constants.config import *
from components.bottom_nav import bottom_nav
from components.ui import card, icon_badge, page_header, bg_gradient, fade_in, btn_style
from services.firestore_service import get_user_profile


def settings_screen_view(page: ft.Page, show_screen):
    nav = bottom_nav(show_screen, 3)
    user_id = getattr(page, "session_user_id", None)
    profile = get_user_profile(user_id) if user_id else None
    name = profile.get("name") if profile else "Guest"
    email = profile.get("email") if profile else "Not logged in"

    def handle_logout(e):
        page.session_user_id = None
        page.session_user_name = None
        show_screen("/login")

    def menu_item(icon, title, route, color, delay):
        tile = ft.Container(
            bgcolor=WHITE, border_radius=20, padding=14,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            shadow=ft.BoxShadow(blur_radius=18, color=ft.Colors.with_opacity(0.08, PRIMARY_COLOR),
                                offset=ft.Offset(0, 6)),
            on_click=lambda e: show_screen(route),
            content=ft.Row(
                spacing=14,
                controls=[
                    icon_badge(icon, color),
                    ft.Text(title, size=14, weight=ft.FontWeight.W_600, color=TEXT_DARK, expand=True),
                    ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, color=TEXT_LIGHT),
                ],
            ),
        )

        def hover(e):
            tile.scale = 1.02 if e.data in ("true", True) else 1
            tile.update()

        tile.on_hover = hover
        return fade_in(tile, delay)

    profile_card = ft.Container(
        border_radius=26, padding=20,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT,
            colors=[PRIMARY_COLOR, PRIMARY_DARK]),
        shadow=ft.BoxShadow(blur_radius=26, color=ft.Colors.with_opacity(0.3, PRIMARY_COLOR),
                            offset=ft.Offset(0, 10)),
        content=ft.Row(
            spacing=16,
            controls=[
                ft.Container(
                    width=60, height=60, border_radius=30,
                    bgcolor=ft.Colors.with_opacity(0.22, WHITE),
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(ft.Icons.PERSON_ROUNDED, size=32, color=WHITE),
                ),
                ft.Column(spacing=2, expand=True, controls=[
                    ft.Text(name, size=18, weight=ft.FontWeight.W_800, color=WHITE),
                    ft.Row(spacing=6, controls=[
                        ft.Icon(ft.Icons.MAIL_OUTLINE_ROUNDED, size=14,
                                color=ft.Colors.with_opacity(0.8, WHITE)),
                        ft.Text(email, size=12, color=ft.Colors.with_opacity(0.85, WHITE)),
                    ]),
                ]),
            ],
        ),
    )
    fade_in(profile_card, 0.1)

    return ft.Column(expand=True, controls=[
        ft.Container(expand=True, gradient=bg_gradient(), padding=20, content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
            controls=[
                page_header("Settings", "Manage your account & pillow"),
                profile_card,
                menu_item(ft.Icons.GRAPHIC_EQ_ROUNDED, "Anti-Snore Vibration", "/vibration", PRIMARY_COLOR, 0.2),
                menu_item(ft.Icons.CLEANING_SERVICES_ROUNDED, "Cleaning Maintenance Guide", "/cleaning", SUCCESS_COLOR, 0.3),
                menu_item(ft.Icons.AIRLINE_SEAT_FLAT_ROUNDED, "Pillow Height / Air Pump", "/height", WARN_COLOR, 0.4),
                ft.Container(height=6),
                fade_in(ft.Button(
                    content="Log Out", icon=ft.Icons.LOGOUT_ROUNDED,
                    width=340, height=54, style=btn_style(DANGER_COLOR, WHITE, 18),
                    on_click=handle_logout,
                ), 0.5),
            ],
        )),
        nav,
    ])