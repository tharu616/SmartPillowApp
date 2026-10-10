import flet as ft
from constants.config import *
from components.bottom_nav import bottom_nav
from components.ui import card, card_title, page_header, bg_gradient, btn_style
from services.firestore_service import get_height_preset, save_height_preset
from services import esp_service


INFLATE_STEP_MS = 600     # level එකක් ඉහළට යන්න pump ධාවන කාලය
DEFLATE_STEP_MS = 600     # level එකක් පහළට යන්න valve විවෘත කාලය


def height_control_screen_view(page: ft.Page, show_screen):
    nav = bottom_nav(show_screen, 2)

    user_id = getattr(page, "session_user_id", None)
    current_value = get_height_preset(user_id) if user_id else 3
    start_level = int(round(current_value)) if current_value else 3
    start_level = max(1, min(5, start_level))

    state = {"level": start_level, "busy": False}

    status_text = ft.Text("", size=12, color=PRIMARY_COLOR)

    height_slider = ft.Slider(
        min=1, max=5, divisions=4, value=start_level, label="{value}",
        active_color=PRIMARY_COLOR, thumb_color=PRIMARY_DARK,
    )

    pillow_visual = ft.Container(
        width=180, height=40 + start_level * 16, border_radius=40,
        gradient=ft.LinearGradient(colors=[ACCENT_COLOR, PRIMARY_COLOR],
                                   begin=ft.Alignment.TOP_CENTER, end=ft.Alignment.BOTTOM_CENTER),
        animate=ft.Animation(700, ft.AnimationCurve.EASE_OUT_BACK),
        alignment=ft.Alignment.CENTER,
        shadow=ft.BoxShadow(blur_radius=30, color=ft.Colors.with_opacity(0.35, PRIMARY_COLOR),
                            offset=ft.Offset(0, 12)),
    )
    level_text = ft.Text(f"Level {start_level}", size=16, weight=ft.FontWeight.BOLD, color=WHITE)
    pillow_visual.content = level_text

    def sync_visual(level):
        pillow_visual.height = 40 + int(level) * 16
        level_text.value = f"Level {int(level)}"

    def set_status(msg):
        status_text.value = msg
        page.update()

    def go_to_level(target: int):
        """Pillow එක ඉලක්ක level එකට ESP එක හරහා ගෙනියන්න."""
        target = max(1, min(5, int(target)))
        diff = target - state["level"]

        if diff == 0:
            height_slider.value = target
            page.update()
            return
        if state["busy"]:
            set_status("Please wait, pillow is moving...")
            return

        state["busy"] = True
        if diff > 0:
            ms = diff * INFLATE_STEP_MS
            set_status(f"Inflating to level {target}...")
            func = esp_service.inflate
        else:
            ms = -diff * DEFLATE_STEP_MS
            set_status(f"Deflating to level {target}...")
            func = esp_service.deflate

        def done(res):
            state["busy"] = False
            if res.get("ok"):
                state["level"] = target
                height_slider.value = target
                sync_visual(target)
                status_text.value = f"Height level {target} set."
            else:
                height_slider.value = state["level"]
                sync_visual(state["level"])
                status_text.value = f"Pillow error: {res.get('error')}"
            page.update()

        esp_service.run_async(func, ms, on_done=done)

    def handle_inflate(e):
        go_to_level(state["level"] + 1)

    def handle_deflate(e):
        go_to_level(state["level"] - 1)

    def handle_slider_release(e):
        go_to_level(round(height_slider.value))

    def handle_stop(e):
        def done(res):
            state["busy"] = False
            status_text.value = "Stopped." if res.get("ok") else f"Pillow error: {res.get('error')}"
            page.update()
        esp_service.run_async(esp_service.stop_all, on_done=done)

    def handle_save(e):
        if not user_id:
            set_status("Please log in first.")
            return
        save_height_preset(user_id, state["level"])
        set_status(f"Preset saved (level {state['level']}).")

    height_slider.on_change_end = handle_slider_release

    return ft.Column(
        expand=True,
        controls=[
            ft.Container(
                expand=True,
                gradient=bg_gradient(),
                padding=20,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    spacing=14,
                    controls=[
                        page_header("Pillow Height Control",
                                    "Adjust air pump inflation to change pillow loft"),
                        card(
                            delay=0.15,
                            content=ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=14,
                                controls=[
                                    ft.Container(
                                        height=150, alignment=ft.Alignment.BOTTOM_CENTER,
                                        content=pillow_visual,
                                    ),
                                    ft.Row(
                                        controls=[ft.Icon(ft.Icons.UNFOLD_LESS_ROUNDED, size=18, color=TEXT_LIGHT),
                                                  ft.Container(content=height_slider, expand=True),
                                                  ft.Icon(ft.Icons.UNFOLD_MORE_ROUNDED, size=18, color=TEXT_LIGHT)],
                                    ),
                                ],
                            ),
                        ),
                        card(
                            delay=0.3,
                            content=ft.Column(
                                spacing=12,
                                controls=[
                                    card_title(ft.Icons.AIR_ROUNDED, "Air pump", "Inflate or deflate one level"),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Button(content="Deflate", icon=ft.Icons.REMOVE_CIRCLE_OUTLINE_ROUNDED,
                                                      on_click=handle_deflate, style=btn_style("#E8EBFF", PRIMARY_DARK)),
                                            ft.Button(content="Inflate", icon=ft.Icons.ADD_CIRCLE_OUTLINE_ROUNDED,
                                                      on_click=handle_inflate, style=btn_style(PRIMARY_COLOR)),
                                        ],
                                    ),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Button(content="Save Preset", icon=ft.Icons.BOOKMARK_ADD_ROUNDED,
                                                      on_click=handle_save, style=btn_style(SUCCESS_COLOR)),
                                            ft.Button(content="Stop", icon=ft.Icons.PAN_TOOL_ROUNDED,
                                                      on_click=handle_stop, style=btn_style(DANGER_COLOR)),
                                        ],
                                    ),
                                    status_text,
                                ],
                            ),
                        ),
                    ],
                ),
            ),
            nav,
        ],
    )