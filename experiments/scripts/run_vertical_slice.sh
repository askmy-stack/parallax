#!/usr/bin/env bash
# Run the tool-semantic-drift vertical-slice experiment.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
ras experiment run --case tool-semantic-drift-001 --compare --export-dir experiments/results
