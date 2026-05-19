import sys
import whisper
from moviepy import VideoFileClip

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <video_file>")
    sys.exit(1)

video = VideoFileClip(sys.argv[1])
video.audio.write_audiofile("temp_audio.wav")

# Transcribe with Whisper
model = whisper.load_model("base")
result = model.transcribe("temp_audio.wav")
print(result["text"])
