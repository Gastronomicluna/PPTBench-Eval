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
        result.append(
            f"{edge:3.0f}-{edge + (bin_edges[1]-bin_edges[0]):3.0f} |"
            + "█" * bar_length
            + f" ({count})"
        )
    return "\n".join(result)


def create_detailed_histogram(
    data: list[float],
    start: float = 95,
    end: float = 100,
    bins: int = 10,
    width: int = 50,
) -> str:
    """
    Create a detailed ASCII histogram for a specific range of scores.

    Args:
        data: List of values to create histogram from
        start: Start of the range to focus on
        end: End of the range to focus on
        bins: Number of bins in histogram
        width: Width of the histogram in characters

    Returns:
        String containing the ASCII histogram
    """
    filtered_data = [x for x in data if start <= x <= end]
    if not filtered_data:
        return "No data points in this range"

    hist, bin_edges = np.histogram(filtered_data, bins=bins, range=(start, end))
    max_count = max(hist)

    result = []
    for count, edge in zip(hist, bin_edges[:-1]):
        bar_length = int(count / max_count * width)
        result.append(
            f"{edge:6.2f}-{edge + (bin_edges[1]-bin_edges[0]):6.2f} |"
            + "█" * bar_length
            + f" ({count})"
        )
    return "\n".join(result)


def analyze_fuzzy_match_distribution(
    result_csv_path: Path,
) -> None:
    """
    Analyze the distribution of fuzzy match scores from a CSV file and print the results.
    Saves the scores back to the same CSV file.

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

    # Add scores to DataFrame
    results_df["fuzzy_match_score"] = scores

    # Save updated DataFrame back to CSV
    results_df.to_csv(result_csv_path, index=False)
    print(f"\nFuzzy match scores saved to {result_csv_path}")

    # Calculate statistics
    mean_score = np.mean(scores)
    median_score = np.median(scores)
    std_score = np.std(scores)

    # Print overall histogram and statistics
    print("\nOverall Distribution of Fuzzy Match Scores:")
    print("-" * 60)
    print(create_ascii_histogram(scores))
    print("-" * 60)

    # Print detailed histogram for high similarity scores
    print("\nDetailed Distribution (95-100% range):")
    print("-" * 60)
    print(create_detailed_histogram(scores))
    print("-" * 60)

    high_scores = len([s for s in scores if s >= 95])
    print(f"Number of scores ≥ 95%: {high_scores} ({high_scores/len(scores)*100:.2f}%)")

    print(f"\nStatistics:")
    print(f"Mean: {mean_score:.2f}%")
    print(f"Median: {median_score:.2f}%")
    print(f"Std: {std_score:.2f}%")


def main() -> None:
    result_csv_path = Path("data/detection_results.csv")
    analyze_fuzzy_match_distribution(result_csv_path)


if __name__ == "__main__":
    main()
