import logging
from typing import Literal, Optional

import pandas as pd
from huggingface_hub import HfApi
from modelscope import MsDataset
from modelscope.utils.constant import DownloadMode

from datasets import Dataset, load_dataset, load_from_disk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _check_dataset_version(dataset_name: str, dataset_path: str) -> bool:
    """
    Check if the locally saved dataset is the newest version.

    Args:
        dataset_name (str): The name of the dataset on Hugging Face Hub.
        dataset_path (str): Local path where dataset is saved.

    Returns:
        bool: True if local version is latest, False if update needed.
    """
    try:
        api = HfApi()
        # Get latest commit hash from Hub
        remote_info = api.dataset_info(dataset_name)
        remote_sha = remote_info.sha

        # Get local version info (stored in dataset_info.json)
        try:
            dataset = load_from_disk(dataset_path)
            local_info = dataset.info.download_checksums
            if not local_info or remote_sha not in str(local_info):
                return False
            return True
        except Exception:
            return False

    except Exception as e:
        logger.warning(f"Failed to check dataset version: {str(e)}")
        return True  # On error, assume local version is OK


def load_save_huggingface_dataset(
    dataset_name: str, dataset_path: Optional[str] = None, force_download: bool = False
) -> Optional[Dataset]:
    """
    Load and save a Hugging Face dataset to disk.

    Args:
        dataset_name (str): The name of the dataset to load.
        dataset_path (Optional[str]): The path to save the dataset to. If None,
            dataset will only be loaded without saving.
        force_download (bool): If True, download and replace existing dataset.

    Returns:
        Optional[Dataset]: The loaded dataset if successful, None otherwise.
    """
    if dataset_path is None:
        try:
            logger.info(f"Loading dataset {dataset_name} without saving")
            dataset = load_dataset(dataset_name)
        except Exception as e:
            logger.error(f"Error downloading dataset {dataset_name}: {str(e)}")
            raise
    else:
        try:
            if force_download:
                logger.info(f"Force downloading dataset {dataset_name}")
                dataset = load_dataset(dataset_name)
                dataset.save_to_disk(dataset_path)
                logger.info(f"Successfully saved dataset to {dataset_path}")
            else:
                try:
                    # First check if local version exists and is up to date
                    is_latest = _check_dataset_version(dataset_name, dataset_path)
                    if is_latest:
                        logger.info(f"Loading latest version from {dataset_path}")
                        dataset = load_from_disk(dataset_path)
                    else:
                        logger.info(
                            f"Local dataset outdated or missing. Downloading {dataset_name}"
                        )
                        dataset = load_dataset(dataset_name)
                        dataset.save_to_disk(dataset_path)
                        logger.info(f"Successfully saved dataset to {dataset_path}")
                except FileNotFoundError:
                    logger.info(f"Dataset not found. Downloading {dataset_name}")
                    dataset = load_dataset(dataset_name)
                    dataset.save_to_disk(dataset_path)
                    logger.info(
                        f"Successfully downloaded and saved dataset to {dataset_path}"
                    )
        except Exception as e:
            logger.error(f"Error handling dataset {dataset_name}: {str(e)}")
            raise

    if dataset is not None:
        try:
            return dataset["train"]
        except KeyError:
            return dataset
    return None


def load_save_huggingface_dataset_df(
    dataset_name: str,
    dataset_path: Optional[str] = None,
    force_download: bool = False,
) -> Optional[pd.DataFrame]:
    """
    Load and save a Hugging Face dataset to disk as a pandas DataFrame.

    Args:
        dataset_name (str): The name of the dataset to load.
        dataset_path (Optional[str]): The path to save the dataset to. If None,
            dataset will only be loaded without saving.
        force_download (bool): If True, download and replace existing dataset.

    Returns:
        Optional[pd.DataFrame]: The loaded dataset as a pandas DataFrame if successful,
        None otherwise.
    """
    try:
        dataset = load_save_huggingface_dataset(
            dataset_name=dataset_name,
            dataset_path=dataset_path,
            force_download=force_download,
        )
        if dataset:
            df = dataset.to_pandas()
            logger.info(f"Dataset converted to DataFrame with shape {df.shape}")
            return df
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        raise
    return None


