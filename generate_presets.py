"""Generate synthetic day/night test traffic images and labels."""

import json
import os

import cv2
import numpy as np


def _draw_road(img: np.ndarray, night: bool = False) -> np.ndarray:
    h, w = img.shape[:2]
    cv2.line(img, (0, int(h * 0.65)), (w, int(h * 0.65)), (0, 255, 255), 6)
    cv2.line(img, (int(w * 0.42), int(h * 0.65)), (int(w * 0.42), h), (255, 255, 255), 8)

    if night:
        noise = np.random.normal(0, 20, img.shape).astype(np.uint8)
        img = cv2.addWeighted(img, 0.85, noise, 0.15, 0)
        img = cv2.convertScaleAbs(img, alpha=0.6, beta=10)
    else:
        noise = np.random.normal(0, 10, img.shape).astype(np.uint8)
        img = cv2.addWeighted(img, 0.92, noise, 0.08, 0)
    return img


def create_day_image() -> np.ndarray:
    img = np.ones((1080, 1920, 3), dtype=np.uint8) * 45
    img = _draw_road(img, night=False)

    cv2.rectangle(img, (200, 400), (600, 820), (50, 50, 200), -1)
    cv2.rectangle(img, (200, 400), (600, 820), (0, 0, 255), 4)
    cv2.rectangle(img, (350, 720), (520, 770), (255, 255, 255), -1)
    cv2.putText(img, "DL3CAM1234", (360, 755), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 3)

    cv2.rectangle(img, (1000, 450), (1300, 900), (200, 100, 50), -1)
    cv2.rectangle(img, (1000, 450), (1300, 900), (255, 165, 0), 4)
    cv2.rectangle(img, (1100, 820), (1250, 860), (255, 255, 255), -1)
    cv2.putText(img, "MH12AB9999", (1110, 850), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    cv2.putText(img, "ENFORCEMENT CAM: NODE-04 (DAY)", (50, 80),
                cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2)
    return img


def create_night_image() -> np.ndarray:
    img = np.ones((1080, 1920, 3), dtype=np.uint8) * 15
    img = _draw_road(img, night=True)

    cv2.rectangle(img, (700, 420), (1100, 850), (40, 40, 180), -1)
    cv2.rectangle(img, (700, 420), (1100, 850), (0, 0, 255), 4)
    cv2.rectangle(img, (850, 760), (980, 805), (220, 220, 220), -1)
    cv2.putText(img, "KA51HA9821", (858, 795), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)

    cv2.circle(img, (1600, 120), 25, (0, 0, 255), -1)

    cv2.putText(img, "ENFORCEMENT CAM: NODE-04 (NIGHT)", (50, 80),
                cv2.FONT_HERSHEY_DUPLEX, 1.2, (200, 200, 200), 2)
    return img


def main():
    os.makedirs("test_data", exist_ok=True)

    day_path = "test_data/sample_intersection_day.jpg"
    night_path = "test_data/sample_intersection_night.jpg"
    scene_path = "test_traffic_scene.jpg"

    cv2.imwrite(day_path, create_day_image())
    cv2.imwrite(night_path, create_night_image())
    cv2.imwrite(scene_path, create_day_image())

    labels = {
        "sample_intersection_day.jpg": {
            "violations": ["Stop-Line Violation", "Helmet Non-Compliance"],
            "plates": ["DL3CAM1234", "MH12AB9999"],
        },
        "sample_intersection_night.jpg": {
            "violations": ["Stop-Line Violation", "Red-Light Violation"],
            "plates": ["KA51HA9821"],
        },
    }
    with open("test_data/labels.json", "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)

    print(f"Created: {day_path}")
    print(f"Created: {night_path}")
    print(f"Created: {scene_path}")
    print("Created: test_data/labels.json")


if __name__ == "__main__":
    main()
