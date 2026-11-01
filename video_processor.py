import os
import re
import subprocess
import tempfile
from pathlib import Path

from audio_processor import process_audio
from image_processor import process_image


SCENE_THRESHOLD = 0.3
MAX_FRAMES = 30


def run_ffmpeg(command):
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg failed:\n{result.stderr}"
        )

    return result


def extract_audio(video_path, temp_dir):
    """Extract audio as mono 16 kHz WAV."""

    audio_path = os.path.join(temp_dir, "audio.wav")

    # Check whether the video actually contains an audio stream.
    probe = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=index",
            "-of", "csv=p=0",
            video_path,
        ],
        capture_output=True,
        text=True,
    )

    if probe.returncode != 0:
        raise RuntimeError(
            f"Could not inspect video audio stream: {probe.stderr}"
        )

    if not probe.stdout.strip():
        return None

    run_ffmpeg([
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-map", "0:a:0",
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        audio_path,
    ])

    return audio_path


def extract_frames(video_path, temp_dir):
    """
    Extract frames at scene changes.

    Returns a list of dictionaries containing:
        path: extracted frame path
        timestamp: frame timestamp in seconds
    """

    frames_dir = os.path.join(temp_dir, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    frames_pattern = os.path.join(
        frames_dir,
        "frame_%05d.jpg",
    )

    filter_expression = (
        f"select='eq(n,0)+gt(scene,{SCENE_THRESHOLD})',"
        "showinfo,"
        "scale=1280:-1"
    )

    result = run_ffmpeg([
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf", filter_expression,
        "-fps_mode", "vfr",
        frames_pattern,
    ])

    # Extract timestamps printed by FFmpeg's showinfo filter.
    timestamps = re.findall(
        r"showinfo.*?pts_time:([0-9.]+)",
        result.stderr,
    )

    frame_paths = sorted(
        Path(frames_dir).glob("*.jpg")
    )

    frames = []

    for frame_path, timestamp in zip(frame_paths, timestamps):
        frames.append({
            "path": frame_path,
            "timestamp": float(timestamp),
        })

    if not frames:
        raise ValueError("No video frames could be extracted.")

    # Limit the number of frames sent to the vision model.
    if len(frames) > MAX_FRAMES:
        selected_indices = [
            round(i * (len(frames) - 1) / (MAX_FRAMES - 1))
            for i in range(MAX_FRAMES)
        ]

        selected_frames = [
            frames[i] for i in selected_indices
        ]

        selected_paths = {
            frame["path"] for frame in selected_frames
        }

        # Remove frames that weren't selected.
        for frame in frames:
            if frame["path"] not in selected_paths:
                frame["path"].unlink()

        frames = selected_frames

    return frames


def transcribe_video_audio(audio_path):
    """Transcribe extracted audio using the existing audio processor."""

    if audio_path is None:
        return ""

    with open(audio_path, "rb") as audio_file:
        audio_bytes = audio_file.read()

    if not audio_bytes:
        return ""

    return process_audio(
        audio_bytes=audio_bytes,
        filename="video_audio.wav",
    )


def format_timestamp(seconds):
    """Convert seconds into HH:MM:SS."""

    total_seconds = int(seconds)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return f"{hours:02}:{minutes:02}:{seconds:02}"


def analyze_video_frames(frames):
    """Analyze frames using the existing image processor."""

    descriptions = []

    for frame in frames:
        image_bytes = frame["path"].read_bytes()

        description = process_image(
            image_bytes=image_bytes,
            mime_type="image/jpeg",
        )

        timestamp = format_timestamp(
            frame["timestamp"]
        )

        descriptions.append(
            f"[Timestamp: {timestamp}]\n{description}"
        )

    return "\n\n".join(descriptions)


def process_video(video_path):
    """
    Process a video and return its audio transcript
    and timestamped visual descriptions.
    """

    with tempfile.TemporaryDirectory(
        prefix="video_processing_"
    ) as temp_dir:

        # 1. Extract audio.
        audio_path = extract_audio(
            video_path,
            temp_dir,
        )

        # 2. Detect scenes and extract timestamped frames.
        frames = extract_frames(
            video_path,
            temp_dir,
        )

        # 3. Transcribe audio.
        transcript = transcribe_video_audio(
            audio_path
        )

        # 4. Analyze frames.
        visual_description = analyze_video_frames(
            frames
        )

        # 5. Combine results.
        results = []

        if transcript:
            results.append(
                "Audio transcript:\n" + transcript
            )

        if visual_description:
            results.append(
                "Visual analysis:\n" + visual_description
            )

        if not results:
            raise ValueError(
                "No useful information could be extracted from video."
            )

        return "\n\n".join(results)