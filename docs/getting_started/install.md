(installation)=
# Installing ORBIT

```console
pip install orbit-nrel
```

## Development Setup

The steps below are for more advanced users that would like to modify and
and contribute to ORBIT.

A couple of notes before you get started:

- It is assumed that you will be using the terminal on MacOS/Linux or the
  Anaconda Prompt on Windows. The instructions refer to both as the
  "terminal", and unless otherwise noted the commands will be the same.
- To verify git is installed, run `git --version` in the terminal. If an error
  occurs, install git using these [directions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

### Instructions

1. Download the latest version of [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
   for the appropriate OS. Follow the remaining [steps](https://conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation)
   for the appropriate OS version.

2. From the terminal, install pip by running: `conda install -c anaconda pip`

3. Next, create a new environment for the project with the following. Change "orbit" to whatever
   name you would like to give your environment, and "3.13" to whichever compatible version of
   Python you prefer.

   ```console
   conda create -n orbit python=3.13 -y
   ```

   To activate/deactivate the environment, use the following commands.

   ```console
   conda activate orbit
   conda deactivate orbit
   ```

4. Clone the repository:

   ```bash
   git clone https://github.com/NLRWindSystems/ORBIT.git
   ```

5. Navigate to the top level of the repository (`<path-to-ORBIT>/ORBIT/`) and install ORBIT as an
   editable package with following command.

   ```console
   # Note the "." at the end
   pip install -e .

   # OR if you are you going to be contributing to the code or building documentation
   pip install -e '.[dev]'
   ```

6. (Development only) Install the pre-commit hooks to autoformat and lint code.

   ```console
   pre-commit install
   ```
