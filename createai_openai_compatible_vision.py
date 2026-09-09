"""Send an image to a vision model with the CreateAI OpenAI-compatible API.

Image input on /chat/completions switches the request to CreateAI's vision
endpoint. Images must be inlined as base64 data URLs; remote URLs are not
fetched on the caller's behalf.

Pass an image as the first CLI argument, or let the script generate a small
solid-color PNG so it runs with nothing extra on disk.

    python createai_openai_compatible_vision.py [path/to/image.png]
"""

import base64
import os
import sys

from config import poc_service_key, base_url
from openai import OpenAI

client = OpenAI(api_key=poc_service_key, base_url=base_url)

# A vision-capable chat model. See https://docs.aiml.asu.edu/models
MODEL = "openai/gpt4o"

# A 2x2 solid green PNG, small but a real decodable image.
_GREEN_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAEklEQVR4nGNk"
    "+M/wn4GBgYEBAA0EAwGiT9M9AAAAAElFTkSuQmCC"
)


def _resolve_image_bytes() -> bytes:
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        with open(sys.argv[1], "rb") as handle:
            return handle.read()
    return _GREEN_PNG


def _data_uri(image_bytes: bytes, mime: str = "image/png") -> str:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


data_uri = _data_uri(_resolve_image_bytes())

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
