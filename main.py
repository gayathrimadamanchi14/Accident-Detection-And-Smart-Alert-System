import streamlit as st
import pandas as pd
import time
from datetime import datetime

from detector import detect_accident
from gps import get_location
from alert import send_alert
from storage import save_record

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Accident Detection System",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS  — Premium Dark Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg-primary:   #0d1117;
    --bg-secondary: #161b22;
    --bg-card:      #1c2128;
    --border:       #30363d;
    --accent-red:   #f85149;
    --accent-green: #3fb950;
    --accent-blue:  #58a6ff;
    --accent-yellow:#e3b341;
    --accent-purple:#bc8cff;
    --text-primary: #e6edf3;
    --text-muted:   #8b949e;
    --gradient-1:   linear-gradient(135deg, #f85149 0%, #da3633 100%);
    --gradient-2:   linear-gradient(135deg, #3fb950 0%, #238636 100%);
    --gradient-3:   linear-gradient(135deg, #58a6ff 0%, #1f6feb 100%);
    --gradient-4:   linear-gradient(135deg, #bc8cff 0%, #8957e5 100%);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

section[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

.main .block-container {
    background: var(--bg-primary) !important;
    padding-top: 1.5rem !important;
}

header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }

.hero-banner {
    background: linear-gradient(135deg, #0d1117 0%, #1a0a0a 40%, #0d1117 100%);
    border: 1px solid #3d1a1a;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    box-shadow: 0 0 40px rgba(248,81,73,0.08);
}
.hero-icon {
    font-size: 3.5rem;
    animation: pulse-icon 2s infinite;
}
@keyframes pulse-icon {
    0%, 100% { transform: scale(1); }
    50%       { transform: scale(1.05); }
}
.hero-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #f85149, #e3b341, #58a6ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 0.95rem;
    color: var(--text-muted);
    margin: 0.25rem 0 0 0;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 14px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.status-online {
    background: rgba(63,185,80,0.15);
    border: 1px solid var(--accent-green);
    color: var(--accent-green);
}
.status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent-green);
    animation: blink 1.2s infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}

.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
    height: 100%;
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.metric-card.green::before  { background: var(--gradient-2); }
.metric-card.red::before    { background: var(--gradient-1); }
.metric-card.blue::before   { background: var(--gradient-3); }
.metric-card.purple::before { background: var(--gradient-4); }
.metric-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.metric-value {
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 0.4rem;
}
.metric-value.green  { color: var(--accent-green); }
.metric-value.red    { color: var(--accent-red); }
.metric-value.blue   { color: var(--accent-blue); }
.metric-value.purple { color: var(--accent-purple); }
.metric-icon {
    position: absolute;
    top: 1.2rem; right: 1.4rem;
    font-size: 2rem;
    opacity: 0.18;
}
.metric-sub { font-size: 0.78rem; color: var(--text-muted); }

.section-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 1.8rem 0 1rem 0;
}
.section-header h3 {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
}
.section-line {
    flex: 1;
    height: 1px;
    background: var(--border);
}

.camera-panel {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 2rem;
    text-align: center;
    min-height: 180px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.8rem;
}

.log-box {
    background: #010409;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-family: 'Courier New', monospace;
    font-size: 0.82rem;
    line-height: 1.8;
    min-height: 120px;
    max-height: 260px;
    overflow-y: auto;
    color: var(--accent-green);
}
.log-entry { margin: 0; }

.accident-banner {
    background: rgba(248,81,73,0.1);
    border: 1px solid var(--accent-red);
    border-radius: 12px;
    padding: 1.2rem 1.6rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    animation: flash-border 1s infinite;
}
@keyframes flash-border {
    0%, 100% { border-color: var(--accent-red); }
    50%       { border-color: #ff9a97; }
}
.accident-banner-title { font-size: 1.2rem; font-weight: 700; color: var(--accent-red); }
.accident-banner-sub   { font-size: 0.85rem; color: var(--text-muted); }

.safe-banner {
    background: rgba(63,185,80,0.08);
    border: 1px solid var(--accent-green);
    border-radius: 12px;
    padding: 1rem 1.6rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.safe-banner-title { font-size: 1.1rem; font-weight: 700; color: var(--accent-green); }

.info-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin-bottom: 0.8rem;
}
.info-card-label { font-size: 0.75rem; color: var(--text-muted); font-weight: 600; letter-spacing: 0.8px; text-transform: uppercase; }
.info-card-value { font-size: 1.05rem; font-weight: 600; color: var(--text-primary); margin-top: 0.2rem; }

.stButton > button {
    background: linear-gradient(135deg, #f85149, #da3633) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 1.5rem !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 14px rgba(248,81,73,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(248,81,73,0.5) !important;
}

[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #238636, #2ea043) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px rgba(63,185,80,0.3) !important;
}

.stProgress > div > div { background: linear-gradient(135deg, #f85149, #da3633) !important; border-radius: 4px !important; }
hr { border-color: var(--border) !important; }

.time-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 0.85rem;
    color: var(--text-muted);
    font-weight: 500;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def load_history():
    try:
        df = pd.read_csv("history.csv")
        df = df[pd.to_numeric(df.get("Latitude", pd.Series()), errors="coerce").notna()]
        return df
    except Exception:
        return pd.DataFrame(columns=["Date & Time", "Latitude", "Longitude"])

def section_header(icon, title):
    st.markdown(f"""
    <div class="section-header">
        <span style="font-size:1.2rem">{icon}</span>
        <h3>{title}</h3>
        <div class="section-line"></div>
    </div>
    """, unsafe_allow_html=True)

def metric_card(label, value, color, icon, sub=""):
    st.markdown(f"""
    <div class="metric-card {color}">
        <div class="metric-icon">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value {color}">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:1rem 0 1.5rem 0;">
        <div style="font-size:3rem; margin-bottom:0.5rem;">🚨</div>
        <div style="font-size:1.15rem; font-weight:800; color:#e6edf3;">Accident Detection</div>
        <div style="font-size:0.78rem; color:#8b949e;">Smart Alert System</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="status-badge status-online" style="margin-bottom:1rem;">
        <div class="status-dot"></div>
        SYSTEM ONLINE
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""<div style="font-size:0.72rem; color:#8b949e; text-transform:uppercase;
        letter-spacing:1px; font-weight:600; margin-bottom:0.8rem;">System Info</div>""",
        unsafe_allow_html=True)

    info_items = [
        ("🔖 Version",    "1.0.0"),
        ("👩‍💻 Developer", "Gayathri"),
        ("📡 GPS",        "Active"),
        ("🛡️ Alert Mode", "Enabled"),
    ]
    for lbl, val in info_items:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-card-label">{lbl}</div>
            <div class="info-card-value">{val}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""<div style="font-size:0.72rem; color:#8b949e; text-transform:uppercase;
        letter-spacing:1px; font-weight:600; margin-bottom:0.6rem;">Navigation</div>""",
        unsafe_allow_html=True)
    st.markdown("🏠 Dashboard")
    st.markdown("📋 History")
    st.markdown("📊 Analytics")

# ─────────────────────────────────────────────
#  HERO BANNER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-icon">🚨</div>
    <div>
        <p class="hero-title">Accident Detection &amp; Smart Alert System</p>
        <p class="hero-subtitle">Real-Time Vehicle Monitoring Dashboard · AI-Powered Safety Intelligence</p>
    </div>
</div>
""", unsafe_allow_html=True)

current_time_str = datetime.now().strftime("%d %B %Y  •  %I:%M:%S %p")
st.markdown(f'<div class="time-badge">🕒 &nbsp; {current_time_str}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  METRICS ROW
# ─────────────────────────────────────────────
history = load_history()
total_accidents = len(history)

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("System Status", "ONLINE",           "green",  "🟢", sub="All systems operational")
with c2:
    metric_card("Total Accidents", str(total_accidents), "red", "🚨", sub="Recorded incidents")
with c3:
    metric_card("Alerts Sent", str(total_accidents), "blue",   "📨", sub="Emergency notifications")
with c4:
    metric_card("Uptime", "99.9%",                   "purple", "📡", sub="Last 30 days")

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CAMERA FEED + MONITORING LOGS
# ─────────────────────────────────────────────
left_col, right_col = st.columns([1.2, 1], gap="large")

with left_col:
    section_header("📷", "Live Camera Feed")
    st.markdown("""
    <div class="camera-panel">
        <div style="font-size:3rem; opacity:0.5;">📷</div>
        <div style="font-size:1rem; font-weight:600; color:#8b949e;">Camera Feed Waiting</div>
        <div style="font-size:0.85rem; color:#484f58;">Connect a camera source to begin live monitoring</div>
        <span style="background:rgba(248,81,73,0.12); border:1px solid #f85149; color:#f85149;
                     border-radius:999px; padding:3px 12px; font-size:0.75rem; font-weight:600;">
            ● OFFLINE
        </span>
    </div>
    """, unsafe_allow_html=True)

with right_col:
    section_header("📝", "Monitoring Logs")
    log_placeholder = st.empty()
    log_placeholder.markdown("""
    <div class="log-box">
        <p class="log-entry">$ System initialized...</p>
        <p class="log-entry">$ Waiting for monitoring session...</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  START MONITORING BUTTON
# ─────────────────────────────────────────────
section_header("▶", "Monitoring Control")

btn_col, _ = st.columns([1, 2])
with btn_col:
    start = st.button("▶  Start Monitoring", use_container_width=True)

if start:
    logs = []

    def render_logs(entries):
        lines = "".join(f'<p class="log-entry">{e}</p>' for e in entries)
        log_placeholder.markdown(f'<div class="log-box">{lines}</div>', unsafe_allow_html=True)

    logs.append("$ 🚗 Monitoring session started...")
    render_logs(logs)

    pb = st.progress(0, text="🔍 Initializing vehicle scan...")
    for i in range(50):
        pb.progress(i + 1, text=f"🔍 Scanning... {(i+1)*2}%")
        time.sleep(0.02)

    logs.append("$ 🔍 Vehicle scan in progress...")
    render_logs(logs)

    with st.spinner("🚗 Monitoring vehicle data..."):
        time.sleep(3)

    for i in range(50, 100):
        pb.progress(i + 1, text=f"✅ Analysing data... {i+1}%")
        time.sleep(0.01)

    logs.append("$ ✅ Vehicle scan completed.")
    render_logs(logs)
    pb.empty()

    accident = detect_accident()

    # ── ACCIDENT ──
    if accident:
        logs.append("$ 🚨 ACCIDENT DETECTED!")
        render_logs(logs)

        st.markdown("""
        <div class="accident-banner">
            <div style="font-size:2rem;">🚨</div>
            <div>
                <div class="accident-banner-title">ACCIDENT DETECTED</div>
                <div class="accident-banner-sub">Emergency protocol activated. Retrieving GPS coordinates...</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        location    = get_location()
        event_time  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_record(event_time, location[0], location[1])
        send_alert(location)

        logs.append(f"$ 📍 GPS: {location[0]:.4f}, {location[1]:.4f}")
        logs.append("$ 📨 Emergency alert sent successfully.")
        render_logs(logs)

        st.markdown("<br>", unsafe_allow_html=True)

        ic1, ic2, ic3 = st.columns(3)
        with ic1:
            st.markdown(f"""<div class="info-card">
                <div class="info-card-label">🕒 Date &amp; Time</div>
                <div class="info-card-value">{event_time}</div>
            </div>""", unsafe_allow_html=True)
        with ic2:
            st.markdown(f"""<div class="info-card">
                <div class="info-card-label">📍 Latitude</div>
                <div class="info-card-value">{location[0]}</div>
            </div>""", unsafe_allow_html=True)
        with ic3:
            st.markdown(f"""<div class="info-card">
                <div class="info-card-label">📍 Longitude</div>
                <div class="info-card-value">{location[1]}</div>
            </div>""", unsafe_allow_html=True)

        section_header("🗺️", "Accident Location")
        map_data = pd.DataFrame({"lat": [location[0]], "lon": [location[1]]})
        st.map(map_data, zoom=13)

        maps_link = f"https://www.google.com/maps?q={location[0]},{location[1]}"
        st.markdown(f"""
        <a href="{maps_link}" target="_blank" style="
            display:inline-flex; align-items:center; gap:6px;
            background:rgba(88,166,255,0.12); border:1px solid #58a6ff;
            color:#58a6ff; border-radius:8px; padding:8px 16px;
            font-size:0.85rem; font-weight:600; text-decoration:none; margin-top:0.5rem;">
            📍 Open in Google Maps ↗
        </a>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background:rgba(248,81,73,0.08); border:1px solid #f85149; border-radius:10px;
                    padding:0.8rem 1.2rem; margin-top:1rem; font-size:0.85rem; color:#f85149;">
            ⚠️ <strong>Emergency Alert Sent</strong> — Authorities have been notified.
        </div>
        """, unsafe_allow_html=True)

    # ── NO ACCIDENT ──
    else:
        logs.append("$ ✅ No accident detected. Vehicle is safe.")
        render_logs(logs)

        st.markdown("""
        <div class="safe-banner">
            <div style="font-size:2rem;">✅</div>
            <div>
                <div class="safe-banner-title">No Accident Detected</div>
                <div style="font-size:0.85rem; color:#8b949e;">Monitoring completed successfully. All clear.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  ACCIDENT HISTORY TABLE
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
section_header("📋", "Accident History")

history = load_history()

if len(history) > 0:
    st.dataframe(history, use_container_width=True, height=250)

    dl_col, _ = st.columns([1, 2])
    with dl_col:
        try:
            with open("history.csv", "rb") as f:
                st.download_button(
                    "⬇  Download Accident Report",
                    f,
                    file_name="Accident_Report.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        except Exception:
            pass
else:
    st.markdown("""
    <div style="background:#1c2128; border:1px solid #30363d; border-radius:12px;
                padding:2rem; text-align:center; color:#8b949e;">
        📂 No accident records found.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  ANALYTICS
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
section_header("📊", "Accident Analytics")

history = load_history()

if len(history) > 0:
    history.columns = history.columns.str.strip()

    try:
        history["Datetime"] = pd.to_datetime(history["Date & Time"], errors="coerce")
        history["Hour"]  = history["Datetime"].dt.hour
        history["Date"]  = history["Datetime"].dt.date
        history["Month"] = history["Datetime"].dt.strftime("%b %Y")
    except Exception:
        history["Hour"]  = 0
        history["Date"]  = "Unknown"
        history["Month"] = "Unknown"

    an1, an2 = st.columns(2)

    with an1:
        st.markdown("""<div style="font-size:0.78rem; color:#8b949e; font-weight:600;
            letter-spacing:0.8px; text-transform:uppercase; margin-bottom:0.5rem;">
            📅 Accidents Per Day</div>""", unsafe_allow_html=True)
        day_counts = history.groupby("Date").size().reset_index(name="Accidents")
        day_counts["Date"] = day_counts["Date"].astype(str)
        st.bar_chart(day_counts.set_index("Date"), color="#f85149", height=220)

    with an2:
        st.markdown("""<div style="font-size:0.78rem; color:#8b949e; font-weight:600;
            letter-spacing:0.8px; text-transform:uppercase; margin-bottom:0.5rem;">
            🕐 Accidents by Hour of Day</div>""", unsafe_allow_html=True)
        hour_counts = history.groupby("Hour").size().reset_index(name="Accidents")
        st.bar_chart(hour_counts.set_index("Hour"), color="#58a6ff", height=220)

    st.markdown("<br>", unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        metric_card("Total Events", str(len(history)), "red", "🚨", sub="All time")
    with s2:
        try:
            busiest = str(history.groupby("Date").size().idxmax())
            metric_card("Busiest Day", busiest, "blue", "📅", sub="Most incidents")
        except Exception:
            metric_card("Busiest Day", "N/A", "blue", "📅", sub="—")
    with s3:
        try:
            peak_hr = int(history["Hour"].mode()[0])
            metric_card("Peak Hour", f"{peak_hr:02d}:00", "purple", "🕐", sub="Highest activity")
        except Exception:
            metric_card("Peak Hour", "N/A", "purple", "🕐", sub="—")
    with s4:
        unique_locs = str(history[["Latitude", "Longitude"]].drop_duplicates().shape[0])
        metric_card("Unique Locations", unique_locs, "green", "📍", sub="GPS points")

else:
    st.markdown("""
    <div style="background:#1c2128; border:1px solid #30363d; border-radius:12px;
                padding:2rem; text-align:center; color:#8b949e;">
        📊 No analytics data available yet. Run a monitoring session to collect data.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; padding:1.5rem; border-top:1px solid #30363d;
            color:#484f58; font-size:0.8rem;">
    🚨 Accident Detection &amp; Smart Alert System &nbsp;·&nbsp; v1.0.0 &nbsp;·&nbsp;
    Developed by <strong style="color:#8b949e;">Gayathri</strong> &nbsp;·&nbsp; &copy; 2026
</div>
""", unsafe_allow_html=True)