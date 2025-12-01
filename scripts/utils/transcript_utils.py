import re
import math
from datetime import timedelta
from typing import List, Dict, Optional
from config.settings import settings

class TranscriptUtils:
    """
    Utilities for parsing time strings and formatting timestamps.
    """
    
    @staticmethod
    def format_seconds(seconds: float) -> str:
        """Return HH:MM:SS.mmm string for given seconds (float)."""
        if seconds is None: return "00:00:00.000"
        millis = int(round((seconds - math.floor(seconds)) * 1000))
        td = timedelta(seconds=int(math.floor(seconds)))
        hms = str(td)
        if td.days > 0:
            total_seconds = td.total_seconds()
            hours = int(total_seconds // 3600)
            remainder = int(total_seconds % 3600)
            mm = remainder // 60
            ss = remainder % 60
            hms = f"{hours:02d}:{mm:02d}:{ss:02d}"
        else:
            parts = hms.split(":")
            if len(parts) == 1:
                hms = f"00:00:{int(parts[0]):02d}"
            elif len(parts) == 2:
                hms = f"00:{int(parts[0]):02d}:{int(parts[1]):02d}"
        return f"{hms}.{millis:03d}"

    @staticmethod
    def parse_time_str(s: str) -> Optional[float]:
        """Parse text timestamps (e.g., '00:01:23.500') into float seconds."""
        if not s: return None
        s = s.strip().strip("[]()")
        m = re.match(r"^(\d{1,2}):(\d{2}):(\d{2})(?:[.,](\d+))?$", s)
        if m:
            h = int(m.group(1))
            mm = int(m.group(2))
            ss = int(m.group(3))
            ms = int(m.group(4)) if m.group(4) else 0
            ms_norm = ms
            if m.group(4):
                digits = len(m.group(4))
                if digits < 3:
                    ms_norm = int(m.group(4) * (10 ** (3 - digits)))
                elif digits > 3:
                    ms_norm = int(m.group(4)[:3])
            return h*3600 + mm*60 + ss + ms_norm/1000.0
        return None

    @staticmethod
    def prefilter_segments(segments: List[Dict]) -> List[Dict]:
        """Return only segments containing relevant cricket keywords."""
        kw_regex = re.compile(r"\b(" + "|".join(re.escape(k) for k in settings.KEYWORDS) + r")\b", flags=re.I)
        return [s for s in segments if kw_regex.search(s["text"])]