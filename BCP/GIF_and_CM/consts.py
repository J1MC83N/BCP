# Use pathlib to determine repository root and compose paths dynamically.
import os
from pathlib import Path, PurePosixPath




REPO_ROOT = PurePosixPath(Path(__file__).resolve().parents[2])
print(f"Determined repository root: {REPO_ROOT}")

# CM
ROOT_PATH_CM_EXE = str(REPO_ROOT / "CompMajor" / "Parameterization_cmd.exe")
ROOT_DIR_CACHE_CM = str(REPO_ROOT / "caches" / "cache_CM")

# GIF
ROOT_PATH_GIF_EXE = str(REPO_ROOT / "GIF" / "GIF" / "x64" / "Release" / "GIF.exe")
ROOT_DIR_CACHE_GIF = str(REPO_ROOT / "caches" / "cache_GIF")

# Meshlib
ROOT_DIR_CACHE_MESHLIB = str(REPO_ROOT / "caches" / "cache_meshlib")

# Parallel transport
ROOT_PATH_PARALLEL_TRANSPORT_EXE = str(REPO_ROOT / "PT" / "x64" / "Release" / "PT.exe")
ROOT_DIR_CACHE_PARALLEL_TRANSPORT = str(REPO_ROOT / "caches" / "cache_gradients")



INTERIOR_FACES_IN_GIF = -1
BOUNDARY_SEGMENT_SIZE_IN_GIF = -1
CURVATURE_META_VERTICES_RATE_IN_GIF = 0.001
OUTER_TERMINATION_CONDITION_RATE_IN_GIF = 0.1
ENERGY_RELATED_TERMINATION_CONDITION_IN_GIF = 0.0
