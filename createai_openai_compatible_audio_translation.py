"""Translate audio into English with the CreateAI OpenAI-compatible API.

Maps to POST {base_url}/audio/translations, sent as a standard multipart file
upload via the OpenAI SDK.

Pass an audio file as the first CLI argument, or let the script pick a real
audio file from this folder (preferring the smallest .mp3). Large files may hit
the request-size limit, so smaller clips are preferred.

    python createai_openai_compatible_audio_translation.py [path/to/audio.mp3]
"""

import os
import sys

from config import poc_service_key, base_url
from openai import OpenAI
from sample_assets import ensure_sample_audio

client = OpenAI(api_key=poc_service_key, base_url=base_url)

# Translation needs a model with language/translate support (whisper-1 or the
# gpt4o transcribe models). See https://docs.aiml.asu.edu/models
MODEL = "openai/whisper-1"


def _resolve_audio_file() -> str:
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        return sys.argv[1]
    return ensure_sample_audio()


audio_file = _resolve_audio_file()
print(f"Audio file: {audio_file}")

try:
    with open(audio_file, "rb") as handle:
        response = client.audio.translations.create(
            model=MODEL,
            file=handle,
            response_format="json",
        )
    print("Translation (English):")
    print(getattr(response, "text", response))
except Exception as e:
    print("Error:", e)
