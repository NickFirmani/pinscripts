# Pinball Commentary Binder

Generate compact, two-column PDF quick references for live pinball commentary. Each game is described in YAML and rendered as a letter-sized sheet covering core rules, important shots, match strategy, danger zones, commentary cues, trivia, and venue notes.

Games are registered in `pins.yaml`

## Requirements

- Python 3
- `make` (optional, but recommended)

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

Render every enabled game that has a content file:

```sh
make all
```

Build the individual PDFs and merge them, in `pins.yaml` order, into a printable binder:

```sh
make binder
```

Generated files are written to `output/`:

```text
output/
├── playboy-bally-1978.pdf
└── binder.pdf
```

Clean generated output:

```sh
make clean
```

## Adding a game

1. Add the game to `pins.yaml`. Its `id` is the filename stem used throughout the project.
2. Create `content/<id>.yaml`, following `schema/game.schema.json` and an existing content file.
3. Optionally add a playfield or machine image at `images/<id>.jpg` and set the YAML `image` field to that path.
4. Validate the YAML, then render the game and inspect the resulting PDF.

For example:

```yaml
# pins.yaml
pins:
  - id: example-game-1999
    name: Example Game
    manufacturer: Example
    year: 1999
    enabled: true
```

### Generating a content draft

`prompts/generate-game.md` contains a prompt and exact YAML shape for drafting a commentator-focused game sheet with an LLM. Replace `{{GAME}}` with the machine name and identifying details, save the returned YAML under `content/`, and fact-check it before rendering. Pinball rules can vary by software revision, tournament settings, and machine setup.
