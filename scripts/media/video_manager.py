import os
import random
from moviepy.editor import VideoFileClip
from PIL import Image
from config.settings import settings
from scriptd.utils.transcript_utils import TranscriptUtils

class VideoManager:
    """
    Handles video splitting, clip generation, and frame extraction.
    """
    def split_transcript_by_words(self, segments, num_splits=6):
        all_words = []
        for seg in segments: all_words.extend(seg['words'])
        
        if not all_words: return []

        total = len(all_words)
        n = total // num_splits
        splits = []

        for i in range(num_splits):
            start_idx = i * n
            end_idx = (i + 1) * n if i < num_splits - 1 else total
            part = all_words[start_idx:end_idx]
            
            if part:
                splits.append({
                    "text": " ".join(w['word'].strip() for w in part),
                    "start": part[0]['start'],
                    "end": part[-1]['end']
                })
        return splits
    def generate_clips(self, video_path, splits):
        os.makedirs(settings.VIDEO_CLIPS_DIR, exist_ok=True)
        video = VideoFileClip(video_path)
        print(f"✂️ Generating {len(splits)} video clips...")
        
        for i, element in enumerate(splits):
            start, end = element['start'], element['end']
            if start < end:
                out_path = os.path.join(settings.VIDEO_CLIPS_DIR, f"scene{i}.mp4")
                video.subclip(start, end).write_videofile(
                    out_path, codec="libx264", audio_codec="aac", 
                    verbose=False, logger=None
                )

        video.close()
    def extract_random_frames(self):
        os.makedirs(settings.FRAMES_OUTPUT_DIR, exist_ok=True)
        clips = sorted([f for f in os.listdir(settings.VIDEO_CLIPS_DIR) if f.endswith('.mp4')])
        
        print(f"📸 Extracting frames from {len(clips)} clips...")
        for clip_file in clips:
            try:
                path = os.path.join(settings.VIDEO_CLIPS_DIR, clip_file)
                with VideoFileClip(path) as vid:
                    ts = random.uniform(0, vid.duration)
                    frame = vid.get_frame(ts)
                    out = os.path.join(settings.FRAMES_OUTPUT_DIR, f"{os.path.splitext(clip_file)[0]}.png")
                    Image.fromarray(frame).save(out)
            except Exception as e:
                print(f"Error on {clip_file}: {e}")

    def extract_event_clips(self, video_path, events, buffer_seconds=0):
        """
        Cuts video clips for specific detected events.
        """
        output_dir = os.path.join(settings.VIDEO_CLIPS_DIR, "highlights")
        os.makedirs(output_dir, exist_ok=True)
        
        video = VideoFileClip(video_path)
        print(f"✂️ Extracting {len(events)} highlight clips to '{output_dir}'...")

        for i, event in enumerate(events):
            try:
                # Parse start/end times
                start = event.get('start_time')
                end = event.get('end_time')

                if isinstance(start, str):
                    start = TranscriptUtils.parse_time_str(start)
                if isinstance(end, str):
                    end = TranscriptUtils.parse_time_str(end)

                if start is None or end is None:
                    continue

                # Add buffer
                start = max(0, start - buffer_seconds)
                end = min(video.duration, end + buffer_seconds)

                if start < end:
                    safe_event_type = event.get('event_type', 'event').replace(" ", "_")
                    filename = f"event_{i}_{safe_event_type}.mp4"
                    out_path = os.path.join(output_dir, filename)

                    print(f"   Saving: {filename} ({start:.2f}s - {end:.2f}s)")
                    
                    video.subclip(start, end).write_videofile(
                        out_path, 
                        codec="libx264", 
                        audio_codec="aac", 
                        verbose=False, 
                        logger=None
                    )
            except Exception as e:
                print(f"❌ Error extracting clip for event {i}: {e}")
        
        video.close()