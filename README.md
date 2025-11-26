# PPTBench Evaluation

PPTBench is a benchmark for evaluating how Large Language Models (LLMs) perform on PowerPoint-related tasks. The suite currently covers four pipelines—detection, generation, modification, and understanding—with shared utilities for dataset loading, prompting, answer formatting, and evaluation.

## Features
- **Task coverage:** Dedicated entry points for detection, generation, modification, and understanding benchmarks in the `src/` tree.
- **Shared utilities:** Common components for LLM access, dataset caching, answer formatting, and scoring to keep task code consistent.
- **Dataset caching:** Built-in helpers download/cached benchmark data locally and verify versions when pulling from Hugging Face Hub.
- **Parallel execution:** Task runners support configurable worker pools for faster multi-model evaluation.

## Repository structure
- `src/shared/`: Core utilities for dataset loading/saving, answer parsing, formatting (CSV/API), generic evaluation, and LLM client helpers.
- `src/detection/`: Pipelines, prompts, and evaluators for PPT content detection tasks.
- `src/generation/`: Prompts, answer generation scripts, and PPTX export helpers for slide synthesis tasks.
- `src/modification/`: Utilities and evaluators for editing existing PPT content with model-generated updates.
- `src/understanding/`: Workflows and judges for comprehension-style tasks over PPT content.
- `notebooks/`: Exploratory notebooks and experiments.
- `tests/`: Automated checks covering shared utilities and task flows.

## Requirements
1. Python 3.11.
2. [Poetry](https://python-poetry.org/docs/#installation) for dependency management.
3. Install dependencies:

   ```bash
   poetry install
   ```

   If `poetry install` hangs, see [this issue](https://github.com/python-poetry/poetry/issues/8623). If you have limited internet access, consider using [HF-Mirror](https://hf-mirror.com).

## Datasets and assets
- Benchmark datasets are fetched automatically via the task entry points and cached under the `data/` directory (for example, detection uses `tyrionhuu/PPTBench-Detection` and saves to `data/PPTBench-Detection`).
- Generation tasks rely on an image asset pack that will be provided via a forthcoming Hugging Face link. After downloading the archive, extract it to `data/dataset/` so that the images live under `data/dataset/extracted_images/` (matching the project tree shown above). Keep the link in this section for quick reference once it is available.

## Running tasks
All task runners live under `src/<task>/main.py` and accept common arguments for worker counts, model selection, and test-mode sampling. Examples below assume execution from the project root with Poetry:

```bash
# Run detection with default settings
poetry run python -m src.detection.main

# Run generation to produce PPTX files
poetry run python -m src.generation.main

# Enable test mode to sample a small subset
poetry run python -m src.detection.main --test_mode True
```

Results, logs, and cached datasets are written to the `data/` and `log/` directories created automatically at runtime. Adjust model lists and API credentials via `src/shared/llm.py` and related prompt files as needed.

## Development
- Format and lint with Black, isort, and Flake8 (configured in `pyproject.toml`).
- Run tests with pytest:

  ```bash
  poetry run pytest
  ```

Contributions should keep shared utilities consistent across tasks to simplify maintenance.
