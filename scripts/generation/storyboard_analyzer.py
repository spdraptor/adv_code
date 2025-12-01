import json
import requests
from config.settings import settings

class StoryboardAnalyzer:
    """
    Uses Azure OpenAI to analyze video frames/scripts.
    """
    def analyze_scenes(self, splits):
        video_clip_data = {"frames": []}
        
        for i, element in enumerate(splits):
            frame_path = f"{settings.FRAMES_OUTPUT_DIR}/scene{i}.png"
            video_clip_data["frames"].append({
                "id": f"f{i+1}",
                "file_name": frame_path,
                "script_snippet": element['text']
            })

        messages = self._build_messages(video_clip_data)
        
        body = {
            "messages": messages,
            "max_tokens": 10000,
            "temperature": 0.0
        }

        print("🧠 Calling Azure OpenAI for Scene Analysis...")
        try:
            resp = requests.post(settings.AZURE_CHAT_URL, headers={"Content-Type": "application/json", "api-key": settings.AZURE_OPENAI_API_KEY}, data=json.dumps(body))
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                parsed = self._safe_parse(content)
                # Merge script back
                for i, item in enumerate(parsed):
                    if i < len(splits): item['script'] = splits[i]['text']
                return parsed
            return []
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return []

    def _build_messages(self, data):
        return [
            {"role": "system", "content": "Analyze video frames. Return JSON array with fields: visual, mood, audio, camera."},
            {"role": "user", "content": f"Analyze these frames: {json.dumps(data)}"}
        ]

    def _safe_parse(self, text):
        try:
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except:
            return []