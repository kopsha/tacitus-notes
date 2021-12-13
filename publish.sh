#!/usr/bin/env bash
set -e

rm -rf dist/*
python3 -m build
twine upload -r testpypi dist/*
