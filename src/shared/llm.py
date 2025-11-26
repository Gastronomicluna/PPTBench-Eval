import base64
import io
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

import ollama
from ollama import Options
from openai import OpenAI
from PIL import Image
from requests.exceptions import ConnectionError
import tiktoken

from .utils import TimeoutException, with_timeout

logging.getLogger("httpx").setLevel(logging.WARNING)

API_LLM_MODELS = [
    # ("api", "claude-3-7-sonnet-202502192-all"),
    ("api", "gpt-4o-2024-11-20"),
    # ("api", "gemma-3-12b-it"),
    # ("api", "o1-2024-12-17"),
    # ("api", "gemini-2.0-flash"),
    # ("api", "gemini-2.0-flash-thinking-exp"),
    # ("api", "qwen-vl-max-0809"),
    # ("api", "llama-3.2-90b-vision-instruct"),
    # ("api", "Qwen/Qwen2.5-VL-72B-Instruct")
    # ("api", "Qwen/Qwen2.5-VL-7B-Instruct"),
    # ("api", "Qwen/Qwen2.5-VL-32B-Instruct"),
    # ("api", "Qwen/Qwen3-8B"),
    # ("api", "Pro/Qwen/Qwen2.5-VL-7B-Instruct"),
    # ("ollama", "llama3-2-vision-11b"),
    # ("ollama", "llava:13b"),
    # ("ollama", "llama3.2-vision:90b"),
    # ("ollama", "llava-34b"),
    # ("ollama", "llava-7b")
    # ("ollama", "minicpm-v"),
    # ("ollama", "gemma3:12b"),
    # ("ollama", "llava:7b")
    # ("vllm","Qwen3-8B"),
    # ("vllm","gemma-3-12b-it")
    # ("vllm", "llama3.2-vision:11b"),
]

# API key and model directory configuration
key = "sk-*********" 


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


def enforce_token_limit(
    prompt: str,
    images: Optional[List[Any]] = None,
    model_name: str = "gpt-4o",
    max_input_tokens: int = 8000
) -> str:
    """Enforces token limit by truncating the prompt if necessary.
    
    Args:
        prompt (str): The text prompt to be processed.
        images (Optional[List[Any]]): List of images. Each image counts as 
            additional tokens.
        model_name (str): Name of the model to consider for tokenization.
        max_input_tokens (int): Maximum allowed input tokens.
        
    Returns:
        str: Truncated prompt if necessary, original otherwise.
    """
    # Estimate image tokens - different models have different token usages for images
    image_token_count = 0
    if images:
        # Approximate token counts for common model types
        if "gpt-4" in model_name or "gpt-4o" in model_name:
            # GPT-4V/GPT-4o uses ~85 tokens per 512x512 image
            image_token_count = len(images) * 85
        elif "gemini" in model_name:
            # Gemini uses ~250 tokens per image
            image_token_count = len(images) * 250
        elif "llava" in model_name or "llama" in model_name:
            # LLaVA/Llama uses ~256 tokens per image
            image_token_count = len(images) * 256
        else:
            # Default conservative estimate for other models
            image_token_count = len(images) * 300
    
    # Get appropriate tokenizer
    try:
        if "gpt-3.5" in model_name or "gpt-4" in model_name or "gpt-4o" in model_name:
            encoding = tiktoken.encoding_for_model(model_name)
        else:
            # Default to cl100k_base for other models
            encoding = tiktoken.get_encoding("cl100k_base")
        
        # Count tokens in the prompt
        text_tokens = len(encoding.encode(prompt))
        total_tokens = text_tokens + image_token_count
        
        # Check if truncation is needed
        if total_tokens > max_input_tokens:
            # Calculate how many text tokens we need to remove
            excess_tokens = total_tokens - max_input_tokens
            target_text_tokens = text_tokens - excess_tokens
            
            if target_text_tokens <= 0:
                # Extreme case: images alone exceed the limit, truncate to minimal prompt
                return "Describe the image(s)."
            
            # Truncate text to meet the token limit
            truncated_text = encoding.decode(encoding.encode(prompt)[:target_text_tokens])
            return truncated_text + "\n[Note: Prompt was truncated to fit token limits]"
        
        return prompt
    except Exception as e:
        logging.warning(f"Error in token counting, using original prompt: {str(e)}")
        return prompt


