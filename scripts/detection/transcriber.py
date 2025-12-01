import torch
import json
from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip
from config.settings import settings

class Transcriber:
    """
    Handles audio extraction and transcription using Faster-Whisper.
    """
    def __init__(self):
        self.model_size = settings.WHISPER_MODEL_SIZE
        self.extracted_audio_file = settings.EXTRACTED_AUDIO_FILE
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        self.model = None

    def model_init(self):
        if self.model is None:
            print(f"🚀 Loading Whisper Model ({self.model_size}) on {self.device}...")
            self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)

    def audio_extract(self, video_path):
        print(f"🔊 Extracting audio from {video_path}...")
        try:
            video = VideoFileClip(video_path)
            audio = video.audio
            audio.write_audiofile(
                self.extracted_audio_file, 
                fps=settings.AUDIO_SAMPLE_RATE, 
                nbytes=2, 
                codec='pcm_s16le',
                verbose=False, logger=None
            )
            video.close()
        except Exception as e:
            print(f"❌ Error extracting audio: {e}")

    def create_transcript(self, video_path):
        """
        Generates a transcript with word-level timestamps.
        Returns a list of segment dictionaries.
        """
        self.audio_extract(video_path)
        self.model_init()

        print("📝 Transcribing audio...")
        segments, info = self.model.transcribe(
            self.extracted_audio_file,
            beam_size=5,
            word_timestamps=True,
            task="transcribe"
        )

        word_level_output = []
        for seg_idx, segment in enumerate(segments, start=1):
            seg_dict = {
                "segment_index": seg_idx,
                "segment_start": float(segment.start),
                "segment_end": float(segment.end),
                "text": segment.text.strip(),
                "words": []
            }
            for w_idx, w in enumerate(segment.words, start=1):
                word_info = {
                    "word_index": w_idx,
                    "word": w.word,
                    "start": float(w.start),
                    "end": float(w.end)
                }
                seg_dict["words"].append(word_info)
            word_level_output.append(seg_dict)

        return word_level_output