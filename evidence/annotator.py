"""Draw detections and violations on evidence frames."""

from __future__ import annotations

import cv2

CLASS_COLORS = {
    "car": (255, 180, 0),
    "motorcycle": (0, 200, 255),
    "bus": (200, 100, 255),
    "truck": (100, 255, 100),
    "bicycle": (255, 255, 0),
    "person": (0, 255, 180),
}


def annotate_frame(
    image,
    detections: list[dict],
    violations: list[dict],
    stop_lines: list[int] | None = None,
) -> "cv2.Mat":
    annotated = image.copy()

    if stop_lines:
        h, w = annotated.shape[:2]
        for y in stop_lines:
            cv2.line(annotated, (0, y), (w, y), (0, 255, 255), 2)
            cv2.putText(annotated, "STOP LINE", (10, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        color = CLASS_COLORS.get(det["class"], (180, 180, 180))
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        label = f"{det['class']} {det['confidence'] * 100:.0f}%"
        cv2.putText(annotated, label, (x1, max(y1 - 6, 14)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

    for v in violations:
        x1, y1, x2, y2 = v["bbox"]
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 0, 255), 3)
        label = f"{v['type']} ({v['confidence'] * 100:.0f}%)"
        cv2.putText(annotated, label, (x1, max(y1 - 10, 18)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)

    return annotated
