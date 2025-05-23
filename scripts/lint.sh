#!/usr/bin/env bash

set -e
set -x

mypy app --allow-redefinition

ruff check app
ruff format app --check

yamllint app/playbooks

ansible-lint app/playbooks
ansible-playbook --inventory localhost, --syntax-check app/playbooks/*
