import os
import json
from config.settings import settings
from src.detection.transcriber import Transcriber
from src.detection.event_finder import EventFinder
from src.detection.confidence import ConfidenceRefiner
from src.utils.transcript_utils import TranscriptUtils
from src.media.video_manager import VideoManager

def get_event(video_path):
    
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return

    # 2. Transcribe
    transcriber = Transcriber()
    segments = transcriber.create_transcript(video_path)
    
    # Save transcript
    os.makedirs(os.path.dirname(settings.TRANSCRIPT_FILE), exist_ok=True)
    with open(settings.TRANSCRIPT_FILE, "w") as f:
        json.dump(segments, f, indent=2)

    # 3. Filter & Detect
    if settings.PREFILTER:
        candidate_segments = TranscriptUtils.prefilter_segments(segments)
    else:
        candidate_segments = segments

    # Limit payload
    candidate_segments = candidate_segments[:150]

    finder = EventFinder()
    raw_events = finder.detect_events_via_llm(candidate_segments)
    
    print(f"🧩 Detected {len(raw_events)} potential events.")

    # 4. Refine Confidence
    refiner = ConfidenceRefiner()
    final_events = []

    for event in raw_events:
        llm_conf = event.get("confidence", 0.5)
        new_conf = refiner.refine(event, segments, llm_conf)
        event["confidence"] = new_conf
        final_events.append(event)

    # 5. Save Detected Events
    final_events.sort(key=lambda x: x["confidence"], reverse=True)
    with open(settings.DETECTED_EVENTS_FILE, "w") as f:
        json.dump(final_events, f, indent=2)

    print(f"✅ Saved events to {settings.DETECTED_EVENTS_FILE}")

    # --- OPTIONAL STEP: Extract Highlight Clips ---
    if settings.EXTRACT_CLIPS:
        print("\n🎥 EXTRACT_CLIPS is True. Extracting highlight clips...")
        
        # Filter for high-confidence events
        high_confidence_events = [e for e in final_events if e['confidence'] > 0.6]
        
        if high_confidence_events:
            mgr = VideoManager()
            # Extract clips with a 2-second buffer
            mgr.extract_event_clips(video_path, high_confidence_events, buffer_seconds=2.0)
            print(f"✅ Extracted {len(high_confidence_events)} clips to assets/video_clips/highlights/")
        else:
            print("⚠️ No high-confidence events found to extract.")
    else:
        print("\n⏩ Skipping clip extraction (EXTRACT_CLIPS = False)")
