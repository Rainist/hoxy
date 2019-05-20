.PHONY: init check format

init:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

check:
	isort --recursive --check-only hoxy.py
	black -S -l 79 --check hoxy.py
	pylint hoxy.py

format:
	isort -rc -y hoxy.py
	black -S -l 79 hoxy.py
