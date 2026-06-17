# Save this temporarily as generate_presets.py and run it once: python generate_presets.py
import os
import cv2
import numpy as np

os.makedirs("test_data", exist_ok=True)

def make_preset(filename, text, bg_color):
    img = np.ones((720, 1280, 3), dtype=np.uint8) * bg_color
    cv2.putText(img, text, (100, 360), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    cv2.imwrite(f"test_data/{filename}", img)

make_preset("sample_intersection_day.jpg", "MOCK PRESET: BENGALURU DAY TRAFFIC", 45)
make_preset("sample_intersection_night.jpg", "MOCK PRESET: BENGALURU NIGHT TRAFFIC", 15)
print("✅ Test data presets created successfully!")