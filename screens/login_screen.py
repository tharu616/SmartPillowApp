import flet as ft
from constants.config import *
from services.auth_service import sign_in_user
from services.firestore_service import get_user_profile


def login_screen_view(page: ft.Page, show_screen):
    email_field = ft.TextField(
        label="Email",
        hint_text="you@example.com",
        prefix_icon=ft.Icons.EMAIL,
        border_radius=14,
        filled=True,
        bgcolor=WHITE,
    )

    password_field = ft.TextField(
        label="Password",
        hint_text="••••••••",
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True,
        border_radius=14,
        filled=True,
        bgcolor=WHITE,
    )

    error_text = ft.Text("", color=ft.Colors.RED, size=12)
    loading = ft.ProgressRing(visible=False, width=20, height=20)

    def handle_login(e):
        error_text.value = ""
        email = email_field.value.strip()
        password = password_field.value.strip()

        if not email or not password:
            error_text.value = "Please enter email and password."
            page.update()
            return

        loading.visible = True
        page.update()

        result = sign_in_user(email, password)

        loading.visible = False

        if "error" in result:
            error_text.value = result["error"].get("message", "Login failed.")
            page.update()
            return

        user_id = result.get("localId")
        profile = get_user_profile(user_id)

        page.session_user_id = user_id
        page.session_user_name = profile.get("name") if profile else "User"

        show_screen("/home")

    return ft.Container(
        expand=True,
        bgcolor=BG_COLOR,
        padding=20,
        content=ft.Column(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: show_screen("/"),
                ),
                ft.Text("Welcome Back", size=24, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(
                    "Log in to sync your sleep data and continue tracking with your Smart Pillow.",
                    size=13,
                    color=TEXT_LIGHT,
                ),
                ft.Container(height=20),
                email_field,
                ft.Container(height=12),
                password_field,
                ft.Container(height=8),
                error_text,
                ft.Container(height=10),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[loading],
                ),
                ft.Button(
                    content="Log In",
                    width=320,
                    height=50,
                    bgcolor=PRIMARY_COLOR,
                    color=WHITE,
                    on_click=handle_login,
                ),
                ft.Container(height=10),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Don't have an account?", size=12, color=TEXT_LIGHT),
                        ft.Button(
                            content="Sign Up",
                            color=PRIMARY_COLOR,
                            on_click=lambda e: show_screen("/signup"),
                        ),
                    ],
                ),
            ],
        ),
    )