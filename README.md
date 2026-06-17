# 🚨 Gridlock 2.0: AutoTraffic Command Center AI
> **Automated Vision Intelligence Engine & Real-Time E-Challan Citation Dispatch Node**

Gridlock 2.0 is an enterprise-grade, edge-optimized computer vision system engineered to automate high-density urban traffic monitoring and traffic infraction enforcement. Specifically tested against the complex, chaotic transit constraints of metropolitan environments (such as Bengaluru), the system mitigates manual administrative overhead by translating raw optical video streams into structured, legally binding citation records instantly.

---

## 🛠️ Core Architecture & Features

### 1. Adaptive Image Preprocessing Layer
* **Context-Aware Normalization:** Integrates Contrast Limited Adaptive Histogram Equalization (**CLAHE**) alongside custom spatial filtering parameters.
* **Environmental Resilience:** Dynamically balances frames to mitigate critical real-world edge challenges including severe low-light/night-vision degradation, heavy monsoon precipitation occlusion, transient shadow patterns, and intense headlight lens flares.

### 2. Unified Object Tracking Tensors
* **Multi-Variant Deep Inference:** Powered by a customized, single-pass **YOLO (Unified Prediction Layer)** model structure.
* **Granular Instance Detection:** Localizes and tracks multi-class entities simultaneously: vehicles (segmented by category), riders, drivers, pedestrians, and localized safety parameters (Helmets, Seatbelts).
* **Heuristic Boundary Tracking:** Computes complex polygon intersections on the fly to flag real-time **Stop-Line Violations**, **Triple Riding**, and **Wrong-Side Driving**.

### 3. Deep License Plate Recognition (OCR Matrix)
* **Localized Region of Interest (ROI):** Isolates the secondary high-confidence bounding box containing the vehicle license matrix.
* **Contextual Indian RTO String Translation:** Custom OCR parsing optimized for variable regional fonts, non-standard plate formats, mud degradation, and high-angle perspective skews (e.g., extracting prefixes like `KA51`, `MH12` smoothly).

### 4. Cryptographic Evidence Generation Workspace
* **Absolute Temporal Logging:** Generates immutable event payload matrices tied to microsecond-accurate server timestamps.
* **Automated Document Pipeline:** Translates verified infractions directly into secure, standalone **Digital E-Challan Citation Tickets via an automated PDF workflow**, ready for legal dispatch.

---

## 📂 Submission Directory Layout

```text
gridlock/
├── .streamlit/
│   └── config.toml           # Core page parameters & global glassmorphism theme locks
├── test_data/                # Synthetic baseline simulation matrices (Day/Night snapshot presets)
├── transient_workspace/      # Dynamic microsecond scratchpad container (Wiped instantly post-inference)
│   └── .gitkeep              # Preserves empty file directory structure within Git trees
├── app.py                    # Premium frontend execution layer with completely fluid layout mechanics
├── pipeline.py               # Deep Learning Backend Engine (CLAHE -> YOLO -> OCR Matrix -> Log Output)
└── requirements.txt          # Explicitly version-locked Python runtime package dependencies