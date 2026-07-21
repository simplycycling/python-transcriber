"""Render Whisper transcription results in various output formats.

This module intentionally has no heavy dependencies (whisper, torch, moviepy)
so it can be imported and unit-tested cheaply.

A "segment" is a mapping with at least ``start`` and ``end`` (floats, seconds)
and ``text`` (str), matching the entries in a Whisper result's ``segments``
list.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

# Output format identifiers accepted on the command line.
FORMATS = ("text", "timestamps", "srt", "vtt")

Segment = Mapping[str, object]


def format_timestamp(seconds: float, *, decimal: str = ".") -> str:
    """Format a number of seconds as ``HH:MM:SS<decimal>mmm``.

    ``decimal`` is the separator before the milliseconds: ``.`` for VTT and the
    human-readable timestamp format, ``,`` for SRT.
    """
    if seconds < 0:
        raise ValueError(f"timestamp cannot be negative: {seconds}")
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{decimal}{milliseconds:03d}"


def _segment_fields(segment: Segment) -> tuple[float, float, str]:
    start = float(segment["start"])  # type: ignore[arg-type]
    end = float(segment["end"])  # type: ignore[arg-type]
    text = str(segment["text"]).strip()
    return start, end, text


def to_text(segments: Iterable[Segment]) -> str:
    """Plain transcript, one segment per line, no timestamps."""
    return "\n".join(_segment_fields(seg)[2] for seg in segments)


def to_timestamps(segments: Iterable[Segment]) -> str:
    """Human-readable transcript with a ``[HH:MM:SS.mmm]`` prefix per line."""
    lines = []
    for seg in segments:
        start, _end, text = _segment_fields(seg)
        lines.append(f"[{format_timestamp(start)}] {text}")
    return "\n".join(lines)


def to_srt(segments: Iterable[Segment]) -> str:
    """SubRip (.srt) subtitle format."""
    blocks = []
    for index, seg in enumerate(segments, start=1):
        start, end, text = _segment_fields(seg)
        blocks.append(
            f"{index}\n"
            f"{format_timestamp(start, decimal=',')} --> "
            f"{format_timestamp(end, decimal=',')}\n"
            f"{text}"
        )
    return "\n\n".join(blocks)


def to_vtt(segments: Iterable[Segment]) -> str:
    """WebVTT (.vtt) subtitle format."""
    blocks = ["WEBVTT"]
    for seg in segments:
        start, end, text = _segment_fields(seg)
        blocks.append(f"{format_timestamp(start)} --> {format_timestamp(end)}\n{text}")
    return "\n\n".join(blocks)


_RENDERERS = {
    "text": to_text,
    "timestamps": to_timestamps,
    "srt": to_srt,
    "vtt": to_vtt,
}


def render(result: Mapping[str, object], fmt: str) -> str:
    """Render a Whisper ``result`` dict in the requested format.

    Falls back to the result's top-level ``text`` for the plain ``text`` format
    when no segments are present.
    """
    if fmt not in _RENDERERS:
        raise ValueError(f"unknown format: {fmt!r}; expected one of {FORMATS}")
    segments = result.get("segments") or []
    if fmt == "text" and not segments:
        return str(result.get("text", "")).strip()
    return _RENDERERS[fmt](segments)  # type: ignore[arg-type]
