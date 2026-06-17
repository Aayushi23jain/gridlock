"""Geometry-based traffic rule analysis (stop lines, lanes, signals)."""

from __future__ import annotations

import cv2
import numpy as np


class GeometryAnalyzer:
    def __init__(self):
        self.stop_lines: list[int] = []
        self.lane_center_x: int | None = None
        self.red_light_active = False
        self.no_parking_zones: list[tuple[int, int, int, int]] = []

    def analyze_scene(self, image: np.ndarray) -> None:
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=w // 6, maxLineGap=20)

        self.stop_lines = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(y2 - y1) < 15 and abs(x2 - x1) > w // 5:
                    y_avg = (y1 + y2) // 2
                    if h * 0.45 < y_avg < h * 0.92:
                        self.stop_lines.append(y_avg)

        self.stop_lines = sorted(set(self.stop_lines))

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        upper = image[: int(h * 0.35)]
        red1 = cv2.inRange(hsv[: upper.shape[0]], np.array([0, 100, 80]), np.array([10, 255, 255]))
        red2 = cv2.inRange(hsv[: upper.shape[0]], np.array([160, 100, 80]), np.array([180, 255, 255]))
        red_mask = cv2.bitwise_or(red1, red2)
        red_ratio = cv2.countNonZero(red_mask) / max(red_mask.size, 1)
        self.red_light_active = red_ratio > 0.002

        yellow = cv2.inRange(hsv, np.array([15, 80, 80]), np.array([35, 255, 255]))
        lane_mask = cv2.morphologyEx(yellow, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        lane_cols = np.where(lane_mask.sum(axis=0) > h * 0.05)[0]
        self.lane_center_x = int(np.median(lane_cols)) if len(lane_cols) > 0 else w // 2

        roadside_w = int(w * 0.18)
        self.no_parking_zones = [
            (0, int(h * 0.55), roadside_w, h),
            (w - roadside_w, int(h * 0.55), w, h),
        ]

    def crosses_stop_line(self, bbox: list[int]) -> bool:
        if not self.stop_lines:
            return False
        _, _, _, y2 = bbox
        nearest = min(self.stop_lines, key=lambda y: abs(y - y2))
        return y2 > nearest - 8

    def is_wrong_side(self, bbox: list[int], vehicle_class: str) -> bool:
        if self.lane_center_x is None:
            return False
        cx = (bbox[0] + bbox[2]) // 2
        if vehicle_class in ("car", "bus", "truck"):
            return cx < self.lane_center_x - 30
        return False

    def is_red_light_violation(self, bbox: list[int]) -> bool:
        if not self.red_light_active:
            return False
        _, y1, _, y2 = bbox
        h_est = bbox[3] - bbox[1] if len(bbox) == 4 else 0
        return y2 > h_est * 3

    def is_illegal_parking(self, bbox: list[int]) -> bool:
        cx, cy = (bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2
        for x1, y1, x2, y2 in self.no_parking_zones:
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                return True
        return False
