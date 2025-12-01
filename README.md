# PPTBench Evaluation

PPTBench is a benchmark for evaluating how Large Language Models (LLMs) perform on PowerPoint-related tasks. The suite currently covers four pipelines—detection, generation, modification, and understanding—with shared utilities for dataset loading, prompting, answer formatting, and evaluation.

## Features
- **Comprehensive task coverage:** Dedicated entry points for detection, generation, modification, and understanding benchmarks in the `src/` tree.
- **Shared utilities:** Common components for LLM access, dataset caching, answer formatting, and scoring to keep task code consistent.
- **Dataset caching:** Built-in helpers download/cached benchmark data locally and verify versions when pulling from Hugging Face Hub.
- **Parallel execution:** Task runners support configurable worker pools for faster multi-model evaluation.

## 🌐 Dataset Access (Hugging Face Collection)

All benchmark datasets used in PPTBench are publicly available on Hugging Face:

👉 **Hugging Face Collection:**  
**https://hf.co/collections/tyrionhuu/pptbench**

This collection hosts:
- PPTBench-Detection  
- PPTBench-Understanding  
- PPTBench-Modification  
- PPTBench-Generation  

Each task module automatically downloads/caches its required subset from this collection under the `data/` directory.

## Repository structure
- `src/shared/`: Core utilities for dataset loading/saving, answer parsing, formatting (CSV/API), generic evaluation, and LLM client helpers.
- `src/detection/`: Pipelines, prompts, and evaluators for PPT content detection tasks.
- `src/generation/`: Prompts, answer generation scripts, and PPTX export helpers for slide synthesis tasks.
- `src/modification/`: Utilities and evaluators for editing existing PPT content with model-generated updates.
- `src/understanding/`: Workflows and judges for comprehension-style tasks over PPT content.
- `dataset/`: Image assets used for generation tasks.
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
4. Download the required [image assets](https://pan.ustc.edu.cn/share/index/c5da64e74bf545829dcb) and put into the project root, which will create: `dataset/extracted_images/`.

## Datasets and assets
- Benchmark datasets are automatically fetched through the task entry points and cached under the `data/` directory (e.g., detection is stored in `data/PPTBench-Detection`).
- Generation tasks require an additional [image asset pack](https://pan.ustc.edu.cn/share/index/c5da64e74bf545829dcb). After downloading, ensure all images are located under: `dataset/extracted_images/` (matching the project tree shown above).

## Running tasks
All task runners live under `src/<task>/main.py` and accept common arguments for worker counts, model selection, and test-mode sampling. The example below assumes execution from the project root with Poetry:

```bash
# Enter the Poetry virtual environment
poetry shell

# Run the detection task
python -m src.detection.main
```

Results, logs, and cached datasets are written to the `data/` and `log/` directories created automatically at runtime. Adjust model lists and API credentials via `src/shared/llm.py` and related prompt files as needed.
