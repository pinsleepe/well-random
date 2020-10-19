#!/usr/bin/env bash

# Run migrations
set -e
. $(pipenv --venv)/bin/activate
python3 /code/src/model.py

# Start R api
Rscript /code/serve.R
