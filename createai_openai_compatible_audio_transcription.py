"""Transcribe audio with the CreateAI OpenAI-compatible API.

Maps to POST {base_url}/audio/transcriptions, sent as a standard multipart
file upload via the OpenAI SDK.

Pass an audio file as the first CLI argument, or let the script pick a real
audio file from this folder (preferring the smallest .mp3). Large files may hit
the request-size limit, so smaller clips are preferred.

    python createai_openai_compatible_audio_transcription.py [path/to/audio.mp3]
"""

import os
import sys

from config import poc_service_key, base_url
from openai import OpenAI
from sample_assets import ensure_sample_audio

client = OpenAI(api_key=poc_service_key, base_url=base_url)

# whisper-1 supports the widest feature set (language, translate, timestamps,
# srt/vtt/verbose_json). See https://docs.aiml.asu.edu/models
MODEL = "openai/whisper-1"


def _resolve_audio_file() -> str:
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        return sys.argv[1]
    return ensure_sample_audio()


audio_file = _resolve_audio_file()
print(f"Audio file: {audio_file}")

try:
    with open(audio_file, "rb") as handle:
        response = client.audio.transcriptions.create(
            model=MODEL,
            file=handle,
            response_format="json",
        )
    print("Transcript:")
    print(getattr(response, "text", response))
except Exception as e:
    print("Error:", e)
