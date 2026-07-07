from config import poc_service_key, base_url
from openai import OpenAI

client = OpenAI(api_key=poc_service_key, base_url=base_url)

try:
    models = client.models.list()
    for model in models.data:
        print(model.id)
except Exception as e:
    print("Error:", e)
