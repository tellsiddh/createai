"""Call the Responses API on the CreateAI OpenAI-compatible API.

Maps to POST {base_url}/responses.

    python createai_openai_compatible_responses.py
"""

from config import poc_service_key, base_url
from openai import OpenAI

client = OpenAI(api_key=poc_service_key, base_url=base_url)

MODEL = "openai/gpt4o"

try:
    response = client.responses.create(
        model=MODEL,
        instructions="Be brief.",
        input="Hello, how are you?",
    )

    # output_text is the SDK convenience accessor for the concatenated text.
    text = getattr(response, "output_text", None)
    if text:
        print(text)
    else:
        print(response)

    usage = getattr(response, "usage", None)
    if usage:
        print("\n\nUsage:")
        print(f"  input_tokens: {getattr(usage, 'input_tokens', None)}")
        print(f"  output_tokens: {getattr(usage, 'output_tokens', None)}")
        print(f"  total_tokens: {getattr(usage, 'total_tokens', None)}")
except Exception as e:
    print("Error:", e)
