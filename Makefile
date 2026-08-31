PYTHON := .venv/bin/python

.PHONY: all all-bw all-color binder binder-bw binder-color clean format-benchmark format-prompt install process-images research-prompt test

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

research-prompt:
	@test -n "$(GAME)" || (echo 'Usage: make research-prompt GAME="Game Name (Manufacturer, Year)"' >&2; exit 2)
	@$(PYTHON) main.py --research-prompt "$(GAME)"

format-prompt:
	@test -n "$(RESEARCH)" || (echo 'Usage: make format-prompt RESEARCH="path/to/research.md"' >&2; exit 2)
	@$(PYTHON) main.py --format-prompt "$(RESEARCH)"

format-benchmark:
	@test -n "$(MODEL)" || (echo 'Usage: make format-benchmark MODEL="ollama-model" [RESEARCH="path"] [MODE="structured-json|direct-yaml"] [THINK="false|true|low|medium|high"] [PROGRESS_INTERVAL="seconds"]' >&2; exit 2)
	$(PYTHON) benchmarks/format_prompt.py --model "$(MODEL)" $(if $(RESEARCH),--research "$(RESEARCH)") $(if $(MODE),--mode "$(MODE)") $(if $(THINK),--think "$(THINK)") $(if $(PROGRESS_INTERVAL),--progress-interval "$(PROGRESS_INTERVAL)")

process-images:
	@test -n "$(IMAGE)" || (echo 'Usage: make process-images IMAGE="images/game.jpg" [OUTPUT_DIR="path"]' >&2; exit 2)
	@$(PYTHON) main.py --process-images "$(IMAGE)" $(if $(OUTPUT_DIR),--image-output-dir "$(OUTPUT_DIR)")

game-color-%:
	$(PYTHON) main.py $* --color

game-bw-%:
	$(PYTHON) main.py $* --black-and-white

game-%:
	$(PYTHON) main.py $*
