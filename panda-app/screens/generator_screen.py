import flet as ft
import flet.canvas as cv
import tkinter as tk
from tkinter import filedialog

from panda.generator import PANDA  

from core.validators import parse_and_validate_inputs
from core.exporters import save_current_stimulus_png, save_all, reset_all

class GeneratorScreen(ft.View):
    def __init__(self, app):
        super().__init__(route="/generator")
        self.app = app
        self.generator = PANDA(window=None)
        
        self.generated_datasets = []
        self.current_index = 0

        self.setup_ui()

    def setup_ui(self):
        self.app_menu = ft.MenuBar(
            expand=False,
            controls=[
                ft.SubmenuButton(
                    content=ft.Text("File"),
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text("Export CSV"),
                            leading=ft.Icon(ft.Icons.SAVE),
                            #on_click=self.handle_export_csv
                        ),
                        ft.MenuItemButton(
                            content=ft.Text("Quit"),
                            leading=ft.Icon(ft.Icons.CLOSE),
                            on_click=self.close_app
                        ),
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text("Generator"),
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text("Generate"),
                            leading=ft.Icon(ft.Icons.REFRESH),
                            on_click=self.handle_generation
                        ),
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text("Help"),
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text("Documentation"),
                            leading=ft.Icon(ft.Icons.HELP_OUTLINE),
                            on_click=self.open_info
                        ),
                    ],
                ),
            ],
        )

        my_appbar = ft.AppBar(
            title=ft.Row([
                ft.Text("PANDA", weight=ft.FontWeight.BOLD),
                ft.VerticalDivider(width=20, thickness=0),
                self.app_menu
            ], alignment=ft.MainAxisAlignment.START, spacing=0),
        )
        
        self.radio_group = ft.RadioGroup(
            value="range",
            on_change=self.handle_type_change,
            content=ft.Row(
                controls=[
                    ft.Radio(value="range", label="Range"),
                    ft.Radio(value="fixed", label="Fixed"),
                    ft.Radio(value="list", label="List"),
                ],
                spacing=10
            )
        )

        self.num_container = ft.Container()

        self.handle_type_change(None)
        
        self.spatial_dropdown = ft.Dropdown(
            label="Spatial Type",
            value="CH",
            options=[
                ft.dropdown.Option("CH", "Convex Hull (CH)"),
                ft.dropdown.Option("ID", "Inter-Distance (ID)"),
            ],
            width=300
        )

        self.size_dropdown = ft.Dropdown(
            label="Size Type",
            value="TA",
            options=[
                ft.dropdown.Option("TA", "Total Area (TA)"),
                ft.dropdown.Option("TP", "Total Perimeter (TP)"),
            ],
            width=300
        )

        self.color_dropdown = ft.Dropdown(
            label="Color scheme",
            value="black_on_white",
            options=[
                ft.dropdown.Option("black_on_white", "Black on White"),
                ft.dropdown.Option("white_on_black", "White on Black"),
            ],
            width=300,
            on_select=self.handle_color_change
        )

        self.sd_text = ft.Text("Size variability", size=14)

        self.sd_slider = ft.Slider(
            min=0.0,
            max=1.0,
            divisions=20,
            value=0.20,
            label="SD of radius: 0.20",
            on_change=self.sd_changed
        )

        self.min_dist_checkbox = ft.Checkbox(
            label="Min spacing between elements",
            value=False,
            label_position=ft.LabelPosition.LEFT,
            on_change=self.min_dist_toggle
        )

        self.min_dist_slider = ft.Slider(
            min=0.5,
            max=3.0,
            divisions=25,
            value=1.0,
            label="MD: 1.00",
            disabled=True,  
            on_change=self.min_dist_changed
        )

        self.TA_settings = ft.TextField(label="Total Area", value="30000.0", width=300, keyboard_type=ft.KeyboardType.NUMBER, input_filter=ft.InputFilter(regex_string=r"[0-9.]"))
        self.CH_settings = ft.TextField(label="Convex Hull Area", value="120000.0", width=300, keyboard_type=ft.KeyboardType.NUMBER, input_filter=ft.InputFilter(regex_string=r"[0-9.]"))
        self.anchor_n = ft.TextField(label="Number of Anchors", value="3", width=300, keyboard_type=ft.KeyboardType.NUMBER, input_filter=ft.NumbersOnlyInputFilter())
        self.seed = ft.TextField(label="Random Seed (optional)", value="", width=300, keyboard_type=ft.KeyboardType.NUMBER, input_filter=ft.NumbersOnlyInputFilter())
        self.info_text = ft.Text("Ready.", size=14, color=ft.Colors.GREY_700)

        generate_btn = ft.Button(
            content=ft.Text("Generate"),
            on_click=self.handle_generation,
            width=300,  
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(
                    radius=4
                )  
            ),
        )

        self.dot_canvas = cv.Canvas(
            shapes=[],
            width=700,
            height=700,
        )

        self.prev_btn = ft.IconButton(icon=ft.Icons.ARROW_LEFT, on_click=self.prev_image, disabled=True, tooltip="Previous", icon_color=ft.Colors.BLACK )
        self.next_btn = ft.IconButton(icon=ft.Icons.ARROW_RIGHT, on_click=self.next_image, disabled=True, tooltip="Next", icon_color=ft.Colors.BLACK)
        self.index_label = ft.Text("No stimuli", size=14, color=ft.Colors.BLACK)
        self.delete_btn = ft.IconButton(icon=ft.Icons.DELETE, on_click=self.delete_current, disabled=True, tooltip="Delete current", icon_color=ft.Colors.BLACK)
        self.save_png_btn = ft.IconButton(icon=ft.Icons.DOWNLOAD, on_click=self.save_png, disabled=True, tooltip="Save as PNG", icon_color=ft.Colors.BLACK)

        nav_bar = ft.Row(
            controls=[
                self.prev_btn,
                self.index_label,
                self.next_btn,
                ft.VerticalDivider(width=20),
                self.delete_btn,
                self.save_png_btn,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )

        self.canvas_container = ft.Container(
            content=ft.Column([
                self.dot_canvas,
                nav_bar
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
            width=700,
            height=760,
            alignment=ft.Alignment.CENTER,
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(1, ft.Colors.GREY_400),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            padding=10
        )

        save_btn = ft.Button(
            content=ft.Text("Save all dots and data"),
            width=300,  
            disabled=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(
                    radius=4
                )  
            )
        )

        reset_btn = ft.Button(
            content=ft.Text("Reset generator"),
            width=300,  
            disabled=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(
                    radius=4
                )  
            )
        )

        self.save_btn = save_btn
        self.reset_btn = reset_btn

        save_btn.on_click = lambda e: self.handle_save_click(e)
        reset_btn.on_click = lambda e: reset_all(self, e)

        self.controls = [
            my_appbar,
            ft.Row([
                self.canvas_container,
                ft.VerticalDivider(width=1),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Number of elements", size=18, weight=ft.FontWeight.BOLD),
                        self.radio_group,
                        self.num_container,
                        ft.Divider(),
                        ft.Text("Parameters", size=18, weight=ft.FontWeight.BOLD),
                        self.spatial_dropdown,
                        self.size_dropdown,
                        self.color_dropdown,
                        self.sd_text,
                        self.sd_slider,
                        self.min_dist_checkbox,
                        self.min_dist_slider,
                        ft.Divider(),
                        ft.Text("Advanced settings", size=18, weight=ft.FontWeight.BOLD),
                        self.TA_settings,
                        self.CH_settings,
                        self.anchor_n,
                        self.seed,
                        ft.Divider(),
                        generate_btn,
                        self.save_btn,
                        self.reset_btn,
                        ft.Divider(),
                        self.info_text
                    ], scroll=ft.ScrollMode.AUTO,
                    spacing=10),
                    width=360,
                    padding=20,
                ),
            ], expand=True)
        ]

    def handle_save_click(self, e):
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        folder_path = filedialog.askdirectory(title="Select destination folder for export")

        root.destroy()  

        if folder_path:
            save_all(self, folder_path)

    def handle_color_change(self, e):
        selected_color = self.color_dropdown.value
        if selected_color == "black_on_white":
            self.canvas_container.bgcolor = ft.Colors.WHITE
            self.generator.color = 'black'
            self.prev_btn.icon_color = ft.Colors.BLACK
            self.next_btn.icon_color = ft.Colors.BLACK
            self.index_label.color = ft.Colors.BLACK
            self.delete_btn.icon_color = ft.Colors.BLACK
            self.save_png_btn.icon_color = ft.Colors.BLACK
        elif selected_color == "white_on_black":
            self.canvas_container.bgcolor = ft.Colors.BLACK
            self.generator.color = 'white'
            self.prev_btn.icon_color = ft.Colors.WHITE
            self.next_btn.icon_color = ft.Colors.WHITE
            self.index_label.color = ft.Colors.WHITE
            self.delete_btn.icon_color = ft.Colors.WHITE
            self.save_png_btn.icon_color = ft.Colors.WHITE
        self.canvas_container.update()

    def sd_changed(self, e):
        self.sd_slider.label = f"SD: {self.sd_slider.value:.2f}"
        self.sd_slider.update()

    def min_dist_changed(self, e):
        self.min_dist_slider.label = f"MD: {self.min_dist_slider.value:.2f}"
        self.min_dist_slider.update()

    def min_dist_toggle(self, e):
        self.min_dist_slider.disabled = not self.min_dist_checkbox.value
        self.min_dist_slider.update()

    def handle_generation(self, e):
        try:
            n_values, s_type, z_type, sd_val, min_dist_val, seed_val = (
                parse_and_validate_inputs(self)
            )

            self.generated_datasets = []
            for num in n_values:
                dots, radii, positions = self.generator.generate_balanced_set(
                    num_elements=num,
                    spatial_type=s_type,
                    size_type=z_type,
                    sd_ratio=sd_val,
                    min_dist_factor=min_dist_val,
                )
                metrics = self.generator.log_ground_truth(
                    num, radii, positions
                )
                self.generated_datasets.append(
                    {
                        "num": num,
                        "radii": radii,
                        "positions": positions,
                        "metrics": metrics,
                    }
                )

            self.current_index = 0
            self.update_view_state()

            if self.generated_datasets:
                m = self.generated_datasets[0]["metrics"]
                seed_info = (
                    f" (Seed: {seed_val})"
                    if seed_val is not None
                    else " (Random)"
                )
                self.info_text.value = f"Success{seed_info}! Generated {len(self.generated_datasets)} items. TSA: {m['TSA']}, CHA: {m['CHA']}"
            else:
                self.info_text.value = "Success! Generated 0 items."
            self.update()

        except ValueError as val_ex:
            self.info_text.value = f"Validation Error: {str(val_ex)}"
            self.update()

        except Exception as ex:
            self.info_text.value = f"Error: {str(ex)}"
            self.update()

    def update_view_state(self):
        shapes = []
        total = len(self.generated_datasets)

        if total == 0:
            self.index_label.value = "No stimuli"
            self.prev_btn.disabled = True
            self.next_btn.disabled = True
            self.delete_btn.disabled = True
            self.save_png_btn.disabled = True
            self.save_btn.disabled = True  
            self.reset_btn.disabled = True
        else:
            item = self.generated_datasets[self.current_index]
            self.index_label.value = f"{self.current_index + 1} of {total} (N={item['num']})"
            
            self.prev_btn.disabled = (self.current_index == 0)
            self.next_btn.disabled = (self.current_index == total - 1)
            self.delete_btn.disabled = False
            self.save_png_btn.disabled = False
            self.save_btn.disabled = False
            self.reset_btn.disabled = False

            canvas_width = 700
            canvas_height = 700
            center_x = canvas_width / 2
            center_y = canvas_height / 2
            
            scale = 1.0  

            for pos, r in zip(item["positions"], item["radii"]):
                x = center_x + (pos[0] * scale)
                y = center_y - (pos[1] * scale)  
                scaled_r = max(2.0, r * scale)   

                shapes.append(
                    cv.Circle(
                        x=x,
                        y=y,
                        radius=scaled_r,
                        paint=ft.Paint(
                            color=ft.Colors.BLACK if self.generator.color == 'black' else ft.Colors.WHITE,
                            style=ft.PaintingStyle.FILL
                        )
                    )
                )

        self.dot_canvas.shapes = shapes
        self.dot_canvas.update()

    def prev_image(self, e):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_view_state()
            self.update()

    def next_image(self, e):
        if self.current_index < len(self.generated_datasets) - 1:
            self.current_index += 1
            self.update_view_state()
            self.update()

    def delete_current(self, e):
        if self.generated_datasets:
            self.generated_datasets.pop(self.current_index)
            if self.current_index >= len(self.generated_datasets) and self.current_index > 0:
                self.current_index -= 1
            self.update_view_state()
            self.info_text.value = "Deleted current stimulus."
            self.update()

    def save_png(self, e):
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder_path = filedialog.askdirectory(title="Select folder to save current stimulus")
        root.destroy()
        
        if folder_path:
            save_current_stimulus_png(self, folder_path)

    async def open_info(self, e):
        await self.app.url_launcher.launch_url("https://yehorh74.github.io/PANDA/") if hasattr(self.app, 'url_launcher') else None

    async def close_app(self, e):
        await self.app.page.window.close()

    def handle_type_change(self, e):
        selected_type = self.radio_group.value

        digit_filter = ft.NumbersOnlyInputFilter()

        self.field_count = ft.TextField(
            label="Number of stimuli (1-100)",
            value="10",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=digit_filter,
        )

        if selected_type == "range":
            self.field_min = ft.TextField(
                label="Min (3-50)",
                value="5",
                width=300,
                keyboard_type=ft.KeyboardType.NUMBER,
                input_filter=digit_filter,
            )
            self.field_max = ft.TextField(
                label="Max (3-50)",
                value="15",
                width=300,
                keyboard_type=ft.KeyboardType.NUMBER,
                input_filter=digit_filter,
            )
            self.num_content = ft.Column(
                controls=[self.field_min, self.field_max, self.field_count],
                spacing=10,
            )

        elif selected_type == "fixed":
            self.field_n = ft.TextField(
                label="N (3-50)",
                value="5",
                width=300,
                keyboard_type=ft.KeyboardType.NUMBER,
                input_filter=digit_filter,
            )
            self.num_content = ft.Column(
                controls=[self.field_n, self.field_count], spacing=10
            )

        elif selected_type == "list":
            list_filter = ft.InputFilter(regex_string=r"[0-9,]")
            self.field_list_nums = ft.TextField(
                label="Enter numbers (3-50, comma-separated)",
                value="5,10,15",
                width=300,
                input_filter=list_filter,
            )
            self.num_content = ft.Column(
                controls=[self.field_list_nums, self.field_count], spacing=10
            )

        self.num_container.content = self.num_content

        if e is not None and self.page is not None:
            self.update()