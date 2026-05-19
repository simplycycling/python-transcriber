# video-transcriber

Transcribes a video file to text using [OpenAI Whisper](https://github.com/openai/whisper).

## Requirements

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- ffmpeg (`brew install ffmpeg` on macOS)

## Setup

```bash
uv sync
```

## Usage

```bash
uv run python video_transcriber.py path/to/video.mp4
```

The transcript is printed to stdout. Redirect it to save to a file:

```bash
uv run python video_transcriber.py path/to/video.mp4 > transcript.txt
```
