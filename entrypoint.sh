#!/usr/bin/env bash

# Run migrations
set -e
. $(pipenv --venv)/bin/activate
python3 --version
pip3 freeze
python3 /code/src/model.py

# Start R api
Rscript /usr/local/src/myscripts/serve.R
