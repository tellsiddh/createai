from config import poc_service_key, base_url
from openai import OpenAI

client = OpenAI(api_key=poc_service_key, base_url=base_url)

response = client.embeddings.create(
    model="openai/te3s",
    input="The quick brown fox jumps over the lazy dog",
)

try:
    print(response.data[0].embedding)
    print()
    print(f"Model: {response.model}")
    print(f"Usage: {response.usage}")
except Exception as e:
    print("Error:", e)
