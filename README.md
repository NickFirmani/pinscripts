# Pinball Commentary Binder Generator

Generate compact, two-page pinball commentary references, a location-neutral
master catalog PDF, and separate PDFs for real physical binders.

## Data model

`content/*.yaml` is the master game catalog. Each file contains reusable rules,
strategy, and commentary material for one gameplay-distinct edition. The catalog
is discovered directly from these files; there is no second master list.
Playfield image paths are derived from each game ID as `images/<id>.webp` and
`images/<id>-bw.webp`; they are not repeated in YAML.

Equivalent cosmetic trims share one catalog entry. Modern Stern Premium and LE
machines use the display suffix `Prem/LE` and ID segment `prem-le`; Pro remains a
separate entry. Jersey Jack Limited and Collector's Editions use `LE/CE` and
`le-ce`; Standard Edition remains separate.

`binders/*.yaml` records one printable or already-printed binder. A binder owns:

- its title and draft/printed state
- permanent physical page labels
- its manually curated game lineup
- venue notes for each game
- an optional Pinball Map location used only as an advisory reference

The saved binder manifest is always the source of truth. Building a PDF never
contacts Pinball Map and never changes a lineup.

## Setup

Requirements are Python 3 and, for image processing only, ImageMagick.

```sh
make setup
make test
```

Run `make` or `make help` at any time to see the supported commands, grouped by
workflow.

## Master catalog

Build all catalog content in alphabetical order:

```sh
make catalog-build
make catalog-build MODE=bw
make catalog-build MODE=both
```

Outputs are `output/catalog.pdf` and `output/catalog-bw.pdf`. Catalog pages use
ordinary sequential numbering and contain no venue-specific notes.

Build one location-neutral game:

```sh
make game-build GAME=playboy-bally-1978
```

## Physical binders

The original printed collection is now recorded in
`binders/lyons-classic-pinball.yaml`.

Build it with its permanent page labels and venue notes:

```sh
make binder-build BINDER=lyons-classic-pinball
make binder-build BINDER=lyons-classic-pinball MODE=bw
make binder-build BINDER=lyons-classic-pinball MODE=both
```

Outputs are written under `output/binders/`.

### Create the front and spine inserts

Generate a printable front cover and a spine insert for a saved binder:

```sh
make binder-cover BINDER=lyons-classic-pinball
```

The command asks for the binder's spine-pocket width in inches (for example,
`1`, `1.5`, or `2`). It writes a two-page letter PDF under `output/binders/`:
the front insert is page 1 and the correctly sized, centered spine strip with
cut guides is page 2. Print at actual size (100%, with no page scaling).

For non-interactive use, pass the size directly:

```sh
make binder-cover BINDER=lyons-classic-pinball SIZE=1.5
```

### Create a binder from a text file

The file contains one catalog ID or unambiguous game name per line:

```sh
make binder-create \
  BINDER=my-event \
  TITLE="My Event" \
  GAMES_FILE=games.txt
```

New binders start as drafts with clean integer pages beginning at page 2.

### Create a binder from Pinball Map

Pass a numeric location ID or a map URL:

```sh
make binder-create \
  BINDER=one-up-westminster \
  MAP='https://pinballmap.com/map/?by_location_id=25303'
```

The importer reads the public HTML used by the Pinball Map website. It does not
use an API token. It fetches only the selected location and its machine-list
fragment. Imported names are matched conservatively using game name,
manufacturer, year, and gameplay-distinct edition. Missing or ambiguous games
are saved to the binder's durable pending queue; binder creation does not stop
for inline research.

If fetching fails or you prefer to copy the visible lineup yourself:

```sh
make binder-create BINDER=my-binder TITLE="My Binder"
```

Paste one game per line in this form, followed by `::end`:

```text
The Addams Family (Bally, 1992)
JAWS (LE) (Stern, 2024)
::end
```

### Synchronize against an advisory listing

```sh
make binder-sync BINDER=one-up-westminster
make binder-sync BINDER=one-up-westminster PASTE=1
```

Sync shows a preview. New unresolved listings are added to the same pending
queue, while games found only in the binder are always retained. Pinball Map is
not treated as authoritative.

The `source` object supports both `pinball-map` and `manual`. Manual add, remove,
or venue-note commands automatically change `source.kind` to `manual` while
retaining any Pinball Map URL and location ID as provenance:

```yaml
source:
  kind: manual
  location_id: '25303'
  url: https://pinballmap.com/map/?by_location_id=25303
  retrieved_at: '2026-09-13'
  notes: Manually curated; any retained Pinball Map URL is an advisory reference only.
```

### Maintain a binder

```sh
make binder-add BINDER=my-binder GAME=jaws-pro-stern-2024
make binder-remove BINDER=my-binder GAME=jaws-pro-stern-2024
make binder-notes BINDER=my-binder GAME=jaws-pro-stern-2024
make binder-mark-printed BINDER=my-binder
```

