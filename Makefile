PYTHON := .venv/bin/python

ifneq ($(filter game-research game-format game-image game-image-bw game-image-low-res shot-labels review-venue-notes,$(MAKECMDGOALS)),)
GAME_RESEARCH_INPUT = $(strip $(if $(GAME),$(GAME),$(filter-out game-research,$(MAKECMDGOALS))))
GAME_FORMAT_INPUT = $(strip $(if $(GAME),$(GAME),$(filter-out game-format,$(MAKECMDGOALS))))
GAME_IMAGE_INPUT = $(strip $(if $(GAME),$(GAME),$(filter-out game-image,$(MAKECMDGOALS))))
GAME_IMAGE_BW_INPUT = $(strip $(if $(GAME),$(GAME),$(filter-out game-image-bw,$(MAKECMDGOALS))))
GAME_IMAGE_LOW_RES_INPUT = $(strip $(if $(GAME),$(GAME),$(filter-out game-image-low-res,$(MAKECMDGOALS))))
SHOT_LABELS_INPUT = $(strip $(if $(GAME),$(GAME),$(filter-out shot-labels,$(MAKECMDGOALS))))
VENUE_NOTES_INPUT = $(strip $(if $(GAME),$(GAME),$(filter-out review-venue-notes,$(MAKECMDGOALS))))

# Treat additional command-line goals as the positional game description.
%:
	@:
endif

.PHONY: all all-bw all-color binder binder-bw binder-color clean format-benchmark format-codex-batch format-prompt game-format game-image game-image-bw game-image-low-res game-research install process-images proofread-content review-venue-notes shot-labels test

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

all:
	$(PYTHON) main.py --all

all-color:
	$(PYTHON) main.py --all --color

all-bw:
	$(PYTHON) main.py --all --black-and-white

binder:
	$(PYTHON) main.py --binder

binder-color:
	$(PYTHON) main.py --binder --color

binder-bw:
	$(PYTHON) main.py --binder --black-and-white

clean:
	rm -rf output
	mkdir -p output

test:
	$(PYTHON) -m unittest discover -s tests

game-research:
	@$(PYTHON) main.py --game-research "$(GAME_RESEARCH_INPUT)"

game-format:
	@$(PYTHON) main.py --game-format "$(GAME_FORMAT_INPUT)"

game-image:
	@$(PYTHON) main.py --game-image "$(GAME_IMAGE_INPUT)"

game-image-bw:
	@$(PYTHON) main.py --game-image-bw "$(GAME_IMAGE_BW_INPUT)"

game-image-low-res:
	@$(PYTHON) main.py --game-image-low-res "$(GAME_IMAGE_LOW_RES_INPUT)"

shot-labels:
	@$(PYTHON) main.py --shot-labels "$(SHOT_LABELS_INPUT)"

review-venue-notes:
	@$(PYTHON) main.py --review-venue-notes "$(VENUE_NOTES_INPUT)"

format-prompt:
	@test -n "$(RESEARCH)" || (echo 'Usage: make format-prompt RESEARCH="path/to/research.md"' >&2; exit 2)
	@$(PYTHON) main.py --format-prompt "$(RESEARCH)"

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
	@$(PYTHON) main.py --process-images "$(IMAGE)" $(if $(OUTPUT_DIR),--image-output-dir "$(OUTPUT_DIR)")

game-color-%:
	$(PYTHON) main.py $* --color

game-bw-%:
	$(PYTHON) main.py $* --black-and-white

game-%:
	$(PYTHON) main.py $*
