import os
import cv2
from glob import glob
from config.settings import settings

class ImageProcessor:
    """
    Handles image manipulations like filters and sketches.
    """
    def convert_to_sketch(self, image_path, save_path):
        try:
            img = cv2.imread(image_path)
            if img is None: return

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            inverted_gray = 255 - gray
            blurred = cv2.GaussianBlur(inverted_gray, (21, 21), 0)
            inverted_blur = 255 - blurred
            sketch = cv2.divide(gray, inverted_blur, scale=256.0)

            cv2.imwrite(save_path, sketch)
        except Exception as e:
            print(f"Error sketching {image_path}: {e}")

    def process_all_frames(self):
        os.makedirs(settings.SKETCH_OUTPUT_DIR, exist_ok=True)
        print("🎨 Converting frames to sketches...")
        
        frames = glob(os.path.join(settings.FRAMES_OUTPUT_DIR, "*.png"))
        for frame_path in frames:
            name = os.path.basename(frame_path)
            save_path = os.path.join(settings.SKETCH_OUTPUT_DIR, f"{name.split('.')[0]}_sketch.jpg")
            self.convert_to_sketch(frame_path, save_path)