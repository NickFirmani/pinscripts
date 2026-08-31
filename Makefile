PYTHON := .venv/bin/python

.PHONY: all all-bw all-color binder binder-bw binder-color clean install process-images prompt test

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

prompt:
	@test -n "$(GAME)" || (echo 'Usage: make prompt GAME="Game Name (Manufacturer, Year)"' >&2; exit 2)
	@$(PYTHON) main.py --prompt "$(GAME)"

process-images:
	@test -n "$(IMAGE)" || (echo 'Usage: make process-images IMAGE="images/game.jpg" [OUTPUT_DIR="path"]' >&2; exit 2)
	@$(PYTHON) main.py --process-images "$(IMAGE)" $(if $(OUTPUT_DIR),--image-output-dir "$(OUTPUT_DIR)")

game-color-%:
	$(PYTHON) main.py $* --color

game-bw-%:
	$(PYTHON) main.py $* --black-and-white

game-%:
	$(PYTHON) main.py $*
