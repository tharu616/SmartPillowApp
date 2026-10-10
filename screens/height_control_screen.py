import flet as ft
from constants.config import *
from components.bottom_nav import bottom_nav
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
        min=1,
        max=5,
        divisions=4,
        value=start_level,
        label="{value}",
    )

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
                status_text.value = f"Height level {target} set."
            else:
                height_slider.value = state["level"]
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
                bgcolor=BG_COLOR,
                padding=20,
                content=ft.Column(
                    controls=[
                        ft.Text("Pillow Height Control", size=24, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                        ft.Text("Adjust air pump inflation to change pillow loft", size=12, color=TEXT_LIGHT),
                        ft.Container(height=20),
                        height_slider,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Button(content="Deflate", on_click=handle_deflate),
                                ft.Button(content="Save Preset", on_click=handle_save),
                                ft.Button(content="Inflate", on_click=handle_inflate),
                            ],
                        ),
                        ft.Container(height=10),
                        ft.Button(content="Stop", on_click=handle_stop),
                        ft.Container(height=10),
                        status_text,
                    ]
                ),
            ),
            nav,
        ],
    )