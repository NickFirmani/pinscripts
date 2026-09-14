PYTHON := .venv/bin/python
MODE ?= color
ACTION ?= color
OPERATION ?= update

.DEFAULT_GOAL := help

.PHONY: \
	help setup validate test check clean \
	catalog-build game-add game-update game-build game-research game-format \
	game-image game-labels binder-create binder-sync binder-populate binder-status \
	binder-add binder-remove binder-notes binder-mark-printed binder-build \
	binder-cover binder-packet dev-content-audit dev-content-proofread \
	dev-image-variants dev-format-prompt dev-benchmark-format dev-benchmark-codex \
	_require-game _require-binder _require-mode _require-image-action \
	_catalog-build-color _catalog-build-bw _catalog-build-both \
	_game-build-color _game-build-bw _game-build-both \
	_game-image-color _game-image-bw _game-image-upgrade \
	_binder-build-color _binder-build-bw _binder-build-both \
	_binder-packet-color _binder-packet-bw _binder-packet-both

help:
	@printf '%s\n' \
		'PinScripts commands' \
		'' \
		'Getting started and repository health:' \
		'  make setup' \
		'  make validate' \
		'  make test' \
		'  make check' \
		'  make clean' \
		'' \
		'Catalog and game workflows:' \
		'  make catalog-build [MODE=color|bw|both]' \
		'  make game-add GAME="description"' \
		'  make game-update GAME=id' \
		'  make game-build GAME=id [MODE=color|bw|both] [BINDER=id]' \
		'  make game-research GAME="description"' \
		'  make game-format GAME=id' \
		'  make game-image GAME=id [ACTION=color|bw|upgrade]' \
		'  make game-labels GAME=id' \
		'' \
		'Binder workflows:' \
		'  make binder-create BINDER=id [TITLE="..."] [MAP=id-or-url | GAMES_FILE=path]' \
		'  make binder-sync BINDER=id [MAP=id-or-url | PASTE=1]' \
		'  make binder-populate BINDER=id' \
		'  make binder-status BINDER=id' \
		'  make binder-add BINDER=id GAME=id' \
		'  make binder-remove BINDER=id GAME=id' \
		'  make binder-notes BINDER=id GAME=id' \
		'  make binder-mark-printed BINDER=id [DATE=YYYY-MM-DD]' \
		'  make binder-build BINDER=id [MODE=color|bw|both]' \
		'  make binder-cover BINDER=id [SIZE=inches]' \
		'  make binder-packet BINDER=id GAME=id [OPERATION=add|update] [MODE=color|bw|both]' \
		'' \
		'Maintainer tools:' \
		'  make dev-content-audit' \
		'  make dev-content-proofread MODEL=name [APPLY=1] [LIMIT=25] [START_SERVER=1]' \
		'  make dev-image-variants IMAGE=path [OUTPUT_DIR=path]' \
		'  make dev-format-prompt RESEARCH=path' \
		'  make dev-benchmark-format MODEL=name [...]' \
		'  make dev-benchmark-codex [MODEL=name] [EFFORT=level] [WORKERS=count]'

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

validate:
	$(PYTHON) main.py validate

test:
	$(PYTHON) -m unittest discover -s tests

check: test validate

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

binder-add: _require-binder _require-game
	$(PYTHON) main.py binder add-game "$(BINDER)" "$(GAME)"

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

binder-packet: _require-binder _require-game _require-mode
	@test -n "$(filter $(OPERATION),add update)" || (echo 'OPERATION must be add or update' >&2; exit 2)
	@$(MAKE) --no-print-directory _binder-packet-$(MODE) BINDER="$(BINDER)" GAME="$(GAME)" OPERATION="$(OPERATION)"

_binder-packet-color:
	$(PYTHON) main.py binder packet "$(BINDER)" "$(GAME)" --operation "$(OPERATION)" --color

_binder-packet-bw:
	$(PYTHON) main.py binder packet "$(BINDER)" "$(GAME)" --operation "$(OPERATION)" --black-and-white

_binder-packet-both: _binder-packet-color _binder-packet-bw

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
