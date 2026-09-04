# Pinball Commentary Binder Generator

Generate compact, two-column PDF quick references for live pinball commentary. Each game is described in YAML and rendered as a letter-sized sheet covering core rules, important shots, match strategy, danger zones, commentary cues, trivia, and venue notes.

`manual.yaml` is the single manifest for included games, binder order, and
permanent printed page labels.

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
`schema/game.schema.json` before writing any PDFs. Full builds validate every
manifest entry first, so validation errors do not produce a partially rebuilt
set of files.

Render every game in `manual.yaml` and merge `output/binder.pdf`:

```sh
make all
```

Color images are used by default. To render with black-and-white images, use
the `-bw` targets:

```sh
make game-bw-playboy-bally-1978
make all-bw
```

The equivalent command-line options are `--color` and
`--black-and-white` (or `--bw`). Black-and-white PDFs are written with a
`-bw` suffix, so they can coexist with the color output.

The binder opens with a simple title page as leaf 1, without a printed number.
Its order and permanent page labels come from `manual.yaml`. The initial printed
edition has 108 games on pages 2 through 217. New games use decimal page labels,
so adding one never renumbers an already-printed page. Games with internet-downloadable
code show the code version, its release date, and the date when the content file
was last updated in Git. Games with materially different gameplay ROMs show the
ROM revision and Git update date. Fixed-rule games omit that footer copy. Binder
page numbers are still shown for every game.

### Maintaining an already-printed manual

Use the guided add workflow for a new game:

```sh
make add
make add GAME="Jaws Premium Stern 2024"
```

The wizard confirms the game ID and its suggested alphabetical location, reserves
two decimal page labels, and walks through research, YAML formatting, image setup,
shot labels, black-and-white image generation, validation, and PDF rendering.
Existing artifacts are detected so an
interrupted add can be resumed by running the same command again. `manual.yaml` is
changed only after the new game validates and you explicitly confirm its page
assignment. Packet generation is a separate confirmation: declining or cancelling
that step leaves the new manifest entry saved. You can generate its replacement
packet later with `make update GAME="<game-id>"`.

For example, a game inserted between printed pages 19 and 20 receives pages 19.1
and 19.2. A later insertion can use 19.01 and 19.02; previously assigned labels
remain unchanged.

Use the update workflow for an existing game:

```sh
make update
make update GAME="jaws-pro-stern-2024"
```

You can refresh researched content, replace the image, redo shot labels, review
venue notes, or build a packet from edits already made. Refreshed YAML is staged
and displayed as a diff before it replaces the current content. Updates retain the
game's existing page labels.

Both workflows can create a four-page file under `output/print/`. The packet
contains the preceding binder leaf, both leaves of the added or updated game, and
the following binder leaf. Print it at actual size, double-sided, flipping on the
long edge. At the beginning of the binder the title page is used as the preceding
leaf; at the end a blank final leaf is added.

The `add` and `update` workflows ask whether the packet should be color or
black-and-white only when you move to the PDF-generation step. Full builds use
`make all` or `make all-bw`. No color choice is stored in `manual.yaml`.

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

Review Venue Notes one game and one note at a time:

```sh
make review-venue-notes
make review-venue-notes GAME="playboy-bally-1978"
```

Press Enter or `a` to accept a note, `r` to remove it, `e` to enter replacement
text, or `q` to save completed decisions for the current game and stop. Only the
`venue_notes` block in each YAML file is rewritten.

## Adding a game

1. Create `content/<id>.yaml`, following `schema/game.schema.json` and an existing content file. Its `id` must match the filename stem.
   Every game must include `rules_basis`. Use `kind: code` with an exact version
   and `YYYY-MM-DD` release date for gameplay code distributed as an internet
   download; use `kind: rom` with a gameplay-ROM revision when materially
   different ROM versions exist; otherwise use `kind: fixed` with null version
   and release-date fields. Sound and display ROMs do not count unless they
   change gameplay rules. Use `Factory stock` as the ROM version only when a
   stock-versus-custom distinction matters and no numbered factory identifier
   can be established.
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

### Placing shot labels

Open the browser-based shot label editor for a specific game:

```sh
make shot-labels GAME="jaws-pro-stern-2024"
```

Or omit the game to open the first selected game whose labels are missing or
stale:

```sh
make shot-labels
```

Click the playfield once for each Important Shots entry. The editor immediately
renders each numbered marker with the same image renderer used by the PDF and
shows the shot description and difficulty while placing it. Use **Another #**
to place the same number at multiple physical targets, **Back** to remove and
reposition the previous action, **Skip this label** when a numbered shot should
not appear on the image, and **Start over** to clear the pass. After a save, the
same editor loads the next selected game whose labels are missing or stale.
**Skip game** discards the current game's unsaved placements and loads the next
game. **Stop without saving this game** ends the batch and closes the editor tab
(or shows a close-tab fallback if the browser blocks scripted tab closure).

