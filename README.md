## pyOutfit

pyOutfit is a small Rust-based Python extension project scaffolded with PyO3 and built using Maturin. The project produces a native Python extension library (`py_outfit`) from Rust sources so you can call Rust code from Python with minimal overhead.

This repository contains the Rust source (in `src/`) and Python packaging metadata (`pyproject.toml`) for building wheels and installing the extension for Python 3.12.

## Quick overview

- Rust crate name: `pyOutfit` (see `Cargo.toml`)
- Python package name: `pyOutfit` (see `pyproject.toml`)
- Native extension module name (import in Python as): `py_outfit`
- Build backend: `maturin` (configured in `pyproject.toml`)
- Supported Python: CPython 3.12 (as specified in `pyproject.toml`)

## Requirements

- Rust toolchain (stable, with Cargo)
- Python 3.12 and development headers
- maturin >= 1.9.4 (used as the build backend)
- A C toolchain (build-essential, clang, or equivalent on Linux)

On Debian/Ubuntu you may need:

```bash
# install system deps (example for Ubuntu/Debian)
sudo apt update
sudo apt install build-essential python3.12-dev libssl-dev pkg-config
```

Install Rust from https://rustup.rs if you don't have it yet.

## Build & install (developer / local use)

The recommended way to build and install the extension into your active Python environment for development is to use `maturin`:

```bash
# install maturin (recommended to use a virtualenv)
python3.12 -m pip install --upgrade pip
python3.12 -m pip install maturin

# build and install into the current venv
maturin develop
```

This command compiles the Rust code and installs the extension in editable/development mode into the active Python environment.

To build distributable wheels:

```bash
# build wheel(s) into the `target/wheels/` directory
maturin build --release

# install from the generated wheel (example)
python3.12 -m pip install target/wheels/pyOutfit-*.whl
```

If you prefer to use `pip` directly (it will call maturin via PEP 517):

```bash
python3.12 -m pip install .
```

## Usage

Import the extension module in Python as `py_outfit` (module name is defined by the Rust `#[pymodule]`):

```python
import py_outfit

# inspect available functions / objects
print(dir(py_outfit))

# call into functions provided by the Rust implementation (see `src/lib.rs` for exported APIs)
# result = py_outfit.some_function(...)
```

Note: This README intentionally doesn't document specific API calls because the Rust module exports may change — check `src/lib.rs` for the current Python-facing functions and their docstrings.

## Development

- Code lives in `src/` (Rust) and is built as a `cdylib` to be imported by Python.
- Python packaging metadata lives in `pyproject.toml`.
- Use `maturin develop` for iterative development.
- Use `maturin build` to produce wheels for distribution.

Recommended quick cycle:

```bash
# after editing Rust code
maturin develop
python3.12 -c "import py_outfit; print('ok', dir(py_outfit))"
```

## Testing

If the project adds Rust unit tests or Python-based tests, run them with the usual tools:

```bash
# Rust unit tests
cargo test

# (optional) Python tests (if present, for example with pytest)
python3.12 -m pip install -r requirements-dev.txt  # if you add one
python3.12 -m pytest
```

## Contributing

Contributions are welcome. Small suggestions:

- Open an issue to discuss larger changes before implementing them.
- Keep Rust and Python APIs stable where practical; document new Python-facing functions in `src/lib.rs`.
- Add unit tests for new behavior (Rust tests under `tests/` or `#[cfg(test)]` modules).

## License

This project is licensed under the CeCILL-C license (see `pyproject.toml` for the license metadata).

## Authors / Maintainer

- FusRoman <roman.le-montagner@ijclab.in2p3.fr>

## Files of interest

- `Cargo.toml` — Rust crate configuration.
- `src/lib.rs` — Rust source that exposes the Python module via PyO3.
- `pyproject.toml` — Python packaging metadata and build-backend configuration.

---

If you'd like, I can add a short example that calls a real exported function (if you point me to one in `src/lib.rs`), or add CI instructions for building wheels automatically.
