import flet as ft
import flet.canvas as cv
import tkinter as tk
from tkinter import filedialog

from panda.generator import PANDA  

from core.validators import parse_and_validate_inputs
from core.exporters import save_current_stimulus_png, save_all, reset_all, handle_load_config, handle_save_config

class GeneratorScreen(ft.View):
    def __init__(self, app):
        super().__init__(route="/generator")
        self.app = app
        self.generator = PANDA(window=None)
        
        self.generated_datasets = []
        self.current_index = 0

        self.setup_ui()

    def setup_ui(self):
        self.save_menu_btn = ft.MenuItemButton(
            content=ft.Text("Save All   Ctrl+S"),
            leading=ft.Icon(ft.Icons.SAVE),
            disabled=True,
            on_click=self.handle_save_click
        )
        self.reset_menu_btn = ft.MenuItemButton(
            content=ft.Text("Reset   Ctrl+R"),
            leading=ft.Icon(ft.Icons.RESTORE),
            disabled=True,
            on_click=lambda e: reset_all(self, e)
        )
        self.save_current_btn = ft.MenuItemButton(
            content=ft.Text("Save Current PNG   Ctrl+D"),
            leading=ft.Icon(ft.Icons.DOWNLOAD),
            disabled=True,
            on_click=self.save_png
        )
        self.delete_current_btn = ft.MenuItemButton(
            content=ft.Text("Delete Current   Del"),
            leading=ft.Icon(ft.Icons.DELETE),
            disabled=True,
            on_click=self.delete_current
        )
        self.theme_menu_btn = ft.MenuItemButton(
            content=ft.Text("Theme: System   Ctrl+T"),
            leading=ft.Icon(ft.Icons.BRIGHTNESS_AUTO),
            on_click=self.toggle_theme
        )
        self.app_menu = ft.MenuBar(
            expand=False,
            style=ft.MenuStyle(
                bgcolor=ft.Colors.TRANSPARENT,  
                elevation=0,
            ),
            controls=[
                ft.SubmenuButton(
                    content=ft.Text("File"),
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text("Save Config   Ctrl+Shift+S"),
                            leading=ft.Icon(ft.Icons.SAVE),
                            on_click=lambda e: handle_save_config(self, e)
                        ),
                        ft.MenuItemButton(
                            content=ft.Text("Load Config   Ctrl+O"),
                            leading=ft.Icon(ft.Icons.IMPORT_EXPORT),
                            on_click=lambda e: handle_load_config(self, e)
                        ),
                        ft.MenuItemButton(
                            content=ft.Text("Quit   Ctrl+Q"),
                            leading=ft.Icon(ft.Icons.CLOSE),
                            on_click=self.close_app
                        ),
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text("Generator"),
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text("Generate   Ctrl+G"),
                            leading=ft.Icon(ft.Icons.REFRESH),
                            on_click=self.handle_generation
                        ),
                        self.save_current_btn,
                        self.delete_current_btn,
                        self.save_menu_btn,
                        self.reset_menu_btn,
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text("Settings"),
                    controls=[
                        self.theme_menu_btn
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text("Help"),
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text("Documentation   F1"),
                            leading=ft.Icon(ft.Icons.HELP_OUTLINE),
                            on_click=self.open_info
                        ),
                        ft.MenuItemButton(
                            content=ft.Text("How to Use?   F2"),
                            leading=ft.Icon(ft.Icons.QUESTION_MARK),
                            on_click=self.open_info_dialog
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
            actions=[
                ft.Container(
                    content=ft.Text(value="MIT License, Copyright (c) 2026 Yehor Horin, Uniwersytet Warszawski", size=14, italic=True),
                    padding=ft.Padding.only(right=15)  
                ),
                ft.Container(
                    content=ft.Text(value=self.app.version, size=14, italic=True),
                    padding=ft.Padding.only(right=15)  
                )
            ]
        )

        num_elements_section = ft.Column([
            ft.Row([
                ft.Text("Number of elements", size=18, weight=ft.FontWeight.BOLD),
                ft.Icon(
                    icon=ft.Icons.HELP_OUTLINE,
                    size=16,
                    color=ft.Colors.GREY_500,
                    tooltip=(
                        "Defines how the element count is determined:\n"
                        "• Range: Randomly varies within a specified min-max range.\n"
                        "• Fixed: Uses a constant number of elements.\n"
                        "• List: Cycles through a predefined sequence of counts."
                    )
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300),
        ], spacing=5)
        
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
            value="CH",
            options=[
                ft.dropdown.Option("CH", "Convex Hull (CH)"),
                ft.dropdown.Option("ID", "Inter-Distance (ID)"),
            ],
            width=300
        )

        spatial_section = ft.Column([
            ft.Row([
                ft.Text("Spatial Type", size=14, weight=ft.FontWeight.W_500),
                ft.Icon(
                    icon=ft.Icons.HELP_OUTLINE,
                    size=16,
                    color=ft.Colors.GREY_500,
                    tooltip="The spatial condition type ('CH' for Convex Hull, 'ID' for Inter-Distance)."
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300),
            self.spatial_dropdown
        ], spacing=5)


        self.size_dropdown = ft.Dropdown(
            value="TA",
            options=[
                ft.dropdown.Option("TA", "Total Area (TA)"),
                ft.dropdown.Option("TP", "Total Perimeter (TP)"),
            ],
            width=300
        )

        size_section = ft.Column([
            ft.Row([
                ft.Text("Size Type", size=14, weight=ft.FontWeight.W_500),
                ft.Icon(
                    icon=ft.Icons.HELP_OUTLINE,
                    size=16,
                    color=ft.Colors.GREY_500,
                    tooltip="The size condition type ('TA' for Total Area, 'TP' for Total Perimeter)."
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300),
            self.size_dropdown
        ], spacing=5)

        self.color_dropdown = ft.Dropdown(
            value="black_on_white",
            options=[
                ft.dropdown.Option("black_on_white", "Black on White"),
                ft.dropdown.Option("white_on_black", "White on Black"),
            ],
            width=300,
            on_select=self.handle_color_change
        )

        color_section = ft.Column([
            ft.Row([
                ft.Text("Color scheme", size=14, weight=ft.FontWeight.W_500),
                ft.Icon(
                    icon=ft.Icons.HELP_OUTLINE,
                    size=16,
                    color=ft.Colors.GREY_500,
                    tooltip="Determines the color contrast scheme of the stimuli.\n• Black on White – black elements on a white background\n• White on Black – white elements on a black background"
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300),
            self.color_dropdown
        ], spacing=5)

        self.sd_text = ft.Text("Size variability", size=14, weight=ft.FontWeight.W_500)

        sd_section = ft.Column([
            ft.Row([
                self.sd_text,
                ft.Icon(
                    icon=ft.Icons.HELP_OUTLINE,
                    size=16,
                    color=ft.Colors.GREY_500,
                    tooltip="Standard deviation ratio of the dot sizes."
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300),
        ], spacing=5)

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
            label_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_500),
            value=False,
            label_position=ft.LabelPosition.LEFT,
            on_change=self.min_dist_toggle,
        )

        min_dist_section = ft.Column([
            ft.Row([
                self.min_dist_checkbox,
                ft.Icon(
                    icon=ft.Icons.HELP_OUTLINE,
                    size=16,
                    color=ft.Colors.GREY_500,
                    tooltip="The minimum distance factor between dots."
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300)
        ], spacing=5)

        self.min_dist_slider = ft.Slider(
            min=0.5,
            max=3.0,
            divisions=25,
            value=1.0,
            label="MD: 1.00",
            disabled=True,  
            on_change=self.min_dist_changed
        )

        self.TA_settings = ft.TextField(value="30000.0", width=300, keyboard_type=ft.KeyboardType.NUMBER, input_filter=ft.InputFilter(regex_string=r"[0-9.]"))

        ta_section = ft.Column([
            ft.Row([
                ft.Text("Total Area", size=14, weight=ft.FontWeight.W_500),
                ft.Icon(
                    icon=ft.Icons.HELP_OUTLINE,
                    size=16,
                    color=ft.Colors.GREY_500,
                    tooltip="The baseline Total Surface Area."
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300),
            self.TA_settings
        ], spacing=5)

        self.CH_settings = ft.TextField(value="120000.0", width=300, keyboard_type=ft.KeyboardType.NUMBER, input_filter=ft.InputFilter(regex_string=r"[0-9.]"))

        ch_section = ft.Column([
            ft.Row([
                ft.Text("Convex Hull", size=14, weight=ft.FontWeight.W_500),
                ft.Icon(
                    icon=ft.Icons.HELP_OUTLINE,
                    size=16,
                    color=ft.Colors.GREY_500,
                    tooltip="The baseline Convex Hull Area."
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300),
            self.CH_settings
        ], spacing=5)
        
        self.anchor_n = ft.TextField(value="3", width=300, keyboard_type=ft.KeyboardType.NUMBER, input_filter=ft.NumbersOnlyInputFilter())

        anchors_section = ft.Column([
            ft.Row([
                ft.Text("Number of Anchors", size=14, weight=ft.FontWeight.W_500),
                ft.Icon(
                    icon=ft.Icons.HELP_OUTLINE,
                    size=16,
                    color=ft.Colors.GREY_500,
                    tooltip="The number of anchor dots."
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300),
            self.anchor_n
        ], spacing=5)
        
        self.seed = ft.TextField(label="e.g. 1234", value="", width=300, keyboard_type=ft.KeyboardType.NUMBER, input_filter=ft.NumbersOnlyInputFilter())

        seed_section = ft.Column([
            ft.Row([
                ft.Text("Random Seed (optional)", size=14, weight=ft.FontWeight.W_500),
                ft.Icon(
                    icon=ft.Icons.HELP_OUTLINE,
                    size=16,
                    color=ft.Colors.GREY_500,
                    tooltip="The random seed for reproducibility."
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=300),
            self.seed
        ], spacing=5)
        
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
                        num_elements_section,
                        self.radio_group,
                        self.num_container,
                        ft.Divider(),
                        ft.Text("Parameters", size=18, weight=ft.FontWeight.BOLD),
                        spatial_section,
                        size_section,
                        color_section,
                        sd_section,
                        self.sd_slider,
                        min_dist_section,
                        self.min_dist_slider,
                        ft.Divider(),
                        ft.Text("Advanced settings", size=18, weight=ft.FontWeight.BOLD),
                        ta_section,
                        ch_section,
                        anchors_section,
                        seed_section,
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

    def open_info_dialog(self, e):
        docs_markdown = """
### 📖 How to Use

1. **Configure Parameters**
   - Set your desired psychophysical settings in the sidebar: **Spatial Type** (Convex Hull vs. Inter-Distance), **Size Type** (Total Area vs. Total Perimeter), **Number of Elements** (Fixed, Range, or List), and **Color Scheme**.
   - Hover over any **`?` help icon** next to parameters for detailed algorithmic definitions.

2. **Generate Stimuli**
   - Click the **Generate** button in the menu or press **`Ctrl + G`** to run the algorithm and create your stimulus set.

3. **Preview & Manage Results**
   - Use the navigation buttons or shortcuts (**`Ctrl + ArrowLeft` / `Ctrl + ArrowRight`**) to browse through generated stimuli.
   - Instantly save a single stimulus and its ground truth using **`Ctrl + D`**, or remove unwanted items using the **`Delete`** key.

4. **Export & Save**
   - Click **Save All** (**`Ctrl + S`**) to export the full set of images along with the complete `ground_truth.csv` file.
   - Use **`Ctrl + Shift + S`** to save your current generator configuration to a JSON file for future replications.

### 💡 Tips & Algorithmic Notes

* **Spatial Control (CH vs. ID):** 
  * *Convex Hull (CH)* regulates spatial dispersion by constraining the total bounding area of the elements. 
  * *Inter-Distance (ID)* focuses on nearest-neighbor spacing, ideal when controlling local visual crowding.
* **Size Metric Balance (TA vs. TP):** 
  * Choose *Total Area (TA)* or *Total Perimeter (TP)* depending on whether cumulative surface or contour length is the critical variable in your psychophysical design.
* **Automatic Ground Truth Derivation (ID & TP):** 
  * Even when you choose primary constraints (such as TA or CH), the PANDA algorithm **automatically computes and exports secondary metrics** (Inter-Distance and Total Perimeter) for every generated stimulus, ensuring you have complete data available in the `ground_truth.csv` for post-hoc analysis.
* **Anchors (Kotwice):** 
  * Use anchor settings to fix specific reference elements in precise coordinates across trials, allowing you to maintain spatial orientation or alignment while other elements vary randomly.
* **Minimum Distance Enforcement:** 
  * The algorithm respects strict separation boundaries; configuring the minimum distance prevents element overlap and controls local density extremes.
* **Deconfounding Variables:** 
  * Utilizing *Range* or *List* modes for element counts helps decorrelate numerosity from continuous visual properties (like total area) across experimental trials.
* **Workflow Speed:** 
  * Combine **`Ctrl + G`** (Generate) and **`Ctrl + S`** (Save All) to rapidly prototype and batch-export stimulus sets without touching the mouse.
        """

        page_ref = getattr(self, "app", None) and getattr(self.app, "page", None)
        if not page_ref:
            page_ref = getattr(self, "page", None)

        if not page_ref:
            print("-> BŁĄD: Nie znaleziono referencji do page!")
            return

        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.HELP_OUTLINE, color=ft.Colors.BLUE),
                ft.Text("How to Use PANDA?", weight=ft.FontWeight.BOLD)
            ]),
            content=ft.Container(
                content=ft.ListView(
                    controls=[ft.Markdown(docs_markdown, selectable=True)],
                    expand=True,
                ),
                width=680,
                height=520,
            ),
            actions=[
                ft.TextButton("Close", on_click=lambda event: page_ref.pop_dialog())
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page_ref.show_dialog(dialog)

    async def handle_keyboard_shortcuts(self, e: ft.KeyboardEvent):
        is_ctrl = e.ctrl or e.meta
        is_shift = e.shift
        key = e.key.lower()

        if is_ctrl and is_shift and key == "s":
            handle_load_config(self, None)  

        elif is_ctrl and not is_shift and key == "s":
            if not self.save_menu_btn.disabled:
                self.handle_save_click(None)

        elif is_ctrl and key == "o":
            handle_load_config(self, None)

        elif is_ctrl and key == "q":
            await self.close_app(None)

        elif is_ctrl and key == "g":
            self.handle_generation(None)

        elif is_ctrl and key == "r":
            if not self.reset_menu_btn.disabled:
                reset_all(self, None)

        elif is_ctrl and key == "t":
            await self.toggle_theme(None)

        elif e.key == "F1":
            await self.open_info(None)

        elif e.key == "F2":
            self.open_info_dialog(None)

        elif is_ctrl and key == "d":
            if hasattr(self, "save_png_btn") and not self.save_png_btn.disabled:
                self.save_png(None)

        elif e.key == "Delete" or (is_ctrl and (key == "backspace" or key == "back")):
            if hasattr(self, "delete_btn") and not self.delete_btn.disabled:
                self.delete_current(None)

        elif is_ctrl and e.key == "ArrowLeft":
            if hasattr(self, "prev_btn") and not self.prev_btn.disabled:
                self.prev_image(None)

        elif is_ctrl and e.key == "ArrowRight":
            if hasattr(self, "next_btn") and not self.next_btn.disabled:
                self.next_image(None)

    def apply_initial_theme_ui(self, theme_mode: str):
        self._theme_cycle_state = theme_mode
        if theme_mode == "light":
            self.theme_menu_btn.content.value = "Theme: Light    Ctrl+T"
            self.theme_menu_btn.leading = ft.Icon(ft.Icons.LIGHT_MODE)
        elif theme_mode == "dark":
            self.theme_menu_btn.content.value = "Theme: Dark     Ctrl+T"
            self.theme_menu_btn.leading = ft.Icon(ft.Icons.DARK_MODE)
        else:
            self.theme_menu_btn.content.value = "Theme: System   Ctrl+T"
            self.theme_menu_btn.leading = ft.Icon(ft.Icons.BRIGHTNESS_AUTO)
        self.update()

    async def toggle_theme(self, e):
        prefs = ft.SharedPreferences()
        current_mode = getattr(self, "_theme_cycle_state", "system")

        if current_mode == "system":
            next_mode = "light"
            self.app.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_menu_btn.content.value = "Theme: Light    Ctrl+T"
            self.theme_menu_btn.leading = ft.Icon(ft.Icons.LIGHT_MODE)
        elif current_mode == "light":
            next_mode = "dark"
            self.app.page.theme_mode = ft.ThemeMode.DARK
            self.theme_menu_btn.content.value = "Theme: Dark     Ctrl+T"
            self.theme_menu_btn.leading = ft.Icon(ft.Icons.DARK_MODE)
        else:
            next_mode = "system"
            self.app.page.theme_mode = ft.ThemeMode.SYSTEM
            self.theme_menu_btn.content.value = "Theme: System   Ctrl+T"
            self.theme_menu_btn.leading = ft.Icon(ft.Icons.BRIGHTNESS_AUTO)

        self._theme_cycle_state = next_mode

        await prefs.set("theme_mode", next_mode)

        self.app.page.update()
        self.update()

    def handle_save_click(self, e):
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        folder_path = filedialog.askdirectory(title="Select destination folder for export all stimulus")

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
            self.save_menu_btn.disabled = True
            self.reset_menu_btn.disabled = True
            self.save_current_btn.disabled = True
            self.delete_current_btn.disabled = True
        else:
            item = self.generated_datasets[self.current_index]
            self.index_label.value = f"{self.current_index + 1} of {total} (N={item['num']})"
            
            self.prev_btn.disabled = (self.current_index == 0)
            self.next_btn.disabled = (self.current_index == total - 1)
            self.delete_btn.disabled = False
            self.save_png_btn.disabled = False
            self.save_btn.disabled = False
            self.reset_btn.disabled = False
            self.save_menu_btn.disabled = False
            self.reset_menu_btn.disabled = False
            self.save_current_btn.disabled = False
            self.delete_current_btn.disabled = False

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