Placements are stored separately from researched content in
`content/shot-labels/<id>.yaml`. Each file records absolute `x` and `y`
coordinates, the oriented source-image dimensions, and a SHA-256 fingerprint.
A changed image, changed shot list, or changed diagram numbering makes the
placements stale and stops the build with an instruction to redo them. Games
without a shot-label file continue to render with an unannotated image, which
allows the collection to be labeled incrementally.

## Manual order and page labels

`manual.yaml` contains the complete ordered set of games included in the binder:

```yaml
version: 1
games:
- id: ac-dc-pro-stern-2012
  pages: ["2", "3"]
- id: example-added-game-2026
  pages: ["3.1", "3.2"]
- id: addams-family-bally-1992
  pages: ["4", "5"]
```

Each entry must have a matching `content/<id>.yaml` file, two unique increasing
page labels, and a unique kebab-case ID. Adding or removing an entry controls
whether it is part of full builds. Prefer `make add` for insertions so decimal
labels and printable packets are assigned safely.

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

### Fetching a game image

Open a Google Image search for a game from `content/list_of_games.txt`:

```sh
make game-image GAME="Jaws (Pro) Stern 2024"
```

The description can also be supplied positionally. If it is omitted, the
command scans `content/list_of_games.txt` in order and selects the first game
that does not already have an image:

```sh
make game-image 'Jaws (Pro) Stern 2024'
make game-image
```

The command opens the search in Google Chrome. Download the desired image,
return to the terminal, and press Enter. The newest completed file added to
`~/Downloads` after the search opened is prepared and copied into `images/`. A matching
`content/research/<id>.md` supplies the destination basename when available;
otherwise, the basename is derived from the entered game name. Before copying,
the command reports the image's pixel dimensions. Images with a long edge below
1000 pixels are treated as low resolution and are rejected by default; confirm
the override only when a better source is unavailable.

Every accepted download is opened for cropping before it is converted to the
canonical WebP. If XnView MP is installed, the image opens there with instructions
to use a fixed 408:750 crop. Otherwise it opens in Preview and the workflow prints
the largest exact pixel selection for the downloaded dimensions, such as
`1292x2375` for a `1600x2400` image. Save the crop in place and return to the
terminal; the workflow verifies the ratio before copying the image. Low-resolution
replacement downloads use the same crop step. A 1% aspect-ratio tolerance allows
the small pixel differences produced by manual crop tools.

In the add and update workflows, a newly downloaded and cropped image proceeds to
shot-label placement and then black-and-white variant generation. The selected
black-and-white companion is created even when the immediate print packet will be
in color, so either format is ready later.

For a one-off pass over existing low-resolution images, search for replacement
playfield images in Chrome:

```sh
make game-image-low-res
```

This scans color images whose long edge is below 1000 pixels and opens a Google
Image search for each corresponding game in Chrome. Download a better result
and press Enter in the terminal. Enter `s` to skip or `q` to stop.

The replacement must pass the resolution check and is converted to preserve
the original filename and format. The low-resolution original is retained in
`images/low-res-backup/`. Any existing black-and-white companion is moved into
the backup directory too, allowing `make game-image-bw` to regenerate it from
the improved source. To inspect just one game or image path, provide it
explicitly:

```sh
make game-image-low-res GAME="Jaws (Pro) Stern 2024"
make game-image-low-res images/jaws-pro-stern-2024.jpg
```

Create a selected black-and-white companion for one color image:

```sh
make game-image-bw GAME="Jaws (Pro) Stern 2024"
```

With no game argument, the command processes every color image that does not
already have a corresponding `<id>-bw.*` file:

```sh
make game-image-bw
```

For each image, it generates four grayscale and posterized variants in
parallel, opens them together in Preview, and asks which one to keep. During
batch review, it also prepares the next two image sets in the background.
Choose by number or variant name. Enter `s` to skip the current image or `q` to
stop the batch. The selected candidate is saved as `images/<id>-bw.png`;
temporary variants are removed after each choice.

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

Audit the rules-basis classification, code release dates, and ROM versions for
every content file without rendering PDFs:

```sh
make audit-rules-basis
```

## Code organization

`main.py` owns only argument parsing, CLI-specific validation, and command
dispatch. Application behavior lives in the `pinscripts` package, grouped by
feature: AI-assisted workflows, content validation and selection, images,
venue-note review, and PDF builds. The existing modules under `scripts/`
remain the lower-level rendering and image-processing backends.

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
