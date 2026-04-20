import cv2
import time
import math
import streamlit as st
from ultralytics import YOLO
import os
from datetime import datetime
from forensic_db import log_abandoned_bag, get_all_abandoned_bags, get_statistics, EVIDENCE_FOLDER, get_bags_by_date_range
import pandas as pd

# ==========================================
# 🎨 STREAMLIT PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Security AI Dashboard", page_icon="🛡️", layout="wide")

st.title("🛡️ Smart Edge AI: Abandoned Luggage Detection")
st.markdown("Powered by Dual-Model Edge Tracking & OpenVINO + Forensic Logging")

# ==========================================
# 🎛️ SIDEBAR NAVIGATION & CONTROLS
# ==========================================
with st.sidebar:
    st.header("⚙️ System Navigation")
    page = st.radio("Select View:", ["🟢 Live Monitoring", "📊 Forensic History", "📈 Statistics"], horizontal=False)
    
    st.markdown("---")
    st.header("⚙️ System Controls")
    time_limit = st.slider("Abandonment Time Limit (Seconds)", min_value=3, max_value=15, value=5)
    run_camera = st.checkbox("🟢 START SECURITY FEED", value=page == "🟢 Live Monitoring")
    st.markdown("---")
    st.markdown("**Primary Model:** `best_int8_openvino` (Bags)")
    st.markdown("**Secondary Model:** `yolov8n.pt` (Humans)")
    st.markdown("**Target Device:** `Intel CPU`")

# ==========================================
# 📊 METRICS & LAYOUT
# ==========================================

if page == "🟢 Live Monitoring":
    col1, col2 = st.columns(2)
    with col1:
        fps_metric = st.empty()  
    with col2:
        status_metric = st.empty() 

    st.markdown("---")
    video_placeholder = st.empty()

# ==========================================
# 🧠 AI & LOGIC INITIALIZATION
# ==========================================
@st.cache_resource
def load_models():
    # If you haven't exported to openvino yet, you can test with normal yolov8n.pt here
    bag_model = YOLO("best_int8_openvino_model", task="detect")
    person_model = YOLO("yolov8n.pt")
    return bag_model, person_model

if page == "🟢 Live Monitoring":
    bag_model, person_model = load_models()

    bag_states = {}
    DYNAMIC_TOLERANCE_PCT = 0.10   # Dynamic tolerance: 10% of bag size to handle AI jitter
    GRACE_PERIOD = 2.0         # Seconds to remember a bag if temporarily blocked
    evidence_saved = {}        # Track which bags have had evidence saved

    # ==========================================
    # 🎥 THE LIVE VIDEO LOOP
    # ==========================================
    if run_camera:
        cap = cv2.VideoCapture(0)
        status_metric.metric("System Status", "🟢 Active & Monitoring", "Secure")
        
        prev_time = time.time()
        frame_counter = 0
        cached_person_boxes = []
        
        while cap.isOpened() and run_camera:
            success, frame = cap.read()
            if not success:
                st.error("❌ Camera connection lost.")
                break

            frame_counter += 1
            current_time = time.time()
            fps = 1 / (current_time - prev_time)
            prev_time = current_time
            
            fps_metric.metric("Live Processing Speed", f"{fps:.1f} FPS", "Load Balanced")

            # ========================================================
            # ⚡ OPTIMIZATION: FRAME SKIPPING FOR HUMAN DETECTION
            # ========================================================
            if frame_counter % 15 == 0:
                person_results = person_model(frame, classes=[0], verbose=False)
                cached_person_boxes = [] 
                
                if person_results[0].boxes is not None:
                    for box in person_results[0].boxes.xyxy.cpu().numpy():
                        px1, py1, px2, py2 = map(int, box)
                        cached_person_boxes.append((px1, py1, px2, py2))

            # Draw subtle blue boxes around people
            for (px1, py1, px2, py2) in cached_person_boxes:
                cv2.rectangle(frame, (px1, py1), (px2, py2), (255, 0, 0), 1)
                cv2.putText(frame, "Human", (px1, py1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

            # ========================================================
            # 🚀 RUN FAST BAG MODEL EVERY FRAME
            # ========================================================
            results = bag_model.track(frame, persist=True, imgsz=320, conf=0.35, classes=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], verbose=False)
            current_ids = []
            alert_triggered = False 

            if results[0].boxes is not None and results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                track_ids = results[0].boxes.id.cpu().numpy()

                for box, track_id in zip(boxes, track_ids):
                    current_ids.append(track_id)
                    x1, y1, x2, y2 = map(int, box)
                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)

                    if track_id not in bag_states:
                        bag_states[track_id] = {'first_seen': current_time, 'last_centroid': (cx, cy), 'stationary_time': 0, 'last_seen': current_time}
                    else:
                        # ========================================================
                        # 1. SPATIAL LOGIC: DYNAMIC JITTER TOLERANCE
                        # ========================================================
                        last_cx, last_cy = bag_states[track_id]['last_centroid']
                        distance = math.sqrt((cx - last_cx)**2 + (cy - last_cy)**2)
                        
                        # Calculate dynamic tolerance based on 10% of the bag's size
                        bag_width = x2 - x1
                        bag_height = y2 - y1
                        dynamic_tolerance = max(bag_width, bag_height) * DYNAMIC_TOLERANCE_PCT

                        if distance > dynamic_tolerance:
                            bag_states[track_id]['stationary_time'] = 0
                            bag_states[track_id]['first_seen'] = current_time
                        else:
                            # ========================================================
                            # 2. OWNER ASSOCIATION: AABB INTERSECTION LOGIC
                            # ========================================================
                            is_accompanied = False
                            for (px1, py1, px2, py2) in cached_person_boxes:
                                # Mathematical check to see if the bag box overlaps the human box
                                overlap = (x1 < px2) and (x2 > px1) and (y1 < py2) and (y2 > py1)
                                
                                if overlap:
                                    is_accompanied = True
                                    # Draw a line linking the centers to show they are touching
                                    pcx, pcy = int((px1 + px2) / 2), int((py1 + py2) / 2)
                                    cv2.line(frame, (cx, cy), (pcx, pcy), (255, 0, 0), 2)
                                    break 
                            
                            if is_accompanied:
                                bag_states[track_id]['first_seen'] = current_time
                                bag_states[track_id]['stationary_time'] = 0
                            else:
                                bag_states[track_id]['stationary_time'] = current_time - bag_states[track_id]['first_seen']

                        bag_states[track_id]['last_centroid'] = (cx, cy)
                        bag_states[track_id]['last_seen'] = current_time

                    # ========================================================
                    # 3. TRIGGER ALERTS
                    # ========================================================
                    stationary_seconds = bag_states[track_id]['stationary_time']
                    
                    if stationary_seconds >= time_limit:
                        alert_triggered = True
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4) 
                        cv2.putText(frame, f"🚨 ABANDONED ({int(stationary_seconds)}s)", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
                        
                        # ========================================================
                        # 📸 SAVE EVIDENCE IMAGE (FULL FRAME VIEW) - ONLY ONCE PER BAG
                        # ========================================================
                        if track_id not in evidence_saved:
                            try:
                                # Save the FULL CCTV frame (entire frame, not cropped)
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                image_filename = f"abandoned_bag_TrackID{int(track_id)}_{timestamp}_FULL_FRAME.jpg"
                                image_filepath = os.path.join(EVIDENCE_FOLDER, image_filename)
                                
                                # Save the entire frame with box drawn on it
                                cv2.imwrite(image_filepath, frame)
                                
                                # Log to database (only once per bag detection)
                                log_abandoned_bag(
                                    track_id=track_id,
                                    duration_seconds=int(stationary_seconds),
                                    image_filepath=image_filepath,
                                    camera_id="Camera-001",
                                    confidence=0.85,
                                    frame_dims=(frame.shape[1], frame.shape[0]),
                                    bag_bbox=(x1, y1, x2, y2)
                                )
                                evidence_saved[track_id] = True
                            except Exception as e:
                                print(f"Error saving evidence: {e}")
                            
                    elif stationary_seconds > 0:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2) 
                        cv2.putText(frame, f"Counting: {int(stationary_seconds)}s", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    else:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, "Accompanied/Moving", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            keys_to_delete = [k for k, state in bag_states.items() if k not in current_ids and (current_time - state['last_seen']) > GRACE_PERIOD]
            for k in keys_to_delete: 
                del bag_states[k]
                if k in evidence_saved:
                    del evidence_saved[k]

            if alert_triggered: 
                status_metric.metric("System Status", "🚨 THREAT DETECTED", "Abandoned Luggage", delta_color="inverse")
            else: 
                status_metric.metric("System Status", "🟢 Active & Monitoring", "Secure")

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            video_placeholder.image(frame, channels="RGB", use_container_width=True)

        cap.release()
    else:
        status_metric.metric("System Status", "⏸️ System Paused", "Camera Offline", delta_color="off")
        video_placeholder.info("👈 Check the box in the sidebar to start the security feed.")

# ==========================================
# 📊 FORENSIC HISTORY PAGE
# ==========================================
elif page == "📊 Forensic History":
    st.header("📊 Forensic Evidence Log")
    st.markdown("All detected abandoned luggage incidents with evidence images and metadata.")
    
    # Get all abandoned bags from database
    df = get_all_abandoned_bags()
    
    if len(df) == 0:
        st.info("📭 No abandoned luggage detected yet.")
    else:
        st.success(f"✅ Found {len(df)} incident(s)")
        st.markdown("---")
        
        # Display records in expandable sections
        for idx, row in df.iterrows():
            try:
                track_id = int(row['track_id'])
                duration = int(row['duration_seconds'])
            except (ValueError, TypeError):
                track_id = idx
                duration = 0
            
            with st.expander(f"📍 **Track ID {track_id}** | {row['timestamp']} | ⏱️ {duration}s abandoned"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    try:
                        frame_w = int(row['frame_width'])
                        frame_h = int(row['frame_height'])
                        x1 = int(row['bag_x1'])
                        y1 = int(row['bag_y1'])
                        x2 = int(row['bag_x2'])
                        y2 = int(row['bag_y2'])
                        conf = float(row['confidence_score'])
                    except (ValueError, TypeError):
                        frame_w, frame_h, x1, y1, x2, y2, conf = 0, 0, 0, 0, 0, 0, 0.0
                    
                    st.markdown(f"""
                    **Detection Details:**
                    - **Timestamp:** {row['timestamp']}
                    - **Track ID:** {track_id}
                    - **Duration:** {duration} seconds
                    - **Camera:** {row['camera_id']}
                    - **Confidence:** {conf:.2%}
                    - **Frame Resolution:** {frame_w}x{frame_h}
                    - **Bounding Box:** ({x1}, {y1}) to ({x2}, {y2})
                    - **Status:** {row['actions_taken']}
                    """)
                
                with col2:
                    # Display evidence image if it exists
                    if row['image_filepath'] and os.path.exists(row['image_filepath']):
                        image = cv2.imread(row['image_filepath'])
                        if image is not None:
                            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                            st.image(image_rgb, caption="Evidence Image", use_container_width=True)
                    else:
                        st.warning("No evidence image available")
        
        st.markdown("---")
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Export as CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"forensic_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("🗑️ Clear All Records"):
                if st.checkbox("I confirm deletion of all records"):
                    from forensic_db import clear_all_records
                    clear_all_records()
                    st.success("✅ All records cleared")
                    st.rerun()

# ==========================================
# 📈 STATISTICS PAGE
# ==========================================
elif page == "📈 Statistics":
    st.header("📈 Security System Statistics")
    
    stats = get_statistics()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Detections",
            stats['total_detections'],
            delta="incidents logged"
        )
    
    with col2:
        st.metric(
            "Average Duration",
            f"{stats['average_duration_seconds']:.1f}s",
            delta="seconds"
        )
    
    with col3:
        st.metric(
            "Max Duration",
            f"{stats['max_duration_seconds']}s",
            delta="longest incident"
        )
    
    with col4:
        st.metric(
            "Avg Confidence",
            f"{stats['average_confidence']:.1%}",
            delta="detection accuracy"
        )
    
    st.markdown("---")
    
    # Time-based analysis
    st.subheader("📅 Incidents Over Time")
    df = get_all_abandoned_bags()
    
    if len(df) > 0:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df_grouped = df.groupby(df['timestamp'].dt.date).size()
        
        st.bar_chart(df_grouped, use_container_width=True)
        
        st.markdown("---")
        st.subheader("📊 Duration Distribution")
        st.histogram(df['duration_seconds'], bins=10, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🎥 Camera Activity")
        camera_counts = df['camera_id'].value_counts()
        st.bar_chart(camera_counts)
    else:
        st.info("No data available yet for statistical analysis.")
