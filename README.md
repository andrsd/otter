# OTTER

[![build](https://github.com/andrsd/otter/actions/workflows/build.yml/badge.svg)](https://github.com/andrsd/otter/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/andrsd/otter/branch/main/graph/badge.svg?token=LT22M7D5AV)](https://codecov.io/gh/andrsd/otter)
[![Documentation Status](https://readthedocs.org/projects/otter-gui/badge/?version=latest)](https://otter-gui.readthedocs.io/en/latest/?badge=latest)


## Installation using conda environment

Create a new conda environment:

```
conda create -n otter
conda activate otter
```

Be sure you have `libpng` and `freetype` installed:

```
conda install libpng freetype
```

Install `otter`:

```
cd /path/to/otter
pip install -e .
```

Run:

```
python -m otter
```

To run a standalone plugin:

```
cd otter/plugins
python -m plugin_name
```
