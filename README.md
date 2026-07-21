# video-transcriber

Transcribes a video file to text using [OpenAI Whisper](https://github.com/openai/whisper), with optional timecodes and subtitle output.

## Requirements

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- ffmpeg (`brew install ffmpeg` on macOS)

## Setup

```bash
uv sync
```

## Usage

```bash
uv run video-transcribe path/to/video.mp4
```

By default the transcript is printed to stdout with a `[HH:MM:SS.mmm]` timecode
on each line.

### Options

| Flag | Description | Default |
| --- | --- | --- |
| `-m`, `--model` | Whisper model size (`tiny`, `base`, `small`, `medium`, `large`, `turbo`). Larger is more accurate but slower. | `base` |
| `-l`, `--language` | Language code (e.g. `en`, `es`). Omit to auto-detect. | auto |
| `-f`, `--format` | Output format: `text`, `timestamps`, `srt`, or `vtt`. | `timestamps` |
| `-o`, `--output` | Write to a file instead of stdout. | stdout |

### Examples

```bash
# Plain text, no timecodes
uv run video-transcribe clip.mp4 -f text

# Generate an SRT subtitle file with the larger, more accurate model
uv run video-transcribe clip.mp4 -m small -f srt -o clip.srt

# Force English and write a WebVTT file
uv run video-transcribe clip.mp4 -l en -f vtt -o clip.vtt
```

## Development

```bash
uv sync --extra dev
uv run pytest
```
