from src.shared.llm import call_vision_model, generate_api_messages
import logging
from .prompts import build_prompt
import dask.dataframe as dd
import pandas as pd
from typing import Any, Dict, List
def get_answers(
    df: dd.DataFrame,
) -> pd.DataFrame:
    """
    Get answers to the questions in the DataFrame.

    Args:
        df (dd.DataFrame): The DataFrame containing the questions.

    Returns:
        pd.DataFrame: The DataFrame with the answers.
    """
    result_df = pd.DataFrame()
    if "hash" not in df.columns:
        raise ValueError("The input DataFrame must contain a 'hash' column.")
    
    result_data = []
    
    # Convert Dask DataFrame to Pandas for iteration
    pandas_df = df.compute()
    
    for _, row in pandas_df.iterrows():
        get_answer_single(row, result_data)
    
    result_df = pd.DataFrame(result_data)
    return result_df

def get_answer_single(row: pd.Series, result_data: List[Dict[str, Any]]) -> None:
    """
    Get the answer to a single question and append it to the result data.

    Args:
        row (pd.Series): The row containing the question data.
        result_data (list[dict]): The list to append the result data to.
    """
    try:
        query = row["query"]
        slide_json = row["slide_json"]
        prompt = build_prompt(query, slide_json)
        image_paths = [row["image_path"]]
        messages = generate_api_messages(image_paths, prompt)
        response = call_vision_model(messages)
        result_data.append(
            {
                "hash": row["hash"],
                "query": query,
                "slide_json": slide_json,
                "response": response,
            }
        )
    except Exception as e:
        logging.error(f"Error in get_answer_single: {str(e)}")
        result_data.append(
            {
                "hash": row["hash"],
                "query": query,
                "slide_json": slide_json,
                "response": str(e),
            }
        )
        return