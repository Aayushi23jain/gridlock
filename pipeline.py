"""End-to-end traffic violation analysis pipeline."""

from __future__ import annotations

import datetime
import os
import time

import cv2

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

    def run_pipeline(self, image_path: str, save_evidence: bool = True) -> tuple:
        start = time.perf_counter()
        original, processed = preprocess_image(image_path)

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
                "image_source": os.path.basename(image_path),
                "evidence_path": evidence_path,
                "detections_count": len(detections),
            }
            save_violation(record)
            records.append(record)

        self._last_latency_ms = (time.perf_counter() - start) * 1000
        return original, annotated, records, detections
