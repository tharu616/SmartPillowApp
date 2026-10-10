import flet as ft
from screens.onboarding_screen import onboarding_screen_view
from screens.login_screen import login_screen_view
from screens.signup_screen import signup_screen_view
from screens.home_screen import home_screen_view
from screens.trends_screen import trends_screen_view
from screens.height_control_screen import height_control_screen_view
from screens.settings_screen import settings_screen_view
from screens.cleaning_screen import cleaning_screen_view
from screens.vibration_screen import vibration_screen_view
from screens.alarm_screen import alarm_screen_view
from constants.config import BG_COLOR
from services import esp_service


def main(page: ft.Page):
    page.title = "Smart Pillow"
    page.bgcolor = BG_COLOR
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    page.window.width = 390
    page.window.height = 760
    page.window.min_width = 360
    page.window.min_height = 640

    current = {"route": "/"}

    def show_screen(route):
        current["route"] = route
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
        elif route == "/vibration":
            page.add(vibration_screen_view(page, show_screen))
        elif route == "/alarm":
            page.add(alarm_screen_view(page, show_screen))
        else:
            page.add(onboarding_screen_view(page, show_screen))

        page.update()

    # Alarm වදින විට alarm screen එක ඉබේම එනවා, නැවැත්තුවාම ආපහු යනවා
    def on_alarm_status(connected, res):
        ringing = bool(connected and res.get("ringing"))
        try:
            if ringing and current["route"] != "/alarm":
                show_screen("/alarm")
            elif (not ringing) and current["route"] == "/alarm":
                if getattr(page, "session_user_id", None):
                    show_screen("/home")
                else:
                    show_screen("/login")
        except Exception as e:
            print("Alarm screen switch error:", e)

    esp_service.set_listener(on_alarm_status, key="alarm_nav")
    esp_service.start_heartbeat(3)

    show_screen("/")


if __name__ == "__main__":
    ft.run(main)