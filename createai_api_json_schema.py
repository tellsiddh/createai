import json
import requests
from config import poc_service_key, createai_base_url

query = {
    "student": {
        "name": "Aaliyah Flores",
        "college": "College of Liberal Arts and Sciences",
    },
    "faculty": {
        "name": "Dr. Jane Smith",
    },
    "selected_category": "Support Services",
    "concern_text": ("medical guidance \n\n" "i want to kill myself"),
    "concern_category": None,
    "flags": {
        "urgent": False,
        "do_not_inform_student": False,
        "support_only": False,
    },
}

system_prompt = """# Faculty Support Routing Playbook (v1-baseline)

You are a routing assistant for ASU faculty connecting students to support resources.
Read the faculty concern and selected destination category, then choose the best email destination.

## Categories

### Support Services
- Housing, roommate, dorm issues -> housing@example.edu (Housing Team)
- Financial aid, scholarships, billing -> finaid@example.edu (Financial Aid Team)
- Accessibility, accommodations -> accessibility@example.edu (Accessibility Services)
- General support when no sub-concern matches -> support@example.edu (General Support)

### Student Concern Form
- Harassment, discrimination, retaliation, classroom safety -> student-concern@example.edu (Student Concern Committee)
- Academic integrity reports -> integrity@example.edu (Academic Integrity Office)

### Writing Center
- Any writing help, citations, drafts, thesis formatting -> writing@example.edu (Writing Center)

### Tutoring Center
- STEM subjects (math, science, CS) -> stem-tutoring@example.edu (STEM Tutoring)
- Humanities subjects -> humanities-tutoring@example.edu (Humanities Tutoring)
- General tutoring when subject unclear -> tutoring@example.edu (Tutoring Center)

## Rules
1. Respect the faculty-selected category unless the concern clearly belongs elsewhere; explain in rationale if you override.
2. Pick exactly one destination email from the playbook.
3. Set status to "needs_clarification" if the concern is ambiguous between two destinations in the same category.
4. Set status to "needs_human_review" for crisis or safety language.
5. Set confidence between 0 and 1.
6. Include every required field from the schema, even when the value is null, false, or an empty array.
7. Use the exact schema field names. Do not use aliases like destination_email, destination_name, or team.
8. Return JSON only matching the provided schema."""

