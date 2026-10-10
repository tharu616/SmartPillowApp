import threading
from datetime import datetime, timedelta, timezone

import flet as ft
import flet_charts as fch
from constants.config import *
from components.bottom_nav import bottom_nav
from components.ui import card, icon_badge, page_header, bg_gradient, fade_in
from services.firestore_service import get_recent_sleep_sessions


def _quality_style(q):
    q = str(q).lower()
    if q == "good":
        return SUCCESS_COLOR, ft.Icons.SENTIMENT_VERY_SATISFIED_ROUNDED
    if q == "fair":
        return WARN_COLOR, ft.Icons.SENTIMENT_NEUTRAL_ROUNDED
    return DANGER_COLOR, ft.Icons.SENTIMENT_DISSATISFIED_ROUNDED


def _dt(s):
    v = s.get("created_at")
    if isinstance(v, datetime):
        return v.replace(tzinfo=None)
    return None


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _avg(lst):
    vals = [x for x in (_num(s.get("sleep_score")) for s in lst) if x is not None]
    return sum(vals) / len(vals) if vals else None


def _snores(lst):
    return sum(int(_num(s.get("snore_count")) or 0) for s in lst)


def _build_period(mode, sessions):
    """returns labels, values(avg score per bucket), cur sessions, prev sessions"""
    dated = [s for s in sessions if _dt(s)]
    today = datetime.now(timezone.utc).date()

    if len(dated) != len(sessions) or not sessions:
        recent = list(reversed(sessions[:7]))
        labels = [f"S{i + 1}" for i in range(len(recent))]
        values = [_num(s.get("sleep_score")) for s in recent]
        return labels, values, sessions[:7], sessions[7:14]

    if mode == "Daily":
        ordered = sorted(dated, key=_dt, reverse=True)
        recent = list(reversed(ordered[:7]))
        labels = [_dt(s).strftime("%d/%m") for s in recent]
        values = [_num(s.get("sleep_score")) for s in recent]
        return labels, values, ordered[:1], ordered[1:2]

    if mode == "Weekly":
        monday = today - timedelta(days=today.weekday())
        labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        values = []
        for i in range(7):
            d = monday + timedelta(days=i)
            day_s = [s for s in dated if _dt(s).date() == d]
            values.append(_avg(day_s))
        cur = [s for s in dated if _dt(s).date() >= monday]
        prev = [s for s in dated if monday - timedelta(days=7) <= _dt(s).date() < monday]
        return labels, values, cur, prev

    labels = ["3w ago", "2w ago", "Last wk", "This wk"]
    buckets = [[], [], [], []]
    for s in dated:
        age = (today - _dt(s).date()).days
        if 0 <= age < 28:
            buckets[3 - age // 7].append(s)
    values = [_avg(b) for b in buckets]
    cur = [s for s in dated if 0 <= (today - _dt(s).date()).days < 30]
    prev = [s for s in dated if 30 <= (today - _dt(s).date()).days < 60]
    return labels, values, cur, prev


def trends_screen_view(page: ft.Page, show_screen):
    nav = bottom_nav(show_screen, 1)

    user_id = getattr(page, "session_user_id", None)
    sessions = get_recent_sleep_sessions(user_id) if user_id else []

    state = {"mode": "Weekly"}
    tabs_row = ft.Row(spacing=10)
    chart_holder = ft.Container()
    pie_holder = ft.Container()
    stats_holder = ft.Container()

    def chart_card(labels, values, cur, prev):
        bars = []
        cols = []
        for lb, v in zip(labels, values):
            target = 0 if v is None else max(6, v / 100 * 150)
            bar = ft.Container(
                width=24, height=0, border_radius=12,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment.TOP_CENTER, end=ft.Alignment.BOTTOM_CENTER,
                    colors=[ACCENT_COLOR, PRIMARY_COLOR]) if v is not None else None,
                bgcolor=None if v is not None else "#EDEFF5",
                animate=ft.Animation(800, ft.AnimationCurve.EASE_OUT),
            )
            bars.append((bar, target if v is not None else 6))
            cols.append(ft.Column(
                spacing=6,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.Text("" if v is None else f"{int(round(v))}", size=10,
                            weight=ft.FontWeight.BOLD, color=PRIMARY_DARK),
                    bar,
                    ft.Text(lb, size=10, weight=ft.FontWeight.W_600, color=TEXT_LIGHT),
                ],
            ))

        def grow():
            for b, h in bars:
                b.height = h
                try:
                    b.update()
                except Exception:
                    pass

        threading.Timer(0.25, grow).start()

        a_cur, a_prev = _avg(cur), _avg(prev)
        if a_cur is not None and a_prev:
            ch = (a_cur - a_prev) / a_prev * 100
            up = ch >= 0
            badge_txt = f"{abs(ch):.0f}% vs last"
            badge_col = SUCCESS_COLOR if up else DANGER_COLOR
            badge_icon = ft.Icons.TRENDING_UP_ROUNDED if up else ft.Icons.TRENDING_DOWN_ROUNDED
        else:
            badge_txt, badge_col, badge_icon = "No compare", TEXT_LIGHT, ft.Icons.REMOVE_ROUNDED

        badge = ft.Container(
            padding=ft.Padding.symmetric(horizontal=10, vertical=5) if hasattr(ft, "Padding") else 6,
            border_radius=20, bgcolor=badge_col,
            content=ft.Row(tight=True, spacing=4, controls=[
                ft.Icon(badge_icon, size=14, color=WHITE),
                ft.Text(badge_txt, size=11, weight=ft.FontWeight.BOLD, color=WHITE),
            ]),
        )
        return card(
            content=ft.Column(spacing=14, controls=[
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    ft.Row(spacing=10, controls=[
                        icon_badge(ft.Icons.INSIGHTS_ROUNDED, PRIMARY_COLOR, 20),
                        ft.Text("Sleep Score Trend", size=15, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                    ]),
                    badge,
                ]),
                ft.Container(
                    height=200,
                    alignment=ft.Alignment.BOTTOM_CENTER,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        controls=cols,
                    ),
                ),
            ]),
        )

    def pie_card(cur):
        data = cur or sessions
        counts = {"good": 0, "fair": 0, "poor": 0}
        for s in data:
            q = str(s.get("quality", "")).lower()
            counts[q if q in counts else "poor"] += 1
        total = sum(counts.values())
        colors = {"good": SUCCESS_COLOR, "fair": WARN_COLOR, "poor": DANGER_COLOR}

        if total == 0:
            body = ft.Text("No data yet", size=12, color=TEXT_LIGHT)
        else:
            sections = [
                fch.PieChartSection(
                    value=n, title=f"{n / total * 100:.0f}%", color=colors[k], radius=46,
                    title_style=ft.TextStyle(size=11, weight=ft.FontWeight.BOLD, color=WHITE),
                )
                for k, n in counts.items() if n > 0
            ]
            avg = _avg(data)
            body = ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Stack(width=170, height=170, controls=[
                        fch.PieChart(sections=sections, sections_space=3,
                                     center_space_radius=44, expand=True),
                        ft.Container(
                            alignment=ft.Alignment.CENTER, expand=True,
                            content=ft.Column(
                                spacing=0, tight=True,
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text("--" if avg is None else f"{avg:.0f}", size=22,
                                            weight=ft.FontWeight.W_800, color=TEXT_DARK),
                                    ft.Text("avg", size=10, color=TEXT_LIGHT),
                                ]),
                        ),
                    ]),
                    ft.Column(spacing=10, controls=[
                        ft.Row(spacing=8, controls=[
                            ft.Container(width=12, height=12, border_radius=6, bgcolor=colors[k]),
                            ft.Text(f"{k.capitalize()} ({n})", size=12, color=TEXT_DARK),
                        ]) for k, n in counts.items()
                    ]),
                ],
            )
        return card(
            content=ft.Column(spacing=10, controls=[
                ft.Row(spacing=10, controls=[
                    icon_badge(ft.Icons.PIE_CHART_ROUNDED, ACCENT_COLOR, 20),
                    ft.Text("Sleep Quality", size=15, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ]),
                body,
            ]),
        )

    def stats_card(cur, prev):
        a, b = _snores(cur), _snores(prev)
        if b > 0:
            ch = (a - b) / b * 100
            ch_txt = f"{ch:+.0f}%"
            ch_col = SUCCESS_COLOR if ch <= 0 else DANGER_COLOR
        else:
            ch_txt, ch_col = "--", TEXT_LIGHT

        def stat(val, label, color=TEXT_DARK):
            return ft.Column(
                spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(val, size=22, weight=ft.FontWeight.W_800, color=color),
                    ft.Text(label, size=11, color=TEXT_LIGHT),
                ])

        return card(
            content=ft.Column(spacing=14, controls=[
                ft.Row(spacing=10, controls=[
                    icon_badge(ft.Icons.GRAPHIC_EQ_ROUNDED, WARN_COLOR, 20),
                    ft.Text("Snore Events", size=15, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ]),
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_AROUND, controls=[
                    stat(str(a), "This period"),
                    stat(str(b), "Previous"),
                    stat(ch_txt, "Change", ch_col),
                ]),
            ]),
        )

    def render():
        labels, values, cur, prev = _build_period(state["mode"], sessions)
        chart_holder.content = chart_card(labels, values, cur, prev)
        pie_holder.content = pie_card(cur)
        stats_holder.content = stats_card(cur, prev)

        tabs_row.controls.clear()
        for m in ("Daily", "Weekly", "Monthly"):
            active = m == state["mode"]

            def on_tab(e, mm=m):
                state["mode"] = mm
                render()
                page.update()

            tabs_row.controls.append(ft.Container(
                expand=True, height=44, border_radius=16,
                alignment=ft.Alignment.CENTER,
                bgcolor=PRIMARY_COLOR if active else "#EAECF6",
                animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
                shadow=ft.BoxShadow(blur_radius=16, color=ft.Colors.with_opacity(0.3, PRIMARY_COLOR),
                                    offset=ft.Offset(0, 6)) if active else None,
                on_click=on_tab,
                content=ft.Text(m, size=13, weight=ft.FontWeight.BOLD,
                                color=WHITE if active else TEXT_LIGHT),
            ))

    render()

    if sessions:
        session_rows = []
        for i, s in enumerate(sessions):
            color, icon = _quality_style(s.get("quality", "--"))
            score = s.get("sleep_score", "--")
            try:
                prog = max(0.0, min(1.0, float(score) / 100))
            except (TypeError, ValueError):
                prog = 0.0
            session_rows.append(card(
                delay=0.1 + min(i, 8) * 0.08, padding=16, radius=20,
                content=ft.Row(
                    spacing=14,
                    controls=[
                        icon_badge(icon, color, 26),
                        ft.Column(
                            spacing=4, expand=True,
                            controls=[
                                ft.Text(
                                    f"Score: {score} - {s.get('quality', '--').upper()}",
                                    weight=ft.FontWeight.BOLD, color=TEXT_DARK,
                                ),
                                ft.ProgressBar(value=prog, color=color,
                                               bgcolor=ft.Colors.with_opacity(0.12, color),
                                               bar_height=6, border_radius=3),
                                ft.Row(spacing=12, controls=[
                                    ft.Icon(ft.Icons.TIMER_OUTLINED, size=14, color=TEXT_LIGHT),
                                    ft.Text(f"{s.get('duration', '--')}", size=12, color=TEXT_LIGHT),
                                    ft.Icon(ft.Icons.GRAPHIC_EQ_ROUNDED, size=14, color=TEXT_LIGHT),
                                    ft.Text(f"Snore events: {s.get('snore_count', 0)}", size=12, color=TEXT_LIGHT),
                                ]),
                            ],
                        ),
                    ],
                ),
            ))
    else:
        session_rows = [
            card(
                delay=0.1, padding=30,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10,
                    controls=[
                        ft.Icon(ft.Icons.BEDTIME_OFF_ROUNDED, size=48, color=ACCENT_COLOR),
                        ft.Text("No sleep sessions recorded yet.", color=TEXT_LIGHT),
                    ],
                ),
            )
        ]

    tip = fade_in(ft.Container(
        border_radius=18, padding=14,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT,
            colors=["#EEF0FD", "#E3E7FF"]),
        content=ft.Row(
            spacing=12, vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Icon(ft.Icons.LIGHTBULB_ROUNDED, color=WARN_COLOR, size=22),
                ft.Text("Keep a regular sleep schedule and use Anti-Snore mode to reduce snoring.",
                        size=12, color=TEXT_DARK, expand=True),
            ]),
    ), 0.5)

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
                        page_header("Sleep Trends", "Your recent sleep sessions"),
                        tabs_row,
                        chart_holder,
                        pie_holder,
                        stats_holder,
                        tip,
                        ft.Text("Recent sessions", size=15, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                        *session_rows,
                        ft.Container(height=10),
                    ],
                ),
            ),
            nav,
        ],
    )