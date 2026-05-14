# Fast Injective Mesh Parameterization via Beltrami Coefficient Prolongation
--------------------------------------------------------------------------------------------------------------------------------------------------------
This code includes the implementation of the Eurographics 2026 paper "Fast Injective Mesh Parameterization via Beltrami Coefficient
Prolongation" authored by Guy Fargion and Ofir Weber. 

The use of this application is limited to academic use only!

The code is provided as-is and without any guarantees.

This GIF submodule is partially based on https://github.com/GuyFa/GIF

The CM submodule is partially based on https://github.com/Roipo/CompMajor

For questions or comments about the code please contact:
Guy Fargion (guy.fargion@gmail.com)

----------------------------------------------------------------------------
The code should be platform independent though we never tested it on other than Windows OS.

## Installlation

### 1) GIF
A Visual Studio 2019 project is provided for easy compilation on Windows machines.

The following prerequisites are necessary for building and running the code:

1) Matlab R2022b

2) Boost 1.83.0 - We downloaded boost from here https://www.boost.org/. Our code only requires the headers of the Boost libraries. Hence, there is no need to build boost.

3) CGAL 5.6 - We installed CGAL 5.6 with the gmp and mpfr auxiliary libraries. There is no need to build CGAL as well.

4) GMM C++ template library version 4.2 (http://getfem.org/download.html).

5) PARDISO 8.2

6) Eigen 3.4.0

7) NLopt 2.10


Other versions of the above listed tools might be compatible but weren't tested!

Now:

1) Install and build the above mentioned prerequisites.

2) Add the following environment variables to your system (see some possible paths):

GMM_INCLUDE_DIR		  (%your GMM folder path%)\gmm-4.2\include

MATLAB_64_DIR		    C:\Program Files\MATLAB\R2022b

CGAL_64_DIR		      C:\Program Files\CGAL-5.6

BOOST_64_DIR		    C:\Program Files\boost\boost_1_83_0

EIGEN_DIR  		      (%your Eigen folder path%)

PARDISO_BIN         (%path to the folder where PARDISO dll and lib are%)

PARDISO_LIC_PATH    (%path to the folder with PARDISO licence%)

OMP_NUM_THREADS  	  number of cores in your CPU (for PARDISO)

NLOPT_DIR           (%path to the nlopt directory)

3) Add the the folder "MatlabScripts" to your Matlab path.

4) Make sure all the required dlls can be loacted by including the relevant paths into the system PATH variable.
For example:

PATH=
%MATLAB_64_DIR%\bin\win64;
%MATLAB_64_DIR%\extern\include;
%MATLAB_64_DIR%\extern\lib\win64\microsoft;
%BOOST_64_DIR%\libs;
%CGAL_64_DIR%\lib;
%CGAL_64_DIR%\auxiliary\gmp\lib;
%CGAL_64_DIR%\include\CGAL;
%PARDISO_BIN%;
%MATLAB_64_DIR%
%NLOPT_DIR%

### 2) CM

After installing GIF, CM should run as well with no further installation, as the environment variables needed for PARDISO already exist. Make sure you clone all the recursive submodules as well.

### 3) PT

This submodule performs computations related to the parallel transport operations. After install GIF, PT should run as well with no further installation.

### 3) BCP
We used python 3.10.

All requirements appear in ```BCP/requirements.txt```.


## Running
```BCP/GIF_and_CM/test_models.py``` contains a script for running the entire algorithm.

The dataset folder is assumed to contain a list of 3D disk-like meshes:

```
dataset
|0_source_textured_by_uv_ours.obj
|1_source_textured_by_uv_ours.obj
| ...
```

and an additional file named ```data.file``` with the list of models:

```
{
"models": [
        "0_source_textured_by_uv_ours.obj",
        "1_source_textured_by_uv_ours.obj",
        ...
    ]
}
```

Now just set the following constants in `test_models.py`:

`DATA_FILE` - the path to `data.json`

`OBJ_RESULTS_PATH` - the path in which the code will save `.obj` result.

`RESULTS_SUMMARY_PATH` - the path to the statistics `.csv` file.

Optional flags:

