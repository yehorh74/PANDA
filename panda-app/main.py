import os
import warnings

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
warnings.filterwarnings("ignore", category=DeprecationWarning)

import flet as ft

from screens.generator_screen import GeneratorScreen

class App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "PANDA (Python Automating Numerical Dot Algorithm)"

        self.version = "v0.0.5"

        self.generator_screen = GeneratorScreen(self)

        self.url_launcher = ft.UrlLauncher()

    def navigate_to(self, route_name: str):
        self.page.route = route_name
        self.route_change(None)

    def route_change(self, e):
        self.page.views.clear()

        if self.page.route == "/generator" or self.page.route == "/":
            self.page.views.append(self.generator_screen)

        self.page.update()

    async def init(self):
        prefs = ft.SharedPreferences()

        self.page.window.width = 1100
        self.page.window.height = 900
        self.page.window.resizable = False
        self.page.window.maximizable = False  
        self.page.window.full_screen = False
        self.page.window.update()
        
        try:
            saved_theme = await prefs.get("theme_mode")
        except Exception:
            saved_theme = "system"

        if saved_theme == "light":
            self.page.theme_mode = ft.ThemeMode.LIGHT
        elif saved_theme == "dark":
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.SYSTEM

        self.page.on_route_change = self.route_change
        
        self.page.route = "/generator"
        self.route_change(None)

        if hasattr(self, "generator_screen") and self.generator_screen:
            self.generator_screen.apply_initial_theme_ui(saved_theme)

        if hasattr(self, "generator_screen") and self.generator_screen:
            self.page.on_keyboard_event = self.generator_screen.handle_keyboard_shortcuts

async def main(page: ft.Page):
    app = App(page)
    await app.init()

if __name__ == "__main__":
    ft.run(main)