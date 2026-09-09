"""Upload a video to CreateAI chat assets (session-scoped) and query it.

Flow:
  1. POST /project  {"resource": "data", "method": "chat_upload"}  -> presigned S3 URL + query_id
  2. Upload the file bytes to the presigned URL
  3. POST /project  {"resource": "data", "method": "list_assets"}  -> poll until the asset is ready
  4. POST /query    with chat_upload.videos -> ask a question about the video
"""

import json
import time

import requests
import uuid

from config import poc_service_key, poc_owner_key, project_id

base_url = "https://api-main-poc.aiml.asu.edu/"
project_base = "project"
query_base = "query"
video_file = "video_test_small.mp4"
session_id = uuid.uuidv4()
db_type = "opensearch"

owner_headers = {
    "Authorization": f"Bearer {poc_owner_key}",
    "Content-Type": "application/json",
}
service_headers = {
    "Authorization": f"Bearer {poc_service_key}",
    "Content-Type": "application/json",
}


def _post(endpoint, payload, headers):
    response = requests.post(base_url + endpoint, json=payload, headers=headers)
    if not response.ok:
        raise RuntimeError(f"{response.status_code} from /{endpoint}: {response.text}")
    return response.json()


def request_upload_url():
    """Ask CreateAI for a presigned upload target for this chat session."""
    payload = {
        "resource": "data",
        "method": "chat_upload",
        "details": {
            "project_id": project_id,
            "session_id": session_id,
            "db_type": db_type,
            "files": [{"file_name": video_file}],
        },
    }
    return _post(project_base, payload, owner_headers)


def _find_upload_target(data):
    """Pull the presigned URL and query_id out of the chat_upload response.

    The response shape varies slightly by API version, so walk the JSON and
    grab the first presigned URL (plain string or {"url", "fields"} form).
    """
    query_id = None
    target = None

    def walk(node):
        nonlocal query_id, target
        if isinstance(node, dict):
            if query_id is None and isinstance(node.get("query_id"), str):
                query_id = node["query_id"]
            if target is None and isinstance(node.get("fields"), dict):
                url = node.get("url") or node.get("presigned_url")
                if isinstance(url, str):
                    target = {"url": url, "fields": node["fields"]}
            if target is None:
                for key in ("presigned_url", "upload_url", "signed_url", "url"):
                    value = node.get(key)
                    if isinstance(value, str) and value.startswith("http"):
                        target = {"url": value, "fields": None}
                        break
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(data)
    return target, query_id


def upload_video():
    """Register the video with the session and push the bytes to S3."""
    registration = request_upload_url()
    # print("chat_upload response:")
    # print(json.dumps(registration, indent=2))

    target, query_id = _find_upload_target(registration)
    if target is None:
        raise RuntimeError("No presigned URL found in the chat_upload response.")

    with open(video_file, "rb") as handle:
        if target["fields"]:
            # Presigned POST: send the returned form fields plus the file.
            upload = requests.post(
                target["url"],
                data=target["fields"],
                files={"file": (video_file, handle, "video/mp4")},
            )
        else:
            # Presigned PUT: raw body upload.
            upload = requests.put(
                target["url"],
                data=handle,
                headers={"Content-Type": "video/mp4"},
            )
    upload.raise_for_status()
    print(f"Uploaded {video_file} -> HTTP {upload.status_code}")
    print(f"query_id: {query_id}")
    return query_id


def list_assets(query_id):
    """Check the status of files uploaded to this chat session.

    query_id is mandatory here; the API rejects the call without it.
    """
    payload = {
        "resource": "data",
        "method": "list_assets",
        "details": {
            "project_id": project_id,
            "session_id": session_id,
            "query_id": query_id,
            "db_type": db_type,
        },
    }
    return _post(project_base, payload, owner_headers)


PENDING_STATUSES = {"updating", "pending", "processing", "in_progress", "queued"}


def wait_for_asset(query_id, attempts=60, delay=5):
    """Poll list_assets until the video leaves the 'updating' state."""
    assets = {}
    for attempt in range(1, attempts + 1):
        assets = list_assets(query_id)
        statuses = {
            entry.get("search_status")
            for entry in assets.get("files", [])
            if entry.get("file_name") == video_file
        }
        print(f"list_assets attempt {attempt}: {statuses or assets}")
        if statuses and not (statuses & PENDING_STATUSES):
            return assets
        time.sleep(delay)
    raise RuntimeError(f"{video_file} never finished processing: {assets}")


def query_video(query_id, question="Explain what happens in this video."):
    """Ask a question with the uploaded video in context."""
    payload = {
        "action": "query",
        "session_id": session_id,
        "query_id": query_id,
        "project_id": project_id,
        "query": question,
        "response_format": {"type": "json"},
        "enable_history": True,
        "search_params": {
            "output_fields": ["source_name", "page_number", "tags", "url"]
        },
        "chat_upload": {
            "images": [],
            "docs": [],
            "audios": [],
            "videos": [video_file],
        },
    }
    return _post(query_base, payload, service_headers)


if __name__ == "__main__":
    returned_query_id = upload_video()
    wait_for_asset(returned_query_id)
    result = query_video(returned_query_id)
    print("query response:")
    print(json.dumps(result, indent=2))
