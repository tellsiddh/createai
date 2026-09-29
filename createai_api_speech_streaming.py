"""Stream speech (text to speech) from the native CreateAI WebSocket API.

Connects to wss://apiws-<api>-<env>.aiml.asu.edu/?access_token=<JWT>, sends one
speech request frame, and receives audio as base64 chunks in {"response": ...}
frames. Chunks are decoded and written to disk as they arrive.

    python createai_api_speech_streaming.py
"""

import asyncio
import base64
import json

import websockets

from config import poc_service_key, ws_base_url

OUTPUT_FILE = "createai_api_speech_streaming_output.mp3"


def _ws_url() -> str:
    return f"{ws_base_url}/?access_token={poc_service_key}"


request = {
    "action": "query",
    "endpoint": "speech",
    "request_source": "override_params",
    "query": "Hello from the native CreateAI websocket API. Hello from the native CreateAI websocket API. Hello from the native CreateAI websocket API. Hello from the native CreateAI websocket API. Hello from the native CreateAI websocket API. Hello from the native CreateAI websocket API. Hello from the native CreateAI websocket API.vHello from the native CreateAI websocket API. Hello from the native CreateAI websocket API. Hello from the native CreateAI websocket API. Hello from the native CreateAI websocket API. Hello from the native CreateAI websocket API.",
    "voice": "alloy",
    "model_name": "gpt4o_mini-tts",
    "model_provider": "openai",
    "model_params": {"system_prompt": "Speak clearly and naturally."},
    "response_format": {"type": "json"},
    "enable_search": False,
}


def _extract_chunk(frame: dict):
    """Return (audio_bytes, done, error) from one decoded frame."""
    if frame.get("error"):
        return None, True, str(frame.get("error"))

    value = frame.get("response")
    if not isinstance(value, str):
        return None, False, None
    if value == "<EOS>":
        return None, True, None

    try:
        return base64.b64decode("".join(value.split())), False, None
    except (ValueError, base64.binascii.Error):
        return None, False, None


async def stream_speech():
    total = 0
    async with websockets.connect(
        _ws_url(), additional_headers={"origin": "https://ai.asu.edu"}
    ) as ws:
        await ws.send(json.dumps(request))

        with open(OUTPUT_FILE, "wb") as handle:
            async for message in ws:
                try:
                    frame = json.loads(message)
                except json.JSONDecodeError:
                    continue
                if not isinstance(frame, dict):
                    continue

                audio, done, error = _extract_chunk(frame)
                if error:
                    print("Error:", error)
                    return
                if audio:
                    handle.write(audio)
                    total += len(audio)
                    print(f"chunk: {len(audio)} bytes (total {total})")
                if done:
                    break

    print(f"Wrote {total} bytes -> {OUTPUT_FILE}")


if __name__ == "__main__":
    try:
        asyncio.run(stream_speech())
    except Exception as e:
        print("Error:", e)
