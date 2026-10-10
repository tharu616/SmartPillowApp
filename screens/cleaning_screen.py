import flet as ft
from constants.config import *
from components.ui import card, icon_badge, page_header, bg_gradient, fade_in


def cleaning_screen_view(page: ft.Page, show_screen):
    steps = [
        (ft.Icons.CHECKROOM_ROUNDED, "Remove the pillow cover before washing.", PRIMARY_COLOR),
        (ft.Icons.WATER_DROP_ROUNDED, "Do not submerge the sensor unit in water.", DANGER_COLOR),
        (ft.Icons.CLEANING_SERVICES_ROUNDED, "Wipe the air pump housing with a damp cloth only.", SUCCESS_COLOR),
        (ft.Icons.AIR_ROUNDED, "Air dry the cover completely before reattaching.", ACCENT_COLOR),
        (ft.Icons.SENSORS_ROUNDED, "Check sensor connections monthly for dust buildup.", WARN_COLOR),
    ]

    rows = []
    for i, (icon, text, color) in enumerate(steps):
        rows.append(card(
            delay=0.1 + i * 0.1, padding=14, radius=18,
            content=ft.Row(
                spacing=14,
                controls=[
                    icon_badge(icon, color),
                    ft.Text(f"{i + 1}. {text}", size=14, color=TEXT_DARK, expand=True),
                ],
            ),
        ))

    return ft.Container(
        expand=True,
        gradient=bg_gradient(),
        padding=20,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
            controls=[
                page_header("Cleaning & Maintenance", "Keep your Smart Pillow fresh",
                            on_back=lambda e: show_screen("/settings")),
                ft.Container(height=6),
                *rows,
            ],
        ),
    )