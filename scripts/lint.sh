#!/usr/bin/env bash

set -e
set -x

mypy app --allow-redefinition
ruff check app
ruff format app --check
