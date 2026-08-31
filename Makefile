PYTHON := .venv/bin/python

.PHONY: all binder clean install

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

all:
	$(PYTHON) scripts/render.py --all

binder:
	$(PYTHON) scripts/render.py --binder

clean:
	rm -rf output
	mkdir -p output

game-%:
	$(PYTHON) scripts/render.py $*
