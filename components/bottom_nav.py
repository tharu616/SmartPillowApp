import flet as ft
from constants.config import *


def bottom_nav(show_screen, selected_index=0):
    routes = ["/home", "/trends", "/height", "/settings"]

    def handle_change(e):
        show_screen(routes[e.control.selected_index])

    return ft.NavigationBar(
        selected_index=selected_index,
        bgcolor=WHITE,
        indicator_color=ft.Colors.with_opacity(0.15, PRIMARY_COLOR),
        elevation=12,
        height=68,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME_ROUNDED, label="Home"),
            ft.NavigationBarDestination(
                icon=ft.Icons.INSIGHTS_OUTLINED, selected_icon=ft.Icons.INSIGHTS_ROUNDED, label="Trends"),
            ft.NavigationBarDestination(
                icon=ft.Icons.AIRLINE_SEAT_FLAT_OUTLINED, selected_icon=ft.Icons.AIRLINE_SEAT_FLAT_ROUNDED, label="Height"),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS_ROUNDED, label="Settings"),
        ],
        on_change=handle_change,
    )