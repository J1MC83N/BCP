import numpy as np

from func_utils import extract_k


def compute_stats_from_V(vertices, faces, uvs):
    k_per_triangle, triangles_areas, sigma_1, sigma_2 = extract_k(vertices, faces, uvs)
    sigma_1_squared = sigma_1**2
    sigma_2_squared = sigma_2**2
    e_sd_per_triangle = 0.5 * (sigma_1_squared + sigma_2_squared + 1 / sigma_1_squared + 1 / sigma_2_squared)
    e_sd_order = np.argsort(e_sd_per_triangle, axis=0)
    percent95 = int(np.round(0.95 * sigma_1.shape[0]))
    percent99 = int(np.round(0.99 * sigma_1.shape[0]))
    percent99_9 = int(np.round(0.999 * sigma_1.shape[0]))
    percent99_99 = int(np.round(0.9999 * sigma_1.shape[0]))

    e_sd = np.sum(triangles_areas * e_sd_per_triangle) / np.sum(triangles_areas)
    percent_95_e_sd = np.sum(
        triangles_areas[e_sd_order[:percent95]] * e_sd_per_triangle[e_sd_order[:percent95]]
    ) / np.sum(triangles_areas[e_sd_order[:percent95]])
    percent_99_9_e_sd = np.sum(
        triangles_areas[e_sd_order[:percent99_9]] * e_sd_per_triangle[e_sd_order[:percent99_9]]
    ) / np.sum(triangles_areas[e_sd_order[:percent99_9]])
    percent_99_99_e_sd = np.sum(
        triangles_areas[e_sd_order[:percent99_99]] * e_sd_per_triangle[e_sd_order[:percent99_99]]
    ) / np.sum(triangles_areas[e_sd_order[:percent99_99]])
    percent_99_e_sd = np.sum(
        triangles_areas[e_sd_order[:percent99]] * e_sd_per_triangle[e_sd_order[:percent99]]
    ) / np.sum(triangles_areas[e_sd_order[:percent99]])
    percent_5_e_sd = np.sum(
        triangles_areas[e_sd_order[percent95:]] * e_sd_per_triangle[e_sd_order[percent95:]]
    ) / np.sum(triangles_areas[e_sd_order[percent95:]])
    percent_1_e_sd = np.sum(
        triangles_areas[e_sd_order[percent99:]] * e_sd_per_triangle[e_sd_order[percent99:]]
    ) / np.sum(triangles_areas[e_sd_order[percent99:]])
    max_e_sd = np.max(e_sd_per_triangle)
    k_energy = np.sum(triangles_areas * k_per_triangle) / np.sum(triangles_areas)

    flips = (sigma_2 <= 0).sum()
    return (
        e_sd,
        percent_99_99_e_sd,
        percent_99_9_e_sd,
        percent_99_e_sd,
        percent_95_e_sd,
        percent_5_e_sd,
        percent_1_e_sd,
        max_e_sd,
        k_energy,
        flips,
    )

