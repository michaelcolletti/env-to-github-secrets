install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

init: 
	python -m venv .venv &&\
		source .venv/bin/activate
test:
	python -m pytest -vv tests/*.py && flake8 --max-line-length=120 --ignore=E501,E203,E266,E402,W503,W504,W605 --exclude=.venv,build,dist,*.egg-info,*.egg,*.pyc,*.pyo,*.pyd --max-complexity=10 --max-line-length=120 src/main.py

refactor: format lint

format:
	black  src/*.py

lint:
	-pylint --disable=R,C src/main.py --ignore-patterns=test_?.py 

run:
	python src/*.py

clean:
	rm -rf __pycache__/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf htmlcov/

all: install format lint test run

