import os
import random
from typing import List, Optional, Tuple, Dict, Any
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
from scipy.spatial.distance import pdist, cdist
from psychopy import visual, core


class PANDA:
    """PANDA (Python Automating Numerical Dot Algorithm).

    An open algorithm dedicated to the precise generation and controlled
    parameterization of multi-element dot arrays.

    Args:
        window (visual.Window, optional): The PsychoPy window in which to display the dot array.
        n_anchor (int, optional): The number of anchor dots. Defaults to 3.
        base_ta (float, optional): The baseline Total Surface Area. Defaults to 30000.0.
        base_cha (float, optional): The baseline Convex Hull Area. Defaults to 120000.0.
        color (str, optional): The color of the dots. Defaults to "black".
        seed (int, optional): The random seed for reproducibility. Defaults to None.

    Attributes:
        win (visual.Window): The PsychoPy window instance.
        color (str): The color specified for the rendered dots.
        results (list[dict]): List storing generated dot array parameters and metadata.
        rng (np.random.Generator): NumPy random number generator.
        n_anchor (int): Number of anchor dots used for baseline metrics.
        base_ta (float): Baseline Total Surface Area value.
        base_cha (float): Baseline Convex Hull Area value.
        mean_r_anchor (float): Calculated mean radius of anchor dots.
        base_tp (float): Calculated baseline Total Perimeter.
        base_id (float): Calculated baseline Inter-item Distance.
        base_density_num (float): Calculated baseline Density (N / CH).
        base_density_surf (float): Calculated baseline Density (TA / CH).
        base_occupancy (float): Calculated baseline Occupancy (CH / N).
    """

    def __init__(
        self,
        window: Optional[visual.Window] = None,
        n_anchor: int = 3,
        base_ta: float | None = 30000.0,
        base_cha: float | None = 120000.0,
        color: str = "black",
        seed: Optional[int] = None,
        default_size: Tuple[int, int] = (700, 700),
    ):
        self.win = window
        self.default_size = default_size
        self.color = color
        self.results: List[Dict[str, Any]] = []

        self.rng = np.random.default_rng(seed)

        self.n_anchor = n_anchor
        self.base_ta = base_ta if base_ta is not None else 30000.0
        self.base_cha = base_cha if base_cha is not None else 120000.0

        self.mean_r_anchor = np.sqrt((self.base_ta / self.n_anchor) / np.pi)
        self.base_tp = self.n_anchor * (2 * np.pi * self.mean_r_anchor)
        self.base_id = (0.51 * np.sqrt(self.base_cha)) + (2 * self.mean_r_anchor)

        self.base_density_num = self.n_anchor / self.base_cha  
        self.base_density_surf = self.base_ta / self.base_cha
        self.base_occupancy = self.base_cha / self.n_anchor

    def _get_radii(self, num: int, target_tsa: float, sd_ratio: float = 0.0) -> np.ndarray:
        """Calculate individual dot radii matching a target Total Surface Area (TSA) and standard deviation ratio.

        Args:
            num (int): number of dots 
            target_tsa (float): target total surface area for the dot array
            sd_ratio (float, optional): standard deviation ratio of the dot sizes. Defaults to 0.0.

        Returns:
            np.ndarray: array of calculated dot radii
        """
        mean_area = target_tsa / num
        if sd_ratio == 0:
            areas = np.full(num, mean_area)
        else:
            sigma = sd_ratio
            mu = np.log(mean_area) - (sigma ** 2) / 2.0
            areas = np.random.lognormal(mean=mu, sigma=sigma, size=num)
        areas *= target_tsa / np.sum(areas)
        return np.sqrt(areas / np.pi)
    

    def _get_radii_tp(self, num: int, target_tp: float, sd_ratio: float = 0.0) -> np.ndarray:
        """Calculate individual dot radii matching a target Total Perimeter (TP) and standard deviation ratio.

        Args:
            num (int): number of dots
            target_tp (float): target total perimeter for the dot array
            sd_ratio (float, optional): standard deviation ratio of the dot perimeters. Defaults to 0.0.

        Returns:
            np.ndarray: array of calculated dot radii
        """
        mean_perim = target_tp / num
        if sd_ratio == 0:
            perims = np.full(num, mean_perim)
        else:
            sigma = sd_ratio
            mu = np.log(mean_perim) - (sigma**2) / 2
            perims = np.random.lognormal(mean=mu, sigma=sigma, size=num)            
        perims *= target_tp / np.sum(perims)
        return perims / (2 * np.pi)

    def _compute_convex_hull_area(self, positions: np.ndarray) -> float:
        """Calculate the convex hull area (CHA) formed by the current dot positions.

        Args:
            positions (np.ndarray): An array of shape (N, 2) representing the x and y coordinates of the dot centers.

        Returns:
            float: The area of the convex hull enclosing the dot positions. Returns 0.0 if there are fewer than 3 points.
        """
        if len(positions) < 3:
            return 0.0
        return float(ConvexHull(positions).volume)

    def _compute_inter_distance(self, positions: np.ndarray) -> float:
        """Compute the mean pairwise inter-individual distance (ID) between dot centers.

        Args:
            positions (np.ndarray): An array of shape (N, 2) representing the x and y coordinates of the dot centers.

        Returns:
            float: The mean pairwise inter-individual distance between dot centers. Returns 0.0 if there are fewer than 2 points.
        """
        if len(positions) < 2:
            return 0.0
        return float(np.mean(pdist(positions)))

    def _compute_density(self, positions: np.ndarray, radii: np.ndarray, density_type: str = 'numerical') -> float:
        """Compute the spatial density of the dot array.
        
        Args:
            positions (np.ndarray): Array of shape (N, 2) with dot centers.
            radii (np.ndarray): Array of shape (N,) with dot radii.
            density_type (str): 'numerical' (N / CH) or 'surface' (TA / CH).
            
        Returns:
            float: The calculated density value. Returns 0.0 if CH cannot be computed.
        """
        if len(positions) < 3:
            return 0.0
        ch_area = self._compute_convex_hull_area(positions)
        if ch_area == 0:
            return 0.0
        if density_type == 'numerical':
            return float(len(positions) / ch_area)
        elif density_type == 'surface':
            radii_np = np.asarray(radii)
            total_area = np.sum(np.pi * (radii_np ** 2))
            return float(total_area / ch_area)
        else:
            raise ValueError("Unsupported density_type. Use 'numerical' or 'surface'.")

    def _compute_mean_occupancy(self, positions: np.ndarray, num_elements: int) -> float:
        """Compute the average area allocated per element (CH / N).
        
        Args:
            positions (np.ndarray): Array of shape (N, 2) with dot centers.
            num_elements (int): Number of elements in the dot array.
            
        Returns:
            float: The calculated mean occupancy value. Returns 0.0 if CH cannot be computed.
        """
        if num_elements < 3 or len(positions) < 3:
            return 0.0
            
        ch_area = self._compute_convex_hull_area(positions)
        if ch_area == 0:
            return 0.0
            
        return float(ch_area / num_elements)

    def _resolve_condition_values(self, spatial_type: str, size_type: str, density_type: str = 'numerical') -> Tuple[float, float]:
        """Retrieve target spatial and size baseline values corresponding to specified condition types.

        Args:
            spatial_type (str): the spatial condition type ('CH' for Convex Hull, 'ID' for Inter-Distance, 'Density', or 'MO' for Mean Occupancy)
            size_type (str): the size condition type ('TA' for Total Area, 'TP' for Total Perimeter)
            density_type (str): 'numerical' (N / CH) or 'surface' (TA / CH). Defaults to 'numerical'.

        Returns:
            Tuple[float, float]: A tuple containing the resolved spatial value and size value for the specified condition types.
        """
        if spatial_type == 'CH':
            s_val = self.base_cha
        elif spatial_type == 'ID':
            s_val = self.base_id
        elif spatial_type == 'Density':
            s_val = self.base_density_num if density_type == 'numerical' else self.base_density_surf
        elif spatial_type == 'MO':
            s_val = self.base_occupancy
        else:
            raise ValueError(f"Unknown spatial_type: {spatial_type}. Use 'CH', 'ID', 'Density', or 'MO'.")

        z_val = self.base_ta if size_type == 'TA' else self.base_tp
        return s_val, z_val

    def _calculate_dynamic_margin(self, num_elements: int, size_type: str, z_val: float) -> float:
        """Compute a dynamic safety spacing margin between dots based on their average size.

        Args:
            num_elements (int): the number of dots in the array
            size_type (str): the size condition type ('TA' for Total Area, 'TP' for Total Perimeter)
            z_val (float): the target size value

        Returns:
            float: The calculated dynamic margin to be used as a minimum distance factor between dots, ensuring they do not overlap and maintain visual clarity.
        """
        if size_type == 'TA':
            current_mean_r = np.sqrt((z_val / num_elements) / np.pi)
        else:
            current_mean_r = (z_val / num_elements) / (2 * np.pi)
        return max(2.0, current_mean_r * 0.3)

    def _update_bases(self):
        """
        Update the baseline parameters (Total Area, Convex Hull Area, Total Perimeter, Inter-Distance, Density, and Occupancy) based on the current number of anchors and their properties.
        """
        self.mean_r_anchor = np.sqrt((self.base_ta / self.n_anchor) / np.pi)
        self.base_tp = self.n_anchor * (2 * np.pi * self.mean_r_anchor)
        self.base_id = (0.51 * np.sqrt(self.base_cha)) + (2 * self.mean_r_anchor)

        self.base_density_num = self.n_anchor / self.base_cha  
        self.base_density_surf = self.base_ta / self.base_cha
        self.base_occupancy = self.base_cha / self.n_anchor

    def generate_balanced_set(
        self,
        num_elements: int,
        spatial_type: str,
        size_type: str,
        density_type: str = 'numerical',
        sd_ratio: float = 0.0,
        min_dist_factor: Optional[float] = None,
    ) -> Tuple[List[visual.Circle], List[float], List[List[float]]]:
        """Generate a spatially balanced array of dots satisfying target geometric and size constraints.

        Args:
            num_elements (int): the number of dots to generate
            spatial_type (str): the spatial condition type ('CH' for Convex Hull, 'ID' for Inter-Distance, 'Density', or 'MO' for Mean Occupancy)
            size_type (str): the size condition type ('TA' for Total Area, 'TP' for Total Perimeter)
            density_type (str): 'numerical' (N / CH) or 'surface' (TA / CH). Defaults to 'numerical'.
            sd_ratio (float, optional): standard deviation ratio of the dot sizes. Defaults to 0.0.
            min_dist_factor (Optional[float], optional): the minimum distance factor between dots. Defaults to None.

        Raises:
            ValueError: If the number of elements is less than 3 for Convex Hull (CH) spatial type.
            RuntimeError: If unable to fit dots in the window while maintaining parameters after multiple attempts.

        Returns:
            Tuple[List[visual.Circle], List[float], List[List[float]]]: A tuple containing the generated dot objects, their radii, and their positions.
        """
        if num_elements < 3 and spatial_type in ['CH', 'Density', 'MO']:
            raise ValueError(
                "Numerosity of elements must be at least 3 for Convex Hull (CH) spatial type."
            )

        self._update_bases()

        spatial_val, size_val = self._resolve_condition_values(
            spatial_type, size_type, density_type
        )

        if min_dist_factor is None:
            min_dist_factor = self._calculate_dynamic_margin(
                num_elements, size_type, size_val
            )

        if size_type == 'TA':
            radii = self._get_radii(num_elements, size_val, sd_ratio)
        else:
            radii = self._get_radii_tp(num_elements, size_val, sd_ratio)

        max_r = np.max(radii)
        win_size = self.win.size if self.win is not None else self.default_size
        half_win = min(win_size) / 2.0
        safe_margin = half_win - max_r - 10.0

        if spatial_type == 'CH':
            target_spawn_radius = np.sqrt(spatial_val / np.pi)
        elif spatial_type == 'ID':
            target_spawn_radius = spatial_val * 1.1
        elif spatial_type == 'Density':
            if density_type == 'numerical':
                target_ch = num_elements / spatial_val
            else:  
                total_area = np.sum(np.pi * (radii ** 2))
                target_ch = total_area / spatial_val  
            target_spawn_radius = np.sqrt(target_ch / np.pi)
        elif spatial_type == 'MO':
            target_ch = num_elements * spatial_val
            target_spawn_radius = np.sqrt(target_ch / np.pi)
        else:
            target_spawn_radius = safe_margin * 0.5

        target_spawn_radius = min(target_spawn_radius, safe_margin)

        for attempt in range(400):
            positions = []
            success = True

            for i in range(num_elements):
                found = False
                for _ in range(2000):
                    angle = self.rng.uniform(0, 2 * np.pi)
                    dist = target_spawn_radius * np.sqrt(self.rng.random())
                    new_pos = np.array(
                        [np.cos(angle) * dist, np.sin(angle) * dist]
                    )

                    if len(positions) > 0:
                        existing_arr = np.array(positions)
                        dists = np.linalg.norm(existing_arr - new_pos, axis=1)
                        min_allowed = radii[: len(positions)] + radii[i] + min_dist_factor
                        if np.any(dists < min_allowed):
                            continue

                    positions.append(new_pos)
                    found = True
                    break

                if not found:
                    success = False
                    break

            if success:
                positions_np = np.array(positions)

                if spatial_type == 'CH':
                    curr = self._compute_convex_hull_area(positions_np)
                    scale = np.sqrt(spatial_val / curr) if curr > 0 else 1.0
                elif spatial_type == 'ID':
                    curr = self._compute_inter_distance(positions_np)
                    scale = spatial_val / curr if curr > 0 else 1.0
                elif spatial_type == 'Density':
                    curr_density = self._compute_density(positions_np, radii, density_type=density_type)
                    if curr_density > 0:
                        if density_type == 'numerical':
                            target_ch = num_elements / spatial_val
                            curr_ch = num_elements / curr_density
                        else: 
                            total_area = np.sum(np.pi * (radii ** 2))
                            target_ch = total_area / spatial_val
                            curr_ch = total_area / curr_density
                            
                        scale = np.sqrt(target_ch / curr_ch)
                    else:
                        scale = 1.0
                elif spatial_type == 'MO':
                    curr_occupancy = self._compute_mean_occupancy(positions_np, num_elements)
                    if curr_occupancy > 0:
                        target_ch = num_elements * spatial_val
                        curr_ch = num_elements * curr_occupancy
                        scale = np.sqrt(target_ch / curr_ch)
                    else:
                        scale = 1.0

                final_positions = positions_np * scale
                
                if np.max(np.abs(final_positions)) < safe_margin:
                    dists_matrix = cdist(final_positions, final_positions)
                    radii_sum = radii[:, None] + radii[None, :]
                    np.fill_diagonal(dists_matrix, np.inf)

                    if not np.any(dists_matrix < radii_sum):
                        if self.win is not None:
                            dots = [
                                visual.Circle(
                                    self.win,
                                    radius=radii[i],
                                    pos=final_positions[i],
                                    fillColor=self.color,
                                    lineColor=self.color,
                                    edges=128,
                                )
                                for i in range(num_elements)
                            ]
                        else:
                            dots = []
                        return dots, radii.tolist(), final_positions.tolist()

        raise RuntimeError(
            f"Error N={num_elements}: Unable to fit dots in window while maintaining parameters."
        )

    def log_ground_truth(self, num_elements: int, radii: list, positions: list) -> Dict[str, Any]:
        """Compute and log exact geometric ground-truth metrics for the generated dot array.

        Args:
            num_elements (int): the number of dots in the array
            radii (list): a list of radii for each dot
            positions (list): a list of (x, y) coordinates for each dot

        Returns:
            Dict[str, Any]: A dictionary containing the computed ground-truth metrics for the generated dot array, including Total Surface Area (TSA), Total Perimeter (TP), Convex Hull Area (CHA), Inter-Distance (ID), Density, Additive Area (AA), and Mean Occupancy (MO).
        """
        radii_np = np.array(radii)
        positions_np = np.array(positions)

        tsa = np.sum(np.pi * radii_np**2)
        tp = np.sum(2 * np.pi * radii_np)
        cha = self._compute_convex_hull_area(positions_np)
        id_val = self._compute_inter_distance(positions_np)

        density_num = self._compute_density(positions_np, radii, density_type='numerical') if cha > 0 else 0.0
        density_surf = self._compute_density(positions_np, radii, density_type='surface') if cha > 0 else 0.0
        additive_area = np.sum(2 * radii_np)
        mean_occupancy = cha / num_elements if num_elements > 0 else 0.0

        metrics ={
            'N': num_elements,
            'TSA': round(tsa, 4),
            'TP': round(tp, 4),
            'CHA': round(cha, 4),
            'ID': round(id_val, 4),
            'Density (numerical)': round(density_num, 6),
            'Density (surface)': round(density_surf, 6),
            'AA': round(additive_area, 4),
            'MO': round(mean_occupancy, 4),
        }
        self.results.append(metrics)
        return metrics

    def generate_and_save(
        self,
        num_elements: int,
        spatial_type: str,
        size_type: str,
        output_filepath: Optional[str] = None,
        sd_ratio: float = 0.0,
        min_dist_factor: Optional[float] = None,
        save_results: bool = True,
        pause_time: float = 0.0,
        density_type: str = 'numerical',
    ) -> List[visual.Circle]:
        """Generate, render, and display a dot array in PsychoPy, optionally capturing and saving the frame.

        Args:
            num_elements (int): the number of dots to generate
            spatial_type (str): the spatial condition type ('CH' for Convex Hull, 'ID' for Inter-Distance, 'Density', or 'MO' for Mean Occupancy)
            size_type (str): the size condition type ('TA' for Total Area, 'TP' for Total Perimeter)
            output_filepath (Optional[str], optional): the path to save the generated image. Defaults to None.
            sd_ratio (float, optional): standard deviation ratio of the dot sizes. Defaults to 0.0.
            min_dist_factor (Optional[float], optional): the minimum distance factor between dots. Defaults to None.
            save_results (bool, optional): whether to save the generated results. Defaults to True.
            pause_time (float, optional): the time to pause between frames. Defaults to 0.0.
            density_type (str): 'numerical' (N / CH) or 'surface' (TA / CH). Defaults to 'numerical'.

        Returns:
            List[visual.Circle]: the list of generated dot objects
        """
        if self.win is None:
            raise RuntimeError("PsychoPy window is required to execute generate_and_save()!")
        dots, radii, positions = self.generate_balanced_set(
            num_elements=num_elements,
            spatial_type=spatial_type,
            size_type=size_type,
            density_type=density_type,
            sd_ratio=sd_ratio,
            min_dist_factor=min_dist_factor,
        )

        self.log_ground_truth(num_elements, radii, positions)

        for dot in dots:
            dot.draw()

        core.wait(pause_time)  

        self.win.flip()
        self.win.getMovieFrame(buffer='front')
        if save_results and output_filepath:
            self.win.saveMovieFrames(output_filepath)
        return dots

    def get_dataframe(self) -> pd.DataFrame:
        """Return all logged stimulus ground-truth metrics as a pandas DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing all logged ground-truth metrics for the generated dot arrays, including Total Surface Area (TSA), Total Perimeter (TP), Convex Hull Area (CHA), Inter-Distance (ID), Density, Additive Area (AA), and Mean Occupancy (MO).
        """
        return pd.DataFrame(self.results)

    def reset_results(self) -> None:
        """Clear all stored ground-truth metrics from internal memory.
        """
        self.results.clear()

    def save_csv(self, filename: str) -> None:
        """Export all accumulated ground-truth metrics to a CSV file.

        Args:
            filename (str): The path to the CSV file where the results will be saved.
        """
        df = self.get_dataframe()
        df.to_csv(filename, index=False)

    @staticmethod
    def suggest_optimal_bases(
        window_res: tuple | list = (700, 700),
        max_n: int = 20,
        n_anchor: int = 3,
        spatial_type: str = 'CH',
        size_type: str = 'TA',
        density_type: str = 'numerical'
    ) -> dict:
        """
        Experimental calculator: suggests the optimal number of dots for a given window resolution, maximum number of dots, number of anchor dots, spatial condition type, size condition type, and density type.

        Args:
            window_res (tuple | list, optional): The window resolution. Defaults to (700, 700).
            max_n (int, optional): The maximum number of dots. Defaults to 20.
            n_anchor (int, optional): The number of anchor dots. Defaults to 3.
            spatial_type (str, optional): The spatial condition type. Defaults to 'CH'.
            size_type (str, optional): The size condition type. Defaults to 'TA'.
            density_type (str, optional): The density type. Defaults to 'numerical'.

        Returns:
            dict: A dictionary containing the suggested optimal number of dots for each condition type.
        """
        half_win = min(window_res) / 2.0
        safe_radius = half_win - 40.0  
        max_safe_ch = np.pi * (safe_radius ** 2)  

        warning_msg = None

        if spatial_type == 'ID':
            recommended_cha = min(120000.0, max_safe_ch * 0.8)
        elif spatial_type == 'CH':
            recommended_cha = min(120000.0, max_safe_ch * 0.7)
        elif spatial_type in ['Occupancy', 'Density']:
            if spatial_type == 'Density' and density_type == 'surface':
                recommended_cha = min(120000.0, max_safe_ch * 0.7)
            else:
                max_allowed_base_cha = max_safe_ch * (n_anchor / max_n)
                recommended_cha = max_allowed_base_cha * 0.5
                max_sensible_cha = 60000.0 
                if recommended_cha > max_sensible_cha:
                    recommended_cha = max_sensible_cha
                if recommended_cha < 3000.0:
                    recommended_cha = 3000.0
                    warning_msg = "Warning: The recommended base_cha is too small."
        else:
            recommended_cha = 50000.0

        if size_type == 'TA':
            recommended_size = recommended_cha * 0.20
        else: 
            recommended_size = 30000.0 if spatial_type == 'ID' else (np.sqrt(recommended_cha) * 50.0)

        return {
            "base_cha": round(float(recommended_cha), 2),
            "base_ta": round(float(recommended_size), 2),
            "n_anchor": n_anchor,
            "max_safe_window_radius": round(float(safe_radius), 2),
            "warning": warning_msg
        }