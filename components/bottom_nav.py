import flet as ft

def bottom_nav(show_screen, selected_index=0):
    routes = ["/home", "/trends", "/height", "/settings"]

    def handle_change(e):
        show_screen(routes[e.control.selected_index])

    return ft.NavigationBar(
        selected_index=selected_index,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
            ft.NavigationBarDestination(icon=ft.Icons.BAR_CHART, label="Trends"),
            ft.NavigationBarDestination(icon=ft.Icons.TUNE, label="Height"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Settings"),
        ],
        on_change=handle_change,
    )