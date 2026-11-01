
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from audio_processor import process_audio

AUDIO_PATH = PROJECT_ROOT / "sample.mp3"

with AUDIO_PATH.open("rb") as audio_file:
    audio_bytes = audio_file.read()

try:
    transcript = process_audio(
        audio_bytes=audio_bytes,
        filename=AUDIO_PATH.name
    )

    print("\nTranscription successful!")
    print(transcript)

except Exception as e:
    print("\nTranscription failed:")
    print(type(e).__name__, e)
    raise
