import os
from io import BytesIO

from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY")
)


def process_audio(
    audio_bytes: bytes,
    filename: str
) -> str:

    if not audio_bytes:
        raise ValueError("Empty audio received")

    audio_file = BytesIO(audio_bytes)
    audio_file.name = filename

    try:
        
        response = client.speech_to_text.transcribe(
            file=audio_file,
            model="saaras:v4",
            mode="transcribe",
            language_code="unknown",
        )

        print("RAW RESPONSE:", repr(response))
        print("RESPONSE TYPE:", type(response))
        print("TRANSCRIPT:", repr(getattr(response, "transcript", None)))
        print("FILENAME:", filename)
        print("AUDIO SIZE:", len(audio_bytes))

        transcript = response.transcript

        if not transcript or not transcript.strip():
            raise RuntimeError("Empty transcript received")

        return transcript.strip()

    except Exception as e:
        raise RuntimeError(
            f"Audio transcription failed: {e}"
        ) from e
