"""Send an image to a vision model with the CreateAI OpenAI-compatible API.

Image input on /chat/completions switches the request to CreateAI's vision
endpoint. Images must be inlined as base64 data URLs; remote URLs are not
fetched on the caller's behalf.

Pass an image as the first CLI argument, or let the script synthesize a small
real JPEG (a red disc on white) so it runs with nothing extra on disk.

    python createai_openai_compatible_vision.py [path/to/image.png]
"""

import base64
import os
import sys

from config import poc_service_key, base_url
from openai import OpenAI
from sample_assets import ensure_sample_image

client = OpenAI(api_key=poc_service_key, base_url=base_url)

# A vision-capable chat model. See https://docs.aiml.asu.edu/models
MODEL = "openai/gpt4o"

_MIME_BY_EXT = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
}


def _resolve_image_path() -> str:
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        return sys.argv[1]
    return ensure_sample_image()


def _data_uri(path: str) -> str:
    extension = path.rsplit(".", 1)[-1].lower()
    mime = _MIME_BY_EXT.get(extension, "image/jpeg")
    with open(path, "rb") as handle:
        encoded = base64.b64encode(handle.read()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


image_path = _resolve_image_path()
print(f"Image file: {image_path}")
data_uri = _data_uri(image_path)

payload = {
    "model": MODEL,
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What color is this image?"},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ],
        }
    ],
}

try:
    response = client.chat.completions.create(**payload)
    print(response.choices[0].message.content)
    usage = getattr(response, "usage", None)
    if usage:
        print("\n\nUsage:")
        print(f"  prompt_tokens: {usage.prompt_tokens}")
        print(f"  completion_tokens: {usage.completion_tokens}")
        print(f"  total_tokens: {usage.total_tokens}")
except Exception as e:
    print("Error:", e)
