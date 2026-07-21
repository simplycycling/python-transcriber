"""Command-line interface for video-transcriber."""

from __future__ import annotations

import argparse
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from . import __version__, core, formats

WHISPER_MODELS = ("tiny", "base", "small", "medium", "large", "turbo")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="video-transcribe",
        description="Transcribe a video file to text using OpenAI Whisper.",
    )
    parser.add_argument("video", type=Path, help="Path to the video file.")
    parser.add_argument(
        "-m",
        "--model",
        default="base",
        help=(
            "Whisper model size (default: base). Larger models are more "
            f"accurate but slower. Common choices: {', '.join(WHISPER_MODELS)}."
        ),
    )
    parser.add_argument(
        "-l",
        "--language",
        default=None,
        help="Language code (e.g. en, es). Omit to auto-detect.",
    )
    parser.add_argument(
        "-f",
        "--format",
        default="timestamps",
        choices=formats.FORMATS,
        help=(
            "Output format (default: timestamps). 'text' is plain text; "
            "'timestamps' prefixes each line with [HH:MM:SS.mmm]; "
            "'srt' and 'vtt' produce subtitle files."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write the transcript to this file instead of stdout.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if not args.video.exists():
        print(f"error: video file not found: {args.video}", file=sys.stderr)
        return 1

    # Extract audio to a temp file that is always cleaned up. A named temp file
    # is needed because ffmpeg/moviepy write to a real path.
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    audio_path = Path(tmp.name)
    tmp.close()
    try:
        try:
            core.extract_audio(args.video, audio_path)
        except core.NoAudioTrackError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1

        result = core.transcribe(
            audio_path, model_name=args.model, language=args.language
        )
    finally:
        audio_path.unlink(missing_ok=True)

    transcript = formats.render(result, args.format)

    if args.output is not None:
        args.output.write_text(transcript + "\n", encoding="utf-8")
    else:
        print(transcript)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
