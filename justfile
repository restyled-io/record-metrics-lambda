# setup for working on this project
setup:
  pip install -r requirements.txt

# run the project's integration tests
test:
  AWS_PROFILE=restyled-ci LOG_LEVEL=error python test_main.py

# Build the dist payload
dist:
  rm -rf dist/*
  mkdir -p dist
  cp main.py dist/
  cp -r .venv/lib/python*/site-packages/* dist/
  cd dist && zip -r lambda.zip .