### Resolve a venue's pending games in parallel

After create or sync, open three terminals and run the same command in each:

```sh
make binder-populate BINDER=one-up-westminster
```

Each terminal atomically claims a different pending game. For every claim, the
workflow first lists closely named catalog entries so you can select a match
before adding anything. Otherwise choose to add a new catalog game, explicitly
match an existing one, ignore a stale source listing, or release the claim back
to the queue. Matches and ignores become durable source overrides, so later
Pinball Map syncs preserve the human correction.

Each successful resolution is merged into the latest binder file under a write
lock. It is therefore safe for all three terminals to finish in any order.
Inspect remaining work at any time with:

```sh
make binder-status BINDER=one-up-westminster
```

A draft binder cannot be marked printed while unresolved games remain.

Draft additions and removals are alphabetized and renumbered. After a binder is
marked printed, existing page labels never change:

- additions receive decimal labels between their neighbors
- removals become `present: false` tombstones and reserve their old labels
- venue notes live only in that binder entry

Generate a four-page replacement packet directly:

```sh
make binder-packet \
  BINDER=lyons-classic-pinball \
  GAME=jaws-pro-stern-2024 \
  OPERATION=update
```

Print packets double-sided at actual size, flipping on the long edge.

## Catalog game workflows

Add a reusable game without assigning it to any binder:

```sh
make game-add GAME="Jaws Prem/LE Stern 2024"
```

`make game-add` is resumable and safe to run in several terminals. Completed
research, content, image, black-and-white image, and shot-label stages are
reused. A per-game lock prevents two terminals from changing the same game at
once: the first continues, while a duplicate invocation exits successfully
without making changes. Different game IDs can proceed concurrently.

Update one game:

```sh
make game-update GAME=jaws-pro-stern-2024
```

Choose image step `2` to recrop or replace the playfield. Recropping is the
default and does not require a new download: the current canonical image is
copied to a temporary working file and opened in XnView MP. Crop that copy to a
fixed 408:750 ratio, save it in place, and return to the terminal to verify it.
The previous color image is retained under `images/low-res-backup/`, the stale
B&W derivative is moved there too, and the update flow offers to redo shot
labels and regenerate the B&W image before validation.

Updates validate every binder containing the game. When requested, one
replacement packet is generated for each affected printed binder, using that
binder's permanent pages and venue notes.

Other asset workflows:

```sh
make game-research GAME="Jaws Prem/LE Stern 2024"
make game-format GAME=jaws-prem-le-stern-2024
make game-image GAME=jaws-prem-le-stern-2024
make game-image GAME=jaws-prem-le-stern-2024 ACTION=bw
make game-image GAME=jaws-prem-le-stern-2024 ACTION=upgrade
make game-labels GAME=jaws-prem-le-stern-2024
```

Every newly downloaded color image goes through the crop editor before it is
accepted, even when the source already has a 408:750 aspect ratio. This keeps
framing review as a required part of adding or replacing a game image.

Catalog content must remain location-neutral. Validation rejects phrases such
as “this venue”; physical settings, feeds, machine condition, and tournament
policy belong in binder venue notes.

## Project health and validation

Run the project doctor after cloning, before a large print, or whenever you want
to work through incomplete assets:

```sh
make doctor
make doctor GAME=jaws-prem-le-stern-2024
make doctor BINDER=one-up-westminster
```

Doctor scans the requested scope before changing anything. It reports invalid
catalog or binder data, missing or unreadable color and black-and-white images,
color images below the 1000-pixel long-edge threshold, missing or stale shot
labels, unresolved binder games, and orphaned image or label files. It then
offers fixes in dependency order: color images, image upgrades, B&W images, shot
labels, and binder population. Declining a fix leaves the item untouched and
the report prints the exact Make command to run later.

For a read-only health check suitable for scripts or CI:

```sh
make doctor CHECK=1
```

It exits nonzero while actionable work remains. Hygiene warnings are printed but
do not fail the check.

Validation and tests remain available separately. `make check` runs the tests,
validation, and the read-only doctor in sequence:

```sh
make validate
make test
make check
```

Validation covers every catalog file and binder manifest, including content
schema, filename/ID agreement, images, shot-label freshness, binder references,
unique increasing physical pages, draft/printed state, and venue-note limits.

Pinball Map data is community maintained and may be stale. When used, preserve
the attribution and advisory-source metadata in the binder manifest.

## Maintainer tools

Commands used for repository maintenance rather than normal game and binder
work are grouped under the `dev-` prefix:

```sh
make dev-content-audit
make dev-content-proofread MODEL="mistral:latest"
make dev-image-variants IMAGE=images/example.jpg
make dev-format-prompt RESEARCH=content/research/example.md
make dev-benchmark-format MODEL="mistral:latest"
make dev-benchmark-codex WORKERS=3
```
