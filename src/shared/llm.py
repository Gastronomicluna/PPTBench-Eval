# llm.py
import base64
import logging
import os
from typing import Any, Dict, List, Literal, Optional

import ollama
import requests.exceptions
from ollama import Options
from openai import OpenAI

# API key and model directory configuration
key = "sk-f1fCP1wFI4K1pQYJORkJF3K9tg1MINok28GAsCsSFIjvajjS"

# Initialize OpenAI client with timeout
client = OpenAI(
    base_url="https://api2.aigcbest.top/v1",
    api_key=key,
)


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
    images: str | List[str] | bytes | List[bytes] | None = None,
    json: bool = False,
    timeout: Optional[int] = None,
) -> str:
    """
    Routes the call to the appropriate vision model provider and returns the response.

    Args:
        model_name (str): The name of the model to use.
        provider (Literal): The provider of the vision model.
        prompt (str): The text prompt for the model.
        temperature (float): Sampling temperature for the model.
        max_tokens (int): Maximum number of tokens in the response.
        images (str | list[str] | bytes | list[bytes] | None): Image file paths, bytes,
            or lists of either. File paths should be strings, image data should be bytes.
        json (bool): Whether the response should be in JSON format.
        timeout (Optional[int], optional): Timeout for the HTTP request. Defaults to None.

    Returns:
        str: The generated response from the vision model.
    """
    if images is None:
        raise ValueError("At least one image must be provided for the vision model.")

    # Convert single items to list
    if isinstance(images, (str, bytes)):
        images = [images]

    # Validate all images
    processed_images = []
    for img in images:
        if isinstance(img, str):
            if not os.path.exists(img):
                raise ValueError(f"Image file not found: {img}")
            processed_images.append(img)
        elif isinstance(img, bytes):
            processed_images.append(img)
        else:
            raise ValueError(f"Invalid image type: {type(img)}. Expected str or bytes.")

    if provider == "ollama":
        return generate_with_image_ollama(
            model_name=model_name,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            images=processed_images,
            json=json,
            timeout=timeout,
        )
    elif provider == "api":
        return generate_with_api(
            model_name=model_name,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            images=processed_images,
            json=json,
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
    images: List[str | bytes],
    json: bool,
    timeout: int = 30,  # Default 30 seconds
) -> str:
    """
    Generates a response using the Ollama model with images.

    Args:
        model_name (str): The name of the model to use.
        prompt (str): The text prompt for the model.
        temperature (float): Sampling temperature for the model.
        max_tokens (int): Maximum number of tokens in the response.
        images (list[str | bytes]): Paths to the image files or image data to include.
        json (bool): Whether the response should be in JSON format.
        timeout (int): Maximum time to wait for the response.

    Returns:
        str: The generated response from the model.
    """
    try:
        options = Options(
            temperature=temperature,
            num_ctx=max_tokens,
            request_timeout=timeout,  # Add timeout to options
        )

        return ollama.generate(
            model=model_name,
            prompt=prompt,
            images=images,
            options=options,
            format="json" if json else "",
        )["response"]

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
    images: List[str | bytes],
    json: bool,
    timeout: int = 30,  # Default 30 seconds
) -> str:
    """
    Generates a response using the API with images.

    Args:
        model_name (str): The name of the model to use.
        prompt (str): The text prompt for the model.
        temperature (float): Sampling temperature for the model.
        max_tokens (int): Maximum number of tokens in the response.
        images (list[str | bytes]): Paths to the image files or image data to include.
        json (bool): Whether the response should be in JSON format.
        timeout (int): Maximum time to wait for the response.

    Returns:
        str: The generated response from the API.
    """
    try:
        messages = generate_api_messages(images=images, prompt=prompt)
        
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"} if json else None,
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
    images: List[str | bytes],
    prompt: str,
) -> List[Dict[str, Any]]:
    """
    Prepares the messages payload for the API call with images and a prompt.

    Args:
        images (list[str | bytes]): List of image file paths or bytes objects.
        prompt (str): The text prompt for the model.

    Returns:
        list[dict]: A list of messages formatted for the API call.
    """
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
