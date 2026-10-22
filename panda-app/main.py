import flet as ft
from screens.generator_screen import GeneratorScreen

class App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "PANDA - Dot Array Generator"
        self.page.window.width = 1100
        self.page.window.height = 900
        self.page.window.resizable = False

        self.version = "0.0.1"

        self.generator_screen = GeneratorScreen(self)

        self.page.on_route_change = self.route_change
        
        self.url_launcher = ft.UrlLauncher()

        self.page.route = "/generator"
        self.route_change(None)

    def navigate_to(self, route_name: str):
        self.page.route = route_name
        self.route_change(None)

    def route_change(self, e):
        self.page.views.clear()

        if self.page.route == "/generator" or self.page.route == "/":
            self.page.views.append(self.generator_screen)

        self.page.update()

def main(page: ft.Page):
    App(page)

if __name__ == "__main__":
    ft.run(main)