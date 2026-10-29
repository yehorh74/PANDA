import numpy as np

def parse_and_validate_inputs(screen):
    selected_type = screen.radio_group.value
    s_type = screen.spatial_dropdown.value
    z_type = screen.size_dropdown.value
    sd_val = float(screen.sd_slider.value)
    min_dist_val = (
        float(screen.min_dist_slider.value)
        if screen.min_dist_checkbox.value
        else None
    )

    seed_str = screen.seed.value.strip() if screen.seed.value else ""
    seed_val = int(seed_str) if seed_str else None
    screen.generator.rng = np.random.default_rng(seed_val)

    if screen.TA_settings.value:
        try:
            base_ta = float(screen.TA_settings.value)
            screen.generator.base_ta = base_ta
            if base_ta <= 0:
                raise ValueError("Total Area must be a positive number!")
        except ValueError:
            raise ValueError("Total Area must be a valid number!")

    if screen.CH_settings.value:
        try:
            base_ch = float(screen.CH_settings.value)
            screen.generator.base_cha = base_ch
            if base_ch <= 0:
                raise ValueError(
                    "Convex Hull Area must be a positive number!"
                )
        except ValueError:
            raise ValueError("Convex Hull Area must be a valid number!")

    if screen.anchor_n.value:
        try:
            anchor_n = int(screen.anchor_n.value)
            screen.generator.n_anchor = anchor_n
            if anchor_n <= 0:
                raise ValueError(
                    "Number of Anchors must be a positive integer!"
                )
        except ValueError:
            raise ValueError("Number of Anchors must be a valid integer!")

    count_str = (
        screen.field_count.value.strip() if screen.field_count.value else ""
    )
    if not count_str or not count_str.isdigit():
        raise ValueError("Number of stimuli must be a valid number!")

    count = int(count_str)
    if not (1 <= count <= 100):
        raise ValueError("Number of stimuli must be between 1 and 100!")

    n_values = []
    if selected_type == "range":
        min_str = (
            screen.field_min.value.strip() if screen.field_min.value else ""
        )
        max_str = (
            screen.field_max.value.strip() if screen.field_max.value else ""
        )
        if not min_str or not max_str:
            raise ValueError("Min and Max fields cannot be empty!")

        min_v, max_v = int(min_str), int(max_str)
        if min_v < 3:
            raise ValueError("Min value cannot be less than 3!")
        if max_v > 50:
            raise ValueError("Max value cannot be greater than 50!")
        if min_v > max_v:
            raise ValueError("Min value cannot be greater than Max value!")

        for num in range(min_v, max_v + 1):
            for _ in range(count):
                n_values.append(num)

    elif selected_type == "fixed":
        n_str = screen.field_n.value.strip() if screen.field_n.value else ""
        if not n_str:
            raise ValueError("Field N cannot be empty!")
        n = int(n_str)
        if not (3 <= n <= 50):
            raise ValueError("Value N must be between 3 and 50!")
        n_values = [n] * count

    elif selected_type == "list":
        raw_val = (
            screen.field_list_nums.value.strip()
            if screen.field_list_nums.value
            else ""
        )
        if not raw_val:
            raise ValueError("List of numbers cannot be empty!")
        parts = [x.strip() for x in raw_val.split(",") if x.strip()]
        for item in parts:
            if not item.isdigit():
                raise ValueError(f"Invalid item '{item}' in list!")
            val = int(item)
            if not (3 <= val <= 50):
                raise ValueError(
                    f"Number {val} in list must be between 3 and 50!"
                )
            for _ in range(count):
                n_values.append(val)

    return n_values, s_type, z_type, sd_val, min_dist_val, seed_val