The use can manually set the target number of faces in the simplified mesh via `TARGET_SIMPLIFICATION_FACES_COUNT` in `MeshProcessor.py`. 

## Object files
The dataset used in the paper is available at https://livebiuac-my.sharepoint.com/:f:/g/personal/guy_fargion_live_biu_ac_il/IgB9ZUKwt23DQbSREXHH049eATo5VFyRF5QgPY1wq1itk2s?e=UY3wN4

The models from the figures in the paper are available at https://livebiuac-my.sharepoint.com/:f:/g/personal/guy_fargion_live_biu_ac_il/IgB8d1R6EdenQaSm7pNEa2FSAac6x-8mLYc2XeSC6yiZzyc?e=GSOp7A

---

## Operations & Maintenance (Windows)

### Running the pipeline

1. Activate the Python virtual environment from the repo root:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

2. Run from the `BCP/GIF_and_CM/` directory (required by path resolution in `consts.py`):
   ```powershell
   cd BCP\GIF_and_CM
   python test_models.py
   ```

3. Edit `test_models.py` to point to your mesh list and output folder:
   - `DATA_FILE` — path to a `data.json` listing input mesh filenames
   - `OBJ_RESULTS_PATH` — folder where textured `.obj` results are written (created automatically)
   - `RESULTS_SUMMARY_PATH` — path for the stats `.csv`

4. The pipeline stages and their executables:
   | Stage | Executable | Working dir |
   |---|---|---|
   | Simplification | Python (meshlib) | — |
   | CM (coarse parameterization) | `CompMajor/Parameterization_cmd.exe` | `CompMajor/` |
   | PT (parallel transport) | `PT/x64/Release/PT.exe` | `PT/x64/Release/` |
   | GIF (full-res flattening) | `GIF/GIF/x64/Release/GIF.exe` | `GIF/GIF/x64/Release/` |

   All `stdout`/`stderr` from executables is printed to the Python console with `[CM]`, `[PT]`, `[GIF]` prefixes.

---

### Key tunable parameters

| Parameter | Location | What it controls |
|---|---|---|
| `TARGET_SIMPLIFICATION_FACES_COUNT` | `BCP/GIF_and_CM/MeshProcessor.py` line 17 | Target face count for simplified mesh. `None` = `max(10 000, 1% of original)`. |
| `INTERIOR_FACES_IN_GIF` | `BCP/GIF_and_CM/consts.py` | GIF coarse hierarchy size. `-1` = auto. |
| `BOUNDARY_SEGMENT_SIZE_IN_GIF` | `BCP/GIF_and_CM/consts.py` | GIF boundary coarsening. `-1` = auto. |
| `CURVATURE_META_VERTICES_RATE_IN_GIF` | `BCP/GIF_and_CM/consts.py` | Fraction of vertices used as cone singularities. |
| `OUTER_TERMINATION_CONDITION_RATE_IN_GIF` | `BCP/GIF_and_CM/consts.py` | Relative improvement threshold for GIF's outer Newton loop. |
| `ENERGY_RELATED_TERMINATION_CONDITION_IN_GIF` | `BCP/GIF_and_CM/consts.py` | Energy-based early stop for GIF. `0.0` = disabled. |
| µ cap | `BCP/GIF_and_CM/run_GIF_CM.py` (`0.99`) | Max Beltrami coefficient magnitude before normalization. Controls injectivity margin. |

**Post-refinement (full-mesh CM initialized with GIF output):** set the third boolean flag in the `compute_stats_to_summary` call in `test_models.py` to `True` (`compare_with_CM_with_our_initialization`). Results appear in the CSV as `CM_*_WITH_OURS_INIT` columns.

---

### Switching MATLAB versions

All three C++ executables (CM, PT, GIF) embed a MATLAB engine. Switching MATLAB versions requires touching four independent systems. Do them in order:

**Step 1 — Environment variable** (System Properties → Advanced → Environment Variables, or Admin PowerShell)

```powershell
[System.Environment]::SetEnvironmentVariable("MATLAB_64_DIR", "C:\Program Files\MATLAB\R<version>", "Machine")
```

This controls which MATLAB headers and `.lib` files are used **at build time**.

