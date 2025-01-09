from pathlib import Path
import numpy as np
import pandas as pd
from thefuzz import fuzz


def create_ascii_histogram(data: list[float], bins: int = 20, width: int = 50) -> str:
    """
    Create an ASCII histogram representation of the data.

    Args:
        data: List of values to create histogram from
        bins: Number of bins in histogram
        width: Width of the histogram in characters

    Returns:
        String containing the ASCII histogram
    """
    hist, bin_edges = np.histogram(data, bins=bins)
    max_count = max(hist)
    
    result = []
    for count, edge in zip(hist, bin_edges[:-1]):
        bar_length = int(count / max_count * width)
        result.append(f"{edge:3.0f}-{edge + (bin_edges[1]-bin_edges[0]):3.0f} |" + 
                     "█" * bar_length + f" ({count})")
    return "\n".join(result)


def analyze_fuzzy_match_distribution(
    result_csv_path: Path,
) -> None:
    """
    Analyze the distribution of fuzzy match scores from a CSV file and print the results.

    Args:
        result_csv_path (Path): Path to the CSV file containing the results.

    Returns:
        None
    """
    # Load the results from the CSV file
    results_df = pd.read_csv(result_csv_path)

    # Calculate fuzzy match scores
    scores = []
    for gt, pred in zip(results_df["ground_truth"], results_df["llm_answer"]):
        score = fuzz.ratio(str(gt).lower(), str(pred).lower())
        scores.append(score)

    # Calculate statistics
    mean_score = np.mean(scores)
    median_score = np.median(scores)
    std_score = np.std(scores)

    # Print histogram and statistics
    print("\nDistribution of Fuzzy Match Scores:")
    print("-" * 60)
    print(create_ascii_histogram(scores))
    print("-" * 60)
    print(f"\nStatistics:")
    print(f"Mean: {mean_score:.2f}%")
    print(f"Median: {median_score:.2f}%")
    print(f"Std: {std_score:.2f}%")


def main() -> None:
    result_csv_path = Path("data/detection_results.csv")
    analyze_fuzzy_match_distribution(result_csv_path)
    
if __name__ == "__main__":
    main()