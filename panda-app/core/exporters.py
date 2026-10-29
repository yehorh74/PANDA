import os
import json
import flet as ft
import pandas as pd
from PIL import Image, ImageDraw

def handle_save_config(screen, e):
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    file_path = filedialog.asksaveasfilename(
        title="Save generator configuration",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    root.destroy()

    if file_path:
        try:
            config = {
                "mode": screen.radio_group.value,
                "spatial_type": screen.spatial_dropdown.value,
                "size_type": screen.size_dropdown.value,
                "color_scheme": screen.color_dropdown.value,
                "sd_ratio": screen.sd_slider.value,
                "min_dist_enabled": screen.min_dist_checkbox.value,
                "min_dist_value": screen.min_dist_slider.value,
                "total_area": screen.TA_settings.value,
                "convex_hull_area": screen.CH_settings.value,
                "anchor_n": screen.anchor_n.value,
                "seed": screen.seed.value,
                "theme_mode": getattr(screen, "_theme_cycle_state", "system"),
            }

            mode = screen.radio_group.value
            if mode == "range":
                config["field_min"] = getattr(screen, "field_min", ft.TextField()).value
                config["field_max"] = getattr(screen, "field_max", ft.TextField()).value
                config["field_count"] = getattr(screen, "field_count", ft.TextField()).value
            elif mode == "fixed":
                config["field_n"] = getattr(screen, "field_n", ft.TextField()).value
                config["field_count"] = getattr(screen, "field_count", ft.TextField()).value
            elif mode == "list":
                config["field_list_nums"] = getattr(screen, "field_list_nums", ft.TextField()).value
                config["field_count"] = getattr(screen, "field_count", ft.TextField()).value

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)

            screen.info_text.value = f"Configuration saved successfully!"
            screen.update()
        except Exception as ex:
            screen.info_text.value = f"Config Save Error: {str(ex)}"
            screen.update()

