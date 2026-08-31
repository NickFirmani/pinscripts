PYTHON := .venv/bin/python

.PHONY: all binder clean install test

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

game-%:
	$(PYTHON) main.py $*
