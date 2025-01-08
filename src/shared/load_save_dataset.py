import logging
from typing import Optional

import pandas as pd
from datasets import Dataset, load_dataset, load_from_disk
from modelscope import MsDataset
from modelscope.utils.constant import DownloadMode
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_save_huggingface_dataset(
    dataset_name: str, dataset_path: str, force_download: bool = False
) -> Optional[Dataset]:
    """
    Load and save a Hugging Face dataset to disk.

    Args:
        dataset_name (str): The name of the dataset to load.
        dataset_path (str): The path to save the dataset to.
        force_download (bool): If True, download and replace existing dataset.

    Returns:
        Optional[Dataset]: The loaded dataset if successful, None otherwise.
    """
    if force_download:
        try:
            logger.info(f"Force downloading dataset {dataset_name}")
            dataset = load_dataset(dataset_name)
            dataset.save_to_disk(dataset_path)
            logger.info(f"Successfully downloaded and saved dataset to {dataset_path}")
        except Exception as e:
            logger.error(f"Error downloading dataset {dataset_name}: {str(e)}")
            raise
    else:
        try:
            logger.info(f"Loading dataset from {dataset_path}")
            dataset = load_from_disk(dataset_path)
            logger.info(f"Successfully loaded dataset from {dataset_path}")
        except FileNotFoundError:
            try:
                logger.info(f"Dataset not found. Downloading {dataset_name}")
                dataset = load_dataset(dataset_name)
                dataset.save_to_disk(dataset_path)
                logger.info(
                    f"Successfully downloaded and saved dataset to {dataset_path}"
                )
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
    force_download: bool = False,
) -> Optional[pd.DataFrame]:
    """
    Load and save a Hugging Face dataset to disk as a pandas DataFrame.

    Args:
        dataset_name (str): The name of the dataset to load.
        dataset_path (str): The path to save the dataset to.
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
    dataset_name: str, 
    dataset_path: str, 
    force_download: bool = False
) -> Optional[Dataset]:
    """
    Load and save a ModelScope dataset to disk.

    Args:
        dataset_name (str): The name of the dataset to load.
        dataset_path (str): The path to save the dataset to.
        force_download (bool): If True, download and replace existing dataset.

    Returns:
        Optional[Dataset]: The loaded dataset if successful, None otherwise.
    """
    try:
        download_mode = (
            DownloadMode.FORCE_REDOWNLOAD if force_download 
            else DownloadMode.REUSE_DATASET_IF_EXISTS
        )
        logger.info(
            f"Loading dataset {dataset_name} with download_mode={download_mode}"
        )
        dataset = MsDataset.load(
            dataset_name,
            subset_name="train",
            download_mode=download_mode,
            cache_dir=dataset_path,
        )
        logger.info(f"Successfully loaded dataset from {dataset_path}")
        
        if dataset is not None:
            return dataset
    except Exception as e:
        logger.error(f"Error loading dataset {dataset_name}: {str(e)}")
        raise
    
    return None

if __name__ == "__main__":
    df = load_save_huggingface_dataset_df(
        dataset_name="tyrionhuu/PPTBench-Detection",
        dataset_path="data/PPTBench-Detection",
        force_download=False,  # Change to True to force download
    )
    print(df.columns)