def call_vision_model(
    model_name: str = "llama3.2-vision:11b",
    provider: Literal["api", "ollama", "openai", "anthropic","vllm"] = "ollama",
    prompt: str = "",
    temperature: float = 0.1,
    max_tokens: int = 3200,
    images: Union[
        str,
        List[str],
        Path,
        List[Path],
        bytes,
        List[bytes],
        Image.Image,
        List[Image.Image],
        None,
    ] = None,
    json_mode: bool = False,
    timeout: Optional[int] = 120,
    retry: int = 3,
    enforce_tokens: bool = True,
    max_input_tokens: int = 8000,
) -> Union[str, Dict[str, Any]]:
    """
    Routes the call to the appropriate vision model provider and returns the response.

    Args:
        model_name (str): The name of the model to use.
        provider (Literal): The provider of the vision model.
        prompt (str): The text prompt for the model.
        temperature (float): Sampling temperature for the model.
        max_tokens (int): Maximum number of tokens in the response.
        images (Union[str, List[str], Path, List[Path], bytes, List[bytes],
               Image.Image, List[Image.Image], None]):
            Image file paths (as strings or Path objects), bytes, PIL Images,
            or lists of any of these. If None, runs in text-only mode.
        json_mode (bool): Whether the response should be in JSON format.
        timeout (Optional[int], optional): Timeout for the HTTP request. Defaults to None.
        retry (int, optional): Number of retry attempts. Defaults to 3.
        enforce_tokens (bool): Whether to enforce token limits. Defaults to True.
        max_input_tokens (int): Maximum allowed input tokens. Defaults to 8000.

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
            if isinstance(img, (str, Path)):
                img_path = str(img) if isinstance(img, Path) else img
                if not os.path.exists(img_path):
                    raise ValueError(f"Image file not found: {img_path}")
                processed_images.append(img_path)
            elif isinstance(img, bytes):
                processed_images.append(img)
            elif isinstance(img, Image.Image):
                # Convert PIL Image to bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format or "PNG")
                processed_images.append(img_byte_arr.getvalue())
            else:
                raise ValueError(
                    f"Invalid image type: {type(img)}. Expected str, Path, bytes, or PIL Image."
                )
    
    # Enforce token limits if requested
    if enforce_tokens:
        prompt = enforce_token_limit(
            prompt=prompt, 
            images=processed_images, 
            model_name=model_name,
            max_input_tokens=max_input_tokens
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
            retry=retry,
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
            retry=retry,
        )
    elif provider == "openai":
        raise NotImplementedError("OpenAI API integration is not implemented yet.")
    elif provider == "anthropic":
        raise NotImplementedError("Anthropic API integration is not implemented yet.")
    elif provider == "vllm":
        return generate_with_vllm_api(
            model_name=model_name,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            images=processed_images,
            json_mode=json_mode,
            timeout=timeout,
            retry=retry,
        )
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
    retry: int = 3,
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
        retry (int): Number of retry attempts. Defaults to 3.

    Returns:
        str: The generated response from the model.
    """
    last_error = None
    for attempt in range(retry):
        try:

            @with_timeout(timeout)
            def _generate() -> str:
                options = Options(
                    temperature=temperature,
                    num_ctx=max_tokens,
                )
                kwargs = {
                    "model": model_name,
                    "prompt": prompt,
                    "options": options,
                    "format": "json" if json_mode else "",
                }
                if images:
                    kwargs["images"] = images
                return ollama.generate(**kwargs)["response"]

            response_str = _generate()
            if json_mode:
                try:
                    return json.loads(response_str)
                except json.JSONDecodeError:
                    return response_str
            return response_str
        except (TimeoutException, ConnectionError, Exception) as e:
            last_error = e
            if "EOF" in str(e) or isinstance(e, ConnectionError):
                logging.warning(
                    f"Attempt {attempt + 1}/{retry}: Connection error occurred: {str(e)}"
                )
                print(
                    f"Attempt {attempt + 1}/{retry}: Connection error occurred: {str(e)}"
                )
                time.sleep(2 * (attempt + 1))  # Exponential backoff
                continue

            if attempt == retry - 1:  # Last attempt
                if isinstance(e, TimeoutException):
                    raise TimeoutError(f"Request timed out after {timeout} seconds")
                logging.error(f"Error in generate_with_image_ollama: {str(e)}")
                raise
            logging.warning(f"Attempt {attempt + 1}/{retry} failed: {str(e)}")
            time.sleep(1)

    # If we get here, all retries failed
    raise Exception(f"All {retry} attempts failed. Last error: {str(last_error)}")


