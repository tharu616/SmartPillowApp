import flet as ft
from screens.onboarding_screen import onboarding_screen_view
from screens.login_screen import login_screen_view
from screens.signup_screen import signup_screen_view
from screens.home_screen import home_screen_view
from screens.trends_screen import trends_screen_view
from screens.height_control_screen import height_control_screen_view
from screens.settings_screen import settings_screen_view
from screens.cleaning_screen import cleaning_screen_view
from constants.config import BG_COLOR


def main(page: ft.Page):
    page.title = "Smart Pillow"
    page.bgcolor = BG_COLOR
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 360
    page.window_height = 740

    def show_screen(route):
        page.clean()

        if route == "/":
            page.add(onboarding_screen_view(page, show_screen))
        elif route == "/login":
            page.add(login_screen_view(page, show_screen))
        elif route == "/signup":
            page.add(signup_screen_view(page, show_screen))
        elif route == "/home":
            page.add(home_screen_view(page, show_screen))
        elif route == "/trends":
            page.add(trends_screen_view(page, show_screen))
        elif route == "/height":
            page.add(height_control_screen_view(page, show_screen))
        elif route == "/settings":
            page.add(settings_screen_view(page, show_screen))
        elif route == "/cleaning":
            page.add(cleaning_screen_view(page, show_screen))
        else:
            page.add(onboarding_screen_view(page, show_screen))

        page.update()

    show_screen("/")


if __name__ == "__main__":
    ft.run(main)