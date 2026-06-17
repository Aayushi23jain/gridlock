# Gridlock 2.0: Traffic Violation AI System

Automated photo identification and classification for traffic violations using computer vision.

## Architecture

```
gridlock/
├── app.py                    # Streamlit UI (detection + analytics)
├── pipeline.py               # End-to-end orchestrator
├── preprocessing.py            # CLAHE, deblur, low-light, rain/haze
├── evaluate.py               # mAP, Precision, Recall, F1, latency
├── generate_presets.py       # Synthetic test images + labels
├── detection/
│   ├── vehicle_detector.py   # YOLOv8 vehicle/person detection
│   ├── violation_detector.py # 7 violation types
│   └── geometry_rules.py     # Stop-line, red-light, parking rules
├── ocr/
│   └── plate_reader.py       # Plate region detection + EasyOCR
├── evidence/
│   └── annotator.py          # Annotated evidence frames
├── storage/
│   ├── database.py           # SQLite violation records
│   └── evidence/             # Saved annotated images
└── analytics/
    └── reports.py            # Statistics, trends, summary reports
```

## Setup

```bash
pip install -r requirements.txt
python generate_presets.py
streamlit run app.py
```

## Evaluation

```bash
python evaluate.py
```

Metrics are saved to `storage/eval_metrics.json` and shown in the UI.

## Violation Types Supported

- Helmet non-compliance
- Seatbelt non-compliance
- Triple riding
- Wrong-side driving
- Stop-line violation
- Red-light violation
- Illegal parking

## Notes

- Uses **YOLOv8n** (COCO pretrained) for vehicle/person detection.
- Helmet/seatbelt use heuristic attribute checks; fine-tuned models can replace these for production.
- License plates are detected via contour analysis within vehicle ROIs, then read with EasyOCR.
