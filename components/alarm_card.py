from datetime import datetime, time as dtime

import flet as ft
from constants.config import *
from components.ui import card, card_title, btn_style
from services import esp_service
from services import alarm_service


def _pretty(t24: str) -> str:
    try:
        return datetime.strptime(t24, "%H:%M").strftime("%I:%M %p")
    except ValueError:
        return t24


def alarm_card(page: ft.Page):
    user_id = getattr(page, "session_user_id", None)
    items = alarm_service.load_alarms(user_id)

    esp_service.set_alarm_times([i["time"] for i in items if i.get("enabled")])

    list_col = ft.Column(spacing=8)
    msg = ft.Text("", size=12, color=PRIMARY_COLOR)
    ring_text = ft.Text("", size=14, weight=ft.FontWeight.BOLD, color=DANGER_COLOR)
    stop_btn = ft.Button(
        content="Stop alarm", icon=ft.Icons.ALARM_OFF_ROUNDED,
        style=btn_style(DANGER_COLOR), visible=False,
    )

    def show_dlg(d):
        if hasattr(page, "show_dialog"):
            page.show_dialog(d)
        else:
            page.open(d)

    def close_dlg(d):
        if hasattr(page, "pop_dialog"):
            page.pop_dialog()
        else:
            d.open = False
            page.update()

    def persist():
        enabled = [i["time"] for i in items if i.get("enabled")]
        esp_service.set_alarm_times(enabled)
        esp_service.run_async(alarm_service.save_alarms, user_id, [dict(i) for i in items])

    def make_row(it):
        on = bool(it.get("enabled", True))
        row = ft.Container(
            padding=ft.Padding.symmetric(horizontal=14, vertical=6) if hasattr(ft, "Padding") else 10,
            border_radius=16,
            bgcolor="#F7F8FD",
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )
        icon = ft.Icon(
            ft.Icons.ALARM_ON_ROUNDED if on else ft.Icons.ALARM_OFF_ROUNDED,
            color=PRIMARY_COLOR if on else TEXT_LIGHT, size=22,
        )
        time_txt = ft.Text(
            _pretty(it["time"]), size=22, weight=ft.FontWeight.W_800,
            color=TEXT_DARK if on else TEXT_LIGHT,
        )

        def on_toggle(e):
            it["enabled"] = bool(e.control.value)
            icon.name = ft.Icons.ALARM_ON_ROUNDED if it["enabled"] else ft.Icons.ALARM_OFF_ROUNDED
            icon.color = PRIMARY_COLOR if it["enabled"] else TEXT_LIGHT
            time_txt.color = TEXT_DARK if it["enabled"] else TEXT_LIGHT
            persist()
            page.update()

        def on_delete(e):
            if it in items:
                items.remove(it)
            persist()
            render()
            page.update()

        row.content = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(spacing=10, controls=[icon, time_txt]),
                ft.Row(
                    spacing=0,
                    controls=[
                        ft.Switch(value=on, on_change=on_toggle, active_color=PRIMARY_COLOR),
                        ft.IconButton(icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                      icon_color=DANGER_COLOR, on_click=on_delete),
                    ],
                ),
            ],
        )
        return row

    def render():
        list_col.controls.clear()
        if not items:
            list_col.controls.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[ft.Icon(ft.Icons.ALARM_ADD_ROUNDED, size=18, color=TEXT_LIGHT),
                              ft.Text("No alarms yet", size=12, color=TEXT_LIGHT)],
                )
            )
        for it in sorted(items, key=lambda x: x["time"]):
            list_col.controls.append(make_row(it))

    def add_time(t):
        if any(i["time"] == t for i in items):
            msg.value = f"Alarm {_pretty(t)} already exists"
            msg.color = WARN_COLOR
            page.update()
            return
        items.append({"time": t, "enabled": True})
        msg.value = f"Alarm {_pretty(t)} added"
        msg.color = SUCCESS_COLOR
        persist()
        render()
        page.update()

    # ---------- time popup ----------
    def open_time_dialog(init_h=None, init_m=None, init_pm=None):
        now = datetime.now()
        h12 = init_h if init_h is not None else (now.hour % 12 or 12)
        mm = init_m if init_m is not None else now.minute
        pm = init_pm if init_pm is not None else (now.hour >= 12)
        st = {"pm": pm}

        def num_field(val, label, mx):
            def limit(e):
                v = (e.control.value or "")[:2]
                if v != e.control.value:
                    e.control.value = v
                    e.control.update()

            return ft.TextField(
                value=f"{val:02d}", label=label, width=96, text_align=ft.TextAlign.CENTER,
                text_size=34,
                keyboard_type=ft.KeyboardType.NUMBER,
                filled=True, bgcolor="#F1F3FF", border_radius=18,
                input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]", replacement_string=""),
                content_padding=14,
                on_change=limit,
            )

        hour_f = num_field(h12, "Hour", 12)
        min_f = num_field(mm, "Min", 59)
        err = ft.Text("", size=12, color=DANGER_COLOR)

        am_box = ft.Container(
            width=64, height=46, border_radius=14, alignment=ft.Alignment.CENTER,
            animate=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
        )
        pm_box = ft.Container(
            width=64, height=46, border_radius=14, alignment=ft.Alignment.CENTER,
            animate=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
        )
        am_txt = ft.Text("AM", weight=ft.FontWeight.BOLD)
        pm_txt = ft.Text("PM", weight=ft.FontWeight.BOLD)
        am_box.content, pm_box.content = am_txt, pm_txt

        def paint():
            for box, txt, active in ((am_box, am_txt, not st["pm"]), (pm_box, pm_txt, st["pm"])):
                box.bgcolor = PRIMARY_COLOR if active else "#EAECF6"
                txt.color = WHITE if active else TEXT_LIGHT

        def set_pm(v):
            st["pm"] = v
            paint()
            page.update()

        am_box.on_click = lambda e: set_pm(False)
        pm_box.on_click = lambda e: set_pm(True)
        paint()

        dlg = ft.AlertDialog(modal=True, shape=ft.RoundedRectangleBorder(radius=26))

        def cancel(e):
            close_dlg(dlg)

        def confirm(e):
            try:
                h = int(hour_f.value)
                m = int(min_f.value)
            except (TypeError, ValueError):
                err.value = "Enter hour and minute"
                page.update()
                return
            if not (1 <= h <= 12) or not (0 <= m <= 59):
                err.value = "Hour 1-12, minute 00-59"
                page.update()
                return
            h24 = (h % 12) + (12 if st["pm"] else 0)
            t = f"{h24:02d}:{m:02d}"
            close_dlg(dlg)
            add_time(t)

        def use_clock(e):
            try:
                h_cur = int(hour_f.value or 0) % 12 + (12 if st["pm"] else 0)
                m_cur = int(min_f.value or 0)
            except ValueError:
                h_cur, m_cur = now.hour, now.minute

            close_dlg(dlg)

            def picked(ev):
                v = ev.control.value
                if v:
                    open_time_dialog(v.hour % 12 or 12, v.minute, v.hour >= 12)

            def dismissed(ev):
                open_time_dialog(h_cur % 12 or 12, m_cur, h_cur >= 12)

            try:
                tp = ft.TimePicker(value=dtime(h_cur % 24, m_cur % 60),
                                   on_change=picked, on_dismiss=dismissed)
                show_dlg(tp)
            except Exception:
                open_time_dialog(h_cur % 12 or 12, m_cur, h_cur >= 12)

        dlg.title = ft.Row(spacing=10, controls=[
            ft.Icon(ft.Icons.ALARM_ADD_ROUNDED, color=WARN_COLOR),
            ft.Text("Set alarm time", weight=ft.FontWeight.W_800, color=TEXT_DARK),
        ])
        dlg.content = ft.Container(
            width=300,
            content=ft.Column(
                tight=True, spacing=14,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Type the time or pick from the clock", size=12, color=TEXT_LIGHT),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            hour_f,
                            ft.Text(":", size=34, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                            min_f,
                            ft.Column(spacing=6, controls=[am_box, pm_box]),
                        ],
                    ),
                    ft.TextButton(
                        content="Pick from clock", icon=ft.Icons.ACCESS_TIME_ROUNDED,
                        style=ft.ButtonStyle(color=PRIMARY_COLOR), on_click=use_clock,
                    ),
                    err,
                ],
            ),
        )
        dlg.actions = [
            ft.TextButton(content="Cancel", style=ft.ButtonStyle(color=TEXT_LIGHT), on_click=cancel),
            ft.Button(content="Add alarm", icon=ft.Icons.CHECK_ROUNDED,
                      style=btn_style(PRIMARY_COLOR), on_click=confirm),
        ]
        dlg.actions_alignment = ft.MainAxisAlignment.END
        show_dlg(dlg)

    def on_open_dialog(e):
        msg.value = ""
        open_time_dialog()

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

    return card(
        delay=0.4,
        content=ft.Column(
            spacing=12,
            controls=[
                card_title(ft.Icons.ALARM_ROUNDED, "Alarms",
                           "Buzzer on the pillow rings at these times", WARN_COLOR),
                list_col,
                ft.Button(
                    content="Add alarm", icon=ft.Icons.ADD_ALARM_ROUNDED,
                    on_click=on_open_dialog, style=btn_style(PRIMARY_COLOR),
                ),
                msg,
                ring_text,
                stop_btn,
            ],
        ),
    )