payload = {
    "request_source": "override_params",
    "query": json.dumps(query, indent=2),
    "enable_search": False,
    "enable_history": False,
    "response_format": {
        "type": "json",
    },
    "model_params": {
        "system_prompt": system_prompt,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "faculty_support_routing",
                "description": (
                    "Return only one JSON object with no markdown fences, no prose, "
                    "and no extra keys. Do not use flat fields like "
                    "destination_email or destination_name; use the nested "
                    "destination object exactly as defined."
                ),
                "strict": True,
                "schema": {
                    "type": "object",
                    "description": (
                        "Required shape: status, selected_category, sub_concern, "
                        "destination.name, destination.email, destination.type, "
                        "confidence, rationale, matched_rules, flags.urgent, "
                        "flags.safety, flags.do_not_inform_student, and "
                        "clarification_question. Include every required field."
                    ),
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": (
                                "Field rule: use routed when one destination is clear; "
                                "needs_clarification when ambiguous; "
                                "needs_human_review for crisis or safety; no_route "
                                "when nothing fits."
                            ),
                            "enum": [
                                "routed",
                                "needs_clarification",
                                "needs_human_review",
                                "no_route",
                            ],
                        },
                        "selected_category": {
                            "type": "string",
                            "description": (
                                "Field rule: echo the faculty-selected category unless "
                                "you override it; explain any override in rationale."
                            ),
                            "enum": [
                                "Support Services",
                                "Student Concern Form",
                                "Writing Center",
                                "Tutoring Center",
                            ],
                        },
                        "sub_concern": {
                            "description": (
                                "Field rule: short label for the matched rule, such as "
                                "Financial aid / billing, Housing, Accessibility, "
                                "Academic integrity, Writing help, STEM tutoring, or "
                                "Humanities tutoring. Use null if none applies."
                            ),
                            "type": [
                                "string",
                                "null",
                            ],
                        },
                        "destination": {
                            "type": "object",
                            "description": (
                                "Field rule: nested destination object for exactly one "
                                "destination from the playbook. Do not use flat fields "
                                "like destination_email, destination_name, or team."
                            ),
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": (
                                        "Field rule: pick exactly one destination name "
                                        "from the playbook. For financial aid concerns, "
                                        "use Financial Aid Team."
                                    ),
                                },
                                "email": {
                                    "type": "string",
                                    "description": (
                                        "Field rule: pick exactly one destination email "
                                        "from the playbook. For financial aid concerns, "
                                        "use finaid@example.edu."
                                    ),
                                },
                                "type": {
                                    "type": "string",
                                    "description": (
                                        "Field rule: use team for office or team inboxes, "
                                        "individual for a named person, and form_link for "
                                        "form-only routes."
                                    ),
                                    "enum": [
                                        "team",
                                        "individual",
                                        "form_link",
                                    ],
                                },
                            },
                            "required": [
                                "name",
                                "email",
                                "type",
                            ],
                            "additionalProperties": False,
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Field rule: number between 0 and 1.",
                        },
                        "rationale": {
                            "type": "string",
                            "description": (
                                "Field rule: brief explanation of why the selected "
                                "destination is the best match, including any category "
                                "override if one was made."
                            ),
                        },
                        "matched_rules": {
                            "type": "array",
                            "description": (
                                "Field rule: include one or more playbook rule strings "
                                "that were applied."
                            ),
                            "items": {
                                "type": "string",
                                "description": (
                                    "One playbook rule string, for example: Financial "
                                    "aid, scholarships, billing -> finaid@example.edu "
                                    "(Financial Aid Team)."
                                ),
                            },
                        },
                        "flags": {
                            "type": "object",
                            "description": (
                                "Field rule: nested boolean flags. Copy input flags when "
                                "present; set safety true for crisis or safety concerns."
                            ),
                            "properties": {
                                "urgent": {
                                    "type": "boolean",
                                    "description": (
                                        "Field rule: copy urgent from input flags when "
                                        "present; otherwise set true only when the concern "
                                        "needs urgent attention."
                                    ),
                                },
                                "safety": {
                                    "type": "boolean",
                                    "description": (
                                        "Field rule: true for crisis, safety, harassment, "
                                        "discrimination, retaliation, or classroom safety "
                                        "concerns; otherwise false."
                                    ),
                                },
                                "do_not_inform_student": {
                                    "type": "boolean",
                                    "description": (
                                        "Field rule: copy do_not_inform_student from input "
                                        "flags when present; otherwise false."
                                    ),
                                },
                            },
                            "required": [
                                "urgent",
                                "safety",
                                "do_not_inform_student",
                            ],
                            "additionalProperties": False,
                        },
                        "clarification_question": {
                            "description": (
                                "Field rule: one question when status is "
                                "needs_clarification; otherwise null."
                            ),
                            "type": [
                                "string",
                                "null",
                            ],
                        },
                    },
                    "required": [
                        "status",
                        "selected_category",
                        "sub_concern",
                        "destination",
                        "confidence",
                        "rationale",
                        "matched_rules",
                        "flags",
                        "clarification_question",
                    ],
                    "additionalProperties": False,
                },
            },
        },
    },
}

response = requests.post(
    createai_base_url,
    headers={
        "Authorization": f"Bearer {poc_service_key}",
        "Content-Type": "application/json",
    },
    json=payload,
)
response_text = response.json()["response"]
response_data = json.loads(response_text)
print(json.dumps(response_data, indent=2))
