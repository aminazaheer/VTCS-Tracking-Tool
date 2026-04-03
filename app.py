import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
import plotly.express as px
from math import radians, cos, sin, asin, sqrt
from pathlib import Path
import re

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="VTCS Auditor Pro",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED UI STYLING ---
st.markdown(
    """
    <style>
    :root {
        --bg: #07111f;
        --panel: rgba(13, 27, 46, 0.72);
        --panel-2: rgba(18, 36, 61, 0.86);
        --border: rgba(255, 255, 255, 0.10);
        --text: #f8fbff;
        --muted: #a7b7cf;
        --accent: #5aa9ff;
        --accent-2: #22c55e;
        --danger: #ff6b6b;
        --warning: #fbbf24;
        --shadow: 0 14px 40px rgba(0, 0, 0, 0.28);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(90, 169, 255, 0.16), transparent 30%),
            radial-gradient(circle at top right, rgba(34, 197, 94, 0.10), transparent 25%),
            linear-gradient(180deg, #07111f 0%, #0b1830 55%, #07111f 100%);
        color: var(--text);
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5,
    .stApp p, .stApp label, .stApp div {
        color: var(--text);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 22, 39, 0.96), rgba(16, 33, 58, 0.96));
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div {
        color: var(--text) !important;
    }

    .hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, rgba(8, 21, 40, 0.92), rgba(17, 60, 118, 0.80));
        border: 1px solid var(--border);
        border-radius: 24px;
        padding: 28px 30px;
        margin-bottom: 20px;
        box-shadow: var(--shadow);
    }

    .hero::before {
        content: "";
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at 85% 20%, rgba(90, 169, 255, 0.28), transparent 22%);
        pointer-events: none;
    }

    .hero-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.10);
        color: #d7e8ff;
        font-size: 0.82rem;
        letter-spacing: 0.04em;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.1;
        color: #ffffff !important;
    }

    .hero-subtitle {
        margin-top: 10px;
        color: var(--muted) !important;
        font-size: 1rem;
    }

    .section-card {
        background: var(--panel);
        backdrop-filter: blur(10px);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 18px 20px;
        box-shadow: var(--shadow);
        margin-bottom: 18px;
    }

    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin: 0 0 2px 0;
        color: #ffffff !important;
    }

    .section-subtitle {
        margin: 0;
        color: var(--muted) !important;
        font-size: 0.92rem;
    }

    div[data-testid="metric-container"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(241,247,255,0.96));
        border: 1px solid rgba(90, 169, 255, 0.18);
        border-radius: 18px;
        padding: 18px 16px;
        box-shadow: 0 12px 28px rgba(4, 14, 28, 0.24);
    }

    div[data-testid="metric-container"] label,
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #10233d !important;
    }

    div[data-testid="metric-container"] label {
        font-weight: 700;
    }

    [data-testid="stFileUploader"] section {
        background: rgba(255,255,255,0.96) !important;
        border-radius: 16px !important;
        border: 1px dashed rgba(16, 35, 61, 0.20) !important;
        padding: 6px !important;
    }

    [data-testid="stFileUploader"] section p,
    [data-testid="stFileUploader"] section span,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] section div {
        color: #163153 !important;
    }

    [data-testid="stFileUploader"] button,
    .stButton > button {
        background: linear-gradient(135deg, #27c46b, #159f53) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
        box-shadow: 0 10px 18px rgba(21, 159, 83, 0.22);
    }

    [data-testid="stFileUploader"] button:hover,
    .stButton > button:hover {
        transform: translateY(-1px);
        opacity: 0.96;
    }

    div[data-baseweb="select"] > div,
    .stTextInput > div > div,
    .stDateInput > div > div,
    .stNumberInput > div > div {
        border-radius: 12px !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 8px;
        border-radius: 16px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 12px;
        color: #d8e7fa;
        font-weight: 700;
        background: transparent;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(90,169,255,0.18), rgba(90,169,255,0.10)) !important;
        border: 1px solid rgba(90,169,255,0.28) !important;
        color: #ffffff !important;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        overflow: hidden;
        box-shadow: var(--shadow);
    }

    .stAlert {
        border-radius: 16px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }

    .status-pill-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 8px;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 999px;
        font-size: 0.84rem;
        font-weight: 700;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .pill-blue { background: rgba(90, 169, 255, 0.12); color: #dcedff; }
    .pill-green { background: rgba(34, 197, 94, 0.14); color: #dcffe9; }
    .pill-amber { background: rgba(251, 191, 36, 0.14); color: #fff0c2; }

    hr {
        border-color: rgba(255,255,255,0.10);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- HEADER SECTION ---
st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">Fleet Audit • Geofencing • Tracker Validation</div>
        <h1 class="hero-title">🚛 VTCS Auditor Pro</h1>
        <p class="hero-subtitle">Precision fleet auditing with a cleaner executive dashboard and a modern operator-first interface.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="status-pill-wrap">
        <div class="status-pill pill-blue">📈 Operational analytics</div>
        <div class="status-pill pill-green">📍 Geofence compliance</div>
        <div class="status-pill pill-amber">⏱ Delay monitoring</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- HELPER: HAVERSINE ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return 2 * R * asin(sqrt(a))

def normalize_name(value):
    if pd.isna(value):
        return ""
    value = str(value).strip().lower()
    value = Path(value).stem
    value = re.sub(r'[^a-z0-9]+', '', value)
    return value

def load_data_file(uploaded_file):
    if uploaded_file.name.lower().endswith("xlsx"):
        return pd.read_excel(uploaded_file)
    return pd.read_csv(uploaded_file)

def prepare_tracking_df(track_df):
    track_df = track_df.copy()

    if "Time" not in [str(c).strip() for c in track_df.columns]:
        for i in range(min(len(track_df), 20)):
            row_values = [str(val).strip() for val in track_df.iloc[i].values]
            if "Time" in row_values:
                track_df.columns = row_values
                track_df = track_df.iloc[i + 1:].reset_index(drop=True)
                break

    track_df.columns = [str(c).strip() for c in track_df.columns]

    if "Time" in track_df.columns:
        track_df["Time"] = pd.to_datetime(track_df["Time"], errors="coerce")

    if "Status" in track_df.columns:
        track_df["Status"] = track_df["Status"].astype(str)

    return track_df

def find_matching_tracking_df(vehicle_name, tracking_files_map):
    v_key = normalize_name(vehicle_name)

    if v_key in tracking_files_map:
        return tracking_files_map[v_key]

    for file_key, df in tracking_files_map.items():
        if v_key and (v_key in file_key or file_key in v_key):
            return df

    return None

if "geo_data" not in st.session_state:
    st.session_state.geo_data = None

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/truck.png", width=84)
    st.markdown("### Control Panel")
    st.caption("Upload source files and manage geofence settings.")

    vtcs_file = st.file_uploader("1. VTCS Daily Data", type=["xlsx", "csv"])

    tracking_files = st.file_uploader(
        "2. Tracker Portal Data",
        type=["xlsx", "csv"],
        accept_multiple_files=True
    )

    st.divider()
    st.markdown("### 📍 Geofence Config")
    with st.expander("TCP & WE Settings", expanded=True):
        geo_upload = st.file_uploader("Upload Coordinate File", type=["xlsx", "csv"])
        if geo_upload:
            st.session_state.geo_data = (
                pd.read_excel(geo_upload)
                if geo_upload.name.endswith("xlsx")
                else pd.read_csv(geo_upload)
            )
            st.success("Coordinates linked successfully")

        if st.session_state.geo_data is not None:
            st.info(f"Active Zones: {len(st.session_state.geo_data)}")
            if st.button("🗑️ Reset Zones", use_container_width=True):
                st.session_state.geo_data = None
                st.rerun()

# --- MAIN PROCESSING LOGIC ---
def process_audit(vtcs_df, tracking_files_map=None):
    vtcs_df = vtcs_df.copy()

    for col in ["Waste Collected (Kg)", "Before Weight", "After Weight (Kg)"]:
        if col in vtcs_df.columns:
            vtcs_df[col] = pd.to_numeric(
                vtcs_df[col].astype(str).str.replace(",", ""), errors="coerce"
            )

    vtcs_df["Tonnage"] = vtcs_df["Waste Collected (Kg)"].fillna(0) / 1000
    vtcs_df["Time In"] = pd.to_datetime(vtcs_df["Time In"], errors="coerce")
    vtcs_df["Time Out"] = pd.to_datetime(vtcs_df["Time Out"], errors="coerce")
    vtcs_df["Duration_Mins"] = (
        vtcs_df["Time Out"] - vtcs_df["Time In"]
    ).dt.total_seconds() / 60
    vtcs_df["Time_Status"] = vtcs_df["Duration_Mins"].apply(
        lambda x: "🚨 Suspicious (>30m)" if x > 30 else "✅ Normal"
    )

    if tracking_files_map:
        gps_audit, zone_check, matched_files = [], [], []

        for _, row in vtcs_df.iterrows():
            vehicle_name = row.get("Vehicle", "")
            track_df = find_matching_tracking_df(vehicle_name, tracking_files_map)
            matched_files.append(vehicle_name if track_df is not None else "No file matched")

            t_time = row["Time In"]
            if track_df is None:
                gps_audit.append("❓ No Tracking File")
                zone_check.append("Unknown")
                continue

            if pd.isnull(t_time):
                gps_audit.append("❓ Invalid")
                zone_check.append("N/A")
                continue

            if "Time" not in track_df.columns:
                gps_audit.append("❓ Invalid Tracking File")
                zone_check.append("Unknown")
                continue

            mask = (track_df["Time"] >= t_time - timedelta(minutes=2)) & (
                track_df["Time"] <= t_time + timedelta(minutes=2)
            )
            pings = track_df[mask]

            if pings.empty:
                gps_audit.append("❓ No Data")
                zone_check.append("Unknown")
            else:
                if "Status" in pings.columns:
                    stts = pings["Status"].astype(str).str.lower().values
                    valid_idle = any(
                        keyword in s
                        for s in stts
                        for keyword in ["idle", "parked", "stopped"]
                    )
                    gps_audit.append("✅ Verified" if valid_idle else "❌ Moving")
                else:
                    gps_audit.append("❓ Status Missing")

                z_found = "❌ Outside Zone"
                if (
                    st.session_state.geo_data is not None
                    and "Latitude" in pings.columns
                    and "Longitude" in pings.columns
                ):
                    valid_ping = pings.dropna(subset=["Latitude", "Longitude"])
                    if not valid_ping.empty:
                        v_lat = valid_ping.iloc[0]["Latitude"]
                        v_lon = valid_ping.iloc[0]["Longitude"]

                        for _, loc in st.session_state.geo_data.iterrows():
                            if (
                                haversine(v_lat, v_lon, loc["Latitude"], loc["Longitude"])
                                <= loc.get("Radius_Meters", 150)
                            ):
                                z_found = f"✅ {loc['Name']}"
                                break

                zone_check.append(z_found)

        vtcs_df["Tracking_File_Match"] = matched_files
        vtcs_df["GPS_Audit"] = gps_audit
        vtcs_df["Zone_Check"] = zone_check

    return vtcs_df


if vtcs_file:
    df_vtcs = pd.read_excel(vtcs_file) if vtcs_file.name.endswith("xlsx") else pd.read_csv(vtcs_file)

    tracking_files_map = {}
    if tracking_files:
        for uploaded_file in tracking_files:
            try:
                temp_df = load_data_file(uploaded_file)
                temp_df = prepare_tracking_df(temp_df)
                file_key = normalize_name(uploaded_file.name)
                tracking_files_map[file_key] = temp_df
            except Exception as e:
                st.warning(f"Could not read tracking file: {uploaded_file.name} | {e}")

    results = process_audit(df_vtcs, tracking_files_map if tracking_files_map else None)

    # --- KPI METRICS ---
    st.markdown(
        """
        <div class="section-card">
            <p class="section-title">Executive KPIs</p>
            <p class="section-subtitle">A fast snapshot of tonnage, trip activity, delays, and GPS validation.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Total Tonnage", f"{results['Tonnage'].sum():.1f} T")
    kpi_cols[1].metric("Trip Count", len(results))
    kpi_cols[2].metric("Delayed (>30m)", len(results[results["Time_Status"].str.contains("🚨")]))
    if "GPS_Audit" in results.columns:
        kpi_cols[3].metric("GPS Conflicts", len(results[results["GPS_Audit"] == "❌ Moving"]))
    else:
        kpi_cols[3].metric("GPS Conflicts", "—")

    # --- ANALYTICS CHARTS ---
    st.markdown(
        """
        <div class="section-card">
            <p class="section-title">📊 Operational Overview</p>
            <p class="section-subtitle">Vehicle-wise tonnage and trip distribution with improved visual hierarchy.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    v_stats = results.groupby("Vehicle").agg({"Tonnage": "sum", "Data ID": "count"}).reset_index()
    v_stats.columns = ["Vehicle", "Tons", "Trips"]

    tons_chart = px.bar(
        v_stats,
        x="Vehicle",
        y="Tons",
        template="plotly_white",
        color="Tons",
        color_continuous_scale="Blues",
        title="Tonnage by Vehicle",
    )
    tons_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.96)",
        margin=dict(l=10, r=10, t=56, b=10),
        title_font_size=18,
        xaxis_title=None,
        yaxis_title="Tons",
        coloraxis_showscale=False,
    )
    tons_chart.update_traces(marker_line_width=0, hovertemplate="Vehicle=%{x}<br>Tons=%{y:.2f}<extra></extra>")

    trips_chart = px.bar(
        v_stats,
        x="Vehicle",
        y="Trips",
        template="plotly_white",
        color="Trips",
        color_continuous_scale="Greens",
        title="Trips by Vehicle",
    )
    trips_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.96)",
        margin=dict(l=10, r=10, t=56, b=10),
        title_font_size=18,
        xaxis_title=None,
        yaxis_title="Trips",
        coloraxis_showscale=False,
    )
    trips_chart.update_traces(marker_line_width=0, hovertemplate="Vehicle=%{x}<br>Trips=%{y}<extra></extra>")

    with c1:
        st.plotly_chart(tons_chart, use_container_width=True)
    with c2:
        st.plotly_chart(trips_chart, use_container_width=True)

    # --- TABS ---
    t1, t2 = st.tabs(["📋 Executive Summary", "🔍 Technical Audit Log"])

    with t1:
        st.markdown(
            """
            <div class="section-card">
                <p class="section-title">Vehicle Summary</p>
                <p class="section-subtitle">High-level fleet output summary for quick management review.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        summ = results.groupby("Vehicle").agg(
            {"Tonnage": "sum", "Data ID": "count", "Duration_Mins": "mean"}
        ).rename(columns={"Data ID": "Trips", "Tonnage": "Total Tons", "Duration_Mins": "Avg Mins"})
        st.dataframe(
            summ.style.background_gradient(cmap="Blues", subset=["Total Tons"]).format("{:.2f}"),
            use_container_width=True,
            height=420,
        )

    with t2:
        st.markdown(
            """
            <div class="section-card">
                <p class="section-title">Detailed Audit Output</p>
                <p class="section-subtitle">Operational event log with duration, tonnage, GPS checks, and zone validation.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        cols = ["Vehicle", "Time In", "Time Out", "Duration_Mins", "Tonnage", "Time_Status"]
        if "Tracking_File_Match" in results.columns:
            cols.append("Tracking_File_Match")
        if "GPS_Audit" in results.columns:
            cols.append("GPS_Audit")
        if "Zone_Check" in results.columns:
            cols.append("Zone_Check")
        st.dataframe(results[cols], use_container_width=True, height=500)

else:
    st.markdown(
        """
        <div class="section-card">
            <p class="section-title">Ready to begin</p>
            <p class="section-subtitle">Upload your VTCS and tracker files from the sidebar to generate the audit dashboard.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("💡 Getting Started: Upload your files in the sidebar.")
