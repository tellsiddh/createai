"""Transcribe audio with the CreateAI OpenAI-compatible API.

Maps to POST {base_url}/audio/transcriptions.

Pass an audio file as the first CLI argument, or let the script synthesize a
short spoken-tone WAV so it runs with nothing extra on disk.

    python createai_openai_compatible_audio_transcription.py [path/to/audio.mp3]
"""

import os
import sys

from config import poc_service_key, base_url
from openai import OpenAI
from sample_assets import ensure_sample_wav

client = OpenAI(api_key=poc_service_key, base_url=base_url)

# whisper-1 supports the widest feature set (language, translate, timestamps,
# srt/vtt/verbose_json). See https://docs.aiml.asu.edu/models
MODEL = "openai/whisper-1"


def _resolve_audio_file() -> str:
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        return sys.argv[1]
    # A pure tone may be rejected as undecodable speech; for a real transcript
    # pass a recording, or the mp3 from createai_openai_compatible_speech.py.
    return ensure_sample_wav()


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
