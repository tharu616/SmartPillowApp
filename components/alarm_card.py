from datetime import datetime

import flet as ft
from constants.config import *
from services import esp_service
from services import alarm_service


def alarm_card(page: ft.Page):
    user_id = getattr(page, "session_user_id", None)
    items = alarm_service.load_alarms(user_id)

    esp_service.set_alarm_times([i["time"] for i in items if i.get("enabled")])

    list_col = ft.Column(spacing=4)
    time_field = ft.TextField(label="Time (HH:MM)", hint_text="06:30", width=150, dense=True)
    msg = ft.Text("", size=12, color=PRIMARY_COLOR)
    ring_text = ft.Text("", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_400)
    stop_btn = ft.Button(content="Stop alarm", visible=False)

    def persist():
        enabled = [i["time"] for i in items if i.get("enabled")]
        esp_service.set_alarm_times(enabled)
        esp_service.run_async(alarm_service.save_alarms, user_id, [dict(i) for i in items])

    def make_row(it):
        def on_toggle(e):
            it["enabled"] = bool(e.control.value)
            persist()

        def on_delete(e):
            if it in items:
                items.remove(it)
            persist()
            render()
            page.update()

        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(it["time"], size=20, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.Switch(value=bool(it.get("enabled", True)), on_change=on_toggle),
                        ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, on_click=on_delete),
                    ],
                ),
            ],
        )

    def render():
        list_col.controls.clear()
        if not items:
            list_col.controls.append(ft.Text("No alarms yet", size=12, color=TEXT_LIGHT))
        for it in sorted(items, key=lambda x: x["time"]):
            list_col.controls.append(make_row(it))

    def on_add(e):
        raw = (time_field.value or "").strip()
        try:
            t = datetime.strptime(raw, "%H:%M").strftime("%H:%M")
        except ValueError:
            msg.value = "Enter time like 06:30 (24-hour)"
            page.update()
            return
        if any(i["time"] == t for i in items):
            msg.value = f"Alarm {t} already exists"
            page.update()
            return
        items.append({"time": t, "enabled": True})
        time_field.value = ""
        msg.value = f"Alarm {t} added"
        persist()
        render()
        page.update()

    def on_stop(e):
        esp_service.run_async(esp_service.alarm_stop)

    stop_btn.on_click = on_stop

    def on_status(connected, res):
        ringing = bool(connected and res.get("ringing"))
        ring_text.value = "Alarm ringing!" if ringing else ""
        stop_btn.visible = ringing
        try:
            page.update()
        except Exception:
            pass

    esp_service.set_listener(on_status, key="alarm")
    render()

    return ft.Container(
        bgcolor=WHITE,
        border_radius=16,
        padding=16,
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Text("Alarms", size=14, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text("Buzzer on the pillow rings at these times", size=12, color=TEXT_LIGHT),
                list_col,
                ft.Row(controls=[time_field, ft.Button(content="Add alarm", on_click=on_add)]),
                msg,
                ring_text,
                stop_btn,
            ],
        ),
    )