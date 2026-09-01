# Pinball Commentary Binder Generator

Generate compact, two-column PDF quick references for live pinball commentary. Each game is described in YAML and rendered as a letter-sized sheet covering core rules, important shots, match strategy, danger zones, commentary cues, trivia, and venue notes.

`pins.yaml` controls which game files are included in bulk builds.

## Requirements

- Python 3
- `make` (optional, but recommended)
- ImageMagick (`magick`, required only for processing image variants)

On macOS, install ImageMagick with Homebrew:

```sh
brew install imagemagick
```

For other platforms, use the
[official ImageMagick installation instructions](https://imagemagick.org/script/download.php).
If `magick` is unavailable, the image helper exits with an installation message;
the rendering and content-generation commands remain usable.

## Setup

Create a local virtual environment and install the dependencies:

```sh
make install
```

Or, to set it up manually:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Usage

Render one game by ID:

```sh
make game-playboy-bally-1978
```

Every render command validates the selected YAML against
`schema/game.schema.json` before writing any PDFs. Bulk and binder builds
validate all available content first, so validation errors do not produce a
partially rebuilt set of files.

Render the games selected by `pins.yaml`:

```sh
make all
```

Color images are used by default. To render with black-and-white images, use
the `-bw` targets:

```sh
make game-bw-playboy-bally-1978
make all-bw
make binder-bw
```

The equivalent command-line options are `--color` and
`--black-and-white` (or `--bw`). Black-and-white PDFs are written with a
`-bw` suffix, so they can coexist with the color output.

Build the individual PDFs and merge them into a printable binder:

```sh
make binder
```

Generated files are written to `output/`:

```text
output/
├── playboy-bally-1978.pdf
├── playboy-bally-1978-bw.pdf
├── binder.pdf
└── binder-bw.pdf
```

Clean generated output:

```sh
make clean
```

## Adding a game

1. Create `content/<id>.yaml`, following `schema/game.schema.json` and an existing content file. Its `id` must match the filename stem.
   Every game must include `skill_shots` and `features`, using an empty array
   when the research audit confirms that the game has none. Skill shots use
   the dedicated `skill_shots` field; ball saves, video modes, extra balls,
   player controls, mystery awards, and other unusual utilities belong in
   `features`.
2. Optionally add a playfield or machine image at `images/<id>.jpg` and set
   the YAML `image` field to that path. The image is assumed to be in color.
   To support black-and-white output, add `images/<id>-bw.jpg` beside it; the
   YAML should continue to reference the color filename.
3. Render the game. `main.py` validates the YAML first; inspect the resulting PDF after validation succeeds.

## Selecting games

`pins.yaml` contains only ordered lists of pin IDs:

```yaml
enabled: []

disabled:
  - example-game-1999
```

When `enabled` is empty, bulk and binder builds include every YAML file directly
under `content/`, sorted by ID, except IDs in `disabled`. This default makes a
new content file eligible automatically.

When `enabled` is non-empty, it is an explicit allowlist and its order becomes
the binder order. Every explicitly enabled ID must have a matching
`content/<id>.yaml` file. Disabled IDs do not require content files. IDs must be
unique kebab-case strings, and the same ID cannot appear in both lists.

### Generating a content draft

Content generation is split between two prompts so each model can focus on
what it does best. The templates are `prompts/research-game.md` and
`prompts/format-game-yaml.md`. Generate a research prompt for a high-power,
general-purpose model with internet access. The command prints the prompt,
offers to copy it to the macOS clipboard (the default when pressing Enter),
and then waits for the response:

```sh
make game-research GAME="Jaws Premium 2024"
```

Once the game description is known, the command sets the terminal title to
that description when the terminal supports title escape sequences.

The description can instead be supplied positionally. Quote it so the shell
passes spaces and parentheses through to `make`:

```sh
make game-research 'JAWS (Pro) (Stern, 2024)'
```

Omit `GAME` to enter the description interactively:

```sh
make game-research
```

After copying the prompt into ChatGPT, return to the waiting command. Enter a
research ID and paste the multiline response. Finish with a line containing
only `::end` (or press Ctrl-D). The response is saved as
`content/research/<id>.md`. Existing files require overwrite confirmation.

Before formatting, the command displays the research brief's `Questions for
the humans` section and asks each numbered question individually. Enter a
multiple-choice letter or a free-text answer. For older briefs without numbered
questions, paste the answers together or enter an explicit `none`. The command
saves the answers in a `Human resolutions` section in the research file.

The command then prints a schema-constrained JSON formatting prompt and offers
to copy it. Paste that prompt into ChatGPT, return to the terminal, and paste
the JSON response using the same `::end` terminator. The command parses and
validates the JSON, verifies its ID and image path, and writes the final artifact
to `content/<id>.yaml`. Existing YAML files also require overwrite confirmation.

To skip research and format an existing brief, pass its ID (the filename without
`content/research/` or `.md`):

```sh
make game-format jaws-pro-2024
```

Run `make game-format` with no ID to enter it interactively. If the brief already
has a non-empty `Human resolutions` section, it is reused. Otherwise, the command
prompts for the human answers before continuing to the formatting prompt.

Fact-check the generated YAML before rendering. Pinball rules can vary by
software revision, tournament settings, and machine setup.

### Benchmarking the formatting phase

The Ollama format-prompt harness defaults to the research brief at
`content/research/jaws.md` and schema-constrained JSON output. It validates the
model response and serializes it to YAML for inspection:

```sh
make format-benchmark MODEL="qwen3.5:27b-q4_K_M"
```

The command prints an elapsed-time heartbeat every 10 seconds. Override it
when desired with `PROGRESS_INTERVAL=5`, or use `PROGRESS_INTERVAL=0` to turn
off heartbeat messages.

Select another research brief or compare the original direct-YAML prompt:

```sh
make format-benchmark \
  MODEL="qwen3.5:9b-q8_0" \
  RESEARCH="content/research/jaws.md" \
  MODE="direct-yaml"
```

Run artifacts are stored under `benchmarks/results/format-prompt/` and include
the exact prompt, raw Ollama response, normalized YAML, validation errors,
token counts, and timing. See `benchmarks/README.md` for details.

## Validation errors

Invalid YAML syntax and schema violations stop the build with a non-zero exit status. Errors identify the content file and field path, for example:

```text
ERROR: validation failed: content/example-game-1999.yaml
  - $.shots[0].risk: 'Very High' is not one of ['Low', 'Medium', 'Medium-High', 'High']
```

### Processing images

Generate grayscale, posterized, and black-and-white print variants of a playfield image:

```sh
make process-images IMAGE="images/example-game-1999.jpg"
```

By default, the variants are written beside the source image in
`<source-name>-variants/`. To choose another directory, set `OUTPUT_DIR`:

```sh
make process-images IMAGE="images/example-game-1999.jpg" OUTPUT_DIR="output/image-variants"
```
