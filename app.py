import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
import plotly.graph_objects as go
from math import radians, cos, sin, asin, sqrt
from pathlib import Path
import re
import base64

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Sargodha Suthra Punjab Tracking Tool",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# BRANDING
# =========================================================
# Try multiple possible paths for logo (fix visibility issue)
LOGO_CANDIDATES = [
    Path("/mnt/data/WhatsApp Image 2025-08-04 at 12.11.30 PM.jpeg"),
    Path("/mnt/data/image(7).png"),
]

LOGO_PATH = next((p for p in LOGO_CANDIDATES if p.exists()), None)


def get_base64_image(path: Path):
    try:
        if path.exists():
            return base64.b64encode(path.read_bytes()).decode()
    except Exception:
        return None
    return None


LOGO_BASE64 = get_base64_image(LOGO_PATH) if LOGO_PATH else None

# =========================================================
# UI STYLE
# =========================================================
st.markdown(
    f"""
    <style>
    :root {{
        --bg-main: #f4f7f2;
        --bg-soft: #edf5ed;
        --panel: #ffffff;
        --panel-soft: #f7fbf6;
        --panel-accent: #f1f8f0;
        --sidebar-dark: #0f2617;
        --sidebar-dark-2: #1d5c33;
        --sidebar-dark-3: #2f7d46;
        --text: #163122;
        --muted: #5e7368;
        --line: #d7e5d8;
        --brand-green: #2f7d46;
        --brand-green-dark: #1f5d33;
        --brand-green-soft: #eaf5eb;
        --brand-black: #111111;
        --brand-gold: #c89b2f;
        --success: #208a43;
        --warning: #c97a11;
        --danger: #bf2f2f;
        --shadow: 0 14px 34px rgba(19, 53, 30, 0.08);
        --shadow-strong: 0 20px 48px rgba(17, 32, 20, 0.14);
    }

    .stApp {{
        background:
            radial-gradient(circle at top left, rgba(47,125,70,0.08), transparent 26%),
            radial-gradient(circle at top right, rgba(200,155,47,0.07), transparent 18%),
            linear-gradient(180deg, #fbfcfa 0%, #f4f8f2 50%, #eef4ee 100%);
        color: var(--text);
    }

    .block-container {{
        max-width: 1540px;
        padding-top: 1.1rem;
        padding-bottom: 2rem;
    }

    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5,
    .stApp p, .stApp label, .stApp div, .stMarkdown {{
        color: var(--text);
    }

    section[data-testid="stSidebar"] {{
        background:
            radial-gradient(circle at 85% 20%, rgba(255,255,255,0.12), transparent 22%),
            radial-gradient(circle at 15% 20%, rgba(200,155,47,0.10), transparent 18%),
            linear-gradient(180deg, var(--sidebar-dark) 0%, var(--sidebar-dark-2) 52%, var(--sidebar-dark-3) 100%);
        border-right: 1px solid rgba(255,255,255,0.10);
    }

    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] span {{
        color: #f8fff8 !important;
    }

    .hero {{
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(circle at 92% 18%, rgba(255,255,255,0.12), transparent 20%),
            radial-gradient(circle at 12% 14%, rgba(200,155,47,0.12), transparent 14%),
            linear-gradient(135deg, #102816 0%, #1f5d33 54%, #2f7d46 100%);
        border-radius: 30px;
        padding: 26px 30px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 22px 50px rgba(16, 40, 22, 0.20);
        margin-bottom: 18px;
    }

    .hero-grid {{
        display: grid;
        grid-template-columns: 112px 1fr;
        gap: 20px;
        align-items: center;
    }

    .hero-logo {{
        width: 104px;
        height: 104px;
        border-radius: 24px;
        background: rgba(255,255,255,0.94);
        border: 1px solid rgba(255,255,255,0.28);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 14px 28px rgba(0,0,0,0.14);
        padding: 8px;
    }

    .hero-logo img {{
        width: 100%;
        height: 100%;
        object-fit: contain;
        border-radius: 18px;
    }

    .hero-badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 7px 14px;
        border-radius: 999px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.16);
        color: #ebf8ef !important;
        font-size: 0.82rem;
        font-weight: 800;
        margin-bottom: 14px;
    }

    .hero-title {{
        font-size: 2.35rem;
        line-height: 1.04;
        margin: 0;
        font-weight: 900;
        color: #ffffff !important;
        letter-spacing: -0.02em;
    }

    .hero-subtitle {{
        margin-top: 12px;
        color: #e4f1e7 !important;
        font-size: 1.01rem;
        max-width: 960px;
    }

    .hero-meta {{
        margin-top: 16px;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }

    .hero-chip {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 10px 14px;
        border-radius: 999px;
        font-size: 0.84rem;
        font-weight: 800;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.14);
        color: #f7fff9 !important;
    }

    .section-card {{
        background: linear-gradient(180deg, #ffffff 0%, #fbfdfb 100%);
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 18px 20px;
        box-shadow: var(--shadow);
        margin-bottom: 18px;
    }

    .section-header {{
        display: flex;
        justify-content: space-between;
        align-items: start;
        gap: 16px;
        margin-bottom: 14px;
        flex-wrap: wrap;
    }

    .section-title {
        font-size: 1.28rem;
        font-weight: 900;
        margin: 0;
        color: var(--text) !important;
        letter-spacing: -0.01em;
    }

    .section-subtitle {{
        margin: 4px 0 0 0;
        color: var(--muted) !important;
        font-size: 0.94rem;
    }

    .insight-grid {{
        display: grid;
        grid-template-columns: 1.45fr 1fr;
        gap: 16px;
        margin-bottom: 18px;
    }

    .summary-banner {{
        background: linear-gradient(135deg, #f7fbf7 0%, #edf6ee 100%);
        border: 1px solid #d6e7d8;
        border-radius: 22px;
        padding: 18px 18px 12px 18px;
        box-shadow: 0 12px 28px rgba(19, 53, 30, 0.06);
    }

    .summary-title {{
        font-size: 1.05rem;
        font-weight: 900;
        margin-bottom: 6px;
        color: #173122 !important;
    }

    .summary-body {{
        color: #52685c !important;
        font-size: 0.94rem;
        line-height: 1.65;
    }

    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 14px;
        margin-top: 6px;
    }

    .kpi-card {
        border-radius: 20px;
        padding: 16px;
        box-shadow: 0 12px 28px rgba(16, 40, 22, 0.06);
    }

    .kpi-card:nth-child(1) {
        background: linear-gradient(180deg, #eef6ff 0%, #e3f0ff 100%);
        border: 1px solid #cfe1ff;
    }

    .kpi-card:nth-child(2) {
        background: linear-gradient(180deg, #eefcf2 0%, #e4f8ea 100%);
        border: 1px solid #cdeed8;
    }

    .kpi-card:nth-child(3) {
        background: linear-gradient(180deg, #fff7eb 0%, #ffefd8 100%);
        border: 1px solid #ffe0b8;
    }

    .kpi-card:nth-child(4) {
        background: linear-gradient(180deg, #f2f7fb 0%, #eaf1f8 100%);
        border: 1px solid #dbe6f0;
    }

    .kpi-label {{
        font-size: 0.84rem;
        font-weight: 800;
        color: #688073 !important;
        margin-bottom: 8px;
    }

    .kpi-value {{
        font-size: 1.55rem;
        font-weight: 900;
        color: #143022 !important;
    }

    .kpi-note {{
        margin-top: 8px;
        font-size: 0.78rem;
        color: #6e8376 !important;
    }

    .module-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 14px;
    }

    .module-badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 999px;
        background: #eef7ef;
        border: 1px solid #d6ead9;
        color: #225b35 !important;
        font-size: 0.82rem;
        font-weight: 800;
    }

    div[data-testid="metric-container"] {{
        background: linear-gradient(180deg, #ffffff 0%, #fbfdfb 100%);
        border: 1px solid #d9e8db;
        border-radius: 20px;
        padding: 22px 18px;
        box-shadow: 0 12px 28px rgba(16, 40, 22, 0.06);
    }

    div[data-testid="metric-container"] label {{
        color: #688073 !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
    }

    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{
        color: #113021 !important;
        font-weight: 900 !important;
        font-size: 2.15rem !important;
        letter-spacing: -0.02em;
    }

    [data-testid="stFileUploader"] section {{
        background: rgba(255,255,255,0.98) !important;
        border-radius: 18px !important;
        border: 2px dashed #b7d1bc !important;
        padding: 10px !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
    }

    [data-testid="stFileUploader"] section p,
    [data-testid="stFileUploader"] section span,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] section div {{
        color: #173122 !important;
    }

    .stButton > button,
    [data-testid="stFileUploader"] button {{
        background: linear-gradient(135deg, #e4f5e8 0%, #bfe4c7 100%) !important;
        color: #19482a !important;
        border: 1.5px solid #7bb28a !important;
        border-radius: 14px !important;
        font-weight: 850 !important;
        padding: 0.72rem 1rem !important;
        box-shadow: 0 10px 22px rgba(47, 125, 70, 0.14) !important;
    }

    .stButton > button:hover,
    [data-testid="stFileUploader"] button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 14px 26px rgba(47, 125, 70, 0.20) !important;
    }

    .sidebar-panel {{
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 20px;
        padding: 14px 14px 10px 14px;
        margin-bottom: 14px;
        backdrop-filter: blur(8px);
        box-shadow: 0 12px 24px rgba(10, 24, 12, 0.18);
    }

    .sidebar-title {{
        font-size: 1rem;
        font-weight: 900;
        color: #ffffff !important;
        margin-bottom: 6px;
    }

    .sidebar-subtitle {{
        font-size: 0.87rem;
        color: #e4f4e8 !important;
        margin-bottom: 6px;
        line-height: 1.45;
    }

    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background: #f7fbf7;
        border: 1px solid #d7e5d8;
        padding: 8px;
        border-radius: 18px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 54px;
        border-radius: 14px;
        color: #355345;
        font-weight: 900;
        font-size: 1.04rem;
        background: transparent;
        padding: 0 18px;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #eef7ef, #f7fbf7) !important;
        border: 1px solid #cfe0d1 !important;
        color: #1e5b33 !important;
        box-shadow: 0 8px 18px rgba(47, 125, 70, 0.10);
    }

    div[data-testid="stDataFrame"] {{
        border: 1px solid #dbe7dd;
        border-radius: 18px;
        overflow: hidden;
        box-shadow: var(--shadow);
        background: #ffffff;
    }

    .stAlert {{
        border-radius: 16px !important;
        border: 1px solid #d7e5d8 !important;
    }

    @media (max-width: 1200px) {{
        .insight-grid {{
            grid-template-columns: 1fr;
        }
    }

    @media (max-width: 900px) {{
        .hero-grid {{
            grid-template-columns: 1fr;
        }

        .hero-logo {{
            width: 92px;
            height: 92px;
        }

        .kpi-grid {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }

    @media (max-width: 700px) {{
        .kpi-grid {{
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
logo_html = (
    f'<img src="data:image/jpeg;base64,{LOGO_BASE64}" alt="SGWMC Logo">'
    if LOGO_BASE64 else '<div style="font-size:40px;">♻️</div>'
)

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-grid">
            <div class="hero-logo">{logo_html}</div>
            <div>
                <div class="hero-badge">SGWMC • VTCS Monitoring • Fleet Verification</div>
                <h1 class="hero-title">Sargodha Suthra Punjab Tracking Tool</h1>
                <p class="hero-subtitle">
                    Unified operational control panel for VTCS daily review, monthly insights, GPS verification,
                    geofence validation, delay monitoring, and management-ready reporting in a cleaner and more
                    professional interface.
                </p>
                <div class="hero-meta">
                    <div class="hero-chip">📊 Executive Summary</div>
                    <div class="hero-chip">🗓️ Monthly Insights</div>
                    <div class="hero-chip">📍 Geofence Validation</div>
                    <div class="hero-chip">🚛 Tracker Matching</div>
                </div>
            </div>
        </div>
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


def prepare_vtcs_df(vtcs_df):
    vtcs_df = vtcs_df.copy()
    vtcs_df.columns = [str(c).strip() for c in vtcs_df.columns]

    for col in ["Waste Collected (Kg)", "Before Weight", "After Weight (Kg)"]:
        if col in vtcs_df.columns:
            vtcs_df[col] = pd.to_numeric(
                vtcs_df[col].astype(str).str.replace(",", "", regex=False), errors="coerce"
            )

    if "Waste Collected (Kg)" not in vtcs_df.columns:
        vtcs_df["Waste Collected (Kg)"] = 0

    if "Time In" in vtcs_df.columns:
        vtcs_df["Time In"] = pd.to_datetime(vtcs_df["Time In"], errors="coerce")
    else:
        vtcs_df["Time In"] = pd.NaT

    if "Time Out" in vtcs_df.columns:
        vtcs_df["Time Out"] = pd.to_datetime(vtcs_df["Time Out"], errors="coerce")
    else:
        vtcs_df["Time Out"] = pd.NaT

    vtcs_df["Tonnage"] = vtcs_df["Waste Collected (Kg)"].fillna(0) / 1000
    vtcs_df["Duration_Mins"] = (
        vtcs_df["Time Out"] - vtcs_df["Time In"]
    ).dt.total_seconds() / 60

    vtcs_df["Time_Status"] = vtcs_df["Duration_Mins"].apply(
        lambda x: "🚨 Suspicious (>30m)" if pd.notna(x) and x > 30 else "✅ Normal"
    )

    return vtcs_df


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
    # Restore original logic: vehicles containing 'T' (TT) are GREEN, others BLUE
    return "#22c55e" if has_t_in_name(vehicle_name) else "#3b82f6"


def find_zone_in_precheck_window(track_df, check_time, geo_df, window_minutes=60):
    if track_df is None or geo_df is None or pd.isna(check_time):
        return "Unknown"

    required_track_cols = {"Time", "Latitude", "Longitude"}
    required_geo_cols = {"Name", "Latitude", "Longitude"}

    if not required_track_cols.issubset(track_df.columns):
        return "Unknown"

    if not required_geo_cols.issubset(geo_df.columns):
        return "Unknown"

    start_time = check_time - timedelta(minutes=window_minutes)
    end_time = check_time

    window_pings = track_df[
        (track_df["Time"] >= start_time) &
        (track_df["Time"] <= end_time)
    ].copy()

    if window_pings.empty:
        return "Unknown"

    window_pings = window_pings.dropna(subset=["Latitude", "Longitude", "Time"])
    if window_pings.empty:
        return "Unknown"

    window_pings = window_pings.sort_values("Time")

    for _, ping in window_pings.iterrows():
        v_lat = ping["Latitude"]
        v_lon = ping["Longitude"]

        for _, loc in geo_df.iterrows():
            if pd.isna(loc["Latitude"]) or pd.isna(loc["Longitude"]):
                continue

            radius = (
                loc["Radius_Meters"]
                if "Radius_Meters" in geo_df.columns and pd.notna(loc.get("Radius_Meters"))
                else 150
            )

            distance = haversine(v_lat, v_lon, loc["Latitude"], loc["Longitude"])
            if distance <= radius:
                return f"✅ {loc['Name']}"

    return "❌ Outside Zone"


def build_column_config(df, min_px=90, max_px=280):
    column_config = {}

    for col in df.columns:
        try:
            max_len_data = df[col].astype(str).map(len).max()
        except Exception:
            max_len_data = len(str(col))

        max_len = max(len(str(col)), int(max_len_data) if pd.notna(max_len_data) else len(str(col)))
        width_px = max(min_px, min(max_px, max_len * 9))

        if width_px <= 110:
            width_label = "small"
        elif width_px <= 180:
            width_label = "medium"
        else:
            width_label = "large"

        column_config[col] = st.column_config.TextColumn(label=col, width=width_label)

    return column_config


def get_tracking_file_map(tracking_files):
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
    return tracking_files_map


def process_audit(vtcs_df, tracking_files_map=None, geo_data=None):
    vtcs_df = prepare_vtcs_df(vtcs_df)

    gps_audit, zone_check, matched_files = [], [], []

    for _, row in vtcs_df.iterrows():
        vehicle_name = row.get("Vehicle", "")
        track_df = find_matching_tracking_df(vehicle_name, tracking_files_map) if tracking_files_map else None
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

        gps_mask = (track_df["Time"] >= t_time - timedelta(minutes=2)) & (
            track_df["Time"] <= t_time + timedelta(minutes=2)
        )
        gps_pings = track_df[gps_mask]

        if gps_pings.empty:
            gps_audit.append("❓ No Data")
        else:
            if "Status" in gps_pings.columns:
                stts = gps_pings["Status"].astype(str).str.lower().values
                valid_idle = any(
                    keyword in s for s in stts for keyword in ["idle", "parked", "stopped"]
                )
                gps_audit.append("✅ Verified" if valid_idle else "❌ Moving")
            else:
                gps_audit.append("❓ Status Missing")

        if geo_data is not None:
            z_found = find_zone_in_precheck_window(
                track_df=track_df,
                check_time=t_time,
                geo_df=geo_data,
                window_minutes=60
            )
        else:
            z_found = "Unknown"

        zone_check.append(z_found)

    vtcs_df["Tracking_File_Match"] = matched_files
    vtcs_df["GPS_Audit"] = gps_audit
    vtcs_df["Zone_Check"] = zone_check

    return vtcs_df


def calculate_module_metrics(results, tracking_files_map, geo_data):
    delayed_count = len(results[results["Time_Status"].astype(str).str.contains("🚨", na=False)])
    gps_conflicts = len(results[results["GPS_Audit"] == "❌ Moving"]) if "GPS_Audit" in results.columns else 0
    avg_trip_time = results["Duration_Mins"].dropna().mean() if "Duration_Mins" in results.columns else 0
    active_vehicles = results["Vehicle"].nunique() if "Vehicle" in results.columns else 0
    total_tonnage = results["Tonnage"].sum() if "Tonnage" in results.columns else 0
    trip_count = len(results)
    verified = len(results[results["GPS_Audit"] == "✅ Verified"]) if "GPS_Audit" in results.columns else 0
    verified_pct = round((verified / trip_count) * 100, 1) if trip_count else 0

    return {
        "total_tonnage": total_tonnage,
        "trip_count": trip_count,
        "delayed_count": delayed_count,
        "gps_conflicts": gps_conflicts,
        "avg_trip_time": 0 if pd.isna(avg_trip_time) else round(avg_trip_time, 1),
        "active_vehicles": active_vehicles,
        "tracker_files": len(tracking_files_map),
        "geofence_status": "Linked" if geo_data is not None else "Not Linked",
        "verified_pct": verified_pct,
    }


def build_exec_summary(daily_metrics=None, monthly_metrics=None):
    messages = []

    if daily_metrics:
        messages.append(
            f"Daily VTCS review processed <b>{daily_metrics['trip_count']}</b> trips across "
            f"<b>{daily_metrics['active_vehicles']}</b> active vehicles with <b>{daily_metrics['total_tonnage']:.1f} tons</b> recorded."
        )
        messages.append(
            f"Daily delay exceptions stand at <b>{daily_metrics['delayed_count']}</b>, while GPS verification coverage is <b>{daily_metrics['verified_pct']}%</b>."
        )

    if monthly_metrics:
        messages.append(
            f"Monthly insights processed <b>{monthly_metrics['trip_count']}</b> trips and <b>{monthly_metrics['total_tonnage']:.1f} tons</b>, using the same VTCS audit logic for consistency."
        )
        messages.append(
            f"Monthly operational exceptions show <b>{monthly_metrics['delayed_count']}</b> delayed trips and <b>{monthly_metrics['gps_conflicts']}</b> GPS movement conflicts."
        )

    if not messages:
        messages.append(
            "Upload daily VTCS data or monthly VTCS data to generate management-ready insights, audit observations, and tracking validation."
        )

    return " ".join(messages)


def render_kpi_grid(metrics, prefix=""):
    st.markdown(
        f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">{prefix} Total Tonnage</div>
                <div class="kpi-value">{metrics['total_tonnage']:.1f} T</div>
                <div class="kpi-note">Waste handled during selected module</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">{prefix} Trip Count</div>
                <div class="kpi-value">{metrics['trip_count']}</div>
                <div class="kpi-note">Total audited VTCS records</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">{prefix} Delayed Trips</div>
                <div class="kpi-value">{metrics['delayed_count']}</div>
                <div class="kpi-note">Trips above 30 minutes</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">{prefix} GPS Conflicts</div>
                <div class="kpi-value">{metrics['gps_conflicts']}</div>
                <div class="kpi-note">Tracker movement mismatch cases</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview_cards(daily_metrics=None, monthly_metrics=None, daily_office_label="—", monthly_office_label="—"):
    def safe_value(value, suffix=""):
        if value is None:
            return "—"
        return f"{value}{suffix}"

    st.markdown(
        f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Daily Trips</div>
                <div class="kpi-value">{safe_value(daily_metrics['trip_count'] if daily_metrics else None)}</div>
                <div class="kpi-note">Current uploaded daily VTCS workload</div>
                <div class="kpi-note"><b>Tehsil:</b> {daily_office_label}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Monthly Trips</div>
                <div class="kpi-value">{safe_value(monthly_metrics['trip_count'] if monthly_metrics else None)}</div>
                <div class="kpi-note">Separate monthly insights workload</div>
                <div class="kpi-note"><b>Tehsil:</b> {monthly_office_label}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Daily Tonnage</div>
                <div class="kpi-value">{safe_value(f"{daily_metrics['total_tonnage']:.1f}" if daily_metrics else None, ' T')}</div>
                <div class="kpi-note">Daily recorded waste quantity</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Monthly Tonnage</div>
                <div class="kpi-value">{safe_value(f"{monthly_metrics['total_tonnage']:.1f}" if monthly_metrics else None, ' T')}</div>
                <div class="kpi-note">Monthly recorded waste quantity</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def detect_office_label(df):
    if df is None or "Office" not in df.columns:
        return "—"

    office_vals = (
        df["Office"]
        .dropna()
        .astype(str)
        .str.strip()
    )
    office_vals = office_vals[office_vals != ""]

    if office_vals.empty:
        return "—"

    unique_vals = office_vals.unique().tolist()
    if len(unique_vals) == 1:
        return unique_vals[0]
    return ", ".join(unique_vals[:3]) + (" ..." if len(unique_vals) > 3 else "")


def render_module(module_title, module_subtitle, results, metrics):
    v_stats = results.groupby("Vehicle").agg({"Tonnage": "sum", "Data ID": "count"}).reset_index()
    v_stats.columns = ["Vehicle", "Tons", "Trips"]
    v_stats["Vehicle_Color"] = v_stats["Vehicle"].apply(vehicle_type_color)

    st.markdown(
        f"""
        <div class="module-header">
            <div>
                <div class="section-title">{module_title}</div>
                <div class="section-subtitle">{module_subtitle}</div>
            </div>
            <div class="module-badge">Operational module ready</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_kpi_grid(metrics)

    c1, c2 = st.columns(2)

    with c1:
        tons_fig = go.Figure()
        tons_fig.add_trace(
            go.Bar(
                x=v_stats["Vehicle"],
                y=v_stats["Tons"],
                marker=dict(
                    color="#3b82f6",
                    line=dict(color="#ffffff", width=1.5)
                ),
                text=[f"{x:.2f}" for x in v_stats["Tons"]],
                textposition="outside",
                textfont=dict(size=12, color="#163122"),
                hovertemplate="<b>%{x}</b><br>Tonnage: %{y:.2f} T<extra></extra>",
            )
        )
        tons_fig.update_layout(
            title=f"{module_title} • Tonnage by Vehicle",
            title_font=dict(size=20, color="#163122"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#ffffff",
            margin=dict(l=20, r=20, t=58, b=20),
            height=420,
            xaxis=dict(
                title="Vehicle",
                tickfont=dict(size=11, color="#476154"),
                title_font=dict(size=13, color="#476154"),
                showgrid=False
            ),
            yaxis=dict(
                title="Tons",
                tickfont=dict(size=11, color="#476154"),
                title_font=dict(size=13, color="#476154"),
                gridcolor="#e3eee4",
                zerolinecolor="#d3e4d5"
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
                    line=dict(color="#ffffff", width=1.5)
                ),
                text=[str(x) for x in v_stats["Trips"]],
                textposition="outside",
                textfont=dict(size=12, color="#163122"),
                hovertemplate="<b>%{x}</b><br>Trips: %{y}<extra></extra>",
            )
        )
        trips_fig.update_layout(
            title=f"{module_title} • Trips by Vehicle",
            title_font=dict(size=20, color="#163122"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#ffffff",
            margin=dict(l=20, r=20, t=58, b=20),
            height=420,
            xaxis=dict(
                title="Vehicle",
                tickfont=dict(size=11, color="#476154"),
                title_font=dict(size=13, color="#476154"),
                showgrid=False
            ),
            yaxis=dict(
                title="Trips",
                tickfont=dict(size=11, color="#476154"),
                title_font=dict(size=13, color="#476154"),
                gridcolor="#e3eee4",
                zerolinecolor="#d3e4d5"
            ),
            showlegend=False
        )
        st.plotly_chart(trips_fig, use_container_width=True)

    tabs = st.tabs(["📋 Executive Summary", "🔍 Technical Audit Log"])

    st.markdown(
        """
        <style>
        button[role="tab"] p {
            font-size: 1.02rem !important;
            font-weight: 900 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with tabs[0]:
        summ = results.groupby("Vehicle").agg(
            {"Tonnage": "sum", "Data ID": "count", "Duration_Mins": "mean"}
        ).rename(
            columns={
                "Data ID": "Trips",
                "Tonnage": "Total Tons",
                "Duration_Mins": "Avg Mins"
            }
        )

        summary_df = summ.reset_index().copy()

        st.dataframe(
            summary_df.style
            .background_gradient(cmap="Greens", subset=["Total Tons"])
            .format({"Total Tons": "{:.2f}", "Avg Mins": "{:.1f}"}),
            use_container_width=True,
            height=420,
            hide_index=True,
            column_config=build_column_config(summary_df)
        )

    with tabs[1]:
        cols = ["Vehicle", "Time In", "Time Out", "Duration_Mins", "Tonnage", "Time_Status"]

        if "Tracking_File_Match" in results.columns:
            cols.append("Tracking_File_Match")
        if "GPS_Audit" in results.columns:
            cols.append("GPS_Audit")
        if "Zone_Check" in results.columns:
            cols.append("Zone_Check")

        audit_df = results[cols].copy()

        st.dataframe(
            audit_df,
            use_container_width=True,
            height=500,
            hide_index=True,
            column_config=build_column_config(audit_df)
        )


# =========================================================
# SESSION STATE
# =========================================================
if "geo_data" not in st.session_state:
    st.session_state.geo_data = None

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    if LOGO_BASE64:
        st.markdown(
            f'<div style="display:flex;justify-content:center;margin-bottom:12px;"><img src="data:image/jpeg;base64,{LOGO_BASE64}" width="92" style="border-radius:18px;background:white;padding:6px;"></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<div style='font-size:50px;text-align:center;'>♻️</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="sidebar-panel">
            <div class="sidebar-title">Professional Control Panel</div>
            <div class="sidebar-subtitle">
                Upload daily VTCS, monthly VTCS, tracker portal files, and geofence coordinates through a cleaner and more structured workflow.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    vtcs_file = st.file_uploader("1. VTCS Daily Data", type=["xlsx", "csv"])
    monthly_vtcs_file = st.file_uploader("2. VTCS Monthly Insights Data", type=["xlsx", "csv"])

    tracking_files = st.file_uploader(
        "3. Tracker Portal Data",
        type=["xlsx", "csv"],
        accept_multiple_files=True,
        help="Upload separate tracker file for each vehicle. File name should match vehicle name."
    )

    st.markdown(
        """
        <div class="sidebar-panel" style="margin-top:10px;">
            <div class="sidebar-title">Geofence Configuration</div>
            <div class="sidebar-subtitle">
                Upload TCP / WE coordinates to enable zone checking for both daily and monthly audit modules.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("TCP & WE Settings", expanded=True):
        geo_upload = st.file_uploader("4. Upload Coordinate File", type=["xlsx", "csv"])

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
            if st.button("Reset Zones", use_container_width=True):
                st.session_state.geo_data = None
                st.rerun()

# =========================================================
# LOAD TRACKING FILES ONCE
# =========================================================
tracking_files_map = get_tracking_file_map(tracking_files)

# =========================================================
# PROCESS DAILY AND MONTHLY MODULES
# =========================================================
daily_results = None
month_results = None

daily_metrics = None
monthly_metrics = None
daily_office_label = "—"
monthly_office_label = "—"

if vtcs_file:
    df_vtcs = pd.read_excel(vtcs_file) if vtcs_file.name.lower().endswith("xlsx") else pd.read_csv(vtcs_file)
    daily_office_label = detect_office_label(df_vtcs)
    daily_results = process_audit(df_vtcs, tracking_files_map if tracking_files_map else None, st.session_state.geo_data)
    daily_metrics = calculate_module_metrics(daily_results, tracking_files_map, st.session_state.geo_data)

if monthly_vtcs_file:
    df_month = pd.read_excel(monthly_vtcs_file) if monthly_vtcs_file.name.lower().endswith("xlsx") else pd.read_csv(monthly_vtcs_file)
    monthly_office_label = detect_office_label(df_month)
    month_results = process_audit(df_month, tracking_files_map if tracking_files_map else None, st.session_state.geo_data)
    monthly_metrics = calculate_module_metrics(month_results, tracking_files_map, st.session_state.geo_data)

# =========================================================
# TOP EXECUTIVE SUMMARY
# =========================================================
st.markdown('<div class="insight-grid">', unsafe_allow_html=True)

col_left, col_right = st.columns([1.45, 1])

with col_left:
    st.markdown(
        f"""
        <div class="summary-banner">
            <div class="summary-title">Executive Summary</div>
            <div class="summary-body">{build_exec_summary(daily_metrics, monthly_metrics)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_right:
    st.markdown(
        f"""
        <div class="section-card" style="margin-bottom:0;">
            <div class="section-title">System Snapshot</div>
            <div class="section-subtitle">Quick operational status across uploaded modules</div>
            <div style="height:8px"></div>
            <div class="kpi-label">Tracker Files Loaded</div>
            <div class="kpi-value">{len(tracking_files_map)}</div>
            <div style="height:12px"></div>
            <div class="kpi-label">Geofence Status</div>
            <div class="kpi-value">{"Linked" if st.session_state.geo_data is not None else "Not Linked"}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('</div>', unsafe_allow_html=True)

render_overview_cards(daily_metrics, monthly_metrics, daily_office_label, monthly_office_label)

# =========================================================
# MODULES
# =========================================================
main_tabs = st.tabs(["Daily VTCS Module", "Monthly Insights Module"])

with main_tabs[0]:
    if daily_results is not None:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        render_module(
            module_title="Daily VTCS Module",
            module_subtitle=f"Operational daily review using tracker validation, delay checks, and geofence logic. Tehsil: {daily_office_label}",
            results=daily_results,
            metrics=daily_metrics,
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">Daily VTCS Module</div>
                <div class="section-subtitle">Upload daily VTCS data from the control panel to generate this module.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.info("Upload VTCS Daily Data to activate the Daily VTCS module.")

with main_tabs[1]:
    if month_results is not None:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        render_module(
            module_title="Monthly Insights Module",
            module_subtitle=f"Separate monthly module using the same logic and functionality as daily VTCS processing. Tehsil: {monthly_office_label}",
            results=month_results,
            metrics=monthly_metrics,
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <div class="section-card">
                <div class="section-title">Monthly Insights Module</div>
                <div class="section-subtitle">Upload monthly VTCS data to run a separate monthly insights workflow with the same audit logic as daily processing.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.info("Upload VTCS Monthly Insights Data to activate the Monthly Insights module.")
