# Installation

This page describes the recommended ways to install `py-outfit` and set up an isolated environment. The package ships pre-built wheels for Linux x86_64 (Python 3.12) and embeds a Rust extension module compiled from the Outfit core. If a wheel is not available for your platform, a local build from source will be attempted (Rust toolchain required).

## Quick start (PyPI / pip)

If you already have a clean Python 3.12 environment (e.g. `venv` or `virtualenv`):

```bash
pip install --upgrade pip
pip install py-outfit
```

Verify your installation:

```bash
python -c "import py_outfit as o; print(o.KeplerianElements)"
```

Expected output is the class representation (not an error). You can also check the version:

```bash
python -c "import importlib.metadata as m; print(m.version('py-outfit'))"
```

## Using PDM (recommended for reproducible workflows)

PDM manages isolated environments and keeps metadata in `pyproject.toml`.

1. Install PDM (user-level):
	```bash
	pip install --upgrade pdm
	```
2. Initialize a new project directory (or reuse an existing one):
	```bash
	pdm init
	```
	Follow the prompts (you can skip dependencies now).
3. Add `py-outfit` as a dependency:
	```bash
	pdm add py-outfit
	```
4. Run Python inside the managed environment:
	```bash
	pdm run python -c "import py_outfit; print(py_outfit.SECONDS_PER_DAY)"
	```

List current dependencies:

```bash
pdm list
```

## Using Conda / Mamba

You can consume the PyPI wheel from within a Conda environment. Ensure the environment uses Python 3.12 so that the published wheel matches.

1. Create and activate the environment (use `mamba` if available for speed):
	```bash
	conda create -n outfit-env python=3.12 -y
	conda activate outfit-env
	```
2. Install via pip inside the environment:
	```bash
	pip install --upgrade pip
	pip install py-outfit
	```
3. Test:
	```bash
	python -c "import py_outfit as o; print(o.GAUSS_GRAV)"
	```

If you need scientific stack packages (NumPy, Pandas, Astropy) with Conda optimizations, you can pre-install them:

```bash
conda install numpy pandas astropy pyarrow -y
pip install py-outfit
```

## Source build (fallback)

If your platform lacks a pre-built wheel, `pip` will build from source. Requirements:

- Rust toolchain (stable, matching the crate `rust-version` requirement).
- Build tools (e.g., `gcc`, `make`, and Python headers). On Debian/Ubuntu:
  ```bash
  sudo apt-get update && sudo apt-get install -y build-essential pkg-config python3-dev
  ```

Then:

```bash
pip install --upgrade pip maturin
pip install py-outfit --no-binary py-outfit
```

You can also clone the repository and build in-place:

```bash
git clone https://github.com/FusRoman/pyOutfit.git
cd pyOutfit
pip install .
```

## Verifying functionality

Minimal smoke test to perform a trivial object creation (no external ephemerides download required for this step):

```bash
python - <<'PY'
import py_outfit as o
ke = o.KeplerianElements(
	 a=2.5,      # semi-major axis (AU)
	 e=0.1,      # eccentricity
	 i=0.2,      # inclination (rad)
	 omega=1.0,  # argument of perihelion (rad)
	 Omega=0.5,  # longitude of ascending node (rad)
	 M=0.0       # mean anomaly (rad)
)
print("KeplerianElements a:", ke.a)
PY
```

If this runs without error, the Rust extension is correctly loaded.

## Selecting a parallel strategy

Parallel features are enabled in the underlying Rust crate. No extra Python-side configuration is required. If you process large batches and want deterministic behavior across runs, pass a seed where exposed by batch APIs (see `estimate_all_orbits`).

## Upgrading

```bash
pip install --upgrade py-outfit
```

With PDM:

```bash
pdm update py-outfit
```

## Uninstalling

```bash
pip uninstall py-outfit
```

Or in PDM:

```bash
pdm remove py-outfit
```

## Troubleshooting

Missing wheel / build fails:
  Ensure Rust is installed (`curl https://sh.rustup.rs -sSf | sh`) and that `rustc --version` meets or exceeds the crate requirement. Install system build dependencies (`build-essential` or equivalents).

ImportError: cannot open shared object file:
  Check that you are not mixing architectures (e.g., installing in a system Python but running inside Conda). Reinstall inside the same environment that runs Python.

Segfault or crash on import:
  Remove conflicting old builds: `pip uninstall py-outfit -y` then reinstall. Ensure only one version of the extension (`py_outfit*.so`) exists in the site-packages path.

Ephemerides download issues:
  The first call that triggers JPL ephemerides access may fetch data. Ensure network access is available, or pre-populate cache directories according to the Outfit core documentation.

If problems persist, open an issue with: Python version, platform, `pip show py-outfit`, and the full install log (add `-vv` to pip commands for verbosity).

## Next steps

Proceed to the API reference or the tutorials (e.g., Initial Orbit Determination) once installation is confirmed.

