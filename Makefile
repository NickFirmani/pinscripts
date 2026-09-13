PYTHON := .venv/bin/python
.DEFAULT_GOAL := all

ifneq ($(filter add update game-research game-format game-image game-image-bw game-image-low-res shot-labels,$(MAKECMDGOALS)),)
ADD_INPUT = $(strip $(GAME))
UPDATE_INPUT = $(strip $(GAME))
GAME_RESEARCH_INPUT = $(strip $(if $(GAME),$(GAME),$(filter-out game-research,$(MAKECMDGOALS))))
GAME_FORMAT_INPUT = $(strip $(if $(GAME),$(GAME),$(filter-out game-format,$(MAKECMDGOALS))))
GAME_IMAGE_INPUT = $(strip $(if $(GAME),$(GAME),$(filter-out game-image,$(MAKECMDGOALS))))
GAME_IMAGE_BW_INPUT = $(strip $(if $(GAME),$(GAME),$(filter-out game-image-bw,$(MAKECMDGOALS))))
GAME_IMAGE_LOW_RES_INPUT = $(strip $(if $(GAME),$(GAME),$(filter-out game-image-low-res,$(MAKECMDGOALS))))
SHOT_LABELS_INPUT = $(strip $(if $(GAME),$(GAME),$(filter-out shot-labels,$(MAKECMDGOALS))))

# Treat additional command-line goals as the positional game description.
%:
	@:
endif

.PHONY: add all all-bw all-color audit-rules-basis binder binder-add binder-create binder-mark-printed binder-notes binder-remove binder-status binder-sync clean format-benchmark format-codex-batch format-prompt game-format game-image game-image-bw game-image-low-res game-research install process-images proofread-content shot-labels test update validate

add:
	@test -z "$(BINDER)" -o -z "$(ADD_INPUT)" || (echo 'Usage: make add GAME="description" or make add BINDER="binder-id"' >&2; exit 2)
	@$(PYTHON) main.py game add $(if $(BINDER),--binder "$(BINDER)","$(ADD_INPUT)")

update:
	@$(PYTHON) main.py game update "$(UPDATE_INPUT)"

audit-rules-basis:
	$(PYTHON) scripts/audit_rules_basis.py

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

all:
	$(PYTHON) main.py catalog build

all-color:
	$(PYTHON) main.py catalog build --color

all-bw:
	$(PYTHON) main.py catalog build --black-and-white

binder:
	@test -n "$(BINDER)" || (echo 'Usage: make binder BINDER="binder-id" [BW="1"]' >&2; exit 2)
	$(PYTHON) main.py binder build "$(BINDER)" $(if $(filter 1 true yes,$(BW)),--bw)

binder-create:
	@test -n "$(BINDER)" || (echo 'Usage: make binder-create BINDER="binder-id" [TITLE="..."] [MAP="url-or-id" | GAMES_FILE="path"], or omit both to paste' >&2; exit 2)
	$(PYTHON) main.py binder create "$(BINDER)" $(if $(TITLE),--title "$(TITLE)") $(if $(MAP),--pinball-map "$(MAP)",$(if $(GAMES_FILE),--games-file "$(GAMES_FILE)",--paste))

binder-sync:
	@test -n "$(BINDER)" || (echo 'Usage: make binder-sync BINDER="binder-id" [MAP="url-or-id" | PASTE="1"]' >&2; exit 2)
	$(PYTHON) main.py binder sync "$(BINDER)" $(if $(MAP),--pinball-map "$(MAP)",$(if $(filter 1 true yes,$(PASTE)),--paste))

binder-add:
	@test -n "$(BINDER)" -a -n "$(GAME)" || (echo 'Usage: make binder-add BINDER="binder-id" GAME="game-id"' >&2; exit 2)
	$(PYTHON) main.py binder add-game "$(BINDER)" "$(GAME)"

binder-remove:
	@test -n "$(BINDER)" -a -n "$(GAME)" || (echo 'Usage: make binder-remove BINDER="binder-id" GAME="game-id"' >&2; exit 2)
	$(PYTHON) main.py binder remove-game "$(BINDER)" "$(GAME)"

