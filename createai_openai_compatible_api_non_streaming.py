from config import poc_service_key, base_url
from openai import OpenAI

client = OpenAI(api_key=poc_service_key, base_url=base_url)

payload = {
    "model": "gpt5.1", # https://docs.aiml.asu.edu/openai-compatible#model-format
    "stream": False,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
    ],
}

response = client.chat.completions.create(**payload)
try:
    print(response.choices[0].message.content)
    usage = getattr(response, "usage", None)
    if usage:
        print("\n\nUsage:")
        print(f"  prompt_tokens: {usage.prompt_tokens}")
        print(f"  completion_tokens: {usage.completion_tokens}")
        print(f"  total_tokens: {usage.total_tokens}")
except Exception as e:
    print("Error:", e)
