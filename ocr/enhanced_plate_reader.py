"""Enhanced license plate detection with improved robustness."""

from __future__ import annotations

import cv2
import easyocr
import numpy as np


class EnhancedPlateReader:
    """Improved plate reader with multiple preprocessing strategies."""
    
    def __init__(self):
        self.ocr_reader = easyocr.Reader(["en"], gpu=False, download_enabled=True)
        
    def _enhanced_preprocessing(self, image: np.ndarray) -> list[np.ndarray]:
        """Apply multiple preprocessing strategies for robust OCR."""
        processed_images = []
        
        # Strategy 1: Current approach
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (0, 0), fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        blurred = cv2.GaussianBlur(gray, (0, 0), 3)
        sharpened = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
        _, binary1 = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_images.append(binary1)
        
        # Strategy 2: Adaptive thresholding
        gray2 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.resize(gray2, (0, 0), fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        binary2 = cv2.adaptiveThreshold(gray2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)
        processed_images.append(binary2)
        
        # Strategy 3: Morphological enhancement
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        binary3 = cv2.morphologyEx(binary1, cv2.MORPH_CLOSE, kernel)
        processed_images.append(binary3)
        
        # Strategy 4: Contrast enhancement
        gray4 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray4 = cv2.resize(gray4, (0, 0), fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced4 = clahe.apply(gray4)
        _, binary4 = cv2.threshold(enhanced4, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_images.append(binary4)
        
        return processed_images
    
    def _ocr_plate_crop_enhanced(self, crop: np.ndarray) -> tuple[str, float]:
        """Enhanced OCR with multiple preprocessing strategies."""
        if crop.size == 0:
            return "UNKNOWN", 0.0
        
        processed_images = self._enhanced_preprocessing(crop)
        best_text, best_conf = "UNKNOWN", 0.0
        
        for processed_img in processed_images:
            try:
                results = self.ocr_reader.readtext(processed_img, paragraph=False, adjust_contrast=False)
                if results:
                    current_best = max(results, key=lambda x: x[2])
                    clean = "".join(c for c in current_best[1].upper() if c.isalnum())
                    if len(clean) >= 4 and current_best[2] > best_conf:
                        best_text, best_conf = clean, float(current_best[2])
            except Exception:
                continue
        
        if best_text == "UNKNOWN":
            return "UNKNOWN", 0.0
        return best_text, best_conf
    
    def _find_plate_regions(self, vehicle_roi: np.ndarray) -> list[tuple[int, int, int, int]]:
        """Enhanced plate region detection with more lenient criteria."""
        if vehicle_roi.size == 0:
            return []
        
        gray = cv2.cvtColor(vehicle_roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Try multiple edge detection thresholds
        edges1 = cv2.Canny(gray, 30, 200)
        edges2 = cv2.Canny(gray, 50, 150)
        edges = cv2.bitwise_or(edges1, edges2)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
        morph = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        h, w = gray.shape[:2]
        candidates = []
        
        for cnt in contours:
            x, y, bw, bh = cv2.boundingRect(cnt)
            aspect = bw / max(bh, 1)
            area = bw * bh
            
            # More lenient criteria for plate detection
            if 1.5 < aspect < 8.0 and area > (w * h * 0.003):
                # Relaxed position requirement
                if y > h * 0.3:  # Changed from 0.4 to 0.3
                    candidates.append((x, y, x + bw, y + bh, area))
        
        candidates.sort(key=lambda c: c[4], reverse=True)
        return [(c[0], c[1], c[2], c[3]) for c in candidates[:5]]  # Return top 5 instead of 3
    
    def extract_from_vehicle(self, image: np.ndarray, bbox: list[int]) -> tuple[str, float, np.ndarray | None]:
        """Enhanced plate extraction with improved detection."""
        x1, y1, x2, y2 = bbox
        h, w = image.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        vehicle_roi = image[y1:y2, x1:x2]
        
        if vehicle_roi.size == 0:
            return "UNKNOWN", 0.0, None
        
        regions = self._find_plate_regions(vehicle_roi)
        best_text, best_conf, best_crop = "UNKNOWN", 0.0, None
        
        # Search detected regions
        search_regions = regions if regions else [(0, int((y2 - y1) * 0.5), x2 - x1, y2 - y1)]
        
        for rx1, ry1, rx2, ry2 in search_regions:
            crop = vehicle_roi[ry1:ry2, rx1:rx2]
            if crop.size == 0:
                continue
                
            text, conf = self._ocr_plate_crop_enhanced(crop)
            if conf > best_conf:
                best_text, best_conf, best_crop = text, conf, crop
        
        return best_text, best_conf, best_crop