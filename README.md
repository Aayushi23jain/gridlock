# Gridlock 2.0: Traffic Violation AI System

Automated photo identification and classification for traffic violations using computer vision.




### Quick Start

```bash
pip install -r requirements.txt
python generate_presets.py
streamlit run app.py
```

## Architecture

```
gridlock/
├── app.py                    # Streamlit UI
├── pipeline.py               # Main detection pipeline
├── detection/
│   ├── vehicle_detector.py   # YOLOv8 detection
│   ├── violation_detector.py # 7 violation types
│   └── geometry_rules.py     # Traffic rule analysis
├── ocr/
│   └── plate_reader.py       # License plate OCR
├── evidence/
│   ├── annotator.py          # Frame annotation
│   └── challan_generator.py  # E-Challan PDF generation
├── storage/
│   ├── database.py           # SQLite database
│   └── evidence/             # Saved images
└── analytics/
    └── reports.py            # Statistics & reports
```

## Violation Types

**Standard Violations:**
- Helmet non-compliance
- Seatbelt non-compliance  
- Triple riding
- Wrong-side driving
- Stop-line violation
- Red-light violation
- Illegal parking

## Key Features

### ️ Data Management
```python
# Delete all records
from analytics.reports import clear_all_violation_data
result = clear_all_violation_data()

# Delete specific record  
from storage.database import delete_violation_by_id
delete_violation_by_id(47)
```

### 📊 E-Challan Generation
Professional PDF challans with:
- Vehicle details and violation evidence
- Camera location and timestamp information
- Legal references and fine amounts

**Fine Structure:**
- Helmet/Seatbelt: ₹1000
- Wrong-side driving: ₹1500
- Stop-line/Illegal parking: ₹500
- Red-light violation: ₹1000

## Usage Examples

### Single Image Processing
```python
from pipeline import TrafficViolationPipeline

pipeline = TrafficViolationPipeline()
original, annotated, records, detections = pipeline.run_pipeline("image.jpg")

for record in records:
    print(f"{record['violation_type']}: {record['license_plate']}")
```

### Database Operations
```python
from storage.database import (
    search_violations, get_all_violations, 
    count_by_type, delete_all_violations
)

# Search
results = search_violations(query="DL12", violation_type="Helmet Non-Compliance")

# Statistics
stats = count_by_type()

# Clear data
delete_all_violations()
```

## API Reference

### Pipeline Methods
- `run_pipeline(image_path, save_evidence=True)` - Process single image

### Database Functions
- `save_violation(record)` - Save violation record
- `search_violations(query="", violation_type="", limit=100)` - Search records
- `get_all_violations(limit=500)` - Get all records
- `count_by_type()` - Get counts by violation type
- `get_total_count()` - Get total violations
- `delete_all_violations()` - Delete all records
- `delete_violation_by_id(violation_id)` - Delete specific record

### Analytics Functions
- `violation_statistics()` - Get comprehensive statistics
- `generate_summary_report()` - Generate text report
- `clear_all_violation_data()` - Clear all records with confirmation

## Testing

```bash
# Model evaluation
python evaluate.py
```

## Database Schema

```sql
CREATE TABLE violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    violation_type TEXT NOT NULL,
    confidence REAL NOT NULL,
    license_plate TEXT,
    plate_confidence REAL,
    vehicle_class TEXT,
    bbox TEXT,
    image_source TEXT,
    evidence_path TEXT,
    timestamp TEXT NOT NULL,
    metadata TEXT
);
```

## Performance Tips

**General Processing:**
- YOLOv8n for CPU efficiency
- Optional evidence saving for performance
- Higher resolution = better accuracy

## Tech Stack

- **Detection:** YOLOv8n (COCO pretrained)
- **OCR:** EasyOCR with ROI optimization
- **Database:** SQLite
- **UI:** Streamlit
- **Image Processing:** OpenCV

## Notes

- Uses YOLOv8n for vehicle/person detection
- Helmet/seatbelt use heuristic checks (can be replaced with fine-tuned models)
- License plates detected via contour analysis + EasyOCR
- Single image processing remains fully backward compatible

## License

For educational and research purposes. Production deployment requires additional testing and legal compliance verification.