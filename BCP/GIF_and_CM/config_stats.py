from pydantic import BaseModel


class StatsResultsDFCols(BaseModel):
    MODEL_PATH: str = "Model path"
    FACES_COUNT: str = "#Faces"
    VERTICES_COUNT: str = "#Vertices"
    # Ours stats
    BOUNDARY_VERTICES_COUNT: str = "#Boundary Vertices"
    SIMPLIFICATION_FACES_COUNT: str = "#Faces Simplification"
    SIMPLIFICATION_E_SD: str = "Simplification E_sd"
    OURS_SIMPLIFICATION_TIME: str = "Ours Simplification Time"
    OURS_CM_SIMPLIFICATION_TIME: str = "CM Over Simplification Time"
    OURS_CM_SIMPLIFICATION_ITERS: str = "Ours CM Over Simplification Iterations"
    OURS_PROLONGATION_TIME: str = "Ours Prolongation Time"
    OURS_GIF_TIME: str = "Ours GIF Time"
    OURS_TOTAL_TIME_CONSUMPTION: str = "Ours Total Time Consumption"
    OURS_E_SD: str = "Ours E_sd"
    OURS_E_SD_BEST_99_99: str = "Ours E_sd Best 99.99%"
    OURS_E_SD_BEST_99_9: str = "Ours E_sd Best 99.9%"
    OURS_E_SD_BEST_99: str = "Ours E_sd Best 99%"
    OURS_E_SD_BEST_95: str = "Ours E_sd Best 95%"
    OURS_E_SD_WORST_5: str = "Ours E_sd Worst 5%"
    OURS_E_SD_WORST_1: str = "Ours E_sd Worst 1%"
    OURS_E_SD_MAX: str = "Ours E_sd Max"
    OURS_K: str = "Ours k"
    OURS_BEFORE_MVC_FIX: str = "Ours Before MVC Fix"
    OURS_AFTER_FINAL_FLIPS_POST_CHECK: str = "Ours #Flips computed in python"
    OURS_AFTER_FINAL_FLIPS: str = "Ours #Flips"
    OURS_MEAN_VALUE_FIX_WAS_APPLIED: str = "Ours - Mean Value Fix was Applied"

    OURS_IDT_EDGE_FLIPS_COUNT: str = "Ours IDT Edge Flips Count"
    OURS_IDT_TIME_CONSUMPTION: str = "Ours IDT Time Consumption"
    OURS_IDT_TIME_ARE_ALL_COT_POSITIVE: str = "Ours IDT Are All Cot Positive"
    OURS_IDT_TIME_MIN_COT_VALUE: str = "Ours IDT Minimum Cot Value"
    OURS_IDT_TIME_NEGATIVE_COT_EDGES_COUNT: str = "Ours IDT Negative Cot Edges Count"
    OURS_IDT_TIME_UNABLED_FLIPS: str = "Ours IDT Unabled Flips"
    OURS_IDT_TIME_IS_SIMPLE_GRAPH: str = "Ours IDT Is Simple Graph"

    GIF_E_SD: str = "GIF E_sd"
    GIF_E_SD_BEST_99_99: str = "GIF E_sd Best 99.99%"
    GIF_E_SD_BEST_99_9: str = "GIF E_sd Best 99.9%"
    GIF_E_SD_BEST_99: str = "GIF E_sd Best 99%"
    GIF_E_SD_BEST_95: str = "GIF E_sd Best 95%"
    GIF_E_SD_WORST_5: str = "GIF E_sd Worst 5%"
    GIF_E_SD_WORST_1: str = "GIF E_sd Worst 1%"
    GIF_E_SD_MAX: str = "GIF E_sd Max"
    GIF_K: str = "GIF k"
    GIF_BEFORE_MVC_FIX: str = "GIF Before MVC Fix"
    GIF_AFTER_FINAL_FLIPS: str = "GIF #Flips"
    GIF_MEAN_VALUE_FIX_WAS_APPLIED: str = "GIF - Mean Value Fix was Applied"
    GIF_TIME_CONSUMPTION: str = "GIF Time Consumption"
    # Original CM stats
    CM_E_SD: str = "CM E_SD"
    CM_E_SD_BEST_99_99: str = "CM E_sd Best 99.99%"
    CM_E_SD_BEST_99_9: str = "CM E_sd Best 99.9%"
    CM_E_SD_BEST_99: str = "CM E_sd Best 99%"
    CM_E_SD_BEST_95: str = "CM E_sd Best 95%"
    CM_E_SD_WORST_5: str = "CM E_sd Worst 5%"
    CM_E_SD_WORST_1: str = "CM E_sd Worst 1%"
    CM_E_SD_MAX: str = "CM E_sd Max"
    CM_K: str = "CM k"
    CM_FLIPS: str = "CM #Flips"
    CM_TIME: str = "CM Total Time Consumption"
    CM_ITERS: str = "CM Iterations"
    # CM with ours initialization - stats
    CM_E_SD_WITH_OURS_INIT: str = "CM E_SD with Ours Init"
    CM_TIME_WITH_OURS_INIT: str = "CM Time with Ours Init"
    CM_ITERS_WITH_OURS_INIT: str = "CM Iterations with Ours Init"
    # CM stopped when reaches our energy - stats
    CM_TIME_TO_REACH_OURS_ENERGY: str = "CM time to reach ours E_SD"
    CM_ITERS_TO_REACH_OURS_ENERGY: str = "CM iters to reach ours E_SD"
    CM_E_SD_AFTER_REACHING_OURS_ENERGY: str = "CM E_SD after reaching ours E_SD"
    # CM stopped when reaches our runtime - stats
    CM_ITERS_TO_REACH_OURS_RUNTIME: str = "CM iters to reach ours runtime"
    CM_E_SD_AFTER_REACHING_OURS_RUNTIME: str = "CM E_SD after reaching ours runtime"


def get_cols_names_values_list(config_cols):
    return list(config_cols.model_dump().values())

class CONFIG:
    def __init__(self):
        self.stats_results_df_cols = StatsResultsDFCols()


def get_config():
    return CONFIG()
