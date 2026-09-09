import json

from config import poc_service_key, base_url
from openai import OpenAI
from pydantic import BaseModel, ConfigDict

client = OpenAI(api_key=poc_service_key, base_url=base_url)


class CalendarEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    date: str
    participants: list[str]


calendar_event_schema = CalendarEvent.model_json_schema()


def extract_json_content(content: str) -> str:
    content = content.strip()
    if not content.startswith("```"):
        return content

    lines = content.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


payload = {
    "model": "openai/gpt5_5",  # https://docs.aiml.asu.edu/openai-compatible#model-format
    "stream": False,
    "messages": [
        {
            "role": "system",
            "content": (
                "Extract event information only from the user's message. "
                "Return only raw JSON with these exact keys: name, date, participants. "
                "Do not include Markdown code fences."
            ),
        },
        {
            "role": "user",
            "content": "Alice and Bob are going to a science fair on Friday.",
        },
    ],
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "calendar_event",
            "schema": calendar_event_schema,
        },
    },
}

response = client.chat.completions.create(**payload)
try:
    print("Raw response:", response.model_dump_json(indent=2))
    message = response.choices[0].message
    content = message.content
    print("Raw message content:", content)
    if content is None:
        tool_calls = message.tool_calls or []
        if tool_calls:
            content = tool_calls[0].function.arguments
        else:
            raise ValueError(
                "The API returned no message content. Full assistant message:\n"
                f"{message.model_dump_json(indent=2)}"
            )

    event = CalendarEvent.model_validate_json(extract_json_content(content))
    print(json.dumps(event.model_dump(), indent=2))
    usage = getattr(response, "usage", None)
    if usage:
        print("\n\nUsage:")
        print(f"  prompt_tokens: {usage.prompt_tokens}")
        print(f"  completion_tokens: {usage.completion_tokens}")
        print(f"  total_tokens: {usage.total_tokens}")
except Exception as e:
    print("Error:", e)
