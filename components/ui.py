import threading
import flet as ft
from constants.config import *

EASE = ft.AnimationCurve.EASE_OUT


def fade_in(ctrl, delay=0.05):
    ctrl.opacity = 0
    ctrl.offset = ft.Offset(0, 0.08)
    ctrl.animate_opacity = ft.Animation(550, EASE)
    ctrl.animate_offset = ft.Animation(550, EASE)

    def go():
        try:
            ctrl.opacity = 1
            ctrl.offset = ft.Offset(0, 0)
            ctrl.update()
        except Exception:
            pass

    threading.Timer(delay, go).start()
    return ctrl


def card(content, padding=18, radius=22, delay=None, bgcolor=WHITE):
    c = ft.Container(
        bgcolor=bgcolor,
        border_radius=radius,
        padding=padding,
        content=content,
        shadow=ft.BoxShadow(
            blur_radius=24,
            spread_radius=0,
            color=ft.Colors.with_opacity(0.10, PRIMARY_COLOR),
            offset=ft.Offset(0, 8),
        ),
    )
    if delay is not None:
        fade_in(c, delay)
    return c


def icon_badge(icon, color=PRIMARY_COLOR, size=22):
    return ft.Container(
        content=ft.Icon(icon, size=size, color=color),
        padding=10,
        border_radius=14,
        bgcolor=ft.Colors.with_opacity(0.12, color),
    )


def card_title(icon, title, subtitle=None, color=PRIMARY_COLOR):
    texts = [ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color=TEXT_DARK)]
    if subtitle:
        texts.append(ft.Text(subtitle, size=11, color=TEXT_LIGHT))
    return ft.Row(
        spacing=12,
        controls=[icon_badge(icon, color), ft.Column(spacing=1, controls=texts, expand=True)],
    )


def page_header(title, subtitle=None, on_back=None):
    left = []
    if on_back:
        left.append(ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_size=18,
                                  icon_color=TEXT_DARK, on_click=on_back))
    col = [ft.Text(title, size=26, weight=ft.FontWeight.W_800, color=TEXT_DARK)]
    if subtitle:
        col.append(ft.Text(subtitle, size=12, color=TEXT_LIGHT))
    return fade_in(ft.Row(controls=[*left, ft.Column(spacing=2, controls=col, expand=True)]), 0.0)


def bg_gradient():
    return ft.LinearGradient(
        begin=ft.Alignment.TOP_CENTER,
        end=ft.Alignment.BOTTOM_CENTER,
        colors=["#EEF0FF", BG_COLOR, "#FFFFFF"],
    )


def btn_style(bg=PRIMARY_COLOR, fg=WHITE, radius=16):
    return ft.ButtonStyle(
        bgcolor=bg,
        color=fg,
        shape=ft.RoundedRectangleBorder(radius=radius),
        elevation=0,
        padding=14,
    )