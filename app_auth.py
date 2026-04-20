"""
Streamlit Dashboard with User Authentication
Multi-user platform for abandoned luggage detection
"""

import cv2
import time
import math
import streamlit as st
from ultralytics import YOLO
import os
from datetime import datetime
from forensic_db import log_abandoned_bag, get_all_abandoned_bags, get_statistics, EVIDENCE_FOLDER, get_bags_by_date_range
from users_db import authenticate_user, register_user, create_access_token, get_user_profile, verify_token
from cameras_db import add_camera, get_user_cameras, get_camera_by_id, delete_camera, test_camera_connection, validate_rtsp_url
import pandas as pd

# ==========================================
# 🎨 STREAMLIT PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Luggage Detection SaaS", page_icon="🛡️", layout="wide")

# ==========================================
# 🔐 SESSION STATE MANAGEMENT
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "token" not in st.session_state:
    st.session_state.token = None

# ==========================================
# 🔐 LOGIN PAGE
# ==========================================
def show_login():
    """Display login/signup page"""
    st.markdown("""
    <style>
    .center {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 🛡️ Abandoned Luggage Detection")
        st.markdown("### Multi-User Security Platform")
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["🔓 Login", "📝 Sign Up"])
        
        with tab1:
            st.subheader("Login to Your Account")
            login_username = st.text_input("Username", key="login_user")
            login_password = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("🔓 Login", use_container_width=True):
                if login_username and login_password:
                    user = authenticate_user(login_username, login_password)
                    
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user["id"]
                        st.session_state.username = user["username"]
                        st.session_state.token = create_access_token({"sub": login_username, "user_id": user["id"]})
                        st.success(f"✅ Welcome, {login_username}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter username and password")
        
        with tab2:
            st.subheader("Create New Account")
            signup_username = st.text_input("Choose Username", key="signup_user")
            signup_email = st.text_input("Email Address", key="signup_email")
            signup_fullname = st.text_input("Full Name (Optional)", key="signup_name")
            signup_password = st.text_input("Password", type="password", key="signup_pass")
            signup_password_confirm = st.text_input("Confirm Password", type="password", key="signup_pass_confirm")
            
            if st.button("📝 Sign Up", use_container_width=True):
                if not signup_username or not signup_email or not signup_password:
                    st.warning("⚠️ Please fill in all required fields")
                elif signup_password != signup_password_confirm:
                    st.error("❌ Passwords do not match")
                elif len(signup_password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    result = register_user(signup_username, signup_email, signup_password, signup_fullname)
                    
                    if result["status"] == "success":
                        st.success("✅ Account created successfully! Please login.")
                    else:
                        st.error(f"❌ {result['message']}")


# ==========================================
# 📊 MAIN DASHBOARD
# ==========================================
def show_dashboard():
    """Display main dashboard for logged-in users"""
    
    st.title("🛡️ Smart Edge AI: Abandoned Luggage Detection")
    st.markdown("Powered by Dual-Model Edge Tracking & OpenVINO + Forensic Logging")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Navigation")
        
        # User info
        user_profile = get_user_profile(st.session_state.user_id)
        if user_profile:
            st.markdown(f"**User:** {user_profile['username']}")
            st.markdown(f"**Email:** {user_profile['email']}")
            st.markdown("---")
        
        page = st.radio("Select View:", ["🟢 Live Monitoring", "� Camera Management", "�📊 Forensic History", "📈 Statistics"], horizontal=False)
        
        st.markdown("---")
        st.header("⚙️ System Controls")
        time_limit = st.slider("Abandonment Time Limit (Seconds)", min_value=3, max_value=15, value=5)
        run_camera = st.checkbox("🟢 START SECURITY FEED", value=page == "🟢 Live Monitoring")
        st.markdown("---")
        st.markdown("**Primary Model:** `best_int8_openvino` (Bags)")
        st.markdown("**Secondary Model:** `yolov8n.pt` (Humans)")
        st.markdown("**Target Device:** `Intel CPU`")
        
        st.markdown("---")
        if st.button("🔓 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.rerun()

    # ==========================================
    # 📊 METRICS & LAYOUT
    # ==========================================

    if page == "🟢 Live Monitoring":
        # Get user's cameras
        cameras = get_user_cameras(st.session_state.user_id)
        
        # Camera selection
        if len(cameras) == 0:
            st.warning("⚠️ No cameras connected. Please add a camera in the Camera Management tab.")
            st.info("ℹ️ You need to connect at least one CCTV camera to use live monitoring.")
        else:
            selected_camera_name = st.selectbox(
                "Select Camera:",
                [f"{c['camera_name']} ({c['connection_status'].title()})" for c in cameras],
                key="camera_select"
            )
            selected_camera = next(c for c in cameras if c['camera_name'] == selected_camera_name.split(" (")[0])
            
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
                bag_model = YOLO("best_int8_openvino_model", task="detect")
                person_model = YOLO("yolov8n.pt")
                return bag_model, person_model

            try:
                bag_model, person_model = load_models()

                bag_states = {}
                DYNAMIC_TOLERANCE_PCT = 0.10
                GRACE_PERIOD = 2.0
            evidence_saved = {}

            # ==========================================
            # 🎥 THE LIVE VIDEO LOOP
            # ==========================================
            if run_camera:
                # Build camera URL with credentials if needed
                camera_url = selected_camera['rtsp_url']
                if selected_camera['username'] and selected_camera['password']:
                    # Embed credentials in RTSP URL
                    camera_url = selected_camera['rtsp_url'].replace(
                        'rtsp://',
                        f"rtsp://{selected_camera['username']}:{selected_camera['password']}@"
                    )
                
                cap = cv2.VideoCapture(camera_url)
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

                    if frame_counter % 15 == 0:
                        person_results = person_model(frame, classes=[0], verbose=False)
                        cached_person_boxes = [] 
                        
                        if person_results[0].boxes is not None:
                            for box in person_results[0].boxes.xyxy.cpu().numpy():
                                px1, py1, px2, py2 = map(int, box)
                                cached_person_boxes.append((px1, py1, px2, py2))

                    for (px1, py1, px2, py2) in cached_person_boxes:
                        cv2.rectangle(frame, (px1, py1), (px2, py2), (255, 0, 0), 1)
                        cv2.putText(frame, "Human", (px1, py1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

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
                                last_cx, last_cy = bag_states[track_id]['last_centroid']
                                distance = math.sqrt((cx - last_cx)**2 + (cy - last_cy)**2)
                                
                                bag_width = x2 - x1
                                bag_height = y2 - y1
                                dynamic_tolerance = max(bag_width, bag_height) * DYNAMIC_TOLERANCE_PCT

                                if distance > dynamic_tolerance:
                                    bag_states[track_id]['stationary_time'] = 0
                                    bag_states[track_id]['first_seen'] = current_time
                                else:
                                    is_accompanied = False
                                    for (px1, py1, px2, py2) in cached_person_boxes:
                                        overlap = (x1 < px2) and (x2 > px1) and (y1 < py2) and (y2 > py1)
                                        
                                        if overlap:
                                            is_accompanied = True
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

                            stationary_seconds = bag_states[track_id]['stationary_time']
                            
                            if stationary_seconds >= time_limit:
                                alert_triggered = True
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 4) 
                                cv2.putText(frame, f"🚨 ABANDONED ({int(stationary_seconds)}s)", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
                                
                                if track_id not in evidence_saved:
                                    try:
                                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                        image_filename = f"abandoned_bag_TrackID{int(track_id)}_{timestamp}_FULL_FRAME.jpg"
                                        image_filepath = os.path.join(EVIDENCE_FOLDER, image_filename)
                                        
                                        cv2.imwrite(image_filepath, frame)
                                        
                                        log_abandoned_bag(
                                            user_id=st.session_state.user_id,
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

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    # ==========================================
    # � CAMERA MANAGEMENT PAGE
    # ==========================================
    elif page == "📹 Camera Management":
        st.header("📹 Camera Management")
        st.markdown("Connect and manage your CCTV cameras for detection")
        
        tab1, tab2 = st.tabs(["📋 My Cameras", "➕ Add New Camera"])
        
        with tab1:
            st.subheader("Connected Cameras")
            cameras = get_user_cameras(st.session_state.user_id)
            
            if len(cameras) == 0:
                st.info("👈 No cameras added yet. Use the 'Add New Camera' tab to connect your first camera.")
            else:
                for camera in cameras:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 1, 1])
                        
                        with col1:
                            status_emoji = "🟢" if camera['connection_status'] == 'connected' else "🔴"
                            st.markdown(f"## {status_emoji} {camera['camera_name']}")
                            st.markdown(f"**Type:** {camera['camera_type']}")
                            st.markdown(f"**URL:** `{camera['rtsp_url']}`")
                            st.markdown(f"**Status:** {camera['connection_status'].title()}")
                            st.markdown(f"**Added:** {camera['created_at'][:10]}")
                            if camera['last_accessed']:
                                st.markdown(f"**Last Used:** {camera['last_accessed'][:10]}")
                        
                        with col2:
                            if st.button(f"🧪 Test", key=f"test_{camera['id']}"):
                                result = test_camera_connection(camera['id'], st.session_state.user_id)
                                if result['status'] == 'connected':
                                    st.success(result['message'])
                                else:
                                    st.error(result['message'])
                        
                        with col3:
                            if st.button(f"❌ Delete", key=f"delete_{camera['id']}"):
                                result = delete_camera(camera['id'], st.session_state.user_id)
                                if result['status'] == 'success':
                                    st.success("✅ Camera deleted")
                                    st.rerun()
                                else:
                                    st.error(f"Error: {result['message']}")
        
        with tab2:
            st.subheader("Add New Camera")
            st.markdown("Connect a new CCTV camera using RTSP protocol")
            
            with st.form("add_camera_form"):
                camera_name = st.text_input(
                    "Camera Name",
                    placeholder="e.g., Terminal 1 Camera, Front Gate",
                    help="Unique name for this camera"
                )
                
                rtsp_url = st.text_input(
                    "RTSP URL",
                    placeholder="rtsp://192.168.1.100:554/stream",
                    help="RTSP stream URL (format: rtsp://host:port/path)"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    camera_username = st.text_input(
                        "Camera Username (Optional)",
                        type="password"
                    )
                
                with col2:
                    camera_password = st.text_input(
                        "Camera Password (Optional)",
                        type="password"
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    camera_port = st.number_input(
                        "Port",
                        value=554,
                        min_value=1,
                        max_value=65535
                    )
                
                with col2:
                    camera_type = st.selectbox(
                        "Camera Type",
                        ["RTSP", "HTTP", "USB"]
                    )
                
                submitted = st.form_submit_button("➕ Add Camera", use_container_width=True)
                
                if submitted:
                    if not camera_name or not rtsp_url:
                        st.error("❌ Camera name and RTSP URL are required")
                    elif not validate_rtsp_url(rtsp_url):
                        st.error("❌ Invalid RTSP URL format. Expected: rtsp://host:port/path")
                    else:
                        result = add_camera(
                            user_id=st.session_state.user_id,
                            camera_name=camera_name,
                            rtsp_url=rtsp_url,
                            username=camera_username if camera_username else None,
                            password=camera_password if camera_password else None,
                            camera_type=camera_type,
                            port=camera_port
                        )
                        
                        if result['status'] == 'success':
                            st.success(f"✅ {result['message']}")
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")
            
            st.markdown("---")
            st.subheader("📖 Common Camera RTSP URLs")
            st.markdown("""
            **Hikvision:** `rtsp://username:password@192.168.1.100:554/Streaming/Channels/101`
            
            **Dahua:** `rtsp://username:password@192.168.1.100:554/stream/ch0`
            
            **Axis:** `rtsp://username:password@192.168.1.100:554/axis-media/media.amp`
            
            **Uniview:** `rtsp://username:password@192.168.1.100:554/media/video1`
            
            **Generic:** `rtsp://192.168.1.100:554/stream`
            """)

    # ==========================================
    # �📊 FORENSIC HISTORY PAGE
    # ==========================================
    elif page == "📊 Forensic History":
        st.header("📊 Forensic Evidence Log")
        st.markdown("Your detected abandoned luggage incidents with evidence images and metadata.")
        
        df = get_all_abandoned_bags(user_id=st.session_state.user_id)
        
        if len(df) == 0:
            st.info("📭 No abandoned luggage detected yet.")
        else:
            st.success(f"✅ Found {len(df)} incident(s)")
            st.markdown("---")
            
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
                        if row['image_filepath'] and os.path.exists(row['image_filepath']):
                            image = cv2.imread(row['image_filepath'])
                            if image is not None:
                                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                                st.image(image_rgb, caption="Evidence Image", use_container_width=True)
                        else:
                            st.warning("No evidence image available")
            
            st.markdown("---")
            
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

    # ==========================================
    # 📈 STATISTICS PAGE
    # ==========================================
    elif page == "📈 Statistics":
        st.header("📈 Your Security System Statistics")
        
        df = get_all_abandoned_bags(user_id=st.session_state.user_id)
        
        if len(df) == 0:
            st.info("📊 No data available yet. Start the live monitoring to collect detections.")
        else:
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Detections",
                    len(df),
                    delta="incidents logged"
                )
            
            with col2:
                avg_duration = df['duration_seconds'].mean() if len(df) > 0 else 0
                st.metric(
                    "Average Duration",
                    f"{avg_duration:.1f}s",
                    delta="seconds"
                )
            
            with col3:
                max_duration = df['duration_seconds'].max() if len(df) > 0 else 0
                st.metric(
                    "Max Duration",
                    f"{max_duration}s",
                    delta="longest incident"
                )
            
            with col4:
                avg_conf = df['confidence_score'].mean() if len(df) > 0 else 0
                st.metric(
                    "Avg Confidence",
                    f"{avg_conf:.1%}",
                    delta="detection accuracy"
                )
            
            st.markdown("---")
            
            st.subheader("📅 Incidents Over Time")
            df_copy = df.copy()
            df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])
            df_grouped = df_copy.groupby(df_copy['timestamp'].dt.date).size()
            
            st.bar_chart(df_grouped, use_container_width=True)
            
            st.markdown("---")
            st.subheader("📊 Duration Distribution")
            st.histogram(df['duration_seconds'], bins=10, use_container_width=True)


# ==========================================
# MAIN APP LOGIC
# ==========================================
if __name__ == "__main__":
    if st.session_state.logged_in:
        show_dashboard()
    else:
        show_login()
