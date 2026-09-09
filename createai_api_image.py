"""Generate an image with the native CreateAI API.

Hits POST {createai_base_url} directly with endpoint = "image", the same call
the OpenAI-compatible /images/generations route makes upstream. The image comes
back base64-encoded in the "response" field.

    python createai_api_image.py
"""

import base64
import json

import requests

from config import poc_service_key, createai_base_url

OUTPUT_FILE = "createai_api_image_output.png"

payload = {
    "action": "query",
    "endpoint": "image",
    "request_source": "override_params",
    "query": "a red bicycle leaning on a white wall",
    "model_name": "gpt_image2",
    "model_provider": "openai",
    "model_params": {"size": "1024x1024", "quality": "low", "n": 1},
    "response_format": {"type": "json"},
    "enable_search": False,
    "enable_history": False,
}

headers = {
    "Authorization": f"Bearer {poc_service_key}",
    "Content-Type": "application/json",
}


def _first_image(response_field):
    """The backend returns a base64 string, a list, or {"images", "description"}."""
    description = ""
    images = response_field
    if isinstance(images, dict):
        description = images.get("description") or ""
        images = images.get("images")
    if isinstance(images, str):
        images = [images]
    if isinstance(images, list) and images:
        return images[0], description
    return None, description


try:
    response = requests.post(createai_base_url, json=payload, headers=headers)
    if not response.ok:
        raise RuntimeError(f"{response.status_code}: {response.text}")

    body = response.json()
    image_b64, description = _first_image(body.get("response"))
    if image_b64:
        with open(OUTPUT_FILE, "wb") as handle:
            handle.write(base64.b64decode(image_b64))
        print(f"Wrote generated image -> {OUTPUT_FILE}")
    else:
        print("No image data returned. Full body:")
        print(json.dumps(body, indent=2))
    if description:
        print(f"description: {description}")
except Exception as e:
    print("Error:", e)
