import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Central configuration for API keys, endpoints, file paths, and constants.
    """
    def __init__(self):
        # ==========================================
        # API KEYS & ENDPOINTS
        # ==========================================
        self.AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
        self.AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2023-12-01-preview")
        self.AZURE_DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4.1")
        
        self.FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

        # Construct Chat URL
        if self.AZURE_OPENAI_ENDPOINT and self.AZURE_DEPLOYMENT_NAME:
            self.AZURE_CHAT_URL = f"{self.AZURE_OPENAI_ENDPOINT}/openai/deployments/{self.AZURE_DEPLOYMENT_NAME}/chat/completions?api-version={self.AZURE_API_VERSION}"
        else:
            self.AZURE_CHAT_URL = ""

        # ==========================================
        # WHISPER / AUDIO CONFIG
        # ==========================================
        self.WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "turbo")
        self.AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", 16000))
        self.EXTRACTED_AUDIO_FILE = "extracted_audio.wav"

        # ==========================================
        # DETECTION CONSTANTS
        # ==========================================
        self.DEFAULT_WORDS_PER_SECOND = 2.5
        self.CHUNK_WORDS = 40
        self.PREFILTER = True

        self.KEYWORDS = [
            "four", "4", "boundary", "six", "6", "sixer",
            "wicket", "bowled", "caught", "stumped", "run out", "run-out", "lbw",
            "appeal", "umpire", "out", "not out", "review", "drs",
            "fifty", "50", "half-century", "century", "100",
            "partnership", "partnerships", "drop", "dropped", "missed", "hattrick", "hat-trick",
            "timeout", "strategic timeout", "powerplay", "end of over", "over",
            "celebrat", "win", "victory", "walk off", "walk-off", "huge one"
        ]

        self.ALLOWED_EVENTS = [
            "four", "six", "wicket", "appeal_umpire_decision", "end_of_over_score_recap",
            "strategic_timeout", "fifty_century", "partnership_50_plus", "dropped_catch_missed_runout",
            "end_of_innings", "winning_celebration", "back_to_back_boundaries", "bowlers_hattrick",
            "middle_over_wicket_cluster", "wicket_and_bowler_celebration"
        ]

        # ==========================================
        # OUTPUT DIRECTORIES & FILES
        # ==========================================
        self.VIDEO_CLIPS_DIR = "assets/video_clips"
        self.FRAMES_OUTPUT_DIR = "assets/random_frames"
        self.SKETCH_OUTPUT_DIR = "assets/sketch_images"
        self.ANALYSIS_OUTPUT_FILE = "data/video_analysis.json"
        self.DETECTED_EVENTS_FILE = "data/detected_events.json"
        self.TRANSCRIPT_FILE = "data/transcript.txt"

    def get_firecrawl_client(self):
        from firecrawl import Firecrawl
        if not self.FIRECRAWL_API_KEY:
            raise ValueError("❌ Missing FIRECRAWL_API_KEY in .env file")
        return Firecrawl(api_key=self.FIRECRAWL_API_KEY)

    def get_openai_client(self):
        from openai import AzureOpenAI
        if not self.AZURE_OPENAI_API_KEY:
            raise ValueError("❌ Missing AZURE_OPENAI_API_KEY in .env file")
        return AzureOpenAI(
            api_key=self.AZURE_OPENAI_API_KEY,
            api_version=self.AZURE_API_VERSION,
            azure_endpoint=self.AZURE_OPENAI_ENDPOINT,
        )

settings = Config()