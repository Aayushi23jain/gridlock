"""License plate detection and OCR extraction."""

from __future__ import annotations

import cv2
import easyocr
import numpy as np


class PlateReader:
    def __init__(self):
        self.ocr_reader = easyocr.Reader(["en"], gpu=False, download_enabled=True)

    def _find_plate_regions(self, vehicle_roi: np.ndarray) -> list[tuple[int, int, int, int]]:
        if vehicle_roi.size == 0:
            return []
        gray = cv2.cvtColor(vehicle_roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        edges = cv2.Canny(gray, 50, 150)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
        morph = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        h, w = gray.shape[:2]
        candidates = []
        for cnt in contours:
            x, y, bw, bh = cv2.boundingRect(cnt)
            aspect = bw / max(bh, 1)
            area = bw * bh
            if 1.8 < aspect < 6.5 and area > (w * h * 0.005) and y > h * 0.4:
                candidates.append((x, y, x + bw, y + bh, area))
        candidates.sort(key=lambda c: c[4], reverse=True)
        return [(c[0], c[1], c[2], c[3]) for c in candidates[:3]]

    def _ocr_plate_crop(self, crop: np.ndarray) -> tuple[str, float]:
        if crop.size == 0:
            return "UNKNOWN", 0.0
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (0, 0), fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        blurred = cv2.GaussianBlur(gray, (0, 0), 3)
        sharpened = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
        _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        try:
            results = self.ocr_reader.readtext(binary, paragraph=False, adjust_contrast=False)
        except Exception:
            return "UNKNOWN", 0.0

        if not results:
            return "UNKNOWN", 0.0

        best = max(results, key=lambda x: x[2])
        clean = "".join(c for c in best[1].upper() if c.isalnum())
        if len(clean) < 4:
            return "UNKNOWN", float(best[2]) * 0.5
        return clean, float(best[2])

    def extract_from_vehicle(self, image: np.ndarray, bbox: list[int]) -> tuple[str, float, np.ndarray | None]:
        x1, y1, x2, y2 = bbox
        h, w = image.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        vehicle_roi = image[y1:y2, x1:x2]
        if vehicle_roi.size == 0:
            return "UNKNOWN", 0.0, None

        regions = self._find_plate_regions(vehicle_roi)
        best_text, best_conf, best_crop = "UNKNOWN", 0.0, None

        search_regions = regions if regions else [(0, int((y2 - y1) * 0.65), x2 - x1, y2 - y1)]
        for rx1, ry1, rx2, ry2 in search_regions:
            crop = vehicle_roi[ry1:ry2, rx1:rx2]
            text, conf = self._ocr_plate_crop(crop)
            if conf > best_conf:
                best_text, best_conf, best_crop = text, conf, crop

        return best_text, best_conf, best_crop
