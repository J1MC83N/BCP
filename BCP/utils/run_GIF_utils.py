import os
import time
from datetime import datetime

import numpy as np
import igl
import torch
import scipy.io as sio
from subprocess import Popen, PIPE, TimeoutExpired

TIMEOUT_SECONDS = 300

def save_data_for_GIF(vertices, faces, cache_path, edge_lengths=None):
    cur_time = datetime.now().strftime("%Y%m%d%H%M%S")
    tmp_obj_file = cache_path + "/" + cur_time + ".obj"
    igl.write_obj(tmp_obj_file, vertices, faces)
    edge_lengths_mat_file = '""'
    if edge_lengths is not None:
        dict1 = {"edge_lengths": edge_lengths.astype(np.float64)}
        edge_lengths_mat_file = cache_path + "/" + cur_time + "_edge_lengths.mat"
        sio.savemat(edge_lengths_mat_file, dict1)
    final_GIF_res_path = cache_path + "/" + cur_time + "GIF_UVs.mat"
    return tmp_obj_file, final_GIF_res_path, edge_lengths_mat_file


def run_GIF(
    vertices,
    faces,
    exe_path,
    cache_path,
    interior_faces: int = -1,
    boundary_segment_size: int = -1,
    curvature_meta_vertices_rate: float = 0.001,
    outer_termination_condition_rate: float = 0.1,
    energy_related_termination_condition: float = 2.0,
    edge_lengths=None,
    allow_IDT_fix=False,
):
    tmp_obj_file, final_GIF_res_path, edge_lengths_mat_file = save_data_for_GIF(vertices, faces, cache_path, edge_lengths)
    exe_file_dir, exe_file_name = exe_path.rsplit("/", 1)
    if allow_IDT_fix:
        cmdline = f"{exe_file_name} {tmp_obj_file} {final_GIF_res_path} True False False {interior_faces} {boundary_segment_size} {curvature_meta_vertices_rate} {outer_termination_condition_rate} {energy_related_termination_condition} {edge_lengths_mat_file}"
        p = Popen(
            "cmd /c " + cmdline,
            cwd=exe_file_dir,
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
        )
        try:
            stdout, stderr = p.communicate(timeout=TIMEOUT_SECONDS)
        except TimeoutExpired:
            # Handle timeout
            print("Command timed out. Terminating the process.")
            p.terminate()  # Terminate the process
        res_GIF = sio.loadmat(final_GIF_res_path)
        time_consumption = res_GIF["parametersMatrix"][4, 0]
    else:
        # run GIF with regular MVC fix
        cmdline = f"{exe_file_name} {tmp_obj_file} {final_GIF_res_path} False True True {interior_faces} {boundary_segment_size} {curvature_meta_vertices_rate} {outer_termination_condition_rate} {energy_related_termination_condition} {edge_lengths_mat_file}"
        p = Popen("cmd /c " + cmdline, cwd=exe_file_dir, shell=True, stdout=PIPE, stderr=PIPE)
        try:
            stdout, stderr = p.communicate(timeout=TIMEOUT_SECONDS)
        except TimeoutExpired:
            # Handle timeout
            print("Command timed out. Terminating the process.")
            p.terminate()  # Terminate the process
        res_GIF = sio.loadmat(final_GIF_res_path)
        time_consumption = res_GIF["parametersMatrix"][4, 0]
    uvs = res_GIF["uvs_ordered"]
    flipsData = res_GIF["flipsData"]
    IDT_stats = res_GIF["IDT_outputs"].reshape(-1)
    edge_compatibility_data = (
        res_GIF["parametersMatrix"][15, 0],
        res_GIF["parametersMatrix"][16, 0],
        res_GIF["parametersMatrix"][17, 0],
        res_GIF["parametersMatrix"][18, 0],
    )
    averaged_edge_lengths = res_GIF["mAverageEdgeLengths"]
    os.remove(tmp_obj_file)
    if edge_lengths_mat_file != '""':
        os.remove(edge_lengths_mat_file)
    os.remove(final_GIF_res_path)
    # in case we run IDT fix, flips_count_before_fix represents wheather the method worked on the IDT model without the MVC fix
    return [
        uvs,
        flipsData,
        IDT_stats,
        time_consumption,
        edge_compatibility_data,
        averaged_edge_lengths
    ]


