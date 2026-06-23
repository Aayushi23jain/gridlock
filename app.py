import os
# Force OpenCV to use headless mode to avoid system library dependencies
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'

import streamlit as st
import zipfile

# PDF processing - gracefully handle if system dependencies not available
try:
    from pdf2image import convert_from_path
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

# Import violation types from existing detection module
from detection.violation_detector import VIOLATION_TYPES

# Load UI metadata dynamically from configuration
from config import (
    get_violation_metadata,
    get_severity_colors,
    get_severity_icons,
    get_app_settings,
    get_default_location
)

# Load configuration data
VIOLATION_DATA = {vtype: get_violation_metadata(vtype) for vtype in VIOLATION_TYPES}
SEVERITY_COLORS = get_severity_colors()
SEVERITY_ICONS = get_severity_icons()
APP_SETTINGS = get_app_settings()
DEFAULT_LOCATION = get_default_location()

from pipeline import TrafficViolationPipeline
from analytics.reports import violation_statistics, generate_summary_report
from storage.database import search_violations
from evidence.challan_generator import generate_challan_for_violation

st.set_page_config(
    layout=APP_SETTINGS.get('layout', 'wide'),
    page_title=APP_SETTINGS.get('title', 'AutoTraffic Command Center'),
    page_icon=APP_SETTINGS.get('page_icon', '🚨'),
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
        .main { background-color: #0a0d14; }
        h1, h2, h3, h4, h5, h6 { font-family: 'Inter', sans-serif; color: #f8f9fa; }
        .header-container {
            background: linear-gradient(90deg, rgba(255,75,75,0.1) 0%, rgba(10,13,20,0) 100%);
            padding: 20px;
            border-left: 4px solid #ff4b4b;
            border-radius: 0 12px 12px 0;
            margin-bottom: 25px;
        }
        .infraction-block {
            background: rgba(255, 75, 75, 0.04);
            border: 1px solid rgba(255, 75, 75, 0.2);
            border-left: 6px solid #ff4b4b;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .badge-critical {
            background: #ff4b4b;
            color: #ffffff;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 800;
            display: inline-block;
            margin-bottom: 8px;
        }
        .badge-high {
            background: #ff8800;
            color: #ffffff;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 800;
            display: inline-block;
            margin-bottom: 8px;
        }
        .badge-medium {
            background: #ffcc00;
            color: #000000;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 800;
            display: inline-block;
            margin-bottom: 8px;
        }
        .badge-low {
            background: #44cc44;
            color: #000000;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 800;
            display: inline-block;
            margin-bottom: 8px;
        }
        .violation-details {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 12px;
            margin-top: 12px;
        }
        .camera-info {
            background: rgba(75, 123, 236, 0.1);
            border-left: 4px solid #4b7bec;
            border-radius: 8px;
            padding: 12px;
            margin-top: 8px;
        }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_pipeline():
    return TrafficViolationPipeline()


pipeline = get_pipeline()
metrics = pipeline.get_performance_metrics()

# Get violation statistics for severity indicators
stats = violation_statistics()
high_risk_count = 0
if stats["by_type"]:
    for vtype in stats["by_type"]:
        if vtype in VIOLATION_DATA:
            if VIOLATION_DATA[vtype]['severity'] in ['Critical', 'High']:
                high_risk_count += stats["by_type"][vtype]

st.markdown(f"""
    <div class="header-container">
        <h1 style='margin:0; font-size:2.2rem; font-weight:800;'>{APP_SETTINGS.get('page_icon', '🚨')} {APP_SETTINGS.get('title', 'AutoTraffic Command Center')}</h1>
        <p style='color:#8a90a6; font-size:1.05rem; margin: 4px 0 0 0;'>
            {APP_SETTINGS.get('subtitle', 'Automated Photo Identification & Classification for Traffic Violations')}
        </p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("mAP (eval)", f"{metrics['mAP'] * 100:.1f}%" if metrics['mAP'] else "Run evaluate.py")
col2.metric("Pipeline Latency", f"{metrics['latency_ms']:.0f} ms" if metrics['latency_ms'] else "—")
col3.metric("OCR Success Rate", f"{metrics['ocr_success_rate'] * 100:.1f}%")

# Add severity indicator to main metrics
severity_icon = SEVERITY_ICONS.get("Critical", "🔴") if high_risk_count > 5 else SEVERITY_ICONS.get("High", "🟠") if high_risk_count > 2 else SEVERITY_ICONS.get("Medium", "🟡")
col4.metric(f"{severity_icon} High-Risk Violations", high_risk_count)

main_tab, analytics_tab = st.tabs(["🔍 Detection Workspace", "📊 Analytics & Reports"])

with main_tab:
    ctrl_panel, view_panel = st.columns([1, 1.8])
    load_day = False
    load_night = False

    with ctrl_panel:
        st.markdown("#### 📥 Ingestion Control Deck")
        feed_type = st.tabs(["🖼️ Multi-Format Ingest", "📹 Live Stream (Simulated)"])

        with feed_type[0]:
            upload_types = ["jpg", "png", "jpeg", "zip"]
            upload_label = "Upload frames or archives (.jpg, .png, .zip"
            if PDF_SUPPORT:
                upload_types.append("pdf")
                upload_label += ", .pdf"
            upload_label += ")"
            uploaded_file = st.file_uploader(
                upload_label,
                type=upload_types,
                key="file_uploader_main",
                help="Upload traffic images or archives for violation detection",
            )

        with feed_type[1]:
            st.info("Live RTSP requires camera URL configuration. Toggle simulates a preset feed.")
            if st.toggle("Connect to Intersection Cam-04 Node", key="camera_toggle"):
                load_day = True

    processing_queue = []

    # File upload processing without transient workspace
    if uploaded_file is not None:
        ext = uploaded_file.name.split(".")[-1].lower()
        if ext in ["jpg", "jpeg", "png"]:
            # Process single image using temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as f:
                f.write(uploaded_file.getbuffer())
                temp_path = f.name
            processing_queue.append({"name": uploaded_file.name, "path": temp_path})
            st.success(f"✅ Uploaded: {uploaded_file.name}")
        elif ext == "zip":
            # Process ZIP file using temporary directory
            import tempfile
            import zipfile
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, uploaded_file.name)
                with open(zip_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                extract_dir = os.path.join(temp_dir, "extracted")
                os.makedirs(extract_dir, exist_ok=True)
                
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zf.extractall(extract_dir)
                
                for root, _, files in os.walk(extract_dir):
                    for file in files:
                        if file.lower().endswith((".png", ".jpg", ".jpeg")):
                            # Copy to temp directory for processing
                            temp_file_path = os.path.join(temp_dir, file)
                            processing_queue.append({
                                "name": file,
                                "path": temp_file_path,
                            })
                if processing_queue:
                    st.success(f"✅ Extracted {len(processing_queue)} images from ZIP")
                else:
                    st.error("❌ No valid images found in ZIP")
        elif ext == "pdf":
            if not PDF_SUPPORT:
                st.error("❌ PDF processing is not available on this deployment platform. Please upload images (.jpg, .png) instead.")
            else:
                # Process PDF file using temporary directory
                import tempfile
                pdf_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)
                with open(pdf_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    for idx, page in enumerate(convert_from_path(pdf_path, dpi=120)):
                        page_path = os.path.join(tempfile.gettempdir(), f"pdf_page_{idx}.jpg")
                        page.save(page_path, "JPEG")
                        processing_queue.append({"name": f"Page {idx + 1}", "path": page_path})
                    if processing_queue:
                        st.success(f"✅ Converted {len(processing_queue)} pages from PDF")
                except Exception as e:
                    st.error(f"❌ PDF parse error: {e}")

    if load_day:
        day_path = "test_data/sample_intersection_day.jpg"
        if os.path.exists(day_path):
            processing_queue.append({"name": "Preset: Day Intersection", "path": day_path})
        elif os.path.exists("test_traffic_scene.jpg"):
            processing_queue.append({"name": "Preset: Traffic Scene", "path": "test_traffic_scene.jpg"})
        else:
            st.warning("Run `python generate_presets.py` to create test images.")

    elif load_night:
        night_path = "test_data/sample_intersection_night.jpg"
        if os.path.exists(night_path):
            processing_queue.append({"name": "Preset: Night Intersection", "path": night_path})
        else:
            st.warning("Run `python generate_presets.py` to create test images.")

    if processing_queue:
        if len(processing_queue) > 1:
            with ctrl_panel:
                sel_name = st.selectbox(
                    "Select frame", 
                    [i["name"] for i in processing_queue],
                    key="frame_selector",
                    help="Choose which frame to analyze from the processing queue"
                )
                selected_item = next(i for i in processing_queue if i["name"] == sel_name)
        else:
            selected_item = processing_queue[0]

        with st.spinner("Running YOLOv8 detection + violation analysis..."):
            original, annotated, records, detections = pipeline.run_pipeline(selected_item["path"])

        with view_panel:
            st.markdown(f"**Active frame:** {selected_item['name']}")
            img_col1, img_col2 = st.columns(2)
            with img_col1:
                st.image(original, use_container_width=True, caption="Source Input")
            with img_col2:
                st.image(annotated, use_container_width=True, caption="Annotated Evidence (YOLOv8 + Rules)")

            st.caption(f"Detected {len(detections)} road users/vehicles · {len(records)} violation(s)")

        st.markdown("### 🗃️ Violations & E-Challan Log")
        st.markdown("---")

        # Dynamic camera location based on violations detected
        if records:
            # Get camera locations from the first violation type (all violations in same frame share camera)
            first_violation = records[0]['violation_type']
            if first_violation in VIOLATION_DATA:
                camera_locations = VIOLATION_DATA[first_violation]['camera_locations']
                primary_camera = camera_locations[0]
                
                with st.expander(f"📍 Camera Location: {primary_camera['name']}", expanded=False):
                    st.markdown(f"**Camera ID:** {primary_camera['cam_id']}")
                    st.markdown(f"**Location:** {primary_camera['name']}")
                    st.markdown(f"**Coordinates:** {primary_camera['lat']:.4f}, {primary_camera['lon']:.4f}")
                    st.map([{"lat": primary_camera['lat'], "lon": primary_camera['lon']}], zoom=13)
                    
                    if len(camera_locations) > 1:
                        st.markdown("**Alternative Cameras for this violation type:**")
                        for cam in camera_locations[1:]:
                            st.markdown(f"- {cam['name']} (ID: {cam['cam_id']})")
            else:
                # Fallback to default location if violation type not found
                with st.expander("📍 Camera Location (Default)", expanded=False):
                    st.map([{"lat": DEFAULT_LOCATION['lat'], "lon": DEFAULT_LOCATION['lon']}], zoom=DEFAULT_LOCATION.get('zoom', 13))
        else:
            with st.expander("📍 Camera Location (Default)", expanded=False):
                st.map([{"lat": DEFAULT_LOCATION['lat'], "lon": DEFAULT_LOCATION['lon']}], zoom=DEFAULT_LOCATION.get('zoom', 13))

        if not records:
            st.info("No traffic violations detected in this frame.")

        for idx, item in enumerate(records):
            violation_type = item['violation_type']
            violation_info = VIOLATION_DATA.get(violation_type, {})
            severity = violation_info.get('severity', 'Medium')
            severity_color = SEVERITY_COLORS.get(severity, '#ffcc00')
            
            # Create severity badge class
            severity_badge_class = f"badge-{severity.lower()}" if severity.lower() in ['critical', 'high', 'medium', 'low'] else "badge-medium"
            
            st.markdown(f"""
                <div class="infraction-block" style="border-left-color: {severity_color}">
                    <span class="{severity_badge_class}">{severity.upper()}</span>
                    <p style="margin:4px 0 0 0; font-size:1.2rem; font-weight:800;">
                        #{idx + 1}: {violation_type}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Show violation-specific details
            if violation_info:
                with st.expander("📋 Violation Details", expanded=False):
                    st.markdown(f"""
                        <div class="violation-details">
                            <p style="margin:0 0 8px 0; font-size:0.9rem; color:#8a90a6;">{violation_info.get('description', 'No description available')}</p>
                            <div style="display:flex; gap:16px; flex-wrap:wrap;">
                                <div>
                                    <span style="color:#ff4b4b; font-weight:700;">Penalty:</span>
                                    <span style="color:#f8f9fa;">{violation_info.get('penalty', 'N/A')}</span>
                                </div>
                                <div>
                                    <span style="color:#ff8800; font-weight:700;">Risk Level:</span>
                                    <span style="color:#f8f9fa;">{violation_info.get('risk_level', 'N/A')}</span>
                                </div>
                                <div>
                                    <span style="color:#4b7bec; font-weight:700;">Common Time:</span>
                                    <span style="color:#f8f9fa;">{violation_info.get('common_times', 'N/A')}</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

            col_meta, col_roi, col_action = st.columns([1.2, 1, 1])
            with col_meta:
                st.markdown(f"""
                    * **Classification:** `{item['violation_type']}`
                    * **Confidence:** {item['confidence'] * 100:.1f}%
                    * **Vehicle:** {item.get('vehicle_class', '—')}
                    * **Timestamp:** `{item['timestamp']}`
                """)
            with col_roi:
                plate = item["license_plate"]
                plate_conf = item.get("plate_confidence", 0)
                st.markdown(f"**Plate:** `{plate}` ({plate_conf * 100:.0f}% OCR conf)")
                if item.get("crop_img") is not None:
                    st.image(item["crop_img"], caption="Plate ROI", width=200)
            with col_action:
                try:
                    # Generate comprehensive E-Challan with all required elements
                    evidence_image_path = item.get("evidence_path")
                    annotated_image_path = item.get("evidence_path")  # Same path for annotated image
                    original_image_path = selected_item.get("path", None)
                    
                    # Generate the challan with dynamic camera ID
                    camera_id = "CAM-001"  # Default fallback
                    if violation_type in VIOLATION_DATA:
                        camera_locations = VIOLATION_DATA[violation_type]['camera_locations']
                        camera_id = camera_locations[0]['cam_id']
                    
                    pdf_name = generate_challan_for_violation(
                        violation_data=item,
                        evidence_image_path=original_image_path,
                        annotated_image_path=annotated_image_path,
                        camera_id=camera_id
                    )
                    
                    # Clean up the PDF file after download
                    with open(pdf_name, "rb") as ticket:
                        st.download_button(
                            label=f"📥 Download Official E-Challan ({plate})",
                            data=ticket,
                            file_name=f"E-Challan_{plate}.pdf",
                            mime="application/pdf",
                            key=f"dl_{idx}",
                            use_container_width=True,
                        )
                    
                    # Clean up the generated PDF file
                    if os.path.exists(pdf_name):
                        os.remove(pdf_name)
                        
                except Exception as e:
                    st.error(f"Error generating challan: {str(e)}")
            st.markdown("---")

with analytics_tab:
    st.markdown("### 📊 Violation Analytics & Searchable Records")

    stats = violation_statistics()
    
    # Enhanced metrics with severity breakdown
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Total Violations", stats["total_violations"])
    a2.metric("Avg Confidence", f"{stats['avg_confidence'] * 100:.1f}%")
    a3.metric("OCR Success", f"{stats['ocr_success_rate'] * 100:.1f}%")
    
    # Calculate high-severity violations
    high_severity_count = 0
    if stats["by_type"]:
        for vtype in stats["by_type"]:
            if vtype in VIOLATION_DATA:
                if VIOLATION_DATA[vtype]['severity'] in ['Critical', 'High']:
                    high_severity_count += stats["by_type"][vtype]
    a4.metric("High Severity", high_severity_count)

    # Enhanced visual analytics
    st.markdown("#### 📈 Violations by Type")
    if stats["by_type"]:
        # Add color coding to the bar chart based on severity
        chart_data = stats["by_type"]
        st.bar_chart(chart_data)
        
        # Show severity breakdown
        st.markdown("**Severity Breakdown:**")
        severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for vtype, count in chart_data.items():
            if vtype in VIOLATION_DATA:
                severity = VIOLATION_DATA[vtype]['severity']
                severity_counts[severity] += count
        
        for severity, count in severity_counts.items():
            if count > 0:
                color = SEVERITY_COLORS.get(severity, '#ffcc00')
                st.markdown(f"<span style='color:{color}; font-weight:bold;'>● {severity}:</span> {count} violations", unsafe_allow_html=True)
    else:
        st.info("No violations logged yet. Process an image in the Detection tab.")
    


    st.markdown("#### 🔎 Search Records")
    col_search, col_filter_type, col_filter_severity = st.columns([2, 1, 1])
    
    with col_search:
        search_q = st.text_input(
            "Search by plate or image name",
            key="search_input",
            help="Enter license plate number or image filename to search records",
            placeholder="e.g., DL12AB3456 or image.jpg"
        )
    
    with col_filter_type:
        type_filter = st.selectbox(
            "Filter by Type",
            ["All"] + list(stats["by_type"].keys()) if stats["by_type"] else ["All"],
            key="type_filter_select",
            help="Filter violation records by type"
        )
    
    with col_filter_severity:
        severity_filter = st.selectbox(
            "Filter by Severity",
            ["All", "Critical", "High", "Medium", "Low"],
            key="severity_filter_select",
            help="Filter violation records by severity level"
        )
    
    vtype = "" if type_filter == "All" else type_filter
    rows = search_violations(query=search_q, violation_type=vtype, limit=50)
    
    # Apply severity filter
    if severity_filter != "All" and rows:
        filtered_rows = []
        for row in rows:
            vtype = row['violation_type']
            if vtype in VIOLATION_DATA:
                if VIOLATION_DATA[vtype]['severity'] == severity_filter:
                    filtered_rows.append(row)
        rows = filtered_rows

    if rows:
        display_rows = []
        for r in rows:
            vtype = r["violation_type"]
            severity = VIOLATION_DATA.get(vtype, {}).get('severity', 'Medium') if vtype in VIOLATION_DATA else 'Medium'
            severity_icon = SEVERITY_ICONS.get(severity, '⚪')
            
            display_rows.append({
                "ID": r["id"],
                "Severity": f"{severity_icon} {severity}",
                "Type": r["violation_type"],
                "Confidence": f"{r['confidence'] * 100:.1f}%",
                "Plate": r["license_plate"],
                "Vehicle": r.get("vehicle_class", ""),
                "Source": r.get("image_source", ""),
                "Timestamp": r["timestamp"],
            })
        st.dataframe(display_rows, use_container_width=True)
    else:
        st.caption("No matching records.")

    st.download_button(
        label="📄 Download Summary Report",
        data=generate_summary_report(),
        file_name="violation_report.txt",
        mime="text/plain",
        key="download_report_button",
    )

    st.markdown("---")
    # Data management functionality removed from frontend
    # Backend functions remain available in analytics.reports

    if st.button("🔄 Run Evaluation (test_data)", key="run_evaluation_button"):
        with st.spinner("Evaluating on test_data..."):
            import subprocess
            result = subprocess.run(
                ["python", "evaluate.py"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__)) or ".",
            )
            st.code(result.stdout or result.stderr)
            st.rerun()
