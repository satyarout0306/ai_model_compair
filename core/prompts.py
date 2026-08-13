import json
from pydantic import BaseModel


def build_prompt(user_input: str, schema: type[BaseModel]) -> str:
    schema_json = json.dumps(schema.model_json_schema(), indent=2)
    return f"""You must respond with ONLY valid JSON that matches this JSON Schema exactly.
Do not include any explanation, markdown formatting, or code fences — just the raw JSON object.

JSON Schema:
{schema_json}

Task input:
{user_input}

Respond with the JSON object now:"""


def build_retry_prompt(error_message: str) -> str:
    return f"""Your previous response failed schema validation with this error:

{error_message}

Fix the JSON so it fully satisfies the schema. Respond with ONLY the corrected JSON object,
no explanation, no markdown."""