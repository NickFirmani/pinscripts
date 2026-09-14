PYTHON := .venv/bin/python
MODE ?= color
ACTION ?= color

.DEFAULT_GOAL := help

.PHONY: \
	help setup doctor validate test check clean \
	catalog-build game-add game-update game-build game-research game-format \
	game-image game-labels binder-create binder-sync binder-populate binder-status \
	binder-add binder-remove binder-notes binder-mark-printed binder-build \
	binder-cover binder-update dev-content-audit dev-content-proofread \
	dev-image-variants dev-format-prompt dev-benchmark-format dev-benchmark-codex \
	_require-game _require-binder _require-mode _require-image-action \
	_catalog-build-color _catalog-build-bw _catalog-build-both \
	_game-build-color _game-build-bw _game-build-both \
	_game-image-color _game-image-bw _game-image-upgrade \
	_binder-build-color _binder-build-bw _binder-build-both

help:
	@printf '%s\n' \
		'PinScripts commands' \
		'' \
		'Getting started and repository health:' \
		'  make check                                      Run tests, validation, and the read-only doctor.' \
		'  make clean                                      Remove generated output files.' \
		'  make doctor [GAME=id | BINDER=id] [CHECK=1]     Diagnose project health and optionally offer repairs.' \
		'  make help                                       Show this command reference.' \
		'  make setup                                      Create the virtual environment and install dependencies.' \
		'  make test                                       Run the automated test suite.' \
		'  make validate                                   Validate all catalog and binder data.' \
		'' \
		'Catalog and game workflows:' \
		'  make catalog-build [MODE=color|bw|both]          Build the location-neutral master catalog PDF.' \
		'  make game-add GAME="description"                 Add a new game through the complete guided workflow.' \
		'  make game-build GAME=id [MODE=...] [BINDER=id]  Build one game, optionally with binder context.' \
		'  make game-format GAME=id                        Format researched material into catalog YAML.' \
		'  make game-image GAME=id [ACTION=...]             Add, regenerate, or upgrade a playfield image.' \
		'  make game-labels GAME=id                       Create or revise playfield shot labels.' \
		'  make game-research GAME="description"            Research a game and save the source notes.' \
		'  make game-update GAME=id                        Update an existing game and its affected binders.' \
		'' \
		'Binder workflows:' \
		'  make binder-add BINDER=id GAME=id [MODE=...]     Add a game and create an insert packet when printed.' \
		'  make binder-build BINDER=id [MODE=...]           Build the complete binder PDF.' \
		'  make binder-cover BINDER=id [SIZE=inches]        Build printable front-cover and spine inserts.' \
		'  make binder-create BINDER=id [...]               Create a draft binder from a list or Pinball Map.' \
		'  make binder-mark-printed BINDER=id [DATE=...]    Make the physical page numbering permanent.' \
		'  make binder-notes BINDER=id GAME=id              Edit venue-specific notes for one game.' \
		'  make binder-populate BINDER=id                   Resolve pending imported games safely in parallel.' \
		'  make binder-remove BINDER=id GAME=id             Remove a game while preserving printed page labels.' \
		'  make binder-status BINDER=id                     Show binder state and unresolved game counts.' \
		'  make binder-sync BINDER=id [MAP=... | PASTE=1]   Compare an advisory listing with the saved binder.' \
		'  make binder-update BINDER=id GAME=id [MODE=...]  Build a replacement packet for an existing game.' \
		'' \
		'Maintainer tools:' \
		'  make dev-benchmark-codex [...]                   Benchmark Codex formatting and promote the winner.' \
		'  make dev-benchmark-format MODEL=name [...]       Benchmark local-model YAML formatting.' \
		'  make dev-content-audit                           Audit rules-basis metadata across the catalog.' \
		'  make dev-content-proofread MODEL=name [...]      Proofread catalog content with a local model.' \
		'  make dev-format-prompt RESEARCH=path             Print a fully expanded formatting prompt.' \
		'  make dev-image-variants IMAGE=path [...]         Generate processed image variants for inspection.'

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

doctor:
	@test -z "$(GAME)" -o -z "$(BINDER)" || (echo 'Use either GAME or BINDER, not both' >&2; exit 2)
	@$(PYTHON) main.py doctor $(if $(GAME),--game "$(GAME)") $(if $(BINDER),--binder "$(BINDER)") $(if $(filter 1 true yes,$(CHECK)),--check)

validate:
	$(PYTHON) main.py validate

test:
	$(PYTHON) -m unittest discover -s tests

check: test validate
	$(PYTHON) main.py doctor --check

clean:
	rm -rf output
	mkdir -p output

catalog-build: _require-mode
	@$(MAKE) --no-print-directory _catalog-build-$(MODE)

_catalog-build-color:
	$(PYTHON) main.py catalog build --color

_catalog-build-bw:
	$(PYTHON) main.py catalog build --black-and-white

_catalog-build-both: _catalog-build-color _catalog-build-bw

game-add: _require-game
	@$(PYTHON) main.py game add "$(GAME)"

game-update: _require-game
	@$(PYTHON) main.py game update "$(GAME)"

game-build: _require-game _require-mode
	@$(MAKE) --no-print-directory _game-build-$(MODE) GAME="$(GAME)" BINDER="$(BINDER)"

_game-build-color:
	$(PYTHON) main.py game build "$(GAME)" --color $(if $(BINDER),--binder "$(BINDER)")

_game-build-bw:
	$(PYTHON) main.py game build "$(GAME)" --black-and-white $(if $(BINDER),--binder "$(BINDER)")

