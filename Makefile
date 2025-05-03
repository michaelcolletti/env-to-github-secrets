install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

init: 
	python -m venv .venv &&\
		source .venv/bin/activate
    
test:
	python -m pytest -vv tests/test_main.py 

refactor: format lint

format:
	black  src/main.py

run:
	python src/main.py

lint:
	-pylint --disable=R,C src/main.py --ignore-patterns=test_?.py 

clean:
	rm -rf __pycache__/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf htmlcov/

all: install lint

