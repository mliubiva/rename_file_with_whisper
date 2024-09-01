import os
import time
import shutil
import re
from datetime import datetime
from typing import Any, Optional
from argparse import ArgumentParser
from tqdm import tqdm
from pydub import AudioSegment
from lightning_whisper_mlx import LightningWhisperMLX

def trim_audio(file_path: str, duration: int = 6, debug: bool = False) -> str:
    dir_name, file_name = os.path.split(file_path)
    name, ext = os.path.splitext(file_name)
    ext = ext[1:]
    
    try:
        audio = AudioSegment.from_file(file_path)
    except Exception as e:
        print(f"Error loading file: {e}")
        print("Make sure you have the necessary codecs installed.")
        return ""
    
    trimmed_audio = audio[:duration*1000]
    new_file_name = f"{duration}sec_{name}.wav"
    new_file_path = os.path.join(dir_name, new_file_name)
    
    try:
        trimmed_audio.export(new_file_path, format="wav")
        if debug:
            print(f"Trimmed audio saved as: {new_file_name}")
        return new_file_path
    except Exception as e:
        print(f"Error saving file: {e}")
        return ""

def transcribe_and_time(whisper: Any, audio_file: str) -> tuple[str, float]:
    start_time = time.time()
    result = whisper.transcribe(audio_path=audio_file, language="uk")
    end_time = time.time()
    return result['text'], end_time - start_time

def transcribe_audio(
    audio_file: str, 
    whisper: Any, 
    initial_duration: int = 8, 
    min_words: int = 8, 
    debug: bool = False
) -> str:
    if whisper is None:
        raise ValueError("Model not loaded. Please load the model before calling this function.")
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"The file {audio_file} does not exist.")
    if initial_duration <= 0:
        raise ValueError("Initial duration must be positive.")

    def process_audio(duration: Optional[int]) -> str:
        try:
            t1 = time.time()
            trimmed_file = trim_audio(audio_file, duration=duration) if duration else audio_file
            t2 = time.time()
            
            if debug:
                print(f"Trimming time: {t2-t1:.2f} seconds")
                print(f"Processing file: {trimmed_file}")

            transcription, processing_time = transcribe_and_time(whisper, trimmed_file)
            
            if trimmed_file != audio_file:
                os.remove(trimmed_file)
            
            if debug:
                print(f"Processing time: {processing_time:.2f} seconds")
                print(f"Transcription: {transcription}")
            
            return transcription
        except Exception as e:
            if debug:
                print(f"Error during transcription: {str(e)}")
            raise

    def check_transcription(text: str) -> bool:
        return len(text.split()) >= min_words

    for duration in [initial_duration, initial_duration * 2, None]:
        transcription = process_audio(duration)
        if check_transcription(transcription):
            return transcription
        if debug and duration is not None:
            print(f"Transcription has less than {min_words} words. Trying with {'double duration' if duration == initial_duration else 'full file'}.")

    return transcription

def clean_filename(filename: str) -> str:
    cleaned = re.sub(r'[^\w\s-]', '', filename)
    cleaned = re.sub(r'[-\s]+', '_', cleaned)
    return cleaned.strip('_')

def main(
    input_dir: str,
    model_type: str = 'large',
    quant: Optional[str] = None,
    initial_duration: int = 8,
    min_words: int = 8,
    debug: bool = False
):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_name = os.path.basename(input_dir)
    output_dir = f"{input_dir}_renamed_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created output directory: {output_dir}")

    print(f"Loading model: {model_type} (quant: {quant})")
    try:
        print("Loading model...")
        whisper = LightningWhisperMLX(model=model_type, batch_size=1, quant=quant)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return

    audio_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.wav', '.mp3', '.m4a', '.flac', '.ogg'))]
    audio_files.sort(key=lambda x: os.path.getctime(os.path.join(input_dir, x)))

    for index, file in tqdm(enumerate(audio_files, start=1), total=len(audio_files), desc="Processing files"):
        input_path = os.path.join(input_dir, file)
        transcription = transcribe_audio(input_path, whisper, initial_duration, min_words, debug)
        words = transcription.split()[:8]
        word_string = "_".join(words)
        word_string = clean_filename(word_string)
        _, extension = os.path.splitext(file)
        new_filename = f"{index}_{word_string}{extension}"
        if len(new_filename) > 255:
            new_filename = new_filename[:251] + extension
        output_path = os.path.join(output_dir, new_filename)
        shutil.copy2(input_path, output_path)

    print("All files have been processed and renamed.")
    print(f"Output directory: {output_dir}")

if __name__ == "__main__":
    # List of multilingual models 
    # models_to_test = ["tiny", "small", "base", "medium", "large", "large-v2", "distil-large-v2", "large-v3", "distil-large-v3"]
    # Quantization options
    # quant_options = [None, "4bit", "8bit"]
    parser = ArgumentParser(description="Transcribe and rename audio files using Whisper")
    parser.add_argument("input_dir", help="Input directory containing audio files")
    parser.add_argument("--model_type", default="large", help="Whisper model type")
    parser.add_argument("--quant", choices=[None, "4bit", "8bit"], default=None, help="Quantization option")
    parser.add_argument("--initial_duration", type=int, default=8, help="Initial duration to process in seconds")
    parser.add_argument("--min_words", type=int, default=8, help="Minimum number of words required in transcription")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()
    main(args.input_dir, args.model_type, args.quant, args.initial_duration, args.min_words, args.debug)