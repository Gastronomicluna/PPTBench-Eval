from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from thefuzz import fuzz


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

    # Create histogram
    plt.figure(figsize=(10, 6))
    plt.hist(scores, bins=20, edgecolor="black")
    plt.title("Distribution of Fuzzy Match Scores")
    plt.xlabel("Match Score (%)")
    plt.ylabel("Frequency")

    # Add statistics to plot
    stats_text = (
        f"Mean: {mean_score:.2f}%\nMedian: {median_score:.2f}%\nStd: {std_score:.2f}%"
    )
    plt.text(
        0.02,
        0.98,
        stats_text,
        transform=plt.gca().transAxes,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    # Save plot
    output_path = result_csv_path.parent / "fuzzy_match_distribution.png"
    plt.savefig(output_path)
    plt.close()

    print(f"Analysis complete. Plot saved to {output_path}")
    print(f"\nStatistics:\n{stats_text}")
