# llm.py
import base64
import io
import logging
import os
from typing import Any, Dict, List, Literal, Optional, Union

import ollama
import requests.exceptions
from ollama import Options
from openai import OpenAI
from PIL import Image

logging.getLogger("httpx").setLevel(logging.WARNING)

API_LLM_MODELS = [
    ("api", "claude-3-5-sonnet-20241022"),
    # ("api", "gpt-4o-2024-11-20"),
    # ("api", "o1-2024-12-17"),
    ("api", "gemini-2.0-flash-exp"),
    # ("api", "gemini-2.0-flash-thinking-exp"),
    # ("api", "qwen-vl-max-0809"),
    # ("api", "llama-3.2-90b-vision-instruct"),
    # ("ollama", "llama3.2-vision:11b"),
    # ("ollama", "llava:13b"),
]

# API key and model directory configuration
key = "sk-f1fCP1wFI4K1pQYJORkJF3K9tg1MINok28GAsCsSFIjvajjS"

if key.strip() == "":
    key = input("Please enter your API key: ")


def encode_image(image_path: str) -> str:
    """Encodes an image file to a base64 string.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The base64 encoded string of the image.
    """
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded


def call_vision_model(
    model_name: str = "llama3.2-vision:11b",
    provider: Literal["api", "ollama", "openai", "anthropic"] = "ollama",
    prompt: str = "",
    temperature: float = 0.1,
    max_tokens: int = 3200,
    images: Union[
        str, List[str], bytes, List[bytes], Image.Image, List[Image.Image], None
    ] = None,
    json_mode: bool = False,
    timeout: Optional[int] = None,
) -> Union[str, Dict[str, Any]]:
    """
    Routes the call to the appropriate vision model provider and returns the response.

    Args:
        model_name (str): The name of the model to use.
        provider (Literal): The provider of the vision model.
        prompt (str): The text prompt for the model.
        temperature (float): Sampling temperature for the model.
        max_tokens (int): Maximum number of tokens in the response.
        images (Union[str, List[str], bytes, List[bytes], Image.Image, List[Image.Image], None]):
            Image file paths, bytes, PIL Images, or lists of any of these. If None, runs in text-only mode.
        json_mode (bool): Whether the response should be in JSON format.
        timeout (Optional[int], optional): Timeout for the HTTP request. Defaults to None.

    Returns:
        str: The generated response from the vision model.
    """
    processed_images = []

    if images is not None:
        # Convert single items to list
        if not isinstance(images, list):
            images = [images]

        # Validate and process all images
        for img in images:
            if isinstance(img, str):
                if not os.path.exists(img):
                    raise ValueError(f"Image file not found: {img}")
                processed_images.append(img)
            elif isinstance(img, bytes):
                processed_images.append(img)
            elif isinstance(img, Image.Image):
                # Convert PIL Image to bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format or "PNG")
                processed_images.append(img_byte_arr.getvalue())
            else:
                raise ValueError(
                    f"Invalid image type: {type(img)}. Expected str, bytes, or PIL Image."
                )

    if provider == "ollama":
        return generate_with_image_ollama(
            model_name=model_name,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            images=processed_images,
            json_mode=json_mode,
            timeout=timeout,
        )
    elif provider == "api":
        return generate_with_api(
            model_name=model_name,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            images=processed_images,
            json_mode=json_mode,
            timeout=timeout,
        )
    elif provider == "openai":
        raise NotImplementedError("OpenAI API integration is not implemented yet.")
    elif provider == "anthropic":
        raise NotImplementedError("Anthropic API integration is not implemented yet.")
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def generate_with_image_ollama(
    model_name: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
    images: Optional[List[str | bytes]] = None,
    json_mode: bool = False,
    timeout: int = 30,  # Default 30 seconds
) -> Union[str, Dict[str, Any]]:
    """
    Generates a response using the Ollama model with optional images.

    Args:
        model_name (str): The name of the model to use.
        prompt (str): The text prompt for the model.
        temperature (float): Sampling temperature for the model.
        max_tokens (int): Maximum number of tokens in the response.
        images (Optional[List[str | bytes]]): Paths to image files or image data.
            If None or empty list, runs in text-only mode.
        json_mode (bool): Whether the response should be in JSON format.
        timeout (int): Maximum time to wait for the response.

    Returns:
        str: The generated response from the model.
    """
    try:
        options = Options(
            temperature=temperature,
            num_ctx=max_tokens,
            request_timeout=timeout,
        )

        kwargs = {
            "model": model_name,
            "prompt": prompt,
            "options": options,
            "format": "json" if json_mode else "",
        }

        if images:  # Only include images if list is not None and not empty
            kwargs["images"] = images

        return ollama.generate(**kwargs)["response"]

    except requests.exceptions.Timeout:
        raise TimeoutError(f"Request timed out after {timeout} seconds")
    except Exception as e:
        logging.error(f"Error in generate_with_image_ollama: {str(e)}")
        raise


