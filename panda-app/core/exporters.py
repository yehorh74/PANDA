import os
import flet as ft
import pandas as pd
from PIL import Image, ImageDraw

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