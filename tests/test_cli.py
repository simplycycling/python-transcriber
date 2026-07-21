"""Tests for the CLI orchestration, with the heavy model calls mocked out."""

from pathlib import Path

import pytest

from video_transcriber import cli, core

RESULT = {
    "text": " Hello world.",
    "segments": [{"start": 0.0, "end": 1.0, "text": " Hello world."}],
}


@pytest.fixture
def fake_video(tmp_path):
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"not really a video")
    return video


def test_missing_file_returns_error(capsys):
    rc = cli.main(["/no/such/video.mp4"])
    assert rc == 1
    assert "not found" in capsys.readouterr().err


def test_no_audio_track_returns_error(monkeypatch, capsys, fake_video):
    def raise_no_audio(video_path, audio_path):
        raise core.NoAudioTrackError("video has no audio track")

    monkeypatch.setattr(core, "extract_audio", raise_no_audio)
    rc = cli.main([str(fake_video)])
    assert rc == 1
    assert "no audio track" in capsys.readouterr().err


def test_happy_path_prints_timestamps_by_default(monkeypatch, capsys, fake_video):
    monkeypatch.setattr(core, "extract_audio", lambda v, a: None)
    monkeypatch.setattr(core, "transcribe", lambda a, model_name, language: RESULT)

    rc = cli.main([str(fake_video)])
    assert rc == 0
    assert capsys.readouterr().out.strip() == "[00:00:00.000] Hello world."


def test_output_file_written(monkeypatch, tmp_path, fake_video):
    monkeypatch.setattr(core, "extract_audio", lambda v, a: None)
    monkeypatch.setattr(core, "transcribe", lambda a, model_name, language: RESULT)

    out = tmp_path / "transcript.txt"
    rc = cli.main([str(fake_video), "-o", str(out), "-f", "text"])
    assert rc == 0
    assert out.read_text(encoding="utf-8") == "Hello world.\n"


def test_temp_audio_is_cleaned_up(monkeypatch, fake_video):
    captured = {}

    def capture(video_path, audio_path):
        captured["audio"] = Path(audio_path)
        assert captured["audio"].exists()  # created before extraction

    monkeypatch.setattr(core, "extract_audio", capture)
    monkeypatch.setattr(core, "transcribe", lambda a, model_name, language: RESULT)

    cli.main([str(fake_video)])
    assert not captured["audio"].exists()  # removed afterwards


def test_temp_audio_cleaned_up_on_transcribe_error(monkeypatch, fake_video):
    captured = {}

    monkeypatch.setattr(
        core, "extract_audio", lambda v, a: captured.__setitem__("audio", Path(a))
    )

    def boom(a, model_name, language):
        raise RuntimeError("model exploded")

    monkeypatch.setattr(core, "transcribe", boom)

    with pytest.raises(RuntimeError):
        cli.main([str(fake_video)])
    assert not captured["audio"].exists()


def test_model_and_language_flags_are_forwarded(monkeypatch, capsys, fake_video):
    seen = {}

    monkeypatch.setattr(core, "extract_audio", lambda v, a: None)

    def record(a, model_name, language):
        seen["model"] = model_name
        seen["language"] = language
        return RESULT

    monkeypatch.setattr(core, "transcribe", record)

    cli.main([str(fake_video), "-m", "small", "-l", "es"])
    assert seen == {"model": "small", "language": "es"}


def test_invalid_format_rejected(fake_video):
    with pytest.raises(SystemExit):
        cli.main([str(fake_video), "-f", "bogus"])
