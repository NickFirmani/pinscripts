# Pinball Commentary Binder Generator

Generate compact, two-column PDF quick references for live pinball commentary. Each game is described in YAML and rendered as a letter-sized sheet covering core rules, important shots, match strategy, danger zones, commentary cues, trivia, and venue notes.

Games are registered in `pins.yaml`

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
4. Render the game. `main.py` validates the YAML first; inspect the resulting PDF after validation succeeds.

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

`prompts/generate-game.md` is a prompt template for drafting a commentator-focused game sheet with an LLM. Generate a ready-to-use prompt with:

```sh
make prompt GAME="Jaws (Stern, 2024)"
```
Save the LLM's YAML under `content/` and fact-check it before rendering. Pinball rules can vary by software revision, tournament settings, and machine setup.

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
