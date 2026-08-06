#!/usr/bin/env bash
set -e
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
[ -f data/samples/sales_2024.csv ] || python scripts/generate_sample_data.py
streamlit run app.py
