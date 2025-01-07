# PPTLayout

This is a repository for PPTLayout

## Prerequisites

This project uses [Poetry](https://python-poetry.org/) for dependency management. You can install it following the instructions [here](https://python-poetry.org/docs/#installation).

Python 3.11 is required to run this project to avoid compatibility issues.

As for the virtual environment, you can use any tool you like.

It is not necessary but totally fine to use [Conda](https://docs.conda.io/en/latest/) to manage the Python environment. You can install it following the instructions [here](https://docs.conda.io/en/latest/miniconda.html).

## Steps

1. Clone this repository

    ``` shell
    git clone git@github.com:tyrionhuu/PPTLayout.git
    cd PPTLayout
    ```

2. Create virtual environment

   1. **conda**
   
    ``` shell
    conda create -n pptlayout python=3.11
    conda activate pptlayout
    ```
   
   2. **poetry**
   
    ``` shell
    poetry env use python3.11
    poetry shell
    ```
   
3. Install the dependencies with Poetry

    ``` shell
    poetry install
    ```

    Then Poetry should already activate the virtual environment for you. If not, you can activate it manually.

4. Install the pre-commit hooks

    ``` shell
    pre-commit install
    ```