def handle_load_config(screen, e):
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    file_path = filedialog.askopenfilename(
        title="Load generator configuration",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    root.destroy()

    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            if "mode" in config:
                screen.radio_group.value = config["mode"]
                screen.handle_type_change(None)

            if "spatial_type" in config:
                screen.spatial_dropdown.value = config["spatial_type"]
            if "size_type" in config:
                screen.size_dropdown.value = config["size_type"]
            if "color_scheme" in config:
                screen.color_dropdown.value = config["color_scheme"]
                screen.handle_color_change(None)

            if "sd_ratio" in config:
                screen.sd_slider.value = config["sd_ratio"]
                screen.sd_slider.label = f"SD: {screen.sd_slider.value:.2f}"

            if "min_dist_enabled" in config:
                screen.min_dist_checkbox.value = config["min_dist_enabled"]
                screen.min_dist_slider.disabled = not screen.min_dist_checkbox.value

            if "min_dist_value" in config:
                screen.min_dist_slider.value = config["min_dist_value"]
                screen.min_dist_slider.label = f"MD: {screen.min_dist_slider.value:.2f}"

            if "total_area" in config:
                screen.TA_settings.value = config["total_area"]
            if "convex_hull_area" in config:
                screen.CH_settings.value = config["convex_hull_area"]
            if "anchor_n" in config:
                screen.anchor_n.value = config["anchor_n"]
            if "seed" in config:
                screen.seed.value = config["seed"]

            mode = screen.radio_group.value
            if mode == "range":
                if "field_min" in config and hasattr(screen, "field_min"):
                    screen.field_min.value = config["field_min"]
                if "field_max" in config and hasattr(screen, "field_max"):
                    screen.field_max.value = config["field_max"]
                if "field_count" in config and hasattr(screen, "field_count"):
                    screen.field_count.value = config["field_count"]
            elif mode == "fixed":
                if "field_n" in config and hasattr(screen, "field_n"):
                    screen.field_n.value = config["field_n"]
                if "field_count" in config and hasattr(screen, "field_count"):
                    screen.field_count.value = config["field_count"]
            elif mode == "list":
                if "field_list_nums" in config and hasattr(screen, "field_list_nums"):
                    screen.field_list_nums.value = config["field_list_nums"]
                if "field_count" in config and hasattr(screen, "field_count"):
                    screen.field_count.value = config["field_count"]

            if "theme_mode" in config:
                screen._theme_cycle_state = config["theme_mode"]
                mode = screen._theme_cycle_state
                if mode == "light":
                    screen.page.theme_mode = ft.ThemeMode.LIGHT
                    screen.theme_menu_btn.content.value = "Theme: Light"
                    screen.theme_menu_btn.leading = ft.Icon(ft.Icons.LIGHT_MODE)
                elif mode == "dark":
                    screen.page.theme_mode = ft.ThemeMode.DARK
                    screen.theme_menu_btn.content.value = "Theme: Dark"
                    screen.theme_menu_btn.leading = ft.Icon(ft.Icons.DARK_MODE)
                else:
                    screen.page.theme_mode = ft.ThemeMode.SYSTEM
                    screen.theme_menu_btn.content.value = "Theme: System"
                    screen.theme_menu_btn.leading = ft.Icon(ft.Icons.BRIGHTNESS_AUTO)

            screen.update()
            screen.info_text.value = f"Configuration loaded successfully from {os.path.basename(file_path)}"
            screen.update()

        except Exception as ex:
            screen.info_text.value = f"Config Load Error: {str(ex)}"
            screen.update()

def save_current_stimulus_png(screen, folder_path: str):
    if not screen.generated_datasets:
        return

    try:
        img_size = 700
        center_x = img_size / 2
        center_y = img_size / 2

        bg_color = "white" if screen.generator.color == 'black' else "black"
        dot_color = "black" if screen.generator.color == 'black' else "white"

        spatial_type = screen.spatial_dropdown.value
        size_type = screen.size_dropdown.value

        idx = screen.current_index
        item = screen.generated_datasets[idx]

        image = Image.new("RGB", (img_size, img_size), bg_color)
        draw = ImageDraw.Draw(image)

        for pos, r in zip(item["positions"], item["radii"]):
            x = center_x + pos[0]
            y = center_y - pos[1]
            scaled_r = max(2.0, r)
            draw.ellipse(
                [x - scaled_r, y - scaled_r, x + scaled_r, y + scaled_r], 
                fill=dot_color, 
                outline=dot_color
            )

        num_elem = item['num']
        base_filename = f"stimulus_{idx + 1}_N{num_elem}_{spatial_type}_{size_type}"
        
        png_path = os.path.join(folder_path, f"{base_filename}.png")
        image.save(png_path)

        metrics = item["metrics"]
        row_data = {
            "stimulus_id": idx + 1,
            "num_elements": num_elem,
            "spatial_type": spatial_type,
            "size_type": size_type,
            **metrics
        }
        
        df = pd.DataFrame([row_data])
        csv_path = os.path.join(folder_path, f"{base_filename}_ground_truth.csv")
        df.to_csv(csv_path, index=False)

        screen.info_text.value = f"Successfully saved stimulus and CSV to {folder_path}!"
        screen.update()

    except Exception as ex:
        screen.info_text.value = f"Single Export Error: {str(ex)}"
        screen.update()

def save_all(screen, folder_path: str):
    try:
        exported_rows = []
        img_size = 700
        center_x = img_size / 2
        center_y = img_size / 2

        bg_color = "white" if screen.generator.color == 'black' else "black"
        dot_color = "black" if screen.generator.color == 'black' else "white"

        spatial_type = screen.spatial_dropdown.value
        size_type = screen.size_dropdown.value

        for idx, item in enumerate(screen.generated_datasets):
            image = Image.new("RGB", (img_size, img_size), bg_color)
            draw = ImageDraw.Draw(image)

            for pos, r in zip(item["positions"], item["radii"]):
                x = center_x + pos[0]
                y = center_y - pos[1]
                scaled_r = max(2.0, r)
                draw.ellipse(
                    [x - scaled_r, y - scaled_r, x + scaled_r, y + scaled_r], 
                    fill=dot_color, 
                    outline=dot_color
                )

            num_elem = item['num']
            filename = f"stimulus_{idx + 1}_N{num_elem}_{spatial_type}_{size_type}.png"
            file_path = os.path.join(folder_path, filename)
            image.save(file_path)

            metrics = item["metrics"]
            row_data = {
                "stimulus_id": idx + 1,
                "num_elements": num_elem,
                "spatial_type": spatial_type,
                "size_type": size_type,
                **metrics
            }
            exported_rows.append(row_data)

        df = pd.DataFrame(exported_rows)
        csv_path = os.path.join(folder_path, "all_stimuli_ground_truth.csv")
        df.to_csv(csv_path, index=False)

        screen.info_text.value = f"Successfully exported {len(screen.generated_datasets)} items to {folder_path}!"
        screen.update()

    except Exception as ex:
        screen.info_text.value = f"Export Error: {str(ex)}"
        screen.update()

def reset_all(screen, e):
    screen.generated_datasets = []
    screen.current_index = 0
    
    screen.radio_group.value = "range"
    screen.handle_type_change(None)
    
    screen.spatial_dropdown.value = "CH"
    screen.size_dropdown.value = "TA"
    screen.color_dropdown.value = "black_on_white"
    
    screen.canvas_container.bgcolor = ft.Colors.WHITE
    screen.generator.color = 'black'
    screen.prev_btn.icon_color = ft.Colors.BLACK
    screen.next_btn.icon_color = ft.Colors.BLACK
    screen.index_label.color = ft.Colors.BLACK
    screen.delete_btn.icon_color = ft.Colors.BLACK
    screen.save_png_btn.icon_color = ft.Colors.BLACK

    screen.sd_slider.value = 0.20
    screen.sd_slider.label = "SD: 0.20"
    screen.min_dist_checkbox.value = False
    screen.min_dist_slider.disabled = True
    screen.min_dist_slider.value = 1.0
    screen.min_dist_slider.label = "MD: 1.00"

    screen.TA_settings.value = "30000.0"
    screen.CH_settings.value = "120000.0"
    screen.anchor_n.value = "3"
    screen.seed.value = ""

    screen.info_text.value = "Generator has been reset to defaults."
    
    screen.update_view_state()
    screen.update()