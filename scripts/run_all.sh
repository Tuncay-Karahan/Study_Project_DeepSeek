#!/usr/bin/env bash
set -euo pipefail
python "src/klausuren/1_latex_to_json.py"
python "src/klausuren/2_send_to_models.py"
python "src/klausuren/3_compare_and_score.py"
