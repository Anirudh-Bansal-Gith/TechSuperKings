
import re
import sys
from pathlib import Path
import tempfile

import pytest

# Make the project root importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import video_processor


VIDEO_PATH = Path(__file__).parent / "test_video.mp4"


@pytest.fixture
def video_path():
    assert VIDEO_PATH.is_file(), (
        f"Test video not found: {VIDEO_PATH}"
    )
    return str(VIDEO_PATH)


def test_extract_frames(video_path):
    """Test FFmpeg scene detection and timestamp extraction."""

    with tempfile.TemporaryDirectory() as temp_dir:
        frames = video_processor.extract_frames(
            video_path,
            temp_dir,
        )

        assert len(frames) > 0

        # Respect the maximum frame limit
        assert len(frames) <= video_processor.MAX_FRAMES

        timestamps = []

        for frame in frames:
            assert frame["path"].exists()
            assert frame["path"].stat().st_size > 0
            assert isinstance(frame["timestamp"], float)

            timestamps.append(frame["timestamp"])

        # Frames must be in chronological order
        assert timestamps == sorted(timestamps)

        print(f"\nExtracted {len(frames)} frames:")

        for frame in frames:
            print(
                f"{frame['timestamp']:.2f}s -> "
                f"{frame['path'].name}"
            )


def test_extract_audio(video_path):
    """Test audio extraction, including videos without audio."""

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = video_processor.extract_audio(
            video_path,
            temp_dir,
        )

        if audio_path is None:
            print("\nVideo has no audio stream.")
        else:
            assert Path(audio_path).exists()
            assert Path(audio_path).stat().st_size > 44

            print(f"\nAudio extracted: {audio_path}")


def test_process_video(video_path, monkeypatch):
    """Test the complete pipeline without calling external AI APIs."""

    calls = {
        "audio": 0,
        "images": 0,
    }

    def fake_process_audio(audio_bytes, filename):
        assert audio_bytes
        assert filename == "video_audio.wav"

        calls["audio"] += 1

        return "Mock audio transcript."

    def fake_process_image(image_bytes, mime_type):
        assert image_bytes
        assert mime_type == "image/jpeg"

        calls["images"] += 1

        return f"Mock visual description {calls['images']}."

    # Replace actual API calls with mock functions
    monkeypatch.setattr(
        video_processor,
        "process_audio",
        fake_process_audio,
    )

    monkeypatch.setattr(
        video_processor,
        "process_image",
        fake_process_image,
    )

    result = video_processor.process_video(video_path)

    # Check combined output
    assert isinstance(result, str)
    assert "Visual analysis:" in result
    assert "Mock visual description" in result

    # At least one image should have been processed
    assert calls["images"] > 0

    # If the video has audio, its transcript should appear
    if calls["audio"] > 0:
        assert "Audio transcript:" in result
        assert "Mock audio transcript." in result

    # Every visual description should have a timestamp
    assert re.search(
        r"\[Timestamp: \d{2}:\d{2}:\d{2}\]",
        result,
    )

    print("\nPipeline output:")
    print(result)

    print("\nCalls made:")
    print(calls)


def test_format_timestamp():
    """Test timestamp formatting."""

    assert video_processor.format_timestamp(0) == "00:00:00"
    assert video_processor.format_timestamp(65) == "00:01:05"
    assert video_processor.format_timestamp(3661) == "01:01:01"
