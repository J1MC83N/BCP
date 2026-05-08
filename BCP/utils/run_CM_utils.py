import os
from datetime import datetime

import igl
from subprocess import Popen, PIPE, TimeoutExpired

import numpy as np
import scipy.io as sio

TIMEOUT_SECONDS = 3600


def save_data_for_CM(vertices, faces, cache_path, init_UVs=None):
    cur_time = datetime.now().strftime("%Y%m%d%H%M%S")
    tmp_input_obj_file = cache_path + "/" + cur_time + ".obj"
    igl.write_obj(tmp_input_obj_file, vertices, faces)
    tmp_uv_obj_file = cache_path + "/" + cur_time + "_CM_uv.obj"
    tmp_result_mat_file = cache_path + "/" + cur_time + "_CM_res.mat"
    tmp_meta_data_txt_file = cache_path + "/" + cur_time + "_CM_res_meta_data.txt"
    tmp_init_obj_file = None
    if init_UVs is not None:
        tmp_init_obj_file = cache_path + "/" + cur_time + "_init.obj"
        igl.write_obj(tmp_init_obj_file, np.hstack([init_UVs, np.zeros((init_UVs.shape[0], 1))]), faces)
    return (
        tmp_input_obj_file,
        tmp_uv_obj_file,
        tmp_result_mat_file,
        tmp_meta_data_txt_file,
        tmp_init_obj_file,
    )


def run_CM(V, F, exe_path, cache_path):
    (
        tmp_input_obj_file,
        tmp_uv_obj_file,
        tmp_result_mat_file,
        tmp_meta_data_txt_file,
        _,
    ) = save_data_for_CM(V, F, cache_path)

    exe_file_dir, exe_file_name = exe_path.rsplit("/", 1)

    cmdline = (
        exe_file_name + ' "' + tmp_input_obj_file + '" "' + tmp_uv_obj_file + '" "' + tmp_result_mat_file + '" "' + tmp_meta_data_txt_file + '"'
    )

    print("------- [CM run_CM] -------")
    print(f">    Command: {cmdline}")
    print(f">    Working directory: {exe_file_dir}")
    p = Popen(
        "cmd /c " + cmdline,
        cwd=exe_file_dir,
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
    )
    try:
        stdout, stderr = p.communicate(timeout=TIMEOUT_SECONDS)
        print("------- [CM run_CM stdout] -------")
        if stdout:
            for line in stdout.decode('utf-8', errors='ignore').split('\n'):
                if line.strip():
                    print(f">    {line}")
        else:
            print(">    (no stdout)")
        print("------- [CM run_CM stderr] -------")
        if stderr:
            for line in stderr.decode('utf-8', errors='ignore').split('\n'):
                if line.strip():
                    print(f">    {line}")
        else:
            print(">    (no stderr)")
        print("------- [CM run_CM end] -------")
    except TimeoutExpired:
        # Handle timeout
        print(">    Command timed out. Terminating the process.")
        p.terminate()  # Terminate the process
        print("------- [CM run_CM end] -------")
    # # If the external CM executable did not create the expected result files,
    # # create a fallback .mat and meta file so downstream code can continue
    # # (useful for development when the compiled exe isn't available).
    # if not os.path.exists(tmp_result_mat_file) or not os.path.exists(tmp_meta_data_txt_file):
    #     try:
    #         # create a dummy uvs array (one UV per face)
    #         uvs_dummy = np.zeros((F.shape[0], 2))
    #         sio.savemat(tmp_result_mat_file, {"uvs": uvs_dummy})
    #         with open(tmp_meta_data_txt_file, "w") as meta_f:
    #             meta_f.write("time:0.0\n")
    #             meta_f.write("iters:0\n")
    #             meta_f.write("esd:inf\n")
    #     except Exception:
    #         # If fallback creation fails, let the subsequent loadmat raise the
    #         # original error so the caller can see a traceback.
    #         pass


    res_CM = sio.loadmat(tmp_result_mat_file)
    uvs = res_CM["uvs"]
    meta_data = open(tmp_meta_data_txt_file, "r").readlines()
    CM_time_consumption = float(meta_data[0].removesuffix("\n").split(":")[1])
    CM_iters_count = float(meta_data[1].removesuffix("\n").split(":")[1])
    try:
        e_sd = float(meta_data[2].removesuffix("\n").split(":")[1])
    except:
        e_sd = np.inf
    # Files intentionally kept for debug inspection (timestamp-named in cache_CM/)
    # os.remove(tmp_input_obj_file)
    # os.remove(tmp_result_mat_file)
    # os.remove(tmp_meta_data_txt_file)
    return uvs, CM_time_consumption, CM_iters_count, e_sd


