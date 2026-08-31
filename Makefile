PYTHON := .venv/bin/python

.PHONY: all binder clean install process-images prompt test

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

all:
	$(PYTHON) main.py --all

binder:
	$(PYTHON) main.py --binder

clean:
	rm -rf output
	mkdir -p output

test:
	$(PYTHON) -m unittest discover -s tests

prompt:
	@test -n "$(GAME)" || (echo 'Usage: make prompt GAME="Game Name (Manufacturer, Year)"' >&2; exit 2)
	@$(PYTHON) main.py --prompt "$(GAME)"

process-images:
	@test -n "$(IMAGE)" || (echo 'Usage: make process-images IMAGE="images/game.jpg" [OUTPUT_DIR="path"]' >&2; exit 2)
	@$(PYTHON) main.py --process-images "$(IMAGE)" $(if $(OUTPUT_DIR),--image-output-dir "$(OUTPUT_DIR)")

game-%:
	$(PYTHON) main.py $*
