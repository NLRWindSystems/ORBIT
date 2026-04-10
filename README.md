# ORBIT

Offshore Renewables Balance of system and Installation Tool

[![PyPI version](https://badge.fury.io/py/orbit-nrel.svg)](https://badge.fury.io/py/orbit-nrel)
[![PyPI downloads](https://img.shields.io/pypi/dm/orbit-nrel?link=https%3A%2F%2Fpypi.org%2Fproject%2Forbit-nrel%2F)](https://pypi.org/project/orbit-nrel/)
[![Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![image](https://img.shields.io/pypi/pyversions/orbit-nrel.svg)](https://pypi.python.org/pypi/orbit-nrel)

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/NLRWindSystems/ORBIT/dev?filepath=examples)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Authors

- [Jake Nunemaker](https://www.linkedin.com/in/jake-nunemaker/)
- [Matt Shields](https://www.linkedin.com/in/matt-shields-834a6b66/)
- [Rob Hammond](https://www.linkedin.com/in/rob-hammond-33583756/)
- [Nick Riccobono](https://www.linkedin.com/in/nicholas-riccobono-674a3b43/)

### Curent Maintainers

- Rob Hammond

Rob Hammond

## Documentation

Please visit the documentation site at https://nlrwindsystems.github.io/ORBIT/

## Installation

`pip install orbit-nrel`.

### Environment Setup

It is highly recommended to use separate Python environments for all projects, as such we recommend
using Anaconda or Miniconda for a lightweight version of Anaconda. Please visit their
documentation for installation details. This guide will assume the use of Miniconda throughout.

1. Download the latest version of [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
2. Create a new environment. Below, we're using the name `orbit` for the environment, but
   any name is allowed, just replace "orbit" with whichever name was used throughout the
   installation instructions. Similarly, any compatible Python version is allowed even though we
   specify 3.13 below.

   ```bash
   conda create -n orbit python=3.13
   ```

3. Activate the environment.

   ```bash
   conda activate orbit
   ```

   To deactivate an environment, simply use `conda deactivate`.

4. Install ORBIT. See the pip installation directions above, or either of the source
   or development sections below for further details.

### Running Examples

For users wishing to run the examples provided as Jupyter Notebooks, please either install
the Jupyter Lab (preferred) or Jupyter Notebook library.

```bash
pip install jupyterlab
```

### Source Installation

For users looking to modify ORBIT or build their own models to incorporte, installing
from the source code is required.

1. Open a terminal/Anaconda Prompt session and navigate to your desired folder location

   ```bash
   cd /path/to/desired/folder
   ```

2. Clone the repository (or your fork). If cloning your own fork, replace "NLRWindSystems"
   with your GitHub username.

   ```bash
   git clone https://github.com/NLRWindSystems/ORBIT.git
   ```

3. Enter the repository.

   ```bash
   cd ORBIT
   ```

4. Install ORBIT.

   ```bash
   pip install .
   ```

   For an editable installation that updates the installed version of ORBIT with any local changes,
   use the `-e` flag.

   ```bash
   pip install -e .
   ```

### Development Setup

For more advanced users, such as those interested in building the documentation localling, running
tests, or even contributing code back to the library, please use the following instructions.

1. Open a terminal/Anaconda Prompt session and navigate to your desired folder location

   ```bash
   cd /path/to/desired/folder
   ```

2. If you are going to contribute code back to the library, fork the repository as you will not
   be able to push your code changes to the library otherwise.

3. Clone the repository (or your fork). If cloning your own fork, replace "NLRWindSystems"
   with your GitHub username.

   ```bash
   git clone https://github.com/NLRWindSystems/ORBIT.git
   ```

4. Enter the repository.

   ```bash
   cd ORBIT
   ```

5. Install an editable version of ORBIT.

   ```bash
   pip install -3 .
   ```

   For developers install the developer dependences in addition:

   ```bash
   pip install -e .[dev,docs]
   ```

   - `dev`: automated code linting and formatting tools, plus the testing suite.
   - `docs`: documentation building tools

6. If contributing code back to the library, install the pre-commit hook to enable automated
   formatting and linting. If this step is skipped, your PR will fail in the CI pipeline, and code
   will not be reviewed until at least this step passes.

   ```bash
   pre-commit install
   ```
