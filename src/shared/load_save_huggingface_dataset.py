import logging
from typing import Optional

import pandas as pd
from datasets import Dataset, load_dataset, load_from_disk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_save_huggingface_dataset(
    dataset_name: str, dataset_path: str
) -> Optional[Dataset]:
    """
    Load and save a Hugging Face dataset to disk.

    Args:
        dataset_name (str): The name of the dataset to load.
        dataset_path (str): The path to save the dataset to.

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

    if dataset is not None:
        try:
            return dataset["train"]
        except KeyError:
            return dataset
    return None


def load_save_huggingface_dataset_df(
    dataset_name: str,
    dataset_path: str,
) -> Optional[pd.DataFrame]:
    """
    Load and save a Hugging Face dataset to disk as a pandas DataFrame.

    Args:
        dataset_name (str): The name of the dataset to load.
        dataset_path (str): The path to save the dataset to.

    Returns:
        Optional[pd.DataFrame]: The loaded dataset as a pandas DataFrame if return_dataset is True, 
        None otherwise.
    """
    try:
        dataset = load_save_huggingface_dataset(
            dataset_name=dataset_name, dataset_path=dataset_path
        )
        if dataset:
            df = dataset.to_pandas()
            logger.info(f"Dataset converted to DataFrame with shape {df.shape}")
            return df
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        raise
    return None


if __name__ == "__main__":
    load_save_huggingface_dataset_df(
        dataset_name="tyrionhuu/PPTBench-Detection",
        dataset_path="data/PPTBench-Detection",
    )