binder-notes:
	@test -n "$(BINDER)" -a -n "$(GAME)" || (echo 'Usage: make binder-notes BINDER="binder-id" GAME="game-id"' >&2; exit 2)
	$(PYTHON) main.py binder notes "$(BINDER)" "$(GAME)"

binder-mark-printed:
	@test -n "$(BINDER)" || (echo 'Usage: make binder-mark-printed BINDER="binder-id" [DATE="YYYY-MM-DD"]' >&2; exit 2)
	$(PYTHON) main.py binder mark-printed "$(BINDER)" $(if $(DATE),--date "$(DATE)")

binder-status:
	@test -n "$(BINDER)" || (echo 'Usage: make binder-status BINDER="binder-id"' >&2; exit 2)
	$(PYTHON) main.py binder status "$(BINDER)"

validate:
	$(PYTHON) main.py validate

clean:
	rm -rf output
	mkdir -p output

test:
	$(PYTHON) -m unittest discover -s tests

game-research:
	@$(PYTHON) main.py game research "$(GAME_RESEARCH_INPUT)"

game-format:
	@$(PYTHON) main.py game format "$(GAME_FORMAT_INPUT)"

game-image:
	@$(PYTHON) main.py game image "$(GAME_IMAGE_INPUT)"

game-image-bw:
	@$(PYTHON) main.py game image-bw "$(GAME_IMAGE_BW_INPUT)"

game-image-low-res:
	@$(PYTHON) main.py game image-low-res "$(GAME_IMAGE_LOW_RES_INPUT)"

shot-labels:
	@$(PYTHON) main.py shot-labels "$(SHOT_LABELS_INPUT)"

format-prompt:
	@test -n "$(RESEARCH)" || (echo 'Usage: make format-prompt RESEARCH="path/to/research.md"' >&2; exit 2)
	@$(PYTHON) main.py format-prompt "$(RESEARCH)"

format-benchmark:
	@test -n "$(MODEL)" || (echo 'Usage: make format-benchmark MODEL="ollama-model" [RESEARCH="path"] [MODE="structured-json|direct-yaml"] [THINK="false|true|low|medium|high"] [PROGRESS_INTERVAL="seconds"]' >&2; exit 2)
	$(PYTHON) benchmarks/format_prompt.py --model "$(MODEL)" $(if $(RESEARCH),--research "$(RESEARCH)") $(if $(MODE),--mode "$(MODE)") $(if $(THINK),--think "$(THINK)") $(if $(PROGRESS_INTERVAL),--progress-interval "$(PROGRESS_INTERVAL)")

format-codex-batch:
	$(PYTHON) benchmarks/format_codex.py --promote $(if $(MODEL),--model "$(MODEL)") $(if $(EFFORT),--effort "$(EFFORT)") $(if $(WORKERS),--workers "$(WORKERS)")

proofread-content:
	@test -n "$(MODEL)" || (echo 'Usage: make proofread-content MODEL="ollama-model" [APPLY="1"] [LIMIT="25"] [START_SERVER="1"]' >&2; exit 2)
	$(PYTHON) scripts/proofread_content.py --model "$(MODEL)" $(if $(filter 1 true yes,$(APPLY)),--apply) $(if $(LIMIT),--limit "$(LIMIT)") $(if $(filter 1 true yes,$(START_SERVER)),--start-server)

process-images:
	@test -n "$(IMAGE)" || (echo 'Usage: make process-images IMAGE="images/game.jpg" [OUTPUT_DIR="path"]' >&2; exit 2)
	@$(PYTHON) main.py process-images "$(IMAGE)" $(if $(OUTPUT_DIR),--output-dir "$(OUTPUT_DIR)")

game-color-%:
	$(PYTHON) main.py game build $* --color

game-bw-%:
	$(PYTHON) main.py game build $* --black-and-white

game-%:
	$(PYTHON) main.py game build $*
