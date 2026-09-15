# Pinball Commentary Binder Generator
A tool for generating compact, two-page pinball commentary references for streaming.

## Local Setup
The project is mostly python, with a few external requirements 
- Python3 
- ImageMagick (for image conversion). Typically installed with `brew install imagemagick`
- XnView MP (for image cropping) from https://www.xnview.com/en/xnviewmp/

```sh
make setup
```
Run `make` or `make help` at any time to see the supported commands, grouped by workflow.

# Main Catalog (all games, not specific to a venue)
Builds a PDF of all games in the content directory

```sh
make catalog-build 
# optional MODE argument for black-and-white or both bw and color
make catalog-build MODE=[color (default) | bw | both]
```
Outputs are located at `output/catalog.pdf` and/or `output/catalog-bw.pdf`. Catalog pages use ordinary sequential numbering and contain no venue-specific notes.

## Adding a new game
Run the interactive game add flow. It will walk you through the AI based research, formatting, image, black-and-white image, and shot-label stages.

```sh
make game-add GAME="Jaws Prem/LE Stern 2024"
```

`make game-add` is resumable and safe to run in several terminals at the same time.

## Updating a game
Run the interactive game-update flow to refresh researched content, recrop or replace the playfield image, redo shot labels, or after a manual update to one of the content YAML files.

```sh
make game-update GAME=jaws-pro-stern-2024
```
After the update, the command validates every binder containing the game. When requested, one replacement printable packet is generated for each affected printed binder, using that binder's durable pages and specific venue notes.

# Printed physical binders (specific to a venue)
For printed binders located on-site, the manifests are stored in the `binders` directory. These manifests track printed page numbers and venue-specific notes.

For example, the **lyons-classic-pinball** binder can be built with its actual page numbers and venue specific notes:

```sh
make binder-build BINDER=lyons-classic-pinball # MODE=[color (default) | bw | both]
```
Outputs are written to `output/binders/`

## Creating a new Binder

### Create a list of games fom Pinball Map or a Text File
Pass a numeric location ID or a map URL from the Pinball Map website:

```sh
make binder-create \
  BINDER=one-up-westminster \
  MAP='https://pinballmap.com/map/?by_location_id=25303'
```
The importer reads the public HTML used by the Pinball Map website. It fetches only the selected location and its machine-list fragment.

If fetching fails, or you prefer to copy the lineup yourself:

```sh
make binder-create BINDER=my-binder TITLE="My Binder"
```
Paste one game per line in this form, followed by `::end` or `CMD+D`

```text
The Addams Family (Bally, 1992)
JAWS (LE) (Stern, 2024)
::end
```
Alternatively a text file containing one catalog ID or unambiguous game name per line can be input

```sh
make binder-create \
  BINDER=my-event \
  TITLE="My Event" \
  GAMES_FILE=games.txt
```

### Create the front and spine inserts
Generate a printable front cover and a spine insert for a binder. Print at 100% (without scaling) on 8.5x11 paper, then trim to size.

```sh
make binder-cover BINDER=lyons-classic-pinball # SIZE=[1, 1.5, 2] (optional size of binder spine in inches)
```

### Adding games to a draft binder
After creating a binder, the following command can be run, in one or more terminals.

```sh
make binder-populate BINDER=one-up-westminster
```
The workflow first lists closely named catalog entries so you can select a matching game from the catalog before adding anything. If there is not an existing catalog entry, the workflow will guide you through the research and content creation process.

### Checking the status of a binder
```sh
make binder-status BINDER=one-up-westminster
```
Returns the current state of the binder, including the number of unresolved games.

### Printing a binder / Marking a binder as printed
Create the final binder PDF:
```shell
make binder-build BINDER=my-binder # MODE=[color (default) | bw | both]
```
Outputs are written to `output/binders/`. The binder is still in draft mode after this step.

```sh
make binder-mark-printed BINDER=my-binder
```
A draft binder cannot be marked printed while unresolved games remain. Additions and removals are alphabetized and the pages are renumbered before a binder is marked printed.

After a binder is marked as printed, existing page labels never change:

- additions receive decimal labels between their neighbors
- removals become `present: false` tombstones and reserve their old labels
- venue notes live only in that binder entry

Print double-sided at actual size, flipping on the long edge.


## Printed Binder Maintenance (add/update games, venue notes)

