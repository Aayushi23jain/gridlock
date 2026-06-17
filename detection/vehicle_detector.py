"""YOLOv8-based vehicle and road user detection."""

from __future__ import annotations

from ultralytics import YOLO

VEHICLE_CLASSES = {
    "car": 2,
    "motorcycle": 3,
    "bus": 5,
    "truck": 7,
    "bicycle": 1,
    "person": 0,
}

COCO_TO_LABEL = {v: k for k, v in VEHICLE_CLASSES.items()}


class VehicleDetector:
    def __init__(self, model_name: str = "yolov8n.pt", conf: float = 0.35):
        self.model = YOLO(model_name)
        self.conf = conf
        self.target_ids = set(VEHICLE_CLASSES.values())

    def detect(self, image) -> list[dict]:
        results = self.model(image, conf=self.conf, verbose=False)
        detections = []
        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                cls_id = int(box.cls[0])
                if cls_id not in self.target_ids:
                    continue
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                detections.append({
                    "class": COCO_TO_LABEL.get(cls_id, "unknown"),
                    "bbox": [x1, y1, x2, y2],
                    "confidence": float(box.conf[0]),
                    "center": ((x1 + x2) // 2, (y1 + y2) // 2),
                })
        return detections
