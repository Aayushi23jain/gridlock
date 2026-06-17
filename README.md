# Gridlock 2.0: Traffic Violation AI System

Automated photo identification and classification for traffic violations using computer vision.

## Quick Start

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
│   ├── violation_detector.py # 8 violation types
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

**Advanced Violations:**
- **Overspeed** - Dynamic speed detection with vehicle tracking

## Key Features

### 🚗 Overspeed Detection
```python
from pipeline import TrafficViolationPipeline

pipeline = TrafficViolationPipeline()
pipeline.set_speed_calibration(reference_pixels=100, reference_meters=10)
pipeline.set_speed_limit("car", 50)

violations = pipeline.process_video("traffic_video.mp4")
```

### 🗑️ Data Management
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
- Camera location and speed information
- Legal references and fine amounts

**Fine Structure:**
- Helmet/Seatbelt: ₹1000
- Wrong-side driving: ₹1500
- Stop-line/Illegal parking: ₹500
- Red-light violation: ₹1000
- Overspeed: ₹2000

## Usage Examples

### Single Image Processing
```python
from pipeline import TrafficViolationPipeline

pipeline = TrafficViolationPipeline()
original, annotated, records, detections = pipeline.run_pipeline("image.jpg")

for record in records:
    print(f"{record['violation_type']}: {record['license_plate']}")
```

### Video Processing for Speed Detection
```python
pipeline.set_speed_calibration(100, 10)  # 100px = 10m
pipeline.set_speed_limit("car", 50)

# Process entire video
violations = pipeline.process_video("video.mp4")

# Real-time frame processing
import cv2
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    timestamp = time.time() - start_time
    _, _, violations, _ = pipeline.process_video_frame(frame, timestamp)
```

### Database Operations
```python
from storage.database import (
    search_violations, get_all_violations, 
    count_by_type, delete_all_violations
)

# Search
results = search_violations(query="DL12", violation_type="Overspeed")

# Statistics
stats = count_by_type()

# Clear data
delete_all_violations()
```

## Configuration

### Speed Calibration
```python
# Calibrate for accurate speed detection
pipeline.set_speed_calibration(reference_pixels=150, reference_meters=10)
```

**How to calibrate:**
1. Identify two points with known distance (e.g., traffic lines 10m apart)
2. Measure pixel distance in image (e.g., 150 pixels)
3. Set calibration: `pipeline.set_speed_calibration(150, 10)`

### Speed Limits by Vehicle Type
```python
pipeline.set_speed_limit("car", 50)        # 50 km/h
pipeline.set_speed_limit("motorcycle", 60) # 60 km/h
pipeline.set_speed_limit("truck", 40)      # 40 km/h
pipeline.set_speed_limit("bus", 45)        # 45 km/h
pipeline.set_speed_limit("bicycle", 25)    # 25 km/h
```

## API Reference

### Pipeline Methods
- `run_pipeline(image_path, save_evidence=True)` - Process single image
- `process_video(video_path, save_evidence=True, fps=30)` - Process video file
- `process_video_frame(image, timestamp, save_evidence=True)` - Process single frame
- `set_speed_calibration(reference_pixels, reference_meters)` - Set calibration
- `set_speed_limit(vehicle_class, limit_kmh)` - Set speed limit

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
# Test overspeed detection
python test_overspeed.py

# Test delete functionality
python test_delete.py

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
    metadata TEXT,
    speed REAL,
    speed_limit REAL
);
```

## Performance Tips

**Overspeed Detection:**
- Minimum 10+ frames for reliable speed calculation
- 30 FPS ideal, 15 FPS minimum
- More frames = higher confidence

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
- Overspeed requires video input and calibration
- Single image processing remains fully backward compatible

## License

For educational and research purposes. Production deployment requires additional testing and legal compliance verification.