All the following commands generate a properly page-numbered printable PDF, called a packet, that is suitable to be inserted into the existing printed binder seamlessly.

### Adding one game to a printed binder
```sh
make binder-add BINDER=my-binder GAME=jaws-pro-stern-2024
```
`binder-add` runs the complete creation flow for a new game. It assigns permanent decimal page labels for insertion into an existing printed binder.

### Updating one game in a printed binder
```sh
make binder-update BINDER=my-binder GAME=jaws-pro-stern-2024
```
`binder-update` walks through the flow of updating the content or venue notes for a game already present in the binder. It generates a replacement packet with the same page labels as the original.

### Removing a game from a binder
```sh
make binder-remove BINDER=my-binder GAME=jaws-pro-stern-2024
```

### Updating venue notes for a game in a binder
```sh
make binder-notes BINDER=my-binder GAME=jaws-pro-stern-2024
```

### Incomplete Assets / Project Doctor

For issues with project setup, or to resolve quality issues with images, shot labels, or binder population, run the project doctor:

```sh
make doctor
make doctor GAME=jaws-prem-le-stern-2024
make doctor BINDER=one-up-westminster
```
The outputs include:
 - invalid catalog or binder data, 
 - missing or unreadable color and black-and-white images 
 - color images below the 1000-pixel long-edge threshold, 
 - missing or stale shot labels, 
 - unresolved binder games, and 
 - orphaned image or label files. 

It then offers fixes. Declining a fix leaves the item untouched and the report prints the exact Make command to run later.

### Synchronize a binder with the Pinball Map

```sh
make binder-sync BINDER=one-up-westminster
```
New unresolved listings are added to the binder's pending queue, to be processed by `make binder-populate`, while games found only in the binder are always retained.

# Development Information

## Data model

`content/*.yaml` is the master game catalog. Each file contains reusable rules, strategy, and commentary material for one gameplay-distinct edition. Playfield image paths are derived from each game ID as `images/<id>.webp` and `images/<id>-bw.webp`.

Equivalent cosmetic trims (with the same playfield/gameplay) share one catalog entry. 
 - Modern Stern Premium and LE machines use the display suffix `Prem/LE` and ID segment `prem-le`; Pro remains a separate entry. 
 - Jersey Jack Limited and Collector's Editions use `LE/CE` and `le-ce`; Standard Edition remains separate.

`binders/*.yaml` records one printable or already-printed binder. A binder owns:

- its title and draft/printed state
- permanent physical page labels
- its manually curated game lineup
- venue notes for each game
- an optional Pinball Map location (used only as an advisory reference)

- The saved binder manifest is always the source of truth. Building a PDF never contacts Pinball Map and never changes a lineup.

## Project health and validation
Run the project doctor after cloning, before a large print, or whenever you want to work through incomplete assets:

```sh
make doctor
make doctor GAME=jaws-prem-le-stern-2024
make doctor BINDER=one-up-westminster
```
Doctor scans the requested scope before changing anything. It reports invalid catalog or binder data, missing or unreadable color and black-and-white images, color images below the 1000-pixel long-edge threshold, missing or stale shot labels, unresolved binder games, and orphaned image or label files. It then offers fixes in dependency order: color images, image upgrades, B&W images, shot labels, and binder population. Declining a fix leaves the item untouched and the report prints the exact Make command to run later.
For a read-only health check suitable for scripts or CI:

```sh
make doctor CHECK=1
```
It exits nonzero while actionable work remains. Hygiene warnings are printed but do not fail the check.
Validation and tests remain available separately. `make check` runs the tests, validation, and the read-only doctor in sequence:

```sh
make validate
make test
make check
```
Validation covers every catalog file and binder manifest, including content schema, filename/ID agreement, images, shot-label freshness, binder references, unique increasing physical pages, draft/printed state, and venue-note limits.
Pinball Map data is community maintained and may be stale. When used, preserve the attribution and advisory-source metadata in the binder manifest.

## Maintainer tools
Commands used for repository maintenance rather than normal game and binder work are grouped under the `dev-` prefix:

```sh

make dev-content-audit
make dev-content-proofread MODEL="mistral:latest"
make dev-image-variants IMAGE=images/example.jpg
make dev-format-prompt RESEARCH=content/research/example.md
make dev-benchmark-format MODEL="mistral:latest"
make dev-benchmark-codex WORKERS=3
```
