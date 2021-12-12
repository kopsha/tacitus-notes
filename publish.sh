#!/usr/bin/env bash
set -e

python3 -m build
# twine upload -r testpypi dist/*
