import json
import os
from config.settings import settings
from scripts.detection.transcriber import Transcriber
from scripts.media.video_manager import VideoManager
from scripts.media.image_manager import ImageProcessor
from scripts.generation.storyboard_analyzer import StoryboardAnalyzer

def StoryBoard_creator(video_path):
    
    if not os.path.exists(video_path):
        print("❌ Video file not found.")
        return

    # 2. Transcription
    transcriber = Transcriber()
    # Returns word-level timestamps
    whisper_data = transcriber.create_transcript(video_path)

    # 3. Split Logic (Divide into 6 scenes)
    video_mgr = VideoManager()
    splits = video_mgr.split_transcript_by_words(whisper_data, num_splits=6)
    
    # 4. Generate Clips & Extract Frames
    video_mgr.generate_clips(video_path, splits)
    video_mgr.extract_random_frames()

    # 5. Analyze Scenes (LLM)
    analyzer = StoryboardAnalyzer()
    analysis_result = analyzer.analyze_scenes(splits)
    
    # Save Analysis
    with open(settings.ANALYSIS_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(analysis_result, f, indent=2, ensure_ascii=False)
    print(f"✅ Analysis saved to {settings.ANALYSIS_OUTPUT_FILE}")

    # 6. Create Pencil Sketches
    img_processor = ImageProcessor()
    img_processor.process_all_frames()

    print("\n🎉 Automated Storyboard Process Complete!")
