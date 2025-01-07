from src.shared.load_save_huggingface_dataset import load_save_huggingface_dataset_df


def main():
    dataset_name = "tyrionhuu/PPTBench-Detection"
    dataset_path = "data/PPTBench-Detection"
    df = load_save_huggingface_dataset_df(
        dataset_name=dataset_name,
        dataset_path=dataset_path,
    )
    print(df.head())


if __name__ == "__main__":
    main()
