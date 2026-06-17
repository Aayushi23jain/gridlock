"""
Performance evaluation for the traffic violation pipeline.

Usage:
    python evaluate.py [--images test_data] [--labels test_data/labels.json]
"""

from __future__ import annotations

import argparse
import json
import os
import time

from pipeline import TrafficViolationPipeline


def compute_metrics(predictions: list[str], ground_truth: list[str]) -> dict:
    tp = sum(1 for p, g in zip(predictions, ground_truth) if p == g and p)
    fp = sum(1 for p, g in zip(predictions, ground_truth) if p != g and p)
    fn = sum(1 for p, g in zip(predictions, ground_truth) if p != g and g)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    accuracy = tp / len(ground_truth) if ground_truth else 0.0
    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "mAP": round((precision + recall) / 2, 4),
    }


def run_evaluation(image_dir: str, labels_path: str | None = None) -> dict:
    pipeline = TrafficViolationPipeline()
    latencies = []
    pred_types = []
    gt_types = []
    total_v = 0

    labels = {}
    if labels_path and os.path.exists(labels_path):
        with open(labels_path, encoding="utf-8") as f:
            labels = json.load(f)

    images = [
        os.path.join(image_dir, f)
        for f in os.listdir(image_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    for img_path in images:
        t0 = time.perf_counter()
        _, _, records, _ = pipeline.run_pipeline(img_path, save_evidence=False)
        latencies.append((time.perf_counter() - t0) * 1000)
        total_v += len(records)

        basename = os.path.basename(img_path)
        gt = labels.get(basename, {}).get("violations", [])
        if gt:
            gt_types.append(gt[0])
            pred_types.append(records[0]["violation_type"] if records else "")

    cls_metrics = compute_metrics(pred_types, gt_types) if gt_types else {
        "accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0, "mAP": 0.0,
    }

    result = {
        **cls_metrics,
        "avg_latency_ms": round(sum(latencies) / len(latencies), 1) if latencies else 0.0,
        "images_evaluated": len(images),
        "violations_detected": total_v,
    }

    os.makedirs("storage", exist_ok=True)
    with open(os.path.join("storage", "eval_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    return result


def main():
    parser = argparse.ArgumentParser(description="Evaluate traffic violation pipeline")
    parser.add_argument("--images", default="test_data", help="Directory of test images")
    parser.add_argument("--labels", default="test_data/labels.json", help="Ground truth labels JSON")
    args = parser.parse_args()

    if not os.path.isdir(args.images):
        print(f"Image directory not found: {args.images}")
        print("Run: python generate_presets.py  first.")
        return

    metrics = run_evaluation(args.images, args.labels)
    print("Evaluation Results")
    print("-" * 30)
    for k, v in metrics.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
