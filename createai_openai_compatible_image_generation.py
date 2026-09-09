"""Generate an image with the CreateAI OpenAI-compatible API.

Maps to POST {base_url}/images/generations. Images come back as base64 in
data[].b64_json and are written to disk.

    python createai_openai_compatible_image_generation.py
"""

import base64

from config import poc_service_key, base_url
from openai import OpenAI

client = OpenAI(api_key=poc_service_key, base_url=base_url)

# Image model ids look like openai/gpt_image2. See https://docs.aiml.asu.edu/models
MODEL = "openai/gpt_image2"
OUTPUT_FILE = "image_generation_output.png"

try:
    response = client.images.generate(
        model=MODEL,
        prompt="a red bicycle leaning on a white wall",
        size="1024x1024",
        quality="low",
        n=1,
    )

    entry = response.data[0]
    b64 = getattr(entry, "b64_json", None)
    if b64:
        with open(OUTPUT_FILE, "wb") as handle:
            handle.write(base64.b64decode(b64))
        print(f"Wrote generated image -> {OUTPUT_FILE}")
    elif getattr(entry, "url", None):
        # asu-air/flux_2 may answer with a link instead of inline base64.
        print(f"Image URL: {entry.url}")
    else:
        print("No image data returned.")

    revised = getattr(entry, "revised_prompt", None)
    if revised:
        print(f"revised_prompt: {revised}")
except Exception as e:
    print("Error:", e)