def run_CM_with_target_energy(V, F, target_energy, exe_path, cache_path):
    (
        tmp_input_obj_file,
        tmp_uv_obj_file,
        tmp_result_mat_file,
        tmp_meta_data_txt_file,
        _,
    ) = save_data_for_CM(V, F, cache_path)

    exe_file_dir, exe_file_name = exe_path.rsplit("/", 1)

    cmdline = (
        exe_file_name
        + ' "'
        + tmp_input_obj_file
        + '" "'
        + tmp_uv_obj_file
        + '" "'
        + tmp_result_mat_file
        + '" "'
        + tmp_meta_data_txt_file
        + '" '
        + str(target_energy)
    )

    print(cmdline)

    p = Popen(
        "cmd /c " + cmdline,
        cwd=exe_file_dir,
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
    )
    try:
        stdout, stderr = p.communicate(timeout=TIMEOUT_SECONDS)
        print("stdout:", stdout.decode())
        print("stderr:", stderr.decode())
    except TimeoutExpired:
        # Handle timeout
        print("Command timed out. Terminating the process.")
        p.terminate()  # Terminate the process

    res_CM = sio.loadmat(tmp_result_mat_file)
    uvs_full = res_CM["uvs"]
    meta_data = open(tmp_meta_data_txt_file, "r").readlines()
    CM_time_consumption = float(meta_data[0].removesuffix("\n").split(":")[1])
    CM_iters_count = float(meta_data[1].removesuffix("\n").split(":")[1])
    e_sd = float(meta_data[2].removesuffix("\n").split(":")[1])

    os.remove(tmp_input_obj_file)
    os.remove(tmp_result_mat_file)
    os.remove(tmp_meta_data_txt_file)
    return uvs_full[:, :2], CM_time_consumption, CM_iters_count, e_sd


def run_CM_with_target_runtime(V, F, target_time, exe_path, cache_path):
    (
        tmp_input_obj_file,
        tmp_uv_obj_file,
        tmp_result_mat_file,
        tmp_meta_data_txt_file,
        _,
    ) = save_data_for_CM(V, F, cache_path)

    exe_file_dir, exe_file_name = exe_path.rsplit("/", 1)

    cmdline = (
        exe_file_name
        + ' "'
        + tmp_input_obj_file
        + '" "'
        + tmp_uv_obj_file
        + '" "'
        + tmp_result_mat_file
        + '" "'
        + tmp_meta_data_txt_file
        + '" 2 '
        + str(target_time)
    )

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

    res_CM = sio.loadmat(tmp_result_mat_file)
    uvs_full = res_CM["uvs"]
    meta_data = open(tmp_meta_data_txt_file, "r").readlines()
    CM_time_consumption = float(meta_data[0].removesuffix("\n").split(":")[1])
    CM_iters_count = float(meta_data[1].removesuffix("\n").split(":")[1])
    e_sd = float(meta_data[2].removesuffix("\n").split(":")[1])

    os.remove(tmp_input_obj_file)
    os.remove(tmp_result_mat_file)
    os.remove(tmp_meta_data_txt_file)
    return uvs_full[:, :2], CM_time_consumption, CM_iters_count, e_sd


def run_CM_with_customized_init(V, F, init_UVs, exe_path, cache_path):
    (
        tmp_input_obj_file,
        tmp_uv_obj_file,
        tmp_result_mat_file,
        tmp_meta_data_txt_file,
        tmp_init_obj_file,
    ) = save_data_for_CM(V, F, cache_path, init_UVs)

    exe_file_dir, exe_file_name = exe_path.rsplit("/", 1)

    cmdline = (
        exe_file_name
        + ' "'
        + tmp_input_obj_file
        + '" "'
        + tmp_uv_obj_file
        + '" "'
        + tmp_result_mat_file
        + '" "'
        + tmp_meta_data_txt_file
        + '" 2 100000 "'
        + tmp_init_obj_file
        + '"'
    )

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

    res_CM = sio.loadmat(tmp_result_mat_file)
    uvs = res_CM["uvs"]
    meta_data = open(tmp_meta_data_txt_file, "r").readlines()
    CM_time_consumption = float(meta_data[0].removesuffix("\n").split(":")[1])
    CM_iters_count = float(meta_data[1].removesuffix("\n").split(":")[1])
    try:
        e_sd = float(meta_data[2].removesuffix("\n").split(":")[1])
    except:
        e_sd = np.inf
    os.remove(tmp_input_obj_file)
    os.remove(tmp_result_mat_file)
    os.remove(tmp_meta_data_txt_file)
    os.remove(tmp_init_obj_file)
    return uvs[:, :2], CM_time_consumption, CM_iters_count, e_sd
