"""End-to-end traffic violation analysis pipeline."""

from __future__ import annotations

import datetime
import os
import time

import cv2
import numpy as np

from analytics.reports import violation_statistics
from detection.vehicle_detector import VehicleDetector
from detection.violation_detector import ViolationDetector
from evidence.annotator import annotate_frame
from ocr.enhanced_plate_reader import EnhancedPlateReader
from preprocessing import preprocess_image
from storage.database import save_violation


class TrafficViolationPipeline:
    def __init__(self):
        self.vehicle_detector = VehicleDetector()
        self.violation_detector = ViolationDetector()
        self.plate_reader = EnhancedPlateReader()
        self._last_latency_ms = 0.0
        self._stats_cache = None
        self._frame_count = 0

    @property
    def last_latency_ms(self) -> float:
        return self._last_latency_ms

    def get_performance_metrics(self) -> dict:
        stats = violation_statistics()
        eval_metrics = self._load_eval_metrics()
        return {
            "latency_ms": round(self._last_latency_ms, 1),
            "avg_confidence": stats["avg_confidence"],
            "ocr_success_rate": stats["ocr_success_rate"],
            "total_logged": stats["total_violations"],
            "mAP": eval_metrics.get("mAP", 0.0),
            "precision": eval_metrics.get("precision", 0.0),
            "recall": eval_metrics.get("recall", 0.0),
            "f1": eval_metrics.get("f1", 0.0),
        }

    def _load_eval_metrics(self) -> dict:
        path = os.path.join("storage", "eval_metrics.json")
        if not os.path.exists(path):
            return {}
        import json
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def set_speed_calibration(self, reference_pixels: float, reference_meters: float):
        """Set calibration for speed calculation."""
        self.violation_detector.set_speed_calibration(reference_pixels, reference_meters)

    def set_speed_limit(self, vehicle_class: str, limit_kmh: float):
        """Set speed limit for a specific vehicle type."""
        self.violation_detector.set_speed_limit(vehicle_class, limit_kmh)

    def process_video_frame(self, image: np.ndarray, timestamp: float, save_evidence: bool = True) -> tuple:
        """Process a single video frame with timestamp for speed tracking."""
        # Set timestamp for tracking
        self.violation_detector.set_frame_timestamp(timestamp)
        
        return self._process_frame(image, save_evidence, f"frame_{self._frame_count}")

    def _process_frame(self, image: np.ndarray, save_evidence: bool = True, image_source: str = "unknown") -> tuple:
        """Common processing logic for both single images and video frames."""
        start = time.perf_counter()
        
        # Preprocess if it's a file path, otherwise assume it's already processed
        if isinstance(image, str):
            original, processed = preprocess_image(image)
            image_source = os.path.basename(image)
        else:
            original = image.copy()
            processed = image.copy()

        detections = self.vehicle_detector.detect(processed)
        violations = self.violation_detector.detect_violations(processed, detections)

        stop_lines = self.violation_detector.geometry.stop_lines
        annotated = annotate_frame(processed, detections, violations, stop_lines)

        os.makedirs("storage/evidence", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        evidence_path = ""

        records = []
        for v in violations:
            plate_text, plate_conf, crop_img = self.plate_reader.extract_from_vehicle(
                processed, v["bbox"]
            )
            if save_evidence:
                evidence_path = os.path.join(
                    "storage/evidence",
                    f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{v['type'][:8].replace(' ', '')}.jpg",
                )
                cv2.imwrite(evidence_path, annotated)

            record = {
                "violation_type": v["type"],
                "confidence": v["confidence"],
                "license_plate": plate_text,
                "plate_confidence": plate_conf,
                "vehicle_class": v.get("vehicle_class", ""),
                "bbox": v["bbox"],
                "timestamp": timestamp,
                "crop_img": crop_img,
                "image_source": image_source,
                "evidence_path": evidence_path,
                "detections_count": len(detections),
            }
            # Add speed data if available
            if "speed" in v:
                record["speed"] = v["speed"]
            if "speed_limit" in v:
                record["speed_limit"] = v["speed_limit"]
            
            save_violation(record)
            records.append(record)

        self._last_latency_ms = (time.perf_counter() - start) * 1000
        self._frame_count += 1
        return original, annotated, records, detections

    def run_pipeline(self, image_path: str, save_evidence: bool = True) -> tuple:
        """Process a single image (backward compatible)."""
        return self._process_frame(image_path, save_evidence)

    def process_video(self, video_path: str, save_evidence: bool = True, fps: float = 30.0) -> list:
        """Process a video file frame by frame for speed detection."""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {video_path}")
        
        all_records = []
        frame_time = 0.0
        frame_interval = 1.0 / fps
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame with timestamp
                _, _, records, _ = self.process_video_frame(frame, frame_time, save_evidence)
                all_records.extend(records)
                
                frame_time += frame_interval
                
                # Process every frame for accuracy, could skip for performance
                # if self._frame_count % 2 == 0:  # Skip every other frame for performance
                #     _, _, records, _ = self.process_video_frame(frame, frame_time, save_evidence)
                #     all_records.extend(records)
                
        finally:
            cap.release()
        
        return all_records
