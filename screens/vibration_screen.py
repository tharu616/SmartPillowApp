import flet as ft
from constants.config import *
from components.bottom_nav import bottom_nav
from services.firestore_service import get_vibration_settings, save_vibration_settings
from services import esp_service
from services.vibration_prefs import raw_level_from_settings, effective_level


def vibration_screen_view(page: ft.Page, show_screen):
    nav = bottom_nav(show_screen, 3)

    user_id = getattr(page, "session_user_id", None)
    settings = (get_vibration_settings(user_id) if user_id else None) or {
        "anti_snore_mode": True,
        "vibration_level": 60,
        "quick_start_mode": True,
        "partner_safe_alerts": False,
    }
    start_level = raw_level_from_settings(settings)

    status_text = ft.Text("", size=12, color=PRIMARY_COLOR)
    level_text = ft.Text(f"{start_level}%", size=13, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR)

    anti_snore_switch = ft.Switch(
        value=settings.get("anti_snore_mode", True),
        active_color=PRIMARY_COLOR,
    )

    intensity_slider = ft.Slider(
        min=10,
        max=100,
        divisions=9,
        value=start_level,
        label="{value}%",
    )

    quick_start_switch = ft.Switch(
        value=settings.get("quick_start_mode", True),
        active_color=PRIMARY_COLOR,
    )

    partner_safe_switch = ft.Switch(
        value=settings.get("partner_safe_alerts", False),
        active_color=PRIMARY_COLOR,
    )

    def current_level():
        return int(round(intensity_slider.value))

    def current_effective():
        return effective_level(current_level(), partner_safe_switch.value)

    def preview(e=None):
        """Pillow එකේ vibration motor එක තත්පරයක් ඇතුළත මේ level එකෙන් පැහැදිලිව vibrate කරනවා."""
        lvl = current_effective()
        esp_service.set_prefs(vib=lvl)
        status_text.value = "Sending to pillow..."
        page.update()

        def done(res):
            if res.get("ok"):
                status_text.value = f"Vibration {lvl}% - you should feel it now"
            else:
                status_text.value = f"Pillow error: {res.get('error')}"
            page.update()

        esp_service.run_async(esp_service.vibrate_preview, lvl, on_done=done)

    def on_slider_change(e):
        level_text.value = f"{current_level()}%"
        page.update()

    def on_slider_end(e):
        level_text.value = f"{current_level()}%"
        preview()

    def on_partner_change(e):
        preview()

    def on_anti_change(e):
        v = bool(anti_snore_switch.value)
        esp_service.set_prefs(anti=v)
        esp_service.run_async(lambda: esp_service.set_config(anti=1 if v else 0))
        status_text.value = "Anti-snore ON" if v else "Anti-snore OFF"
        page.update()

    intensity_slider.on_change = on_slider_change
    intensity_slider.on_change_end = on_slider_end
    partner_safe_switch.on_change = on_partner_change
    anti_snore_switch.on_change = on_anti_change

    def handle_save(e):
        if not user_id:
            status_text.value = "Please log in first."
            page.update()
            return

        lvl = current_level()
        legacy = 0 if lvl <= 40 else 1 if lvl <= 70 else 2
        save_vibration_settings(user_id, {
            "anti_snore_mode": anti_snore_switch.value,
            "vibration_level": lvl,
            "vibration_intensity": legacy,
            "quick_start_mode": quick_start_switch.value,
            "partner_safe_alerts": partner_safe_switch.value,
        })
        esp_service.set_prefs(vib=current_effective(), anti=anti_snore_switch.value)
        status_text.value = "Settings saved."
        page.update()

    def setting_row(label, sub, control):
        return ft.Container(
            padding=ft.Padding(top=14, bottom=14, left=0, right=0),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(label, size=13, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                            ft.Text(sub, size=11, color=TEXT_LIGHT),
                        ],
                    ),
                    control,
                ],
            ),
        )

    card1 = ft.Container(
        bgcolor=WHITE,
        border_radius=20,
        padding=18,
        content=ft.Column(
            controls=[
                setting_row(
                    "Anti-Snore Mode",
                    "Vibrate gently when snoring is detected",
                    anti_snore_switch,
                ),
                ft.Divider(height=1, color="#EDEFF5"),
                ft.Container(height=8),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Vibration Intensity", size=13, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                        level_text,
                    ],
                ),
                intensity_slider,
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Gentle", size=10, color=TEXT_LIGHT),
                        ft.Text("Medium", size=10, color=TEXT_LIGHT),
                        ft.Text("Strong", size=10, color=TEXT_LIGHT),
                    ],
                ),
                ft.Text("Release the slider to feel the vibration on your pillow.", size=11, color=TEXT_LIGHT),
                ft.Button(content="Test vibration", on_click=preview),
            ],
        ),
    )

    card2 = ft.Container(
        bgcolor=WHITE,
        border_radius=20,
        padding=18,
        content=ft.Column(
            controls=[
                setting_row(
                    "Quick Start Mode",
                    "Skip nightly check-in questions",
                    quick_start_switch,
                ),
                ft.Divider(height=1, color="#EDEFF5"),
                setting_row(
                    "Partner-Safe Alerts",
                    "Reduce vibration reach to avoid waking partner",
                    partner_safe_switch,
                ),
            ],
        ),
    )

    insight_box = ft.Container(
        bgcolor="#EEF0FD",
        border_radius=16,
        padding=14,
        content=ft.Text(
            "\U0001F3AF Tip: try a low intensity with Partner-Safe Alerts on if you sleep with a partner.",
            size=12,
            color=TEXT_DARK,
        ),
    )

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
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda e: show_screen("/settings"),
                        ),
                        ft.Text("Anti-Snore Settings", size=20, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                        ft.Container(height=16),
                        card1,
                        card2,
                        insight_box,
                        ft.Container(height=10),
                        ft.Button(
                            content="Save Settings",
                            width=320,
                            height=50,
                            bgcolor=PRIMARY_COLOR,
                            color=WHITE,
                            on_click=handle_save,
                        ),
                        ft.Container(height=6),
                        status_text,
                        ft.Container(height=20),
                    ],
                    spacing=16,
                ),
            ),
            nav,
        ],
    )