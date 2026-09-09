"""Generate speech (text to speech) with the CreateAI OpenAI-compatible API.

Maps to POST {base_url}/audio/speech. The clip comes back as mp3 bytes and is
written to disk.

    python createai_openai_compatible_speech.py
"""

from config import poc_service_key, base_url
from openai import OpenAI

client = OpenAI(api_key=poc_service_key, base_url=base_url)

# TTS model ids look like openai/gpt4o_mini-tts. See https://docs.aiml.asu.edu/models
MODEL = "openai/gpt4o_mini-tts"
VOICE = "alloy"
OUTPUT_FILE = "speech_output.mp3"

payload = {
    "model": MODEL,
    "voice": VOICE,
    "input": "Hello from the CreateAI OpenAI compatible API.",
    # instructions maps to the backend system_prompt; only mp3 output is offered.
    "instructions": "Speak clearly and naturally.",
    "response_format": "mp3",
}

try:
    response = client.audio.speech.create(**payload)
    response.write_to_file(OUTPUT_FILE)
    print(f"Wrote spoken audio -> {OUTPUT_FILE}")
except Exception as e:
    print("Error:", e)
