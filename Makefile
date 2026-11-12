# Optional shortcuts for macOS/Linux. Everything goes through run.py, which also
# works on Windows:  conda activate specmine  then  python run.py <step>
PY ?= conda run --no-capture-output -n specmine python

.PHONY: env check-data explore checks checks-sample test all

env:
	conda env create -f environment.yml || conda env update -n specmine -f environment.yml

check-data:
	$(PY) run.py check-data

explore:
	$(PY) run.py explore

checks:
	$(PY) run.py checks

checks-sample:
	$(PY) run.py checks --sample

test:
	$(PY) run.py test

all:
	$(PY) run.py all
