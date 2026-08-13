"""The core generate -> validate -> retry loop.

This is the piece worth understanding deeply: Ollama's format="json" only
guarantees syntactically valid JSON. It does NOT guarantee your Pydantic
schema is satisfied (right fields, right types, enum values, custom
validators). That's on us -- validate locally, and on failure, feed the
*specific* Pydantic error back to the model so it can self-correct.
"""

import time
from dataclasses import dataclass, field

import ollama
from pydantic import BaseModel, ValidationError

from core.prompts import build_prompt, build_retry_prompt

MODEL_NAME = "llama2-7b-chat"  # Ollama model name to use for structured generation

@dataclass
class GenerationResult:
    success: bool
    attempts: int
    latency_seconds: float
    parsed: BaseModel | None = None
    final_error: str | None = None
    raw_history: list[str] = field(default_factory=list)


def generate_structured(
    model: str,
    user_input: str,
    schema: type[BaseModel],
    max_retries: int = 3,
) -> GenerationResult:
    """Call `model` via Ollama, validate against `schema`, retry on failure.

    Returns a GenerationResult with attempt count and latency so the
    benchmark harness can score reliability, not just correctness.
    """
    messages = [{"role": "user", "content": build_prompt(user_input, schema)}]
    raw_history: list[str] = []
    start = time.perf_counter()

    for attempt in range(1, max_retries + 1):
        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            format="json",  # forces syntactically valid JSON, not schema-valid
            options={"temperature": 0.2},
        )
        content = response["message"]["content"]
        raw_history.append(content)

        try:
            parsed = schema.model_validate_json(content)
            return GenerationResult(
                success=True,
                attempts=attempt,
                latency_seconds=time.perf_counter() - start,
                parsed=parsed,
                raw_history=raw_history,
            )
        except ValidationError as e:
            error_text = str(e)
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content": build_retry_prompt(error_text)})
            last_error = error_text
        except Exception as e:
            # Malformed JSON entirely (not even parseable) -- still retry
            last_error = f"Could not parse as JSON: {e}"
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content": build_retry_prompt(last_error)})

    return GenerationResult(
        success=False,
        attempts=max_retries,
        latency_seconds=time.perf_counter() - start,
        final_error=last_error,
        raw_history=raw_history,
    )
