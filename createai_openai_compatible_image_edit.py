"""Edit an image with the CreateAI OpenAI-compatible API.

Maps to POST {base_url}/images/edits (multipart form data). Editing only works
on gcp-deepmind image models; the openai/asu-air image models drop the input
image and would return a brand new picture instead.

Pass an input image as the first CLI argument, or let the script synthesize a
small real JPEG (a red disc on white) so it runs with nothing extra on disk.
Keep inputs well under the 4MB decoded limit the route enforces.

    python createai_openai_compatible_image_edit.py [path/to/image.png]
"""

import base64
import os
import sys

from config import poc_service_key, base_url
from openai import OpenAI
from sample_assets import ensure_sample_image

client = OpenAI(api_key=poc_service_key, base_url=base_url)

# Editing is only supported on gcp-deepmind models, e.g. nano_banana_pro.
MODEL = "gcp-deepmind/nano_banana_pro"
OUTPUT_FILE = "image_edit_output.png"


def _resolve_image_file() -> str:
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        return sys.argv[1]
    return ensure_sample_image()


image_file = _resolve_image_file()
print(f"Input image: {image_file}")

try:
    with open(image_file, "rb") as handle:
        response = client.images.edit(
            model=MODEL,
            image=handle,
            prompt="Make the image bright red. Keep everything else identical.",
        )

    entry = response.data[0]
    b64 = getattr(entry, "b64_json", None)
    if b64:
        with open(OUTPUT_FILE, "wb") as out:
            out.write(base64.b64decode(b64))
        print(f"Wrote edited image -> {OUTPUT_FILE}")
    elif getattr(entry, "url", None):
        print(f"Image URL: {entry.url}")
    else:
        print("No image data returned.")

    revised = getattr(entry, "revised_prompt", None)
    if revised:
        print(f"revised_prompt: {revised}")
except Exception as e:
    print("Error:", e)
