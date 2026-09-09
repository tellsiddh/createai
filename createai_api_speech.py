"""Generate speech (text to speech) with the native CreateAI API.

Hits POST {createai_base_url} directly with endpoint = "speech", the same call
the OpenAI-compatible /audio/speech route makes upstream. The clip comes back
base64-encoded in the "response" field and is written as mp3.

    python createai_api_speech.py
"""

import base64
import json

import requests

from config import poc_service_key, createai_base_url

OUTPUT_FILE = "createai_api_speech_output.mp3"

payload = {
    "action": "query",
    "endpoint": "speech",
    "request_source": "override_params",
    "query": "Hello from the native CreateAI API.",
    "voice": "alloy",
    "model_name": "gpt4o_mini-tts",
    "model_provider": "openai",
    "model_params": {"system_prompt": "Speak clearly and naturally."},
    "response_format": {"type": "json"},
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
    encoded = body.get("response")
    if isinstance(encoded, str) and encoded.strip():
        with open(OUTPUT_FILE, "wb") as handle:
            handle.write(base64.b64decode("".join(encoded.split())))
        print(f"Wrote spoken audio -> {OUTPUT_FILE}")
    else:
        print("No audio data returned. Full body:")
        print(json.dumps(body, indent=2))
except Exception as e:
    print("Error:", e)
