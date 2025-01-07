import logging
from typing import Optional

from datasets import Dataset, load_dataset, load_from_disk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_save_huggingface_dataset(
    dataset_name: str, dataset_path: str, return_dataset: bool = False
) -> Optional[Dataset]:
    """
    Load and save a Hugging Face dataset to disk.

    Args:
        dataset_name (str): The name of the dataset to load.
        dataset_path (str): The path to save the dataset to.
        return_dataset (bool): Whether to return the loaded dataset.

    Returns:
        Optional[Dataset]: The loaded dataset if return_dataset is True, None otherwise.
    """
    try:
        logger.info(f"Loading dataset from {dataset_path}")
        dataset = load_from_disk(dataset_path)
        logger.info(f"Successfully loaded dataset from {dataset_path}")
    except FileNotFoundError:
        try:
            logger.info(
                f"Dataset not found at {dataset_path}. Downloading and saving dataset..."
            )
            dataset = load_dataset(dataset_name)
            dataset.save_to_disk(dataset_path)
            logger.info(f"Successfully downloaded and saved dataset to {dataset_path}")
        except Exception as e:
            logger.error(f"Error loading dataset {dataset_name}: {str(e)}")
            raise

    return dataset if return_dataset else None


if __name__ == "__main__":
    try:
        dataset = load_save_huggingface_dataset(
            dataset_name="tyrionhuu/PPTBench-Detection",
            dataset_path="data/PPTBench-Detection",
            return_dataset=True,
        )
        if dataset:
            logger.info(f"Dataset loaded successfully with {len(dataset)} examples")
    except Exception as e:
        logger.error(f"Failed to load dataset: {str(e)}")
