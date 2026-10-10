import flet as ft
from constants.config import *
from components.bottom_nav import bottom_nav
from components.ui import card, card_title, icon_badge, page_header, bg_gradient, fade_in, btn_style
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
    level_text = ft.Text(f"{start_level}%", size=15, weight=ft.FontWeight.W_800, color=WHITE)

    level_chip = ft.Container(
        content=level_text,
        padding=ft.Padding.symmetric(horizontal=14, vertical=6) if hasattr(ft, "Padding") else 8,
        border_radius=20,
        gradient=ft.LinearGradient(colors=[ACCENT_COLOR, PRIMARY_COLOR]),
        scale=1,
        animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT_BACK),
    )

    vib_icon = ft.Container(
        width=70, height=70, border_radius=35,
        bgcolor=ft.Colors.with_opacity(0.15, PRIMARY_COLOR),
        alignment=ft.Alignment.CENTER,
        scale=1,
        animate_scale=ft.Animation(250, ft.AnimationCurve.EASE_OUT_BACK),
        content=ft.Icon(ft.Icons.VIBRATION_ROUNDED, size=34, color=PRIMARY_COLOR),
    )

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
        active_color=PRIMARY_COLOR,
        thumb_color=PRIMARY_DARK,
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

    def bump():
        vib_icon.scale = 1.2
        level_chip.scale = 1.12
        try:
            vib_icon.update()
            level_chip.update()
        except Exception:
            pass

        def back(e=None):
            vib_icon.scale = 1
            level_chip.scale = 1
            try:
                vib_icon.update()
                level_chip.update()
            except Exception:
                pass

        vib_icon.on_animation_end = back

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
        bump()
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

    def setting_row(icon, color, label, sub, control):
        return ft.Container(
            padding=ft.Padding(top=10, bottom=10, left=0, right=0),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=12,
                        expand=True,
                        controls=[
                            icon_badge(icon, color, 20),
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(label, size=13, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                                    ft.Text(sub, size=11, color=TEXT_LIGHT),
                                ],
                            ),
                        ],
                    ),
                    control,
                ],
            ),
        )

    card1 = card(
        delay=0.15,
        content=ft.Column(
            spacing=8,
            controls=[
                setting_row(
                    ft.Icons.GRAPHIC_EQ_ROUNDED, PRIMARY_COLOR,
                    "Anti-Snore Mode",
                    "Vibrate gently when snoring is detected",
                    anti_snore_switch,
                ),
                ft.Divider(height=1, color="#EDEFF5"),
                ft.Container(height=4),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(spacing=12, controls=[
                            vib_icon,
                            ft.Text("Vibration Intensity", size=13,
                                    weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                        ]),
                        level_chip,
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
                ft.Row(spacing=6, controls=[
                    ft.Icon(ft.Icons.TOUCH_APP_ROUNDED, size=14, color=TEXT_LIGHT),
                    ft.Text("Release the slider to feel the vibration on your pillow.",
                            size=11, color=TEXT_LIGHT, expand=True),
                ]),
                ft.Button(
                    content="Test vibration",
                    icon=ft.Icons.WAVES_ROUNDED,
                    on_click=preview,
                    style=btn_style("#E8EBFF", PRIMARY_DARK),
                ),
            ],
        ),
    )

    card2 = card(
        delay=0.3,
        content=ft.Column(
            controls=[
                setting_row(
                    ft.Icons.BOLT_ROUNDED, WARN_COLOR,
                    "Quick Start Mode",
                    "Skip nightly check-in questions",
                    quick_start_switch,
                ),
                ft.Divider(height=1, color="#EDEFF5"),
                setting_row(
                    ft.Icons.PEOPLE_ALT_ROUNDED, SUCCESS_COLOR,
                    "Partner-Safe Alerts",
                    "Reduce vibration reach to avoid waking partner",
                    partner_safe_switch,
                ),
            ],
        ),
    )

    insight_box = fade_in(ft.Container(
        border_radius=18,
        padding=14,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT,
            colors=["#EEF0FD", "#E3E7FF"]),
        content=ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Icon(ft.Icons.LIGHTBULB_ROUNDED, color=WARN_COLOR, size=22),
                ft.Text(
                    "Tip: try a low intensity with Partner-Safe Alerts on if you sleep with a partner.",
                    size=12,
                    color=TEXT_DARK,
                    expand=True,
                ),
            ],
        ),
    ), 0.45)

    save_btn = fade_in(ft.Button(
        content="Save Settings",
        icon=ft.Icons.SAVE_ROUNDED,
        width=340,
        height=54,
        style=btn_style(PRIMARY_COLOR, WHITE, 18),
        on_click=handle_save,
    ), 0.55)

    return ft.Column(
        expand=True,
        controls=[
            ft.Container(
                expand=True,
                gradient=bg_gradient(),
                padding=20,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        page_header("Anti-Snore Settings", "Fine-tune vibration & alerts",
                                    on_back=lambda e: show_screen("/settings")),
                        ft.Container(height=6),
                        card1,
                        card2,
                        insight_box,
                        ft.Container(height=6),
                        save_btn,
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