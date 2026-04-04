import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
import plotly.graph_objects as go
from math import radians, cos, sin, asin, sqrt
from pathlib import Path
import re

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="VTCS Auditor Pro",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# UI STYLE
# =========================================================
st.markdown(
    """
    <style>
    :root {
        --bg-main: #f5f8fc;
        --bg-soft: #eef4fb;
        --panel: #ffffff;
        --panel-soft: #f8fbff;
        --sidebar-dark: #0f1f46;
        --sidebar-dark-2: #13295c;
        --text: #15233b;
        --muted: #6e7f99;
        --line: #dde6f2;

        --blue: #3b82f6;
        --blue-soft: #eaf3ff;

        --green: #22c55e;
        --green-soft: #eaf9f0;

        --orange: #f59e0b;
        --orange-soft: #fff4e4;

        --shadow: 0 14px 34px rgba(19, 41, 92, 0.10);
        --shadow-strong: 0 18px 40px rgba(19, 41, 92, 0.16);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(59,130,246,0.08), transparent 24%),
            radial-gradient(circle at top right, rgba(34,197,94,0.07), transparent 22%),
            linear-gradient(180deg, #f9fbfe 0%, #f4f7fb 45%, #edf3fa 100%);
        color: var(--text);
    }

    .block-container {
        max-width: 1520px;
        padding-top: 1.05rem;
        padding-bottom: 2rem;
    }

    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5,
    .stApp p, .stApp label, .stApp div, .stMarkdown {
        color: var(--text);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--sidebar-dark) 0%, var(--sidebar-dark-2) 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] span {
        color: #f8fbff !important;
    }

    .hero {
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(circle at 85% 20%, rgba(255,255,255,0.16), transparent 24%),
            radial-gradient(circle at 15% 20%, rgba(147,197,253,0.20), transparent 18%),
            linear-gradient(135deg, #112654 0%, #1d4ed8 52%, #2563eb 100%);
        border-radius: 28px;
        padding: 30px 34px;
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: 0 20px 44px rgba(17, 38, 84, 0.22);
        margin-bottom: 18px;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 14px;
        border-radius: 999px;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.18);
        color: #eaf2ff !important;
        font-size: 0.83rem;
        font-weight: 700;
        margin-bottom: 14px;
    }

    .hero-title {
        font-size: 2.8rem;
        line-height: 1.05;
        margin: 0;
        font-weight: 850;
        color: #ffffff !important;
        letter-spacing: -0.02em;
    }

    .hero-subtitle {
        margin-top: 12px;
        color: #e3edff !important;
        font-size: 1.02rem;
        max-width: 880px;
    }

    .insight-row {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 18px;
    }

    .insight-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 11px 16px;
        border-radius: 999px;
        font-weight: 800;
        font-size: 0.88rem;
        border: 1px solid transparent;
        box-shadow: 0 8px 18px rgba(21, 35, 59, 0.06);
    }

    .pill-blue {
        background: #eaf3ff;
        color: #1d4ed8 !important;
        border-color: #cfe1ff;
    }

    .pill-green {
        background: #ebfbf1;
        color: #15803d !important;
        border-color: #cfeedd;
    }

    .pill-orange {
        background: #fff4e4;
        color: #c27007 !important;
        border-color: #ffe0b2;
    }

    .kpi-shell {
        background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        border: 1px solid #dfe8f3;
        border-radius: 22px;
        padding: 10px;
        box-shadow: 0 16px 34px rgba(17, 38, 84, 0.08);
        margin-bottom: 16px;
    }

    div[data-testid="metric-container"] {
        background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%);
        border: 1px solid #dbe7f3;
        border-radius: 20px;
        padding: 22px 18px;
        box-shadow: 0 12px 28px rgba(17, 38, 84, 0.06);
    }

    div[data-testid="metric-container"] label {
        color: #63758d !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
    }

    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #0d2a52 !important;
        font-weight: 900 !important;
        font-size: 2.25rem !important;
        letter-spacing: -0.02em;
    }

    .mini-kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 14px;
        margin: 6px 0 24px 0;
    }

    .mini-kpi-card {
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 10px 24px rgba(17, 38, 84, 0.07);
        border: 1px solid #deebf7;
    }

    .mini-kpi-blue {
        background: linear-gradient(180deg, #eef6ff 0%, #e3f0ff 100%);
        border: 1px solid #cfe1ff;
    }

    .mini-kpi-green {
        background: linear-gradient(180deg, #eefcf2 0%, #e4f8ea 100%);
        border: 1px solid #cdeed8;
    }

    .mini-kpi-orange {
        background: linear-gradient(180deg, #fff7eb 0%, #ffefd8 100%);
        border: 1px solid #ffe0b8;
    }

    .mini-kpi-slate {
        background: linear-gradient(180deg, #f2f7fb 0%, #eaf1f8 100%);
        border: 1px solid #dbe6f0;
    }

    .mini-kpi-label {
        color: #6f8197 !important;
        font-size: 0.84rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .mini-kpi-value {
        color: #102447 !important;
        font-size: 1.2rem;
        font-weight: 900;
    }

    .soft-card {
        background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 18px 20px;
        box-shadow: var(--shadow);
        margin-bottom: 18px;
    }

    .soft-card-title {
        font-size: 1.05rem;
        font-weight: 800;
        margin: 0 0 4px 0;
        color: var(--text) !important;
    }

    .soft-card-subtitle {
        margin: 0;
        color: var(--muted) !important;
        font-size: 0.94rem;
    }

    [data-testid="stFileUploader"] section {
        background: rgba(255,255,255,0.98) !important;
        border-radius: 18px !important;
        border: 2px dashed #c8d7ea !important;
        padding: 9px !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
    }

    [data-testid="stFileUploader"] section p,
    [data-testid="stFileUploader"] section span,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] section div {
        color: #173153 !important;
    }

    .stButton > button,
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #c7f4d3 0%, #8ee6a3 100%) !important;
        color: #0d5a2a !important;
        border: 2px solid #5dc57b !important;
        border-radius: 14px !important;
        font-weight: 850 !important;
        padding: 0.72rem 1rem !important;
        box-shadow: 0 10px 22px rgba(34, 197, 94, 0.18) !important;
    }

    .stButton > button:hover,
    [data-testid="stFileUploader"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 26px rgba(34, 197, 94, 0.24) !important;
    }

    .sidebar-panel {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 14px 14px 10px 14px;
        margin-bottom: 14px;
        backdrop-filter: blur(6px);
    }

    .sidebar-title {
        font-size: 1rem;
        font-weight: 900;
        color: #ffffff !important;
        margin-bottom: 6px;
    }

    .sidebar-subtitle {
        font-size: 0.87rem;
        color: #d4e1ff !important;
        margin-bottom: 6px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: #f8fbff;
        border: 1px solid #dbe7f3;
        padding: 8px;
        border-radius: 18px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 14px;
        color: #42556e;
        font-weight: 850;
        background: transparent;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #e9f2ff, #f3f8ff) !important;
        border: 1px solid #c7daf4 !important;
        color: #1d4ed8 !important;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #dfe8f3;
        border-radius: 18px;
        overflow: hidden;
        box-shadow: var(--shadow);
        background: #ffffff;
    }

    .stAlert {
        border-radius: 16px !important;
        border: 1px solid #d9e6f3 !important;
    }

    @media (max-width: 1100px) {
        .mini-kpi-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }

    @media (max-width: 700px) {
        .mini-kpi-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# HEADER
# =========================================================
st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">Fleet Audit • Geofencing • Tracker Validation</div>
        <h1 class="hero-title">🚛 VTCS Auditor Pro</h1>
        <p class="hero-subtitle">
            Smart fleet audit dashboard with refined analytics, stronger geofence validation,
            cleaner operator workflow, and a more professional visual interface.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="insight-row">
        <div class="insight-pill pill-blue">📊 Executive analytics</div>
        <div class="insight-pill pill-green">📍 Geofence validation</div>
        <div class="insight-pill pill-orange">⏱ Delay monitoring</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# HELPERS
# =========================================================
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
    value = re.sub(r"[^a-z0-9]+", "", value)
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

    if "Latitude" in track_df.columns:
        track_df["Latitude"] = pd.to_numeric(track_df["Latitude"], errors="coerce")

    if "Longitude" in track_df.columns:
        track_df["Longitude"] = pd.to_numeric(track_df["Longitude"], errors="coerce")

    return track_df


def find_matching_tracking_df(vehicle_name, tracking_files_map):
    v_key = normalize_name(vehicle_name)

    if v_key in tracking_files_map:
        return tracking_files_map[v_key]

    for file_key, df in tracking_files_map.items():
        if v_key and (v_key in file_key or file_key in v_key):
            return df

    return None


def prepare_geofence_file(geo_df):
    geo_df = geo_df.copy()
    geo_df.columns = [str(c).strip() for c in geo_df.columns]

    if "Latitude" in geo_df.columns and "Longitude" in geo_df.columns:
        if "Name" not in geo_df.columns:
            for col in ["TCP", "WE", "Location", "Zone", "Site"]:
                if col in geo_df.columns:
                    geo_df["Name"] = geo_df[col]
                    break

        if "Name" not in geo_df.columns:
            geo_df["Name"] = [f"Zone {i+1}" for i in range(len(geo_df))]

        if "Radius_Meters" not in geo_df.columns:
            geo_df["Radius_Meters"] = 150

        geo_df["Latitude"] = pd.to_numeric(geo_df["Latitude"], errors="coerce")
        geo_df["Longitude"] = pd.to_numeric(geo_df["Longitude"], errors="coerce")
        geo_df["Radius_Meters"] = pd.to_numeric(
            geo_df["Radius_Meters"], errors="coerce"
        ).fillna(150)

        return geo_df.dropna(subset=["Latitude", "Longitude"]).reset_index(drop=True)

    latlong_col = None
    for col in geo_df.columns:
        col_key = str(col).strip().lower()
        if col_key in ["lat/long", "lat,long", "lat long", "coordinates", "coord"]:
            latlong_col = col
            break

    if latlong_col is not None:
        split_vals = (
            geo_df[latlong_col]
            .astype(str)
            .str.strip()
            .str.rstrip(",")
            .str.split(",", n=1, expand=True)
        )

        geo_df["Latitude"] = pd.to_numeric(split_vals[0].str.strip(), errors="coerce")
        geo_df["Longitude"] = pd.to_numeric(split_vals[1].str.strip(), errors="coerce")

        if "TCP" in geo_df.columns:
            geo_df["Name"] = geo_df["TCP"]
        elif "WE" in geo_df.columns:
            geo_df["Name"] = geo_df["WE"]
        else:
            geo_df["Name"] = [f"Zone {i+1}" for i in range(len(geo_df))]

        if "Radius_Meters" not in geo_df.columns:
            geo_df["Radius_Meters"] = 150

        geo_df["Radius_Meters"] = pd.to_numeric(
            geo_df["Radius_Meters"], errors="coerce"
        ).fillna(150)

        return geo_df.dropna(subset=["Latitude", "Longitude"]).reset_index(drop=True)

    raise ValueError(
        "Invalid geofence file format. Use either [Name, Latitude, Longitude] or [TCP/WE, Lat/Long]."
    )


def has_t_in_name(vehicle_name):
    return "T" in str(vehicle_name).upper()


def vehicle_type_color(vehicle_name):
    return "#22c55e" if has_t_in_name(vehicle_name) else "#3b82f6"


# =========================================================
# SESSION STATE
# =========================================================
if "geo_data" not in st.session_state:
    st.session_state.geo_data = None

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/truck.png", width=82)

    st.markdown(
        """
        <div class="sidebar-panel">
            <div class="sidebar-title">Control Panel</div>
            <div class="sidebar-subtitle">
                Upload source files, tracker files, and geofence locations with a cleaner professional workflow.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    vtcs_file = st.file_uploader("1. VTCS Daily Data", type=["xlsx", "csv"])

    tracking_files = st.file_uploader(
        "2. Tracker Portal Data",
        type=["xlsx", "csv"],
        accept_multiple_files=True,
        help="Upload separate tracker file for each vehicle. File name should match vehicle name."
    )

    st.markdown(
        """
        <div class="sidebar-panel" style="margin-top:10px;">
            <div class="sidebar-title">📍 Geofence Config</div>
            <div class="sidebar-subtitle">
                Upload TCP / WE coordinates to enable zone checking in the audit log.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("TCP & WE Settings", expanded=True):
        geo_upload = st.file_uploader("Upload Coordinate File", type=["xlsx", "csv"])

        if geo_upload:
            try:
                raw_geo_df = (
                    pd.read_excel(geo_upload)
                    if geo_upload.name.lower().endswith("xlsx")
                    else pd.read_csv(geo_upload)
                )
                st.session_state.geo_data = prepare_geofence_file(raw_geo_df)
                st.success("Geofence zones linked successfully")
            except Exception as e:
                st.session_state.geo_data = None
                st.error(f"Geofence file error: {e}")

        if st.session_state.geo_data is not None:
            st.info(f"Active Zones: {len(st.session_state.geo_data)}")
            if st.button("🗑️ Reset Zones", use_container_width=True):
                st.session_state.geo_data = None
                st.rerun()

# =========================================================
# MAIN PROCESSING
# =========================================================
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
        lambda x: "🚨 Suspicious (>30m)" if pd.notna(x) and x > 30 else "✅ Normal"
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
                        keyword in s for s in stts for keyword in ["idle", "parked", "stopped"]
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
                    if not valid_ping.empty and {"Name", "Latitude", "Longitude"}.issubset(
                        st.session_state.geo_data.columns
                    ):
                        v_lat = valid_ping.iloc[0]["Latitude"]
                        v_lon = valid_ping.iloc[0]["Longitude"]

                        for _, loc in st.session_state.geo_data.iterrows():
                            if pd.isna(loc["Latitude"]) or pd.isna(loc["Longitude"]):
                                continue

                            radius = (
                                loc["Radius_Meters"]
                                if "Radius_Meters" in st.session_state.geo_data.columns
                                and pd.notna(loc.get("Radius_Meters"))
                                else 150
                            )

                            if haversine(v_lat, v_lon, loc["Latitude"], loc["Longitude"]) <= radius:
                                z_found = f"✅ {loc['Name']}"
                                break

                zone_check.append(z_found)

        vtcs_df["Tracking_File_Match"] = matched_files
        vtcs_df["GPS_Audit"] = gps_audit
        vtcs_df["Zone_Check"] = zone_check

    return vtcs_df

# =========================================================
# APP BODY
# =========================================================
if vtcs_file:
    df_vtcs = (
        pd.read_excel(vtcs_file)
        if vtcs_file.name.lower().endswith("xlsx")
        else pd.read_csv(vtcs_file)
    )

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

    delayed_count = len(results[results["Time_Status"].str.contains("🚨", na=False)])
    gps_conflicts = len(results[results["GPS_Audit"] == "❌ Moving"]) if "GPS_Audit" in results.columns else 0
    avg_trip_time = results["Duration_Mins"].dropna().mean() if "Duration_Mins" in results.columns else 0
    active_vehicles = results["Vehicle"].nunique() if "Vehicle" in results.columns else 0

    st.markdown('<div class="kpi-shell">', unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Tonnage", f"{results['Tonnage'].sum():.1f} T")
    k2.metric("Trip Count", len(results))
    k3.metric("Delayed (>30m)", delayed_count)
    k4.metric("GPS Conflicts", gps_conflicts if "GPS_Audit" in results.columns else "—")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="mini-kpi-grid">
            <div class="mini-kpi-card mini-kpi-blue">
                <div class="mini-kpi-label">Active Vehicles</div>
                <div class="mini-kpi-value">{active_vehicles}</div>
            </div>
            <div class="mini-kpi-card mini-kpi-green">
                <div class="mini-kpi-label">Average Trip Time</div>
                <div class="mini-kpi-value">{0 if pd.isna(avg_trip_time) else round(avg_trip_time, 1)} mins</div>
            </div>
            <div class="mini-kpi-card mini-kpi-orange">
                <div class="mini-kpi-label">Geofence Status</div>
                <div class="mini-kpi-value">{"Linked" if st.session_state.geo_data is not None else "Not Linked"}</div>
            </div>
            <div class="mini-kpi-card mini-kpi-slate">
                <div class="mini-kpi-label">Tracker Files</div>
                <div class="mini-kpi-value">{len(tracking_files_map)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    v_stats = results.groupby("Vehicle").agg({"Tonnage": "sum", "Data ID": "count"}).reset_index()
    v_stats.columns = ["Vehicle", "Tons", "Trips"]
    v_stats["Vehicle_Color"] = v_stats["Vehicle"].apply(vehicle_type_color)

    c1, c2 = st.columns(2)

    with c1:
        tons_fig = go.Figure()
        tons_fig.add_trace(
            go.Bar(
                x=v_stats["Vehicle"],
                y=v_stats["Tons"],
                marker=dict(
                    color="#3b82f6",
                    line=dict(color="#ffffff", width=1.6)
                ),
                text=[f"{x:.2f}" for x in v_stats["Tons"]],
                textposition="outside",
                textfont=dict(size=12, color="#16304f"),
                hovertemplate="<b>%{x}</b><br>Tonnage: %{y:.2f} T<extra></extra>",
            )
        )
        tons_fig.update_layout(
            title="Tonnage by Vehicle",
            title_font=dict(size=20, color="#143155"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#ffffff",
            margin=dict(l=20, r=20, t=58, b=20),
            height=450,
            xaxis=dict(
                title="Vehicle",
                tickfont=dict(size=11, color="#47617f"),
                title_font=dict(size=13, color="#47617f"),
                showgrid=False
            ),
            yaxis=dict(
                title="Tons",
                tickfont=dict(size=11, color="#47617f"),
                title_font=dict(size=13, color="#47617f"),
                gridcolor="#e3edf8",
                zerolinecolor="#d1dfef"
            ),
            showlegend=False
        )
        st.plotly_chart(tons_fig, use_container_width=True)

    with c2:
        trips_fig = go.Figure()
        trips_fig.add_trace(
            go.Bar(
                x=v_stats["Vehicle"],
                y=v_stats["Trips"],
                marker=dict(
                    color=v_stats["Vehicle_Color"],
                    line=dict(color="#ffffff", width=1.6)
                ),
                text=[str(x) for x in v_stats["Trips"]],
                textposition="outside",
                textfont=dict(size=12, color="#16304f"),
                hovertemplate="<b>%{x}</b><br>Trips: %{y}<extra></extra>",
            )
        )
        trips_fig.update_layout(
            title="Trips by Vehicle",
            title_font=dict(size=20, color="#143155"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#ffffff",
            margin=dict(l=20, r=20, t=58, b=20),
            height=450,
            xaxis=dict(
                title="Vehicle",
                tickfont=dict(size=11, color="#47617f"),
                title_font=dict(size=13, color="#47617f"),
                showgrid=False
            ),
            yaxis=dict(
                title="Trips",
                tickfont=dict(size=11, color="#47617f"),
                title_font=dict(size=13, color="#47617f"),
                gridcolor="#e3edf8",
                zerolinecolor="#d1dfef"
            ),
            showlegend=False
        )
        st.plotly_chart(trips_fig, use_container_width=True)

    t1, t2 = st.tabs(["📋 Executive Summary", "🔍 Technical Audit Log"])

    with t1:
        st.markdown(
            """
            <div class="soft-card">
                <p class="soft-card-title">Vehicle Summary</p>
                <p class="soft-card-subtitle">Management-ready summary with trips, tonnage, and average cycle time by vehicle.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        summ = results.groupby("Vehicle").agg(
            {"Tonnage": "sum", "Data ID": "count", "Duration_Mins": "mean"}
        ).rename(
            columns={
                "Data ID": "Trips",
                "Tonnage": "Total Tons",
                "Duration_Mins": "Avg Mins"
            }
        )

        st.dataframe(
            summ.style
            .background_gradient(cmap="Blues", subset=["Total Tons"])
            .format({"Total Tons": "{:.2f}", "Avg Mins": "{:.1f}"}),
            use_container_width=True,
            height=430,
        )

    with t2:
        st.markdown(
            """
            <div class="soft-card">
                <p class="soft-card-title">Detailed Audit Output</p>
                <p class="soft-card-subtitle">Complete operational log with tracker matching, GPS audit result, and zone validation.</p>
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

        st.dataframe(results[cols], use_container_width=True, height=520)

else:
    st.markdown(
        """
        <div class="soft-card">
            <p class="soft-card-title">Ready to begin</p>
            <p class="soft-card-subtitle">
                Upload VTCS data, tracker files, and geofence locations from the control panel to generate the audit dashboard.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("Upload files from the sidebar to start the fleet audit.")
