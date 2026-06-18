import streamlit as st
import os
import zipfile

# PDF processing - gracefully handle if system dependencies not available
try:
    from pdf2image import convert_from_path
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

from pipeline import TrafficViolationPipeline
from analytics.reports import violation_statistics, generate_summary_report, clear_all_violation_data
from storage.database import search_violations
from evidence.challan_generator import generate_challan_for_violation

st.set_page_config(
    layout="wide",
    page_title="AutoTraffic Command Center",
    page_icon="🚨",
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
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_pipeline():
    return TrafficViolationPipeline()


pipeline = get_pipeline()
metrics = pipeline.get_performance_metrics()

st.markdown("""
    <div class="header-container">
        <h1 style='margin:0; font-size:2.2rem; font-weight:800;'>🚨 Gridlock 2.0: AutoTraffic Command Center</h1>
        <p style='color:#8a90a6; font-size:1.05rem; margin: 4px 0 0 0;'>
            Automated Photo Identification & Classification for Traffic Violations
        </p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("mAP (eval)", f"{metrics['mAP'] * 100:.1f}%" if metrics['mAP'] else "Run evaluate.py")
col2.metric("Pipeline Latency", f"{metrics['latency_ms']:.0f} ms" if metrics['latency_ms'] else "—")
col3.metric("OCR Success Rate", f"{metrics['ocr_success_rate'] * 100:.1f}%")
col4.metric("Violations Logged", metrics["total_logged"])

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
            if PDF_SUPPORT:
                upload_types.append("pdf")
            uploaded_file = st.file_uploader(
                f"Upload frames or archives (.jpg, .png, .zip{'', .pdf' if PDF_SUPPORT else ''})",
                type=upload_types,
            )
            st.markdown("**Sandbox Presets:**")
            load_day = st.button("☀️ Analyze Daytime Feed Snapshot", use_container_width=True)
            load_night = st.button("🌙 Analyze Night-Vision Feed Snapshot", use_container_width=True)

        with feed_type[1]:
            st.info("Live RTSP requires camera URL configuration. Toggle simulates a preset feed.")
            if st.toggle("Connect to Intersection Cam-04 Node"):
                load_day = True

    processing_queue = []
    os.makedirs("transient_workspace", exist_ok=True)

    if uploaded_file is not None:
        ext = uploaded_file.name.split(".")[-1].lower()
        if ext in ["jpg", "jpeg", "png"]:
            path = "transient_workspace/live_workspace_frame.jpg"
            with open(path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            processing_queue.append({"name": uploaded_file.name, "path": path})
        elif ext == "zip":
            zip_path = f"transient_workspace/{uploaded_file.name}"
            with open(zip_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall("transient_workspace/extracted_zip")
            for root, _, files in os.walk("transient_workspace/extracted_zip"):
                for file in files:
                    if file.lower().endswith((".png", ".jpg", ".jpeg")):
                        processing_queue.append({
                            "name": file,
                            "path": os.path.join(root, file),
                        })
        elif ext == "pdf":
            if not PDF_SUPPORT:
                st.error("PDF processing is not available on this deployment platform. Please upload images (.jpg, .png) instead.")
            else:
                pdf_path = f"transient_workspace/{uploaded_file.name}"
                with open(pdf_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                try:
                    for idx, page in enumerate(convert_from_path(pdf_path, dpi=120)):
                        page_path = f"transient_workspace/pdf_page_{idx}.jpg"
                        page.save(page_path, "JPEG")
                        processing_queue.append({"name": f"Page {idx + 1}", "path": page_path})
                except Exception as e:
                    st.error(f"PDF parse error: {e}")

    elif load_day:
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
                sel_name = st.selectbox("Select frame", [i["name"] for i in processing_queue])
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

        with st.expander("📍 Camera Location", expanded=False):
            st.map([{"lat": 12.9716, "lon": 77.5946}], zoom=13)

        if not records:
            st.info("No traffic violations detected in this frame.")

        for idx, item in enumerate(records):
            st.markdown(f"""
                <div class="infraction-block">
                    <span class="badge-critical">VIOLATION</span>
                    <p style="margin:4px 0 0 0; font-size:1.2rem; font-weight:800;">
                        #{idx + 1}: {item['violation_type']}
                    </p>
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
                    
                    # Generate the challan
                    pdf_name = generate_challan_for_violation(
                        violation_data=item,
                        evidence_image_path=original_image_path,
                        annotated_image_path=annotated_image_path,
                        camera_id="CAM-001"  # Can be made dynamic
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
    a1, a2, a3 = st.columns(3)
    a1.metric("Total Violations", stats["total_violations"])
    a2.metric("Avg Confidence", f"{stats['avg_confidence'] * 100:.1f}%")
    a3.metric("OCR Success", f"{stats['ocr_success_rate'] * 100:.1f}%")

    if stats["by_type"]:
        st.bar_chart(stats["by_type"])
    else:
        st.info("No violations logged yet. Process an image in the Detection tab.")

    if stats["daily_counts"]:
        st.line_chart(stats["daily_counts"])

    st.markdown("#### 🔎 Search Records")
    search_q = st.text_input("Search by plate or image name")
    type_filter = st.selectbox(
        "Filter by violation type",
        ["All"] + list(stats["by_type"].keys()) if stats["by_type"] else ["All"],
    )
    vtype = "" if type_filter == "All" else type_filter
    rows = search_violations(query=search_q, violation_type=vtype, limit=50)

    if rows:
        display_rows = [{
            "ID": r["id"],
            "Type": r["violation_type"],
            "Confidence": f"{r['confidence'] * 100:.1f}%",
            "Plate": r["license_plate"],
            "Vehicle": r.get("vehicle_class", ""),
            "Source": r.get("image_source", ""),
            "Timestamp": r["timestamp"],
        } for r in rows]
        st.dataframe(display_rows, use_container_width=True)
    else:
        st.caption("No matching records.")

    st.download_button(
        label="📄 Download Summary Report",
        data=generate_summary_report(),
        file_name="violation_report.txt",
        mime="text/plain",
    )

    st.markdown("---")
    st.markdown("#### 🗑️ Data Management")
    
    col_delete1, col_delete2 = st.columns([3, 1])
    
    with col_delete1:
        st.warning("⚠️ This will permanently delete all violation records from the database. This action cannot be undone.")
    
    with col_delete2:
        if st.button("🗑️ Delete All Records", type="secondary"):
            if st.session_state.get("delete_confirmed", False):
                result = clear_all_violation_data()
                st.success(f"✅ {result['message']}")
                st.session_state.delete_confirmed = False
                st.rerun()
            else:
                st.session_state.delete_confirmed = True
                st.error("🚨 Click again to confirm deletion!")
                st.rerun()

    if st.button("🔄 Run Evaluation (test_data)"):
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
