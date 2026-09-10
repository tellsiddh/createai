"""Convert mp3 files in this folder to compact 16kHz mono WAV for testing.

Each mp3 gets a sibling .wav (same name). Existing .wav files are left alone.
Requires ffmpeg on PATH (e.g. 'brew install ffmpeg').

    python convert_mp3_to_wav.py            # convert every *.mp3 in this folder
    python convert_mp3_to_wav.py a.mp3 b.mp3 # convert only the given files
"""

import os
import sys

from sample_assets import convert_all_mp3s, mp3_to_wav

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if os.path.isfile(a)]
    if args:
        for mp3_path in args:
            wav_path = mp3_to_wav(mp3_path)
            print(f"{mp3_path} -> {wav_path}")
    else:
        wavs = convert_all_mp3s(".")
        if not wavs:
            print("No mp3 files found in this folder.")
        for wav_path in wavs:
            print(f"ready: {wav_path}")
