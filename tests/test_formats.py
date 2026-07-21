"""Tests for the pure formatting functions (no whisper/moviepy needed)."""

import pytest

from video_transcriber import formats

SEGMENTS = [
    {"start": 0.0, "end": 2.5, "text": " Hello there."},
    {"start": 2.5, "end": 3665.0, "text": " General Kenobi."},
]
RESULT = {"text": " Hello there. General Kenobi.", "segments": SEGMENTS}


class TestFormatTimestamp:
    def test_zero(self):
        assert formats.format_timestamp(0) == "00:00:00.000"

    def test_sub_second_millis(self):
        assert formats.format_timestamp(1.234) == "00:00:01.234"

    def test_hours_minutes_seconds(self):
        # 1h 1m 5s
        assert formats.format_timestamp(3665.0) == "01:01:05.000"

    def test_srt_uses_comma_decimal(self):
        assert formats.format_timestamp(2.5, decimal=",") == "00:00:02,500"

    def test_rounds_to_nearest_millisecond(self):
        assert formats.format_timestamp(0.0006) == "00:00:00.001"

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            formats.format_timestamp(-1)


class TestRender:
    def test_text_strips_and_joins(self):
        assert formats.render(RESULT, "text") == "Hello there.\nGeneral Kenobi."

    def test_text_falls_back_to_top_level_when_no_segments(self):
        assert (
            formats.render({"text": " just text ", "segments": []}, "text")
            == "just text"
        )

    def test_timestamps_prefix(self):
        out = formats.render(RESULT, "timestamps")
        # The timestamps format uses each segment's *start* time.
        assert out == ("[00:00:00.000] Hello there.\n" "[00:00:02.500] General Kenobi.")

    def test_srt_structure(self):
        out = formats.render(RESULT, "srt")
        assert out == (
            "1\n"
            "00:00:00,000 --> 00:00:02,500\n"
            "Hello there.\n"
            "\n"
            "2\n"
            "00:00:02,500 --> 01:01:05,000\n"
            "General Kenobi."
        )

    def test_vtt_starts_with_header(self):
        out = formats.render(RESULT, "vtt")
        assert out.startswith("WEBVTT\n\n")
        assert "00:00:00.000 --> 00:00:02.500" in out

    def test_unknown_format_raises(self):
        with pytest.raises(ValueError):
            formats.render(RESULT, "bogus")