def compute_edges_vectors(vertices, faces):
    # This function computes the edge vectors.
    # The returned matrix is of size #F x 3 x 3:
    # edges_vectors[f_ind, edge_ind, :] is the vector of the edge_ind edge in the f_ind face.
    # The order of the faces in edges_vectors is the same order of faces in th faces matrix.
    # The edges order is 01, 12, 20
    faces_vertices = np.zeros((faces.shape[0], 3, 3))
    faces_vertices[:, 0, :] = vertices[faces[:, 0]]
    faces_vertices[:, 1, :] = vertices[faces[:, 1]]
    faces_vertices[:, 2, :] = vertices[faces[:, 2]]
    edges_vectors = np.stack(
        (
            faces_vertices[:, 1, :] - faces_vertices[:, 0, :],
            faces_vertices[:, 2, :] - faces_vertices[:, 1, :],
            faces_vertices[:, 0, :] - faces_vertices[:, 2, :],
        ),
        axis=1,
    )
    return edges_vectors


def compute_EL_from_metric_tensors(metric_tensors, vertices, faces, local_bases=None):
    edges_vectors = torch.from_numpy(compute_edges_vectors(vertices, faces)).to("cuda:0")
    if local_bases is not None:
        edge_vectors_projected = torch.einsum(
            "abc, acd->abd", local_bases[:, :2, :], edges_vectors.transpose(2, 1)
        ).transpose(2, 1)
    else:
        edge_vectors_projected = edges_vectors
    edges_vectors_mul = torch.einsum("adb, adc->adbc", edge_vectors_projected, edge_vectors_projected)
    metric_tensors_rep = metric_tensors.unsqueeze(1).repeat(1, 3, 1, 1)
    edge_lengths = torch.sqrt((metric_tensors_rep * edges_vectors_mul).sum(3).sum(2))
    return edge_lengths


def compute_UVs_from_metric_tensors_GIF(
    metric_tensors,
    vertices,
    faces,
    exe_path,
    cache_path,
    interior_faces: int,
    boundary_segment_size: int,
    curvature_meta_vertices_rate: float,
    outer_termination_condition_rate: float,
    energy_related_termination_condition: float,
    allow_IDT_fix=True,
    local_basis=None,
):
    start = time.time()
    edge_lengths = compute_EL_from_metric_tensors(metric_tensors, vertices, faces, local_basis)
    end = time.time()
    edge_lengths_computation_time = end - start
    print(f"Edge lengths computation time: {edge_lengths_computation_time}")

    assert compute_triangle_inequality_satisfying_rate(edge_lengths) == 1, (
        "Triangle inequality is not satisfied after fixing the predicted metric tensor!"
    )
    i = 0
    while True:
        i += 1
        try:
            res_GIF = run_GIF(
                vertices,
                faces,
                exe_path,
                cache_path,
                interior_faces,
                boundary_segment_size,
                curvature_meta_vertices_rate,
                outer_termination_condition_rate,
                energy_related_termination_condition,
                edge_lengths.cpu().numpy(),
                allow_IDT_fix,
            )
            break
        except Exception as e:
            print(f"Exception {e}")
            print(f"{i}th attempt to run GIF failed")
            continue

    res_GIF[3] = res_GIF[3] + edge_lengths_computation_time
    return res_GIF


def compute_triangle_inequality_satisfying_rate(edge_lengths):
    triangle_inequality_criteria = torch.full_like(edge_lengths, False)
    triangle_inequality_criteria[:, 0] = edge_lengths[:, 0] + edge_lengths[:, 1] > edge_lengths[:, 2]
    triangle_inequality_criteria[:, 1] = edge_lengths[:, 1] + edge_lengths[:, 2] > edge_lengths[:, 0]
    triangle_inequality_criteria[:, 2] = edge_lengths[:, 2] + edge_lengths[:, 0] > edge_lengths[:, 1]
    triangle_inequality_holds = triangle_inequality_criteria.all(axis=1)
    if triangle_inequality_holds.sum() == triangle_inequality_holds.shape[0]:
        return 1
    triangle_inequality_holds_rate = triangle_inequality_holds.sum() / triangle_inequality_holds.shape[0]
    return triangle_inequality_holds_rate
