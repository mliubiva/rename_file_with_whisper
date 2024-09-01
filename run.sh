#!/bin/bash

# Set the path to your input directory
INPUT_DIR="/Users/mariiakovalenko/Downloads/all_records/records_malaysia"
INPUT_DIR="/Users/mariiakovalenko/Downloads/all_records/records_malaysia_test"


# Run the Python script with specified parameters
python rename_audio_records.py "$INPUT_DIR" #\
    # --model_type large \
    # --quant None \
    # --initial_duration 8 \
    # --min_words 8 \
    # --debug

# Note: Remove the --debug flag if you don't want debug output