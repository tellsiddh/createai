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
| `.gitignore` | Ignores Python build artifacts, virtual environments, caches, and local config. |
| `.vscode/settings.json` | VS Code workspace settings for Python environment/package manager defaults. |

