# Format-prompt benchmark harness

`format_prompt.py` exercises the second phase of the content workflow against
a local Ollama model. It does not modify canonical files under `content/`.

## Modes

- `structured-json` is the default. It sends `schema/game.schema.json` through
  Ollama's structured-output `format` field, parses the JSON response, validates
  it, and serializes it as YAML.
- `direct-yaml` sends the current production formatting prompt without a
  structured-output constraint, then parses and validates the returned YAML.

Keeping both modes makes it possible to measure whether constrained decoding
improves conformance without changing the source research brief.

`schema/game.schema.json` also stays within OpenAI's Structured Outputs subset:
every object property is required, every object rejects additional properties,
and the schema avoids unsupported conditional/composition keywords. The schema
can therefore be passed directly to `codex exec --output-schema` as well as to
Ollama's structured-output `format` field.

For an authenticated Codex CLI batch, format every research brief that has
human resolutions and no existing canonical YAML, validate each result, and
promote valid outputs to `content/`:

```sh
make format-codex-batch \
  MODEL="gpt-5.6-terra" \
  EFFORT="medium" \
  WORKERS="3"
```

The batch stops launching model calls after a usage/rate-limit response and is
safe to resume: a later invocation skips content files already promoted. Exact
prompts, JSONL events, responses, YAML, per-game reports, and a batch manifest
are stored under `benchmarks/results/format-prompt/`.

## Usage

From the repository root:

```sh
.venv/bin/python benchmarks/format_prompt.py \
  --model qwen3.5:27b-q4_K_M \
  --research content/research/jaws.md
```

Useful options:

```text
--mode structured-json|direct-yaml
--think auto|false|true|low|medium|high
--num-ctx 16384
--timeout 900
--progress-interval 10
--ollama-url http://127.0.0.1:11434
--results-dir benchmarks/results/format-prompt
```

Qwen models accept Boolean thinking settings. GPT-OSS models use `low`,
`medium`, or `high`. Use `--think auto` to omit the setting and retain the
model's default.

The harness prints run details immediately and an elapsed-time heartbeat every
10 seconds while Ollama is loading or generating. Set `--progress-interval 0`
to disable heartbeat messages.

## Results

Each invocation creates a timestamped directory:

```text
benchmarks/results/format-prompt/
└── jaws/
    └── 20260831T120000Z--qwen3.5-27b-q4_K_M--structured-json/
        ├── output.yaml
        ├── prompt.md
        ├── report.json
        └── response.json
```

`report.json` records schema validity, validation errors, model and mode,
research and prompt hashes, context and thinking settings, Ollama durations,
token counts, and output tokens per second. Generated run directories are
ignored by Git; the harness and its documentation remain versioned in the
repository.

A valid result means the output parses and conforms to the JSON Schema. It does
not establish factual accuracy. Review generated drafts against the research
brief before moving them into `content/`.

## Local sentence-level proofreading

`scripts/proofread_content.py` proofreads only prose-bearing fields in canonical
YAML. It sends short prompts sequentially through one persistent HTTP connection
to one warm Ollama model. Sentence results are cached, so an interrupted or
repeated run does not need to regenerate completed suggestions.

Run a review-only pass first:

```sh
make proofread-content MODEL="mistral:latest" START_SERVER="1"
```

The run writes `review.jsonl`, a manifest, and schema-valid corrected copies
under `benchmarks/results/proofread/`; it does not modify `content/`. Inspect the
proposals, then use `APPLY=1` to atomically apply safe changes:

```sh
make proofread-content MODEL="mistral:latest" APPLY="1" START_SERVER="1"
```

Suggestions that alter numbers, symbols, protected capitalized terms, or text
length substantially are flagged in `review.jsonl` and never auto-applied. Use
`LIMIT="25"` for a quick calibration run. This is a grammar and copy-edit pass,
not factual verification against the research briefs.
