"""Helpers that produce small, real media assets for the test scripts.

The providers behind CreateAI reject synthetic 1-2 pixel images and tone-only
audio as undecodable, so the multimodal scripts need a genuine raster image and
a real recording to exercise the happy path. These helpers create such assets
on demand, and cache them in the repo folder so repeated runs are cheap.
"""

import math
import os
import struct
import wave


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


def ensure_sample_wav(path: str = "sample_tone.wav") -> str:
    """Create a 1-second 440Hz mono WAV if it does not exist.

    Note: some providers reject a pure tone as undecodable speech. For a
    transcription happy path, pass a real recording (or the mp3 produced by
    createai_openai_compatible_speech.py) as the first argument instead.
    """
    if os.path.isfile(path):
        return path

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