**Step 2 — System PATH** (Admin PowerShell — replace `R2022b` / `R2026a` with old/new version)

```powershell
$p = [System.Environment]::GetEnvironmentVariable("PATH", "Machine")
$p = $p -replace [regex]::Escape("C:\Program Files\MATLAB\R<old>"), "C:\Program Files\MATLAB\R<new>"
[System.Environment]::SetEnvironmentVariable("PATH", $p, "Machine")
```

Key PATH entries to keep for the target version: `\bin`, `\bin\win64`, `\extern\include`, `\extern\lib\win64\microsoft`.

**Step 3 — Windows Registry** (Admin PowerShell)

`engOpen()` (the C API used to start MATLAB from C++) picks the **highest** version key under `HKLM\SOFTWARE\MathWorks\MATLAB\`.

- To switch **to a newer version** — add its key:
  ```powershell
  New-Item -Path "HKLM:\SOFTWARE\MathWorks\MATLAB\26.1" -Force
  Set-ItemProperty -Path "HKLM:\SOFTWARE\MathWorks\MATLAB\26.1" -Name "MATLABROOT" -Value "C:\Program Files\MATLAB\R2026a"
  ```
- To switch **to an older version** — delete the newer version's key:
  ```powershell
  Remove-Item -Path "HKLM:\SOFTWARE\MathWorks\MATLAB\26.1" -Recurse -Force
  ```
- Verify what's registered: `reg query "HKLM\SOFTWARE\MathWorks\MATLAB" /s`

**Step 4 — `copied_libs/` directory**

If `C:\Users\gmu_a\dev\BCP\copied_libs\` contains MATLAB runtime DLLs (`libeng.dll`, `libmx.dll`, etc.), they must match the target version — or remove them and let PATH handle it. The directory is high-priority in PATH, so stale DLLs here will override the correct ones.

Currently only `nlopt.dll` (Luksan-enabled, 531 KB) lives here. Do not replace it.

**Step 5 — Kill running processes**

```powershell
Get-Process | Where-Object { $_.Name -imatch "Parameterization_cmd|MATLAB|GIF|PT" } | Stop-Process -Force
```

If a rebuild fails with `LNK1104: cannot open file '*.exe'`, the exe is locked. Rename it (`.exe` → `.exe.old`), rebuild, then delete the old file.

**Step 6 — Rebuild all executables** (in a fresh terminal so PATH is picked up)

```powershell
# Using MSBuild directly, or trigger via msbuild-mcp-server
msbuild CompMajor\CompMajor.sln /p:Configuration=Release /p:Platform=x64 /t:Rebuild
msbuild PT\PT.sln               /p:Configuration=Release /p:Platform=x64 /t:Rebuild
msbuild GIF\GIF\GIF.sln         /p:Configuration=Release /p:Platform=x64 /t:Rebuild
```

**Step 7 — MATLAB `.m` scripts** (no rebuild needed)

Script edits take effect immediately on the next run. MATLAB re-reads `.m` files from disk each call — there is no compiled cache. However:
- MATLAB uses `%` for comments, not `//`. Invalid syntax prevents the whole script from executing.
- GPU forward compatibility: add `parallel.gpu.enableCUDAForwardCompatibility(true);` at the top of `newtonWithScaffoldPreps.m` if the GPU compute capability exceeds what the installed MATLAB natively supports (e.g., R2022b + CC 12.0 GPU). R2026a supports CC 12.0 natively — this line is not needed.

---

### nlopt.dll (Luksan support)

The `nlopt.dll` shipped in the repo does **not** include Luksan code, which GIF requires for `NLOPT_LD_LBFGS`. The correct DLL (531 KB, Luksan-enabled) lives in `copied_libs/` and is found via PATH. Do **not** place `nlopt.dll` in `GIF/GIF/x64/Release/` — GIF rebuilds will overwrite it with the wrong version.

To rebuild `nlopt.dll` with Luksan support:
1. Open `%NLOPT_DIR%\build\nlopt.vcxproj` in Visual Studio
2. Verify `NLOPT_LUKSAN` preprocessor define is present
3. Build Release|x64
4. Copy the resulting `nlopt.dll` to `copied_libs/`
