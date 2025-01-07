import logging
from typing import Optional, Tuple
import os
import json
from datetime import datetime

import pandas as pd
from datasets import Dataset, load_dataset, load_from_disk
from huggingface_hub import HfApi

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_dataset_info(dataset_name: str) -> Tuple[str, datetime]:
    """Get dataset version and last modified date from Hugging Face Hub.

    Args:
        dataset_name (str): The name of the dataset.

    Returns:
        Tuple[str, datetime]: The SHA of the dataset and the last modified date.
    """
    try:
        api = HfApi()
        dataset_info = api.dataset_info(dataset_name)
        return dataset_info.sha, dataset_info.lastModified
    except Exception as e:
        logger.error(f"Failed to get dataset info: {str(e)}")
        return None, None


def is_dataset_current(dataset_path: str, dataset_name: str) -> bool:
    """Check if local dataset is up to date with Hugging Face version.

    Args:
        dataset_path (str): The path to the local dataset.
        dataset_name (str): The name of the dataset.

    Returns:
        bool: True if the local dataset is up to date, False otherwise.
    """
    metadata_path = os.path.join(dataset_path, "dataset_metadata.json")

    if not os.path.exists(metadata_path):
        return False

    try:
        with open(metadata_path, 'r') as f:
            local_metadata = json.load(f)

        remote_sha, remote_modified = get_dataset_info(dataset_name)
        if not remote_sha:
            return True  # If we can't check, assume current version is okay

        return local_metadata.get('sha') == remote_sha
    except Exception as e:
        logger.error(f"Error checking dataset version: {str(e)}")
        return False


def load_save_huggingface_dataset(
    dataset_name: str, dataset_path: str, force_update: bool = False
) -> Optional[Dataset]:
    """
    Load and save a Hugging Face dataset to disk, checking for updates.

    Args:
        dataset_name (str): The name of the dataset to load.
        dataset_path (str): The path to save the dataset to.
        force_update (bool): Force update regardless of version.

    Returns:
        Optional[Dataset]: The loaded dataset if successful, None otherwise.
    """
    should_download = force_update or not os.path.exists(dataset_path)

    if not should_download:
        should_download = not is_dataset_current(dataset_path, dataset_name)
        if should_download:
            logger.info("New version available, updating dataset...")

    try:
        if should_download:
            dataset = load_dataset(dataset_name)
            dataset.save_to_disk(dataset_path)

            # Save metadata
            sha, modified = get_dataset_info(dataset_name)
            metadata = {
                'sha': sha,
                'last_modified': modified.isoformat() if modified else None,
                'download_date': datetime.now().isoformat()
            }
            with open(os.path.join(dataset_path, "dataset_metadata.json"), 'w') as f:
                json.dump(metadata, f)

            logger.info(f"Successfully downloaded and saved dataset to {dataset_path}")
        else:
            dataset = load_from_disk(dataset_path)
            logger.info(f"Using cached dataset from {dataset_path}")

        return dataset
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        raise


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
        Optional[pd.DataFrame]: The loaded dataset as a pandas DataFrame if 
        successful, None otherwise.
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
