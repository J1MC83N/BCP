import json
import igl
import pandas as pd

import sys
sys.path.append("C:/Users/gmu_a/dev/BCP/BCP")
sys.path.append("C:/Users/gmu_a/dev/BCP/BCP/utils")

from GIF_and_CM.consts import ROOT_DIR_CACHE_GIF, ROOT_PATH_CM_EXE, ROOT_DIR_CACHE_CM, ROOT_PATH_GIF_EXE
from run_GIF_CM import run_GIF_and_CM_with_simplification, run_GIF_and_CM_with_simplification_with_IDT
from save_stats import compute_stats_to_summary

# Input and output files
DATA_FILE = "C:/Users/gmu_a/dev/BCP/meshes/data.json"
OBJ_RESULTS_PATH = "C:/Users/gmu_a/dev/BCP/meshes"
RESULTS_SUMMARY_PATH = "C:/Users/gmu_a/dev/BCP/meshes/res.csv"


OBJ_FOLDER = DATA_FILE.rsplit("/", 1)[0]
with open(DATA_FILE, 'r') as file:
    data = json.load(file)
obj_files = ['/'.join([OBJ_FOLDER, p]) for p in data["models"]]

results_df = pd.DataFrame()
start_running = False
for obj_file in obj_files:
    print("Processing file: ", obj_file)
    v, f, = igl.read_triangle_mesh(obj_file)
    obj_name = obj_file.split("/")[-1].split(".")[0]
    simplification_time, CM_time, mt_computation_time, time_GIF, pred_V, flipsData, CM_iters, simplification_f_count, simplification_Esd, IDT_stats = run_GIF_and_CM_with_simplification(
        v, f)
    # simplification_time, CM_time, mt_computation_time, time_GIF, pred_V, flipsData, CM_iters, simplification_f_count, simplification_Esd, IDT_stats = run_GIF_and_CM_with_simplification_with_IDT(
    #         v, f)
    results_df = compute_stats_to_summary(results_df,
                                          obj_file,
                                          OBJ_RESULTS_PATH + obj_name,
                                          pred_V,
                                          simplification_f_count,
                                          simplification_time,
                                          CM_time,
                                          mt_computation_time,
                                          CM_iters,
                                          simplification_Esd,
                                          time_GIF,
                                          IDT_stats,
                                          f,
                                          v,
                                          False,
                                          False,
                                          False,
                                          False,
                                          False,
                                          False,
                                          flipsData,
                                          ROOT_DIR_CACHE_CM,
                                          ROOT_PATH_CM_EXE,
                                          ROOT_DIR_CACHE_GIF,
                                          ROOT_PATH_GIF_EXE
                                          )

    results_df.to_csv(RESULTS_SUMMARY_PATH)
