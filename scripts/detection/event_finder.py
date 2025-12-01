import json
import requests
from config.settings import settings
from src.utils.transcript_utils import TranscriptUtils

class EventFinder:
    """
    Interacts with Azure OpenAI to identify cricket events from text segments.
    """
    
    def detect_events_via_llm(self, candidate_segments: list):
        """
        Sends segments to LLM and returns raw JSON list of events.
        """
        # 1. Build Payload
        messages = self._build_chat_messages(candidate_segments)
        
        body = {
            "messages": messages,
            "max_tokens": 10000,
            "temperature": 0.0,
            "top_p": 1.0,
            "n": 1,
        }

        # 2. Call API
        print("🤖 Calling Azure OpenAI for event detection...")
        resp = requests.post(
            settings.AZURE_CHAT_URL, 
            headers={"Content-Type": "application/json", "api-key": settings.AZURE_OPENAI_API_KEY}, 
            data=json.dumps(body)
        )
        
        if resp.status_code != 200:
            print(f"❌ Azure Request Failed: {resp.status_code} - {resp.text}")
            return []

        # 3. Parse Response
        try:
            content = resp.json()["choices"][0]["message"]["content"]
            return self._extract_json(content)
        except Exception as e:
            print(f"❌ Error parsing response: {e}")
            return []

    def _build_chat_messages(self, segments):
        # Format segments for the prompt
        payload = {
            "segments": [
                {
                    "start": TranscriptUtils.format_seconds(s.get("segment_start", 0)),
                    "end": TranscriptUtils.format_seconds(s.get("segment_end", 0)),
                    "text": s["text"]
                }
                for s in segments
            ]
        }
        
        system_prompt = (
            "You are a cricket highlight assistant. Detect events from these allowed types: " 
            + ", ".join(settings.ALLOWED_EVENTS) + 
            ". Return a JSON array. Each object must have: event_type, start_time, end_time, confidence (0.0-1.0), excerpt, notes."
        )
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze these segments and return JSON array: {json.dumps(payload, ensure_ascii=False)}"}
        ]

    def _extract_json(self, text):
        try:
            start = text.find("[")
            end = text.rfind("]")
            if start != -1 and end != -1:
                return json.loads(text[start:end+1])
            return json.loads(text)
        except:
            return []