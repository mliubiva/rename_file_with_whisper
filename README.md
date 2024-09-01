# Audio Transcription and Renaming Script

This script uses the Whisper model to transcribe audio files and rename them based on the transcription content.

## Prerequisites

- Python 3.7+
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone this repository or download the script.
2. Install the required packages:

```
pip install -r requirements.txt
```

## Usage

Run the script using the following command:

```
python transcribe_and_rename.py <input_directory> [options]
```

### Options:

- `--model_type`: Whisper model type (default: "large")
- `--quant`: Quantization option (choices: None, "4bit", "8bit", default: None)
- `--initial_duration`: Initial duration to process in seconds (default: 8)
- `--min_words`: Minimum number of words required in transcription (default: 8)
- `--debug`: Enable debug mode (flag)

Example:

```
python transcribe_and_rename.py /path/to/audio/files --model_type medium --quant 8bit --initial_duration 10 --min_words 8 --debug
```

## Output

The script will create a new directory with the renamed audio files. The new directory name will include the original directory name and a timestamp.

## Note

Ensure you have the necessary audio codecs installed on your system to process various audio file formats.