from datetime import datetime

import flet as ft
from constants.config import *
from services import esp_service
from services.firestore_service import save_sleep_session


def _stop_and_collect():
    """Session stop කරන්න කලින් ESP එකෙන් කාලයයි snore count එකයි ගන්නවා."""
    st = esp_service.get_status()
    if not st.get("ok"):
        return st
    r = esp_service.stop_session()
    if not r.get("ok"):
        return r
    return {
        "ok": True,
        "secs": int(st.get("sessionSec", 0)),
        "snores": int(st.get("snores", 0)),
    }


def pillow_card(page: ft.Page):
    info = ft.Text("Not checked yet", size=12, color=TEXT_LIGHT)
    session_text = ft.Text("No active session", size=12, color=TEXT_LIGHT)
    ip_field = ft.TextField(
        label="Pillow IP",
        value=esp_service.get_ip(),
        dense=True,
        on_change=lambda e: esp_service.set_ip(e.control.value),
    )
    session_btn = ft.Button(content="Start sleep session")
    state = {"active": False}

    def check(e=None):
        info.value = "Connecting..."
        page.update()

        def done(res):
            if res.get("ok"):
                info.value = (
                    f"Connected ({res.get('ip')})\n"
                    f"Sound {res.get('sound')} | Pressure {res.get('pressDiff')} hPa\n"
                    f"Pump {'ON' if res.get('pump') else 'off'} | "
                    f"Valve {'ON' if res.get('valve') else 'off'}"
                )
            else:
                info.value = f"Not connected: {res.get('error')}"
            page.update()

        esp_service.run_async(esp_service.get_status, on_done=done)

    # ESP එකේ session status එක auto update වෙනවා (head detect වුනාම)
    def on_status(connected, res):
        if not connected:
            state["active"] = False
            session_btn.content = "Start sleep session"
            session_text.value = "Pillow not connected"
        elif res.get("session"):
            sec = int(res.get("sessionSec", 0))
            state["active"] = True
            session_btn.content = "Stop & save"
            session_text.value = (
                f"Sleeping... {sec // 60}m {sec % 60}s | snores {res.get('snores', 0)}"
            )
        else:
            state["active"] = False
            session_btn.content = "Start sleep session"
            if res.get("headOn"):
                session_text.value = "Head detected"
            else:
                session_text.value = esp_service.get_last_saved() or "No active session"
        try:
            page.update()
        except Exception:
            pass

    esp_service.set_listener(on_status, key="pillow")

    def toggle_session(e):
        if not state["active"]:
            def started(res):
                if res.get("ok"):
                    state["active"] = True
                    session_btn.content = "Stop & save"
                    session_text.value = "Session running..."
                else:
                    session_text.value = f"Error: {res.get('error')}"
                page.update()

            esp_service.run_async(esp_service.start_session, on_done=started)
        else:
            def stopped(res):
                if not res.get("ok"):
                    session_text.value = f"Error: {res.get('error')}"
                    page.update()
                    return
                secs = int(res.get("secs", 0))
                snores = int(res.get("snores", 0))
                score = max(40, 100 - snores * 4)
                quality = "good" if score >= 80 else "fair" if score >= 60 else "poor"
                duration = f"{secs // 3600}h {(secs % 3600) // 60}m"
                user_id = getattr(page, "session_user_id", None)
                if user_id:
                    save_sleep_session(user_id, {
                        "sleep_score": score,
                        "quality": quality,
                        "duration": duration,
                        "snore_count": snores,
                        "created_at": datetime.utcnow(),
                    })
                msg = f"Saved: {duration}, {snores} snore events, score {score}"
                esp_service.set_last_saved(msg)
                state["active"] = False
                session_btn.content = "Start sleep session"
                session_text.value = msg
                page.update()

            esp_service.run_async(_stop_and_collect, on_done=stopped)

    session_btn.on_click = toggle_session

    return ft.Container(
        bgcolor=WHITE,
        border_radius=16,
        padding=16,
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Text("Pillow device", size=14, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ip_field,
                info,
                ft.Button(content="Check pillow", on_click=check),
                session_text,
                session_btn,
            ],
        ),
    )