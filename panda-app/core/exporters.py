from PIL import Image, ImageDraw

def save_current_stimulus_png(screen):
    try:
        if not screen.generated_datasets:
            return None
        item = screen.generated_datasets[screen.current_index]

        img_size = 700
        image = Image.new("RGB", (img_size, img_size), "white")
        draw = ImageDraw.Draw(image)

        center_x = img_size / 2
        center_y = img_size / 2
        scale = 1.0

        for pos, r in zip(item["positions"], item["radii"]):
            x = center_x + (pos[0] * scale)
            y = center_y - (pos[1] * scale)
            scaled_r = max(2.0, r * scale)
            draw.ellipse(
                [x - scaled_r, y - scaled_r, x + scaled_r, y + scaled_r],
                fill="black",
                outline="black",
            )

        filename = f"stimulus_{screen.current_index + 1}_N{item['num']}.png"
        image.save(filename)
        return filename
    except Exception as ex:
        raise RuntimeError(f"Error saving PNG: {str(ex)}")