"""Stream speech (text to speech) with the CreateAI OpenAI-compatible API.

Uses the OpenAI SDK streaming-response API against POST {base_url}/audio/speech
and writes the audio to disk as the body arrives.

Note: the CreateAI OpenAI-compatible /audio/speech route returns the whole clip
in one REST response (it does not chunk audio over the wire; chunked audio only
exists on the native websocket path). So this streams the HTTP body to the
file, not provider-side audio chunks. For per-chunk streaming use
createai_api_speech_streaming.py.

    python createai_openai_compatible_speech_streaming.py
"""

from config import poc_service_key, base_url
from openai import OpenAI

client = OpenAI(api_key=poc_service_key, base_url=base_url)

MODEL = "openai/gpt4o_mini-tts"
VOICE = "alloy"
OUTPUT_FILE = "createai_openai_compatible_speech_streaming_output.mp3"

try:
    with client.audio.speech.with_streaming_response.create(
        model=MODEL,
        voice=VOICE,
        input="Hello from the CreateAI OpenAI compatible API.",
        instructions="Speak clearly and naturally.",
        response_format="mp3",
    ) as response:
        response.stream_to_file(OUTPUT_FILE)
    print(f"Wrote spoken audio -> {OUTPUT_FILE}")
except Exception as e:
    print("Error:", e)