def generate_with_api(
    model_name: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
    images: Optional[List[str | bytes]] = None,
    json_mode: bool = False,
    timeout: int = 30,  # Default 30 seconds
) -> Union[str, Dict[str, Any]]:
    """
    Generates a response using the API with optional images.

    Args:
        model_name (str): The name of the model to use.
        prompt (str): The text prompt for the model.
        temperature (float): Sampling temperature for the model.
        max_tokens (int): Maximum number of tokens in the response.
        images (Optional[list[str | bytes]]): Paths to image files or image data.
            If None, runs in text-only mode.
        json_mode (bool): Whether the response should be in JSON format.
        timeout (int): Maximum time to wait for the response.

    Returns:
        str: The generated response from the API.
    """
    try:
        # Initialize OpenAI client with timeout
        client = OpenAI(
            base_url="https://api2.aigcbest.top/v1",
            api_key=key,
        )
        messages = generate_api_messages(images=images, prompt=prompt)

        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"} if json_mode else None,
                seed=42,
                timeout=timeout,
            )
            return response.choices[0].message.content
        except requests.exceptions.Timeout:
            raise TimeoutError(f"API request timed out after {timeout} seconds")

    except Exception as e:
        logging.error(f"Error in generate_with_api: {str(e)}")
        raise


def generate_api_messages(
    prompt: str,
    images: Optional[List[str | bytes]] = None,
) -> List[Dict[str, Any]]:
    """
    Prepares the messages payload for the API call with optional images and a prompt.

    Args:
        prompt (str): The text prompt for the model.
        images (Optional[list[str | bytes]]): List of image file paths or bytes objects.
            If None, returns text-only message format.

    Returns:
        list[dict]: A list of messages formatted for the API call.
    """
    if not images:
        return [{"role": "user", "content": prompt}]

    if len(images) == 1:
        base64_image = (
            encode_image(images[0])
            if isinstance(images[0], str)
            else base64.b64encode(images[0]).decode("utf-8")
        )
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ]
    else:
        base64_images = [
            (
                encode_image(img)
                if isinstance(img, str)
                else base64.b64encode(img).decode("utf-8")
            )
            for img in images
        ]
        content = [
            {
                "type": "text",
                "text": prompt,
            }
        ]
        content.extend(
            [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                }
                for base64_image in base64_images
            ]
        )
        messages = [
            {
                "role": "user",
                "content": content,
            }
        ]
    return messages


def main() -> None:
    from ..shared.load_save_dataset import load_save_huggingface_dataset_df
    import json
    dataset_name = "tyrionhuu/PPTBench-Detection"
    dataset_path = "data/PPTBench-Detection"
    df = load_save_huggingface_dataset_df(
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        force_download=False,
    )
    row = df.sample(random_state=20).iloc[0]
    image_data = row["image"]
    image_bytes = image_data["bytes"] if isinstance(image_data, dict) else image_data
    # Reder image bytes
    # with open("image.jpg", "wb") as f:
    #     f.write(image_bytes)
    result = call_vision_model(
        model_name="gemini-2.0-flash-exp",
        provider="api",
        prompt="describe the image",
        temperature=0.7,
        max_tokens=1000,
        images=image_bytes,
        json_mode=True,
        timeout=30,
    )
    print(result)
    result_json = json.loads(result)
    print(result_json)

if __name__ == "__main__":
    main()
