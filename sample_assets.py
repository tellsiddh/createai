"""Helpers that locate or produce real media assets for the test scripts.

The providers behind CreateAI reject synthetic 1-2 pixel images and tone-only
audio as undecodable, so the multimodal scripts need a genuine raster image and
a real recording to exercise the happy path. These helpers prefer real media
files present in the repo folder, and fall back to synthesizing an asset only
when none is available.
"""

import glob
import os
import shutil
import subprocess

AUDIO_EXTENSIONS = (".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm")


def ensure_sample_image(path: str = "sample_image.jpg") -> str:
    """Create a small real JPEG (a red disc on white) if it does not exist.

    Kept well under the 4MB decoded limit that /images/edits enforces, and a
    real raster the vision and edit providers accept.
    """
    if os.path.isfile(path):
        return path

    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise RuntimeError(
            "Pillow is required to synthesize a sample image. Install it with "
            "'pip install pillow', or pass your own image path as the first "
            "argument."
        ) from exc

    size = (256, 256)
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    draw.ellipse((48, 48, 208, 208), fill=(220, 30, 30))
    image.save(path, "JPEG", quality=85)
    return path


def find_sample_audio(directory: str = ".", prefer_ext: str = ".mp3"):
    """Return a real audio file from the folder, or None if there is none.

    Prefers files with prefer_ext, and picks the smallest match so the
    size-constrained OpenAI-compatible route (base64 inside a 6MB request)
    has the best chance of succeeding. Synthesized helper outputs
    (sample_tone.wav, speech_output.mp3) are skipped so a real recording wins.
    """
    skip = {"sample_tone.wav"}
    candidates = []
    for name in os.listdir(directory):
        lower = name.lower()
        if name in skip:
            continue
        if lower.endswith(AUDIO_EXTENSIONS):
            full = os.path.join(directory, name)
            if os.path.isfile(full):
                candidates.append(full)

    if not candidates:
        return None

    def sort_key(path):
        is_preferred = 0 if path.lower().endswith(prefer_ext) else 1
        return (is_preferred, os.path.getsize(path))

    candidates.sort(key=sort_key)
    return candidates[0]


def mp3_to_wav(mp3_path: str, wav_path: str = None, sample_rate: int = 16000) -> str:
    """Convert an mp3 (or any ffmpeg-readable audio) to a compact mono WAV.

    16kHz mono PCM is what speech models expect and keeps the uncompressed WAV
    small. Requires ffmpeg on PATH. Returns the wav path.
    """
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "ffmpeg is required to convert audio to WAV. Install it (e.g. "
            "'brew install ffmpeg')."
        )

    if wav_path is None:
        wav_path = os.path.splitext(mp3_path)[0] + ".wav"

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            mp3_path,
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            wav_path,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return wav_path


def convert_all_mp3s(directory: str = ".", sample_rate: int = 16000):
    """Convert every mp3 in a folder to a 16kHz mono WAV alongside it.

    Skips an mp3 when its wav already exists. Returns the list of wav paths.
    """
    wavs = []
    for mp3_path in sorted(glob.glob(os.path.join(directory, "*.mp3"))):
        wav_path = os.path.splitext(mp3_path)[0] + ".wav"
        if os.path.isfile(wav_path):
            wavs.append(wav_path)
            continue
        wavs.append(mp3_to_wav(mp3_path, wav_path, sample_rate))
    return wavs


def ensure_sample_audio(directory: str = ".") -> str:
    """Return a real audio file to test with.

    Prefers a real recording found in the folder; only falls back to a
    synthesized tone (which some providers reject) when nothing else exists.
    """
    found = find_sample_audio(directory)
    if found:
        return found
    return ensure_sample_wav()


def ensure_sample_wav(path: str = "sample_tone.wav") -> str:
    """Create a 1-second 440Hz mono WAV if it does not exist.

    Fallback only: some providers reject a pure tone as undecodable speech.
    Prefer a real recording via ensure_sample_audio / find_sample_audio.
    """
    if os.path.isfile(path):
        return path

    import math
    import struct
    import wave

    framerate = 16000
    amplitude = 16000
    frames = bytearray()
    for i in range(framerate):
        sample = int(amplitude * math.sin(2 * math.pi * 440 * (i / framerate)))
        frames += struct.pack("<h", sample)

    with wave.open(path, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(framerate)
        handle.writeframes(bytes(frames))
    return path
