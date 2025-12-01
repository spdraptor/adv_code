import re
from typing import Dict, List
from src.utils.transcript_utils import TranscriptUtils

class ConfidenceRefiner:
    """
    Refines LLM confidence scores using rule-based heuristics.
    """

    def refine(self, event: Dict, all_segments: List[Dict], llm_confidence: float) -> float:
        """
        Calculates final score based on keywords, duration, and LLM input.
        """
        keyword_score = self._calculate_keyword_strength(event["event_type"], event.get("excerpt", ""))
        duration_score = self._calculate_duration_plausibility(event)
        
        # Weighted Score
        base_score = (keyword_score * 0.6) + (duration_score * 0.4)
        
        # Blend with LLM (50% rules, 50% LLM)
        final_score = (base_score * 0.5) + (llm_confidence * 0.5)
        
        event["confidence_breakdown"] = {
            "keyword_score": round(keyword_score, 2),
            "duration_score": round(duration_score, 2),
            "llm_score": llm_confidence
        }
        
        return round(min(1.0, final_score), 3)

    def _calculate_keyword_strength(self, event_type: str, excerpt: str) -> float:
        excerpt_lower = excerpt.lower()
        strong_keywords = {
            "four": [r"shot", r"boundary", r"four"],
            "six": [r"maximum", r"six", r"huge"],
            "wicket": [r"out", r"bowled", r"caught", r"gone", r"depart"],
            "winning_celebration": [r"win", r"champion", r"victory"]
        }
        
        score = 0.2 # Base
        if event_type in strong_keywords:
            for pattern in strong_keywords[event_type]:
                if re.search(pattern, excerpt_lower): score += 0.4
        
        return min(1.0, score)

    def _calculate_duration_plausibility(self, event: Dict) -> float:
        try:
            s = TranscriptUtils.parse_time_str(event["start_time"])
            e = TranscriptUtils.parse_time_str(event["end_time"])
            if s is None or e is None: return 0.5
            duration = e - s
            # Events typically last 3-20 seconds
            if 3 <= duration <= 20: return 1.0
            return 0.5
        except:
            return 0.5