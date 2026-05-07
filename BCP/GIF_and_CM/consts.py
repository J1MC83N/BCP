# Use pathlib to determine repository root and compose paths dynamically.
import os
from pathlib import Path

_root = Path(__file__).resolve().parents[2]

REPO_ROOT = _root.as_posix()
print(f"Determined repository root: {REPO_ROOT}")

# CM
ROOT_PATH_CM_EXE = (_root / "CompMajor" / "Parameterization_cmd.exe").as_posix()
ROOT_DIR_CACHE_CM = (_root / "caches" / "cache_CM").as_posix()

# GIF
ROOT_PATH_GIF_EXE = (_root / "GIF" / "GIF" / "x64" / "Release" / "GIF.exe").as_posix()
ROOT_DIR_CACHE_GIF = (_root / "caches" / "cache_GIF").as_posix()

# Meshlib
ROOT_DIR_CACHE_MESHLIB = (_root / "caches" / "cache_meshlib").as_posix()

# Parallel transport
ROOT_PATH_PARALLEL_TRANSPORT_EXE = (_root / "PT" / "x64" / "Release" / "PT.exe").as_posix()
ROOT_DIR_CACHE_PARALLEL_TRANSPORT = (_root / "caches" / "cache_gradients").as_posix()



INTERIOR_FACES_IN_GIF = -1
BOUNDARY_SEGMENT_SIZE_IN_GIF = -1
CURVATURE_META_VERTICES_RATE_IN_GIF = 0.001
OUTER_TERMINATION_CONDITION_RATE_IN_GIF = 0.1
ENERGY_RELATED_TERMINATION_CONDITION_IN_GIF = 0.0