def generate_with_api(
    model_name: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
    images: Optional[List[str | bytes]] = None,
    json_mode: bool = False,
    timeout: int = 30,  # Default 30 seconds
    retry: int = 3,
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
        retry (int): Number of retry attempts. Defaults to 3.

    Returns:
        str: The generated response from the API.
    """
    last_error = None
    for attempt in range(retry):
        try:

            @with_timeout(timeout)
            def _generate():
                client = OpenAI(
                    base_url="https://api.siliconflow.cn/v1",
                    api_key=key,
                )
                messages = generate_api_messages(images=images, prompt=prompt)
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    response_format={"type": "json_object"} if json_mode else None,
                    seed=42,
                )
                return response.choices[0].message.content

            response_str = _generate()
            if json_mode:
                try:
                    return json.loads(response_str)
                except json.JSONDecodeError:
                    return response_str
            return response_str
        except (TimeoutException, ConnectionError, Exception) as e:
            last_error = e
            if "EOF" in str(e) or isinstance(e, ConnectionError):
                logging.warning(
                    f"Attempt {attempt + 1}/{retry}: Connection error occurred: {str(e)}"
                )
                time.sleep(2 * (attempt + 1))  # Exponential backoff
                continue

            if attempt == retry - 1:  # Last attempt
                if isinstance(e, TimeoutException):
                    raise TimeoutError(f"Request timed out after {timeout} seconds")
                logging.error(f"Error in generate_with_api: {str(e)}")
                raise
            logging.warning(f"Attempt {attempt + 1}/{retry} failed: {str(e)}")
            time.sleep(1)

    # If we get here, all retries failed
    raise Exception(f"All {retry} attempts failed. Last error: {str(last_error)}")



def generate_with_vllm_api(
    model_name: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
    images: Optional[List[str | bytes]] = None,
    json_mode: bool = False,
    timeout: int = 30,  # Default 30 seconds
    retry: int = 3,
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
        retry (int): Number of retry attempts. Defaults to 3.

    Returns:
        str: The generated response from the API.
    """
    last_error = None
    for attempt in range(retry):
        try:

            @with_timeout(timeout)
            def _generate():
                client = OpenAI(
                    base_url="https://api.siliconflow.cn/v1",
                    api_key=key,
                )
                messages = generate_api_messages(images=images, prompt=prompt)
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    response_format={"type": "json_object"} if json_mode else None,
                    seed=42,
                )
                return response.choices[0].message.content

            response_str = _generate()
            if json_mode:
                try:
                    return json.loads(response_str)
                except json.JSONDecodeError:
                    return response_str
            return response_str
        except (TimeoutException, ConnectionError, Exception) as e:
            last_error = e
            if "EOF" in str(e) or isinstance(e, ConnectionError):
                logging.warning(
                    f"Attempt {attempt + 1}/{retry}: Connection error occurred: {str(e)}"
                )
                time.sleep(2 * (attempt + 1))  # Exponential backoff
                continue

            if attempt == retry - 1:  # Last attempt
                if isinstance(e, TimeoutException):
                    raise TimeoutError(f"Request timed out after {timeout} seconds")
                logging.error(f"Error in generate_with_api: {str(e)}")
                raise
            logging.warning(f"Attempt {attempt + 1}/{retry} failed: {str(e)}")
            time.sleep(1)

    # If we get here, all retries failed
    raise Exception(f"All {retry} attempts failed. Last error: {str(last_error)}")



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
    assert isinstance(result, dict)


if __name__ == "__main__":
    main()
