#!/bin/bash
python process_results/extract_from_files.py
python process_results/process_json.py
python process_results/plot_squares.py
python process_results/plot_entropy.py