.PHONY: setup
	python -m virtualenv .venv
	source .venv/bin/activate
	pip install --upgrade pip
	pip install --requirements requirements.txt

.PHONY: test
test:
	AWS_PROFILE=restyled-ci ENV=test python test_main.py

dist/lambda.zip: main.py
	rm -rf dist/*
	mkdir -p dist
	cp main.py dist/
	cp -r .venv/lib/python3.8/site-packages/* dist/
	cd dist && zip -r lambda.zip .
