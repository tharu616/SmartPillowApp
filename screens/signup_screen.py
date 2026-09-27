import flet as ft
from constants.config import *
from services.auth_service import sign_up_user
from services.firestore_service import save_user_profile


def signup_screen_view(page: ft.Page, show_screen):
    name_field = ft.TextField(
        label="Full Name",
        hint_text="Your name",
        prefix_icon=ft.Icons.PERSON,
        border_radius=14,
        filled=True,
        bgcolor=WHITE,
    )

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
        hint_text="At least 6 characters",
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True,
        border_radius=14,
        filled=True,
        bgcolor=WHITE,
    )

    error_text = ft.Text("", color=ft.Colors.RED, size=12)
    loading = ft.ProgressRing(visible=False, width=20, height=20)

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

    return ft.Container(
        expand=True,
        bgcolor=BG_COLOR,
        padding=20,
        content=ft.Column(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: show_screen("/login"),
                ),
                ft.Text("Create Account", size=24, weight=ft.FontWeight.BOLD, color=TEXT_DARK),
                ft.Text(
                    "Sign up to start tracking your sleep with Smart Pillow.",
                    size=13,
                    color=TEXT_LIGHT,
                ),
                ft.Container(height=20),
                name_field,
                ft.Container(height=12),
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
                    content="Create Account",
                    width=320,
                    height=50,
                    bgcolor=PRIMARY_COLOR,
                    color=WHITE,
                    on_click=handle_signup,
                ),
                ft.Container(height=10),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Already have an account?", size=12, color=TEXT_LIGHT),
                        ft.Button(
                            content="Log In",
                            color=PRIMARY_COLOR,
                            on_click=lambda e: show_screen("/login"),
                        ),
                    ],
                ),
            ],
        ),
    )