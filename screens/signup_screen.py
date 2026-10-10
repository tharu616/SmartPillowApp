import flet as ft
from constants.config import *
from components.ui import fade_in, btn_style
from services.auth_service import sign_up_user
from services.firestore_service import save_user_profile


def _field(label, hint, icon, **kw):
    return ft.TextField(
        label=label, hint_text=hint, prefix_icon=icon,
        border_radius=16, filled=True, bgcolor=WHITE,
        border_color=ft.Colors.TRANSPARENT, focused_border_color=PRIMARY_COLOR,
        **kw,
    )


def signup_screen_view(page: ft.Page, show_screen):
    name_field = _field("Full Name", "Your name", ft.Icons.PERSON_ROUNDED)
    email_field = _field("Email", "you@example.com", ft.Icons.EMAIL_ROUNDED)
    password_field = _field("Password", "At least 6 characters", ft.Icons.LOCK_ROUNDED,
                            password=True, can_reveal_password=True)

    error_text = ft.Text("", color=DANGER_COLOR, size=12)
    loading = ft.ProgressRing(visible=False, width=20, height=20, color=PRIMARY_COLOR)

    def handle_signup(e):
        error_text.value = ""
        name = name_field.value.strip()
        email = email_field.value.strip()
        password = password_field.value.strip()

        if not name or not email or not password:
            error_text.value = "Please fill in all fields."
            page.update()
            return

        if len(password) < 6:
            error_text.value = "Password must be at least 6 characters."
            page.update()
            return

        loading.visible = True
        page.update()

        result = sign_up_user(email, password)

        loading.visible = False

        if "error" in result:
            error_text.value = result["error"].get("message", "Sign up failed.")
            page.update()
            return

        user_id = result.get("localId")

        save_user_profile(user_id, name, email)

        page.session_user_id = user_id
        page.session_user_name = name

        show_screen("/home")

    logo = ft.Container(
        width=72, height=72, border_radius=24,
        gradient=ft.LinearGradient(colors=[ACCENT_COLOR, PRIMARY_COLOR]),
        alignment=ft.Alignment.CENTER,
        shadow=ft.BoxShadow(blur_radius=24, color=ft.Colors.with_opacity(0.35, PRIMARY_COLOR),
                            offset=ft.Offset(0, 10)),
        content=ft.Icon(ft.Icons.PERSON_ADD_ALT_1_ROUNDED, size=34, color=WHITE),
    )

    return ft.Container(
        expand=True,
        padding=22,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER, end=ft.Alignment.BOTTOM_CENTER,
            colors=["#E6E9FF", BG_COLOR, WHITE]),
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.IconButton(icon=ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, icon_size=18,
                              icon_color=TEXT_DARK, on_click=lambda e: show_screen("/login")),
                fade_in(logo, 0.05),
                ft.Container(height=6),
                fade_in(ft.Text("Create Account", size=28, weight=ft.FontWeight.W_800, color=TEXT_DARK), 0.15),
                fade_in(ft.Text("Sign up to start tracking your sleep with Smart Pillow.",
                                size=13, color=TEXT_LIGHT), 0.25),
                ft.Container(height=20),
                fade_in(name_field, 0.35),
                ft.Container(height=12),
                fade_in(email_field, 0.45),
                ft.Container(height=12),
                fade_in(password_field, 0.55),
                ft.Container(height=8),
                error_text,
                ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[loading]),
                fade_in(ft.Button(
                    content="Create Account", icon=ft.Icons.CHECK_CIRCLE_ROUNDED,
                    width=340, height=54, style=btn_style(PRIMARY_COLOR, WHITE, 18),
                    on_click=handle_signup,
                ), 0.65),
                ft.Container(height=10),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Already have an account?", size=12, color=TEXT_LIGHT),
                        ft.TextButton(
                            content="Log In",
                            style=ft.ButtonStyle(color=PRIMARY_COLOR),
                            on_click=lambda e: show_screen("/login"),
                        ),
                    ],
                ),
            ],
        ),
    )