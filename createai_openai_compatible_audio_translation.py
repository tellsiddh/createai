"""Translate audio into English with the CreateAI OpenAI-compatible API.

Maps to POST {base_url}/audio/translations.

Pass an audio file as the first CLI argument, or let the script synthesize a
short tone WAV so it runs with nothing extra on disk.

    python createai_openai_compatible_audio_translation.py [path/to/audio.mp3]
"""

import os
import sys

from config import poc_service_key, base_url
from openai import OpenAI
from sample_assets import ensure_sample_wav

client = OpenAI(api_key=poc_service_key, base_url=base_url)

# Translation needs a model with language/translate support (whisper-1 or the
# gpt4o transcribe models). See https://docs.aiml.asu.edu/models
MODEL = "openai/whisper-1"


def _resolve_audio_file() -> str:
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        return sys.argv[1]
    # A pure tone may be rejected as undecodable speech; for a real result pass
    # a recording, or the mp3 from createai_openai_compatible_speech.py.
    return ensure_sample_wav()


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
