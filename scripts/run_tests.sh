#!/usr/bin/env bash
set -e

conda run -n testmofbuilder env PYTHONPATH=src python -m pytest "$@"