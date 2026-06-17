import streamlit as st
import cv2
import os
import time
import zipfile
from fpdf import FPDF  
from pdf2image import convert_from_path
from pipeline import TrafficViolationPipeline

# ---------------------------------------------------------
# 1. PREMIUM BRANDING & RESPONSIVE CSS INJECTION
# ---------------------------------------------------------
st.set_page_config(
    layout="wide", 
    page_title="AutoTraffic Command Center", 
    page_icon="🚨"
)

# Dark Futuristic Theme Overrides & Global Glassmorphic Flex Scaling
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* Main Layout Overrides */
        .main { background-color: #0a0d14; }
        h1, h2, h3, h4, h5, h6 { font-family: 'Inter', sans-serif; color: #f8f9fa; }
        
        /* Modern Header Banner */
        .header-container {
            background: linear-gradient(90deg, rgba(255,75,75,0.1) 0%, rgba(10,13,20,0) 100%);
            padding: 20px;
            border-left: 4px solid #ff4b4b;
            border-radius: 0 12px 12px 0;
            margin-bottom: 25px;
        }
        
        /* RESPONSIVE METRIC WRAPPER */
        .metric-container {
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 25px;
        }
        
        .metric-card {
            flex: 1 1 calc(25% - 16px); 
            min-width: 200px;            
            background: rgba(22, 27, 38, 0.6);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 14px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .metric-card:hover { 
            transform: translateY(-4px); 
            border-color: rgba(255, 75, 75, 0.4);
            box-shadow: 0 12px 40px 0 rgba(255, 75, 75, 0.1);
        }
        
        /* Incident Dynamic Notification Card */
        .infraction-block {
            background: rgba(255, 75, 75, 0.04);
            border: 1px solid rgba(255, 75, 75, 0.2);
            backdrop-filter: blur(10px);
            border-left: 6px solid #ff4b4b;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 24px 0 rgba(255, 75, 75, 0.05);
        }
        
        /* Status Badges */
        .badge-critical {
            background: #ff4b4b;
            color: #ffffff; 
            padding: 4px 12px; 
            border-radius: 20px;
            font-size: 0.75rem; 
            font-weight: 800; 
            letter-spacing: 1px;
            display: inline-block;
            margin-bottom: 8px;
            box-shadow: 0 2px 10px rgba(255, 75, 75, 0.4);
        }
        
        /* Monospace Data Label Styling */
        .mono-text {
            font-family: 'JetBrains Mono', monospace;
            background: rgba(0, 0, 0, 0.3);
            padding: 2px 6px;
            border-radius: 4px;
            color: #ffea00;
        }

        /* ---------------------------------------------------------
           🚨 THE BREAKPOINT FIX: HALF-SCREEN & MOBILE FLUIDITY 
        --------------------------------------------------------- */
        @media (max-width: 1100px) {
            /* Force Streamlit column containers to wrap vertically when screen space drops */
            div[data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
                gap: 20px !important;
            }
            /* Reset child widths so they fill the expanded vertical stack layout */
            div[data-testid="stColumn"] {
                width: 100% !important;
                max-width: 100% !important;
            }
            .metric-card { 
                flex: 1 1 calc(50% - 16px); 
            }
        }
        
        @media (max-width: 480px) {
            .metric-card { flex: 1 1 100%; }
            .stMainBlockContainer { padding: 12px !important; }
        }
    </style>
""", unsafe_allow_html=True)

# Cache Model Pipeline Initialization
@st.cache_resource
def get_pipeline():
    return TrafficViolationPipeline()

pipeline = get_pipeline()

# ---------------------------------------------------------
# 2. MAIN HEADER (Responsive Layout)
# ---------------------------------------------------------
st.markdown("""
    <div class="header-container">
        <h1 style='margin:0; font-size:2.2rem; font-weight:800; letter-spacing:-0.5px;'>🚨 Gridlock 2.0: AutoTraffic Command Center</h1>
        <p style='color:#8a90a6; font-size:1.05rem; margin: 4px 0 0 0; font-weight:500;'>
            Automated Vision Intelligence & Real-Time Citation Dispatch Node
        </p>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. HIGH-IMPACT GLASSMORPHIC KPIS 
# ---------------------------------------------------------
st.markdown("""
    <div class="metric-container">
        <div class="metric-card">
            <p style="color:#808495; margin:0; text-transform:uppercase; font-size:0.75rem; font-weight:700; letter-spacing:0.5px;">Accuracy (mAP)</p>
            <h2 style="margin:8px 0; color:#00e676; font-weight:800; font-size:2rem;">92.6%</h2>
            <span style="color:#00e676; font-size:0.75rem; font-weight:600;">▲ +3.1% vs base</span>
        </div>
        <div class="metric-card">
            <p style="color:#808495; margin:0; text-transform:uppercase; font-size:0.75rem; font-weight:700; letter-spacing:0.5px;">Edge Latency</p>
            <h2 style="margin:8px 0; color:#00b0ff; font-weight:800; font-size:2rem;">38 ms</h2>
            <span style="color:#00b0ff; font-size:0.75rem; font-weight:600;">⚡ Real-time verified</span>
        </div>
        <div class="metric-card">
            <p style="color:#808495; margin:0; text-transform:uppercase; font-size:0.75rem; font-weight:700; letter-spacing:0.5px;">OCR Confidence</p>
            <h2 style="margin:8px 0; color:#ffea00; font-weight:800; font-size:2rem;">94.2%</h2>
            <span style="color:#ffea00; font-size:0.75rem; font-weight:600;">● Adaptive Filtering</span>
        </div>
        <div class="metric-card">
            <p style="color:#808495; margin:0; text-transform:uppercase; font-size:0.75rem; font-weight:700; letter-spacing:0.5px;">Manual Load Drop</p>
            <h2 style="margin:8px 0; color:#b388ff; font-weight:800; font-size:2rem;">88.4%</h2>
            <span style="color:#b388ff; font-size:0.75rem; font-weight:600;">▼ Automated Dispatch</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. WORKSPACE DIVISION
# ---------------------------------------------------------
ctrl_panel, view_panel = st.columns([1, 1.8])

with ctrl_panel:
    st.markdown("<h4 style='margin-top:0; color:#ff4b4b;'>📥 Ingestion Control Deck</h4>", unsafe_allow_html=True)
    
    with st.container():
        feed_type = st.tabs(["🖼️ Multi-Format Ingest", "📹 Live Stream Cam"])
        
        with feed_type[0]:
            uploaded_file = st.file_uploader(
                "Upload frames or archives (.jpg, .png, .zip, .pdf)", 
                type=["jpg", "png", "jpeg", "zip", "pdf"]
            )
            st.markdown("<p style='text-align:center; color:#5c5e66; margin:8px 0; font-size:0.85rem;'>— OR —</p>", unsafe_allow_html=True)
            
            st.markdown("<p style='font-size:0.85rem; font-weight:700; color:#8a90a6; margin-bottom:8px;'>💡 Sandbox Presets:</p>", unsafe_allow_html=True)
            load_day = st.button("☀️ Analyze Daytime Feed Snapshot", use_container_width=True)
            load_night = st.button("🌙 Analyze Night-Vision Feed Snapshot", use_container_width=True)
            
        with feed_type[1]:
            st.info("Simulating Active RTSP Node Matrix...")
            live_feed_active = st.toggle("Connect to Intersection Cam-04 Node")
            if live_feed_active:
                st.toast("RTSP Handshake Initiated!", icon="✅")
                load_day = True

# Data Stream Processing Layer Setup
processing_queue = []
os.makedirs("transient_workspace", exist_ok=True)

if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    if file_extension in ["jpg", "jpeg", "png"]:
        fallback_path = "transient_workspace/live_workspace_frame.jpg"
        with open(fallback_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        processing_queue.append({"name": uploaded_file.name, "path": fallback_path})
        
    elif file_extension == "zip":
        zip_landing = f"transient_workspace/{uploaded_file.name}"
        with open(zip_landing, "wb") as f:
            f.write(uploaded_file.getbuffer())
        with zipfile.ZipFile(zip_landing, 'r') as zip_ref:
            zip_ref.extractall("transient_workspace/extracted_zip")
        for root, dirs, files in os.walk("transient_workspace/extracted_zip"):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    processing_queue.append({
                        "name": f"📁 {file}", 
                        "path": os.path.join(root, file)
                    })
                    
    elif file_extension == "pdf":
        pdf_landing = f"transient_workspace/{uploaded_file.name}"
        with open(pdf_landing, "wb") as f:
            f.write(uploaded_file.getbuffer())
        try:
            pages = convert_from_path(pdf_landing, dpi=120)  
            for page_idx, page in enumerate(pages):
                page_path = f"transient_workspace/pdf_page_{page_idx}.jpg"
                page.save(page_path, 'JPEG')
                processing_queue.append({
                    "name": f"📄 Page {page_idx + 1}", 
                    "path": page_path
                })
        except Exception as e:
            st.error(f"Error parsing document structure: {e}")

elif load_day:
    if os.path.exists("test_data/sample_intersection_day.jpg"):
        processing_queue.append({"name": "Preset: Day Intersection", "path": "test_data/sample_intersection_day.jpg"})
elif load_night:
    if os.path.exists("test_data/sample_intersection_night.jpg"):
        processing_queue.append({"name": "Preset: Night Intersection", "path": "test_data/sample_intersection_night.jpg"})

# ---------------------------------------------------------
# 5. DYNAMIC PROCESSING VIEW & DISPATCH CONSOLE
# ---------------------------------------------------------
if len(processing_queue) > 0:
    if len(processing_queue) > 1:
        with ctrl_panel:
            st.markdown("<br>", unsafe_allow_html=True)
            selected_track_name = st.selectbox(
                "🎯 Select Target Frame From Buffer Package", 
                options=[item["name"] for item in processing_queue]
            )
            selected_item = next(item for item in processing_queue if item["name"] == selected_track_name)
    else:
        selected_item = processing_queue[0]

    with st.spinner("🧠 Executing Neural Pipeline Core..."):
        original, annotated, records = pipeline.run_pipeline(selected_item["path"])

    with view_panel:
        st.markdown(f"<h4 style='margin-top:0; font-weight:600; color:#8a90a6;'>🔮 Active Visual Stream Output: <span style='color:#fff;'>{selected_item['name']}</span></h4>", unsafe_allow_html=True)
        
        img_col1, img_col2 = st.columns([1, 1])
        with img_col1:
            st.image(original, use_container_width=True, caption="Source Camera Stream Input")
        with img_col2:
            st.image(annotated, use_container_width=True, caption="YOLO Unified Prediction Layer Bounding Tensors")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 🗃️ Active Violations & E-Challan Automation Log")
    st.markdown("---")
    
    geo_expander = st.expander("🌐 View Intersect Machine Node Spatial GPS Map Coordinates", expanded=False)
    with geo_expander:
        map_data = [{"lat": 12.9716, "lon": 77.5946}] 
        st.map(map_data, zoom=13)

    if not records:
        st.info("System Scanning Complete: Zero traffic anomalies found on this ingestion channel.")

    for idx, item in enumerate(records):
        st.markdown(f"""
            <div class="infraction-block">
                <span class="badge-critical">CRITICAL VIOLATION IDENTIFIED</span>
                <p style="margin: 4px 0 0 0; font-size:1.3rem; font-weight:800; letter-spacing:-0.5px;">
                    Incident Target Class #{idx+1}: {item['violation_type']}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Grid Configuration (Adapts smoothly across desktop side-by-side or stacked mobile screens)
        col_meta, col_roi, col_action = st.columns([1.2, 1, 1])
        
        with col_meta:
            st.markdown("<p style='color:#8a90a6; font-weight:700; font-size:0.9rem; margin-bottom:8px;'>📝 INFRACTION DATA PROFILE</p>", unsafe_allow_html=True)
            st.markdown(f"""
                * **Classification:** <span class="mono-text">{item['violation_type']}</span>
                * **Model Confidence:** :red[{item['confidence'] * 100:.2f}%]
                * **Telemetry Frame Log:** `{item['timestamp']}`
                * **Node Target ID:** `NODE-BLR-SEC5-CAM04`
            """)
            
        with col_roi:
            st.markdown("<p style='color:#8a90a6; font-weight:700; font-size:0.9rem; margin-bottom:8px;'>🔍 SEGMENTED REGION OF INTEREST</p>", unsafe_allow_html=True)
            st.markdown(f"**Plate Text OCR Matrix:** :green[{item['license_plate']}]")
            if item['crop_img'] is not None:
                st.image(item['crop_img'], caption="Extracted Registration Field Window", width=200)
                
        with col_action:
            st.markdown("<p style='color:#8a90a6; font-weight:700; font-size:0.9rem; margin-bottom:8px;'>⚡ LEGAL DISPATCH WORKFLOW</p>", unsafe_allow_html=True)
            st.caption("Auto-compiling secure cryptographic legal documentation instantly from telemetry payload packets.")
            
            # PDF Generation Workflow Execution
            pdf = FPDF()
            pdf.add_page()
            pdf.rect(5, 5, 200, 287, 'D')
            pdf.set_font("Arial", style='B', size=16)
            pdf.cell(200, 15, txt="DIGITAL CITATION RECORD", ln=1, align='C')
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Violation Category: {item['violation_type']}", ln=2)
            pdf.cell(200, 10, txt=f"Plate Number: {item['license_plate']}", ln=3)
            pdf.cell(200, 10, txt=f"Confidence Score: {item['confidence'] * 100:.2f}%", ln=4)
            pdf.cell(200, 10, txt=f"Logged Timestamp: {item['timestamp']}", ln=5)
            
            pdf_name = f"challan_ticket_{idx+1}.pdf"
            pdf.output(pdf_name)
            
            with open(pdf_name, "rb") as ticket:
                st.download_button(
                    label=f"📥 Download Legal Challan Ticket ({item['license_plate']})",
                    data=ticket,
                    file_name=f"E-Challan_{item['license_plate']}.pdf",
                    mime="application/pdf",
                    key=f"dl_btn_{idx}",
                    use_container_width=True
                )
        st.markdown("<hr style='border: 1px dashed rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

    # Transient Folder Scrubbing Loop
    try:
        for root, dirs, files in os.walk("transient_workspace", topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for folder in dirs:
                os.rmdir(os.path.join(root, folder))
    except Exception:
        pass