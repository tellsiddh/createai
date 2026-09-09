"""Transcribe audio with the native CreateAI API.

Hits POST {createai_base_url} directly with endpoint = "audio", the same call
the OpenAI-compatible /audio/transcriptions route makes upstream. The audio is
sent inline as a base64 data URI in "audio_file"; the transcript comes back in
the "response" field.

Pass an audio file as the first CLI argument, or let the script synthesize a
short tone WAV so it runs with nothing extra on disk.

    python createai_api_audio.py [path/to/audio.mp3]
"""

import base64
import json
import math
import os
import struct
import sys
import wave

import requests

from config import poc_service_key, createai_base_url

EXTENSION_MIME = {
    "flac": "audio/flac",
    "m4a": "audio/m4a",
    "mp3": "audio/mpeg",
    "mp4": "audio/mp4",
    "ogg": "audio/ogg",
    "wav": "audio/wav",
    "webm": "audio/webm",
}


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


def _data_uri(path: str) -> str:
    extension = path.rsplit(".", 1)[-1].lower()
    mime = EXTENSION_MIME.get(extension, "audio/wav")
    with open(path, "rb") as handle:
        encoded = base64.b64encode(handle.read()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


audio_file = _resolve_audio_file()
print(f"Audio file: {audio_file}")

payload = {
    "action": "query",
    "endpoint": "audio",
    "request_source": "override_params",
    "query": "transcribe",
    "audio_file": _data_uri(audio_file),
    "model_name": "whisper-1",
    "model_provider": "openai",
    "model_params": {},
    "response_format": {"type": "json"},
    "enable_history": False,
}

headers = {
    "Authorization": f"Bearer {poc_service_key}",
    "Content-Type": "application/json",
}

try:
    response = requests.post(createai_base_url, json=payload, headers=headers)
    if not response.ok:
        raise RuntimeError(f"{response.status_code}: {response.text}")

    body = response.json()
    transcript = body.get("response")
    if isinstance(transcript, str):
        print("Transcript:")
        print(transcript)
    else:
        print("No transcript returned. Full body:")
        print(json.dumps(body, indent=2))
except Exception as e:
    print("Error:", e)