def load_save_modelscope_dataset(
    dataset_name: str, dataset_path: Optional[str] = None, force_download: bool = False
) -> Optional[Dataset]:
    """
    Load and save a ModelScope dataset to disk.

    Args:
        dataset_name (str): The name of the dataset to load.
        dataset_path (Optional[str]): The path to save the dataset to. If None,
            dataset will be loaded using default cache directory.
        force_download (bool): If True, download and replace existing dataset.

    Returns:
        Optional[Dataset]: The loaded dataset if successful, None otherwise.
    """
    try:
        download_mode = (
            DownloadMode.FORCE_REDOWNLOAD
            if force_download
            else DownloadMode.REUSE_DATASET_IF_EXISTS
        )
        logger.info(
            f"Loading dataset {dataset_name} with download_mode={download_mode}"
        )
        dataset = MsDataset.load(
            dataset_name,
            subset_name="default",
            download_mode=download_mode,
            cache_dir=dataset_path if dataset_path else None,
        )
        logger.info("Successfully loaded dataset")
        return dataset["train"]
    except Exception as e:
        logger.error(f"Error loading dataset {dataset_name}: {str(e)}")
        raise


def load_save_modelscope_dataset_df(
    dataset_name: str,
    dataset_path: Optional[str] = None,
    force_download: bool = False,
) -> Optional[pd.DataFrame]:
    """
    Load and save a ModelScope dataset to disk as a pandas DataFrame.

    Args:
        dataset_name (str): The name of the dataset to load.
        dataset_path (Optional[str]): The path to save the dataset to. If None,
            dataset will be loaded using default cache directory.
        force_download (bool): If True, download and replace existing dataset.

    Returns:
        Optional[pd.DataFrame]: The loaded dataset as a pandas DataFrame if successful,
        None otherwise.
    """
    try:
        dataset = load_save_modelscope_dataset(
            dataset_name=dataset_name,
            dataset_path=dataset_path,
            force_download=force_download,
        )
        if dataset:
            df = pd.DataFrame(dataset)
            logger.info(f"Dataset converted to DataFrame with shape {df.shape}")
            return df
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        raise
    return None


def load_save_dataset_df(
    dataset_name: str,
    dataset_path: Optional[str] = None,
    force_download: bool = False,
    source: Literal["modelscope", "huggingface"] = "huggingface",
) -> Optional[pd.DataFrame]:
    """
    Load and save a dataset to disk as a pandas DataFrame.
    Args:
        dataset_name (str): The name of the dataset to load.
        dataset_path (Optional[str]): The path to save the dataset to. If None,
            dataset will only be loaded without saving.
        force_download (bool): If True, download and replace existing dataset.
        source (str): The source of the dataset ("huggingface" or "modelscope").

    Returns:
        Optional[pd.DataFrame]: The loaded dataset as a pandas DataFrame if successful,
        None otherwise.
    """
    if source == "huggingface":
        return load_save_huggingface_dataset_df(
            dataset_name=dataset_name,
            dataset_path=dataset_path,
            force_download=force_download,
        )
    elif source == "modelscope":
        return load_save_modelscope_dataset_df(
            dataset_name=dataset_name,
            dataset_path=dataset_path,
            force_download=force_download,
        )
    else:
        raise ValueError(f"Unsupported source: {source}")


def main() -> None:
    df = load_save_dataset_df(
        dataset_name="tyrionhuu/PPTBench-Modification",
        dataset_path="data/PPTBench-Modification",
        force_download=True,
        source="huggingface",
    )
    print(df.columns)


if __name__ == "__main__":
    main()