_game-build-both: _game-build-color _game-build-bw

game-research: _require-game
	@$(PYTHON) main.py game research "$(GAME)"

game-format: _require-game
	@$(PYTHON) main.py game format "$(GAME)"

game-image: _require-game _require-image-action
	@$(MAKE) --no-print-directory _game-image-$(ACTION) GAME="$(GAME)"

_game-image-color:
	@$(PYTHON) main.py game image "$(GAME)"

_game-image-bw:
	@$(PYTHON) main.py game image-bw "$(GAME)"

_game-image-upgrade:
	@$(PYTHON) main.py game image-low-res "$(GAME)"

game-labels: _require-game
	@$(PYTHON) main.py shot-labels "$(GAME)"

binder-create: _require-binder
	$(PYTHON) main.py binder create "$(BINDER)" $(if $(TITLE),--title "$(TITLE)") $(if $(MAP),--pinball-map "$(MAP)",$(if $(GAMES_FILE),--games-file "$(GAMES_FILE)",--paste))

binder-sync: _require-binder
	$(PYTHON) main.py binder sync "$(BINDER)" $(if $(MAP),--pinball-map "$(MAP)",$(if $(filter 1 true yes,$(PASTE)),--paste))

binder-populate: _require-binder
	@$(PYTHON) main.py game add --binder "$(BINDER)"

binder-status: _require-binder
	$(PYTHON) main.py binder status "$(BINDER)"

binder-add: _require-binder _require-game _require-mode
	$(PYTHON) main.py binder add-game "$(BINDER)" "$(GAME)" --mode "$(MODE)"

binder-remove: _require-binder _require-game
	$(PYTHON) main.py binder remove-game "$(BINDER)" "$(GAME)"

binder-notes: _require-binder _require-game
	$(PYTHON) main.py binder notes "$(BINDER)" "$(GAME)"

binder-mark-printed: _require-binder
	$(PYTHON) main.py binder mark-printed "$(BINDER)" $(if $(DATE),--date "$(DATE)")

binder-build: _require-binder _require-mode
	@$(MAKE) --no-print-directory _binder-build-$(MODE) BINDER="$(BINDER)"

_binder-build-color:
	$(PYTHON) main.py binder build "$(BINDER)" --color

_binder-build-bw:
	$(PYTHON) main.py binder build "$(BINDER)" --black-and-white

_binder-build-both: _binder-build-color _binder-build-bw

binder-cover: _require-binder
	@$(PYTHON) main.py binder cover "$(BINDER)" $(if $(SIZE),--size "$(SIZE)")

binder-update: _require-binder _require-game _require-mode
	$(PYTHON) main.py binder update-game "$(BINDER)" "$(GAME)" --mode "$(MODE)"

dev-content-audit:
	$(PYTHON) scripts/audit_rules_basis.py

dev-content-proofread:
	@test -n "$(MODEL)" || (echo 'Usage: make dev-content-proofread MODEL="ollama-model" [APPLY=1] [LIMIT=25] [START_SERVER=1]' >&2; exit 2)
	$(PYTHON) scripts/proofread_content.py --model "$(MODEL)" $(if $(filter 1 true yes,$(APPLY)),--apply) $(if $(LIMIT),--limit "$(LIMIT)") $(if $(filter 1 true yes,$(START_SERVER)),--start-server)

dev-image-variants:
	@test -n "$(IMAGE)" || (echo 'Usage: make dev-image-variants IMAGE="images/game.jpg" [OUTPUT_DIR=path]' >&2; exit 2)
	@$(PYTHON) main.py process-images "$(IMAGE)" $(if $(OUTPUT_DIR),--output-dir "$(OUTPUT_DIR)")

dev-format-prompt:
	@test -n "$(RESEARCH)" || (echo 'Usage: make dev-format-prompt RESEARCH="path/to/research.md"' >&2; exit 2)
	@$(PYTHON) main.py format-prompt "$(RESEARCH)"

dev-benchmark-format:
	@test -n "$(MODEL)" || (echo 'Usage: make dev-benchmark-format MODEL="ollama-model" [RESEARCH=path] [FORMAT_MODE=structured-json|direct-yaml] [THINK=false|true|low|medium|high] [PROGRESS_INTERVAL=seconds]' >&2; exit 2)
	$(PYTHON) benchmarks/format_prompt.py --model "$(MODEL)" $(if $(RESEARCH),--research "$(RESEARCH)") $(if $(FORMAT_MODE),--mode "$(FORMAT_MODE)") $(if $(THINK),--think "$(THINK)") $(if $(PROGRESS_INTERVAL),--progress-interval "$(PROGRESS_INTERVAL)")

dev-benchmark-codex:
	$(PYTHON) benchmarks/format_codex.py --promote $(if $(MODEL),--model "$(MODEL)") $(if $(EFFORT),--effort "$(EFFORT)") $(if $(WORKERS),--workers "$(WORKERS)")

_require-game:
	@test -n "$(GAME)" || (echo 'GAME is required; run make help for examples' >&2; exit 2)

_require-binder:
	@test -n "$(BINDER)" || (echo 'BINDER is required; run make help for examples' >&2; exit 2)

_require-mode:
	@test -n "$(filter $(MODE),color bw both)" || (echo 'MODE must be color, bw, or both' >&2; exit 2)

_require-image-action:
	@test -n "$(filter $(ACTION),color bw upgrade)" || (echo 'ACTION must be color, bw, or upgrade' >&2; exit 2)
