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
        window (visual.Window): The PsychoPy window in which to display the dot array.
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
    """

    def __init__(
        self,
        window: visual.Window,
        n_anchor: int = 3,
        base_ta: float = 30000.0,
        base_cha: float = 120000.0,
        color: str = "black",
        seed: Optional[int] = None,
    ):
        self.win = window
        self.color = color
        self.results: List[Dict[str, Any]] = []

        self.rng = np.random.default_rng(seed)
        if seed is not None:
            random.seed(seed)

        self.n_anchor = n_anchor
        self.base_ta = base_ta
        self.base_cha = base_cha

        self.mean_r_anchor = np.sqrt((self.base_ta / self.n_anchor) / np.pi)
        self.base_tp = self.n_anchor * (2 * np.pi * self.mean_r_anchor)
        self.base_id = (0.51 * np.sqrt(self.base_cha)) + (2 * self.mean_r_anchor)

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
            sd_area = mean_area * sd_ratio
            areas = np.random.normal(loc=mean_area, scale=sd_area, size=num)
            areas = np.clip(areas, mean_area * 0.1, None)
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
            sd_perim = mean_perim * sd_ratio
            perims = np.random.normal(
                loc=mean_perim, scale=sd_perim, size=num
            )
            perims = np.clip(perims, mean_perim * 0.1, None)
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

    def _resolve_condition_values(self, spatial_type: str, size_type: str) -> Tuple[float, float]:
        """Retrieve target spatial and size baseline values corresponding to specified condition types.

        Args:
            spatial_type (str): the spatial condition type ('CH' for Convex Hull, 'ID' for Inter-Distance)
            size_type (str): the size condition type ('TA' for Total Area, 'TP' for Total Perimeter)

        Returns:
            Tuple[float, float]: A tuple containing the resolved spatial value and size value for the specified condition types.
        """
        s_val = self.base_cha if spatial_type == 'CH' else self.base_id
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
        return max(15.0, current_mean_r * 0.5)

    def generate_balanced_set(
        self,
        num_elements: int,
        spatial_type: str,
        size_type: str,
        sd_ratio: float = 0.0,
        min_dist_factor: Optional[float] = None,
    ) -> Tuple[List[visual.Circle], List[float], List[List[float]]]:
        """Generate a spatially balanced array of dots satisfying target geometric and size constraints.

        Args:
            num_elements (int): the number of dots to generate
            spatial_type (str): the spatial condition type ('CH' for Convex Hull, 'ID' for Inter-Distance)
            size_type (str): the size condition type ('TA' for Total Area, 'TP' for Total Perimeter)
            sd_ratio (float, optional): standard deviation ratio of the dot sizes. Defaults to 0.0.
            min_dist_factor (Optional[float], optional): the minimum distance factor between dots. Defaults to None.

        Raises:
            ValueError: If the number of elements is less than 3 for Convex Hull (CH) spatial type.
            RuntimeError: If unable to fit dots in the window while maintaining parameters after multiple attempts.

        Returns:
            Tuple[List[visual.Circle], List[float], List[List[float]]]: A tuple containing the generated dot objects, their radii, and their positions.
        """
        if num_elements < 3 and spatial_type == 'CH':
            raise ValueError(
                "Numerosity of elements must be at least 3 for Convex Hull (CH) spatial type."
            )

        spatial_val, size_val = self._resolve_condition_values(
            spatial_type, size_type
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
        half_win = min(self.win.size) / 2.0
        safe_margin = half_win - max_r - 10.0

        if spatial_type == 'CH':
            target_spawn_radius = np.sqrt(spatial_val / np.pi)
        else:
            target_spawn_radius = spatial_val * 1.1

        target_spawn_radius = min(target_spawn_radius, safe_margin)

        for attempt in range(400):
            positions = []
            success = True

            for i in range(num_elements):
                found = False
                for _ in range(2000):
                    angle = random.uniform(0, 2 * np.pi)
                    dist = target_spawn_radius * np.sqrt(random.random())
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
                    scale = np.sqrt(spatial_val / curr)
                else:
                    curr = self._compute_inter_distance(positions_np)
                    scale = spatial_val / curr

                final_positions = positions_np * scale
                
                if np.max(np.abs(final_positions)) < safe_margin:
                    dists_matrix = cdist(final_positions, final_positions)
                    radii_sum = radii[:, None] + radii[None, :]
                    np.fill_diagonal(dists_matrix, np.inf)

                    if not np.any(dists_matrix < radii_sum):
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

        density = tsa / cha if cha > 0 else 0.0
        additive_area = np.sum(2 * radii_np)
        mean_occupancy = cha / num_elements if num_elements > 0 else 0.0

        metrics ={
            'N': num_elements,
            'TSA': round(tsa, 4),
            'TP': round(tp, 4),
            'CHA': round(cha, 4),
            'ID': round(id_val, 4),
            'Density': round(density, 6),
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
    ) -> List[visual.Circle]:
        """Generate, render, and display a dot array in PsychoPy, optionally capturing and saving the frame.

        Args:
            num_elements (int): the number of dots to generate
            spatial_type (str): the spatial condition type ('CH' for Convex Hull, 'ID' for Inter-Distance)
            size_type (str): the size condition type ('TA' for Total Area, 'TP' for Total Perimeter)
            output_filepath (Optional[str], optional): the path to save the generated image. Defaults to None.
            sd_ratio (float, optional): standard deviation ratio of the dot sizes. Defaults to 0.0.
            min_dist_factor (Optional[float], optional): the minimum distance factor between dots. Defaults to None.
            save_results (bool, optional): whether to save the generated results. Defaults to True.
            pause_time (float, optional): the time to pause between frames. Defaults to 0.0.

        Returns:
            List[visual.Circle]: the list of generated dot objects
        """
        dots, radii, positions = self.generate_balanced_set(
            num_elements=num_elements,
            spatial_type=spatial_type,
            size_type=size_type,
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