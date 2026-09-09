"""Transcribe audio with the CreateAI OpenAI-compatible API.

Maps to POST {base_url}/audio/transcriptions.

Pass an audio file as the first CLI argument, or let the script synthesize a
short spoken-tone WAV so it runs with nothing extra on disk.

    python createai_openai_compatible_audio_transcription.py [path/to/audio.mp3]
"""

import math
import os
import struct
import sys
import wave

from config import poc_service_key, base_url
from openai import OpenAI

client = OpenAI(api_key=poc_service_key, base_url=base_url)

# whisper-1 supports the widest feature set (language, translate, timestamps,
# srt/vtt/verbose_json). See https://docs.aiml.asu.edu/models
MODEL = "openai/whisper-1"


def _make_sample_wav(path: str) -> str:
    """Write a 1-second 440Hz tone as a 16-bit mono WAV for a smoke test."""
    framerate = 16000
    amplitude = 16000
    frames = bytearray()
    for i in range(framerate):
        sample = int(amplitude * math.sin(2 * math.pi * 440 * (i / framerate)))
        frames += struct.pack("<h", sample)

    with wave.open(path, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(framerate)
        handle.writeframes(bytes(frames))
    return path


def _resolve_audio_file() -> str:
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        return sys.argv[1]
    sample = "sample_tone.wav"
    if not os.path.isfile(sample):
        _make_sample_wav(sample)
    return sample


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
