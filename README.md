# createai

Small Python examples for calling the CreateAI OpenAI-compatible API with the official `openai` Python SDK.

## Setup

1. Create and activate a virtual environment:

	```bash
	python -m venv .venv
	source .venv/bin/activate
	```

    or to use conda:
    ```bash
    conda create -n createai python=3.11
    conda activate createai
    ```

2. Install dependencies:

	```bash
	python -m pip install -r requirements.txt
	```

3. Create your local config file from the example:

	```bash
	cp config.example.py config.py
	```

4. Open `config.py` and replace the placeholder service key:

	```python
	poc_service_key = "your_real_service_key_here"
	base_url = "https://api-main-poc.aiml.asu.edu/v1"
	```

	Change `base_url` if you need a different environment, such as beta, prod, or dev.

## Run The Scripts

List available models:

```bash
python createai_openai_compatible_models.py
```

Run a non-streaming chat completion:

```bash
python createai_openai_compatible_api_non_streaming.py
```

Run a streaming chat completion:

```bash
python createai_openai_compatible_api_streaming.py
```

The streaming script requests usage with `stream_options={"include_usage": True}` and prints token usage after the streamed response finishes, if the API returns usage data.

### OpenAI-compatible multimodal paths

These use the official `openai` SDK against `base_url`. The audio, image, and
vision scripts synthesize a small self-contained asset when no file is passed,
so they run with nothing extra on disk. Pass your own file as the first
argument where noted.

```bash
# Responses API
python createai_openai_compatible_responses.py

# Audio: speech-to-text
python createai_openai_compatible_audio_transcription.py [path/to/audio.mp3]
python createai_openai_compatible_audio_translation.py [path/to/audio.mp3]

# Audio: text-to-speech (writes speech_output.mp3)
python createai_openai_compatible_speech.py

# Images (writes image_generation_output.png / image_edit_output.png)
python createai_openai_compatible_image_generation.py
python createai_openai_compatible_image_edit.py [path/to/image.png]

# Vision: image input to a chat model
python createai_openai_compatible_vision.py [path/to/image.png]
```

Image editing only works on `gcp-deepmind` image models; the `openai` and
`asu-air` image models drop the input image. Speech only returns mp3.

### Native CreateAI API paths

These use `requests` against `createai_base_url` with the platform's own
payload shape (`endpoint: "image" | "speech" | "audio"`), the same call the
OpenAI-compatible routes make upstream.

```bash
python createai_api_image.py                     # writes createai_api_image_output.png
python createai_api_speech.py                     # writes createai_api_speech_output.mp3
python createai_api_audio.py [path/to/audio.mp3]  # prints the transcript
```

## Resources

Documentation - https://docs.aiml.asu.edu/openai-compatible
Model format - https://docs.aiml.asu.edu/openai-compatible#model-format
Available models - https://docs.aiml.asu.edu/models

## Files

| File | Purpose |
| --- | --- |
| `README.md` | Project setup, run commands, and file overview. |
| `requirements.txt` | Python package dependencies. Currently installs the `openai` SDK. |
| `config.example.py` | Example config shape. Copy this to `config.py` before running scripts. |
| `config.py` | Local config containing your service key and API base URL. Do not commit real keys. |
| `createai_openai_compatible_models.py` | Lists model IDs returned by the API. |
| `createai_openai_compatible_api_non_streaming.py` | Sends one chat completion request and prints the full response text plus token usage. |
| `createai_openai_compatible_api_streaming.py` | Sends one streaming chat completion request, prints tokens as they arrive, then prints token usage. |
| `createai_openai_compatible_api_json_schema.py` | Chat completion with a JSON schema response format. |
| `createai_openai_compatible_api_embeddings.py` | Creates an embedding for a piece of text. |
| `createai_openai_compatible_responses.py` | Calls the Responses API (`/responses`). |
| `createai_openai_compatible_audio_transcription.py` | Speech-to-text via `/audio/transcriptions`; synthesizes a tone WAV if no file is given. |
| `createai_openai_compatible_audio_translation.py` | Audio-to-English via `/audio/translations`; synthesizes a tone WAV if no file is given. |
| `createai_openai_compatible_speech.py` | Text-to-speech via `/audio/speech`; writes `speech_output.mp3`. |
| `createai_openai_compatible_image_generation.py` | Image generation via `/images/generations`; writes `image_generation_output.png`. |
| `createai_openai_compatible_image_edit.py` | Image editing via `/images/edits` (gcp-deepmind models only); writes `image_edit_output.png`. |
| `createai_openai_compatible_vision.py` | Chat completion with a base64 image input (vision). |
| `createai_api_json_schema.py` | Native CreateAI API call (`createai_base_url`) with a JSON schema. |
| `createai_api_image.py` | Native CreateAI API image generation (`endpoint: "image"`). |
| `createai_api_speech.py` | Native CreateAI API text-to-speech (`endpoint: "speech"`). |
| `createai_api_audio.py` | Native CreateAI API transcription (`endpoint: "audio"`). |
| `createai_video_analysis.py` | Uploads a video to a chat session and queries it via the native API. |
| `.gitignore` | Ignores Python build artifacts, virtual environments, caches, and local config. |
| `.vscode/settings.json` | VS Code workspace settings for Python environment/package manager defaults. |

