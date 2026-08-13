# Offline Model Compairision

Benchmark local Ollama models on their ability to produce valid, schema-conformant
JSON output — with an automatic validate → retry-on-failure loop.

## What this measures

For each (model, task) pair, across several test prompts:
- **First-try success rate** — did the model get valid JSON matching the Pydantic schema on attempt 1?
- **Avg attempts to success** — how many retries (with the validation error fed back) were needed?
- **Latency** — wall-clock time per generation
- **Failure rate** — how often it never validated within `max_retries`

## Setup

```bash
# 1. Install Ollama: https://ollama.com/download
# 2. Pull a few models to compare (mix sizes so results have spread)
ollama pull llama3.2:3b
ollama pull qwen2.5:7b
ollama pull phi3:mini

# 3. Python deps
pip install -r requirements.txt --break-system-packages
```

## Project layout

```
offline-llm-bench/
├── schemas/           # Pydantic models, one file per task (easy → hard)
│   ├── simple.py       # flat object: name, age
│   ├── medium.py       # nested object: invoice with line items
│   └── hard.py         # enums, optional fields, cross-field validators
├── core/
│   ├── generator.py    # the generate → validate → retry loop
│   └── prompts.py      # prompt templates that inject the JSON schema
├── benchmarks/
│   ├── tasks.py         # test cases per schema (input text + expected shape)
│   └── run_benchmark.py # orchestrates model x task x test case, logs results
├── results/            # CSV/JSON output from benchmark runs (gitignored)
├── tests/               # unit tests for the retry loop and schemas
└── cli.py               # simple CLI entrypoint: `python cli.py run` / `python cli.py report`
```

## Quickstart

```bash
# 1. Generate a synthetic eval set WITH ground truth (so accuracy can be scored,
#    not just "was the JSON schema-valid"). Deterministic via --seed, so results
#    are reproducible across runs.
python -m benchmarks.generate_data --count 20

# 2. Run the full benchmark across all configured models
python cli.py run

# 3. Print a summary report from the latest results
python cli.py report
```

## Where the test data comes from

`benchmarks/generate_data.py` builds a random Pydantic instance first (so the
correct answer is known), then renders it into natural-language text a model
has to extract from. This gives you real ground truth to score field-level
accuracy against -- not just whether the JSON happened to validate. If
`benchmarks/generated_cases.json` exists, the runner uses it automatically;
otherwise it falls back to the small hand-written cases in `benchmarks/tasks.py`.

Other places to pull real-world (unlabeled) text from if you want to stress-test
robustness on messier input later: Kaggle's "Customer Support Ticket Dataset"
(maps to the `Ticket` schema) or "Invoice OCR" datasets (maps to `Invoice`).
You'd need to hand-label a sample of these for accuracy scoring.

## How the retry loop works

1. Build a prompt that includes the task instructions + `schema.model_json_schema()`.
2. Call Ollama with `format="json"` (forces syntactically valid JSON, not schema-valid).
3. Try `YourSchema.model_validate_json(response)`.
4. On `ValidationError`, append the model's bad output + the actual error message to the
   conversation and ask it to fix it. This is the important bit — feeding back the *specific*
   validation error (not just "try again") is what makes retries actually converge.
5. Give up after `max_retries` and log a failure.

## Next steps / stretch goals

- Swap the hand-rolled loop for the `instructor` library and compare reliability.
- Try Ollama's native JSON-schema-constrained decoding (`format=<schema>` instead of `format="json"`)
  and see if it beats prompt-only enforcement.
- Wrap `core/generator.py` in a small CLI chat assistant that always returns structured actions
  (e.g. a local "offline assistant" that outputs `{intent, args}` for a fixed tool set).
