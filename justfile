# Setup virtualenv
venv:
  python -m venv .venv
  . .venv/bin/activate && pip install -r requirements.txt

# Run project tests
test:
  pytest

# Build the dist payload
dist:
  [ -d .venv ] || just venv
  rm -rf dist/*
  mkdir -p dist
  cp main.py dist/
  cp -r .venv/lib/python*/site-packages/* dist/
  cd dist && zip -r lambda.zip .
