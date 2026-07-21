"""Audio extraction and Whisper transcription.

The heavy third-party imports (moviepy, whisper) are done lazily inside the
functions so that importing this module stays cheap and side-effect free.
"""

from __future__ import annotations

from pathlib import Path


class NoAudioTrackError(ValueError):
    """Raised when a video file has no audio stream to transcribe."""


def extract_audio(video_path: Path, audio_path: Path) -> None:
    """Extract the audio track of ``video_path`` to ``audio_path`` (a WAV file).

    Raises:
        FileNotFoundError: if ``video_path`` does not exist.
        NoAudioTrackError: if the video has no audio stream.
    """
    from moviepy import VideoFileClip

    if not video_path.exists():
        raise FileNotFoundError(f"video file not found: {video_path}")

    clip = VideoFileClip(str(video_path))
    try:
        if clip.audio is None:
            raise NoAudioTrackError(f"video has no audio track: {video_path}")
        # logger=None suppresses moviepy's progress bars, which would
        # otherwise pollute stdout when the transcript is redirected.
        clip.audio.write_audiofile(str(audio_path), logger=None)
    finally:
        clip.close()


def transcribe(
    audio_path: Path,
    model_name: str = "base",
    language: str | None = None,
) -> dict:
    """Transcribe ``audio_path`` with Whisper and return the raw result dict.

    Args:
        audio_path: Path to an audio file readable by ffmpeg.
        model_name: Whisper model size (tiny, base, small, medium, large, ...).
        language: Optional ISO language code to skip auto-detection.
    """
    import whisper

    model = whisper.load_model(model_name)
    return model.transcribe(str(audio_path), language=language)
