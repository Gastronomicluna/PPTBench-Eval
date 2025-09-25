from pathlib import Path


def get_project_root() -> Path:
    """Get the absolute path to the project root directory.

    Returns:
        Path: Absolute path to the project root directory.
    """
    current_file = Path(__file__).resolve()
    return current_file.parent.parent.parent


project_root = get_project_root()
model_name = "Gpt4o.mini"


results_dir = project_root / "data" / "detection_results"
prefix_path = f"{model_name.replace('.', '-')}-text.csv"


csv_path=results_dir / prefix_path

print(csv_path)