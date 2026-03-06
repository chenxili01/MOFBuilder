# Installation

## Clone and install from source

```bash
git clone https://github.com/chenxili01/MofBuilder.git
cd MofBuilder
pip install -e .
```

## Recommended environment setup

```bash
conda create -n mofbuilder python=3.10
conda activate mofbuilder
```

## Optional extras

```bash
pip install -e ".[docs]"
pip install -e ".[dev]"
pip install -e ".[core,md,visualization]"
```

## Build documentation

```bash
cd docs
make html
```

Generated pages are written to `docs/_build/html`.
