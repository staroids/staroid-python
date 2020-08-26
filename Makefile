
init:
	pip install -r requirements.txt

test:
	python -m unittest

.PHONY: init test
