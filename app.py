import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
import plotly.express as px
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
# PROFESSIONAL UI THEME
# =========================================================
st.markdown(
    """
    <style>
    :root {
        --bg-main: #f4f7fb;
        --bg-soft: #eaf0f7;
        --panel: #ffffff;
        --panel-2: #f9fbfd;
        --sidebar: #0f172a;
        --sidebar-2: #172554;
        --text: #0f172a;
        --muted: #64748b;
        --line: #d9e2ec;
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --success: #16a34a;
        --success-dark: #15803d;
        --warning: #d97706;
        --danger: #dc2626;
        --shadow: 0 12px 32px rgba(15, 23, 42, 0.10);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(37, 99, 235, 0.08), transparent 25%),
            linear-gradient(180deg, #f8fbff 0%, #f4f7fb 45%, #eef4fa 100%);
        color: var(--text);
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    .stApp, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5,
    .stApp p, .stApp label, .stApp div, .stMarkdown {
        color: var(--text);
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--sidebar) 0%, var(--sidebar-2) 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div {
        color: #f8fafc !important;
    }

    .hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 30px 32px;
        margin-bottom: 18px;
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.20);
    }

    .hero::before {
        content: "";
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at 88% 20%, rgba(255,255,255,0.16), transparent 24%);
        pointer-events: none;
    }

    .hero-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.14);
        color: #dbeafe;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.08;
        color: #ffffff !important;
    }

    .hero-subtitle {
        margin-top: 10px;
        color: #dbeafe !important;
        font-size: 1rem;
    }

    .section-card {
        background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 18px 20px;
        box-shadow: var(--shadow);
        margin-bottom: 18px;
    }

    .section-title {
        font-size: 1.05rem;
        font-weight: 800;
        margin: 0 0 3px 0;
        color: #0f172a !important;
    }

    .section-subtitle {
        margin: 0;
        color: var(--muted) !important;
        font-size: 0.93rem;
    }

    .status-pill-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 2px;
        margin-bottom: 18px;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 10px 14px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
        border: 1px solid var(--line);
        background: #ffffff;
        box-shadow: 0 6px 14px rgba(15, 23, 42, 0.05);
    }

    .pill-blue { color: #1d4ed8; }
    .pill-green { color: #15803d; }
    .pill-amber { color: #b45309; }

    div[data-testid="metric-container"] {
        background: linear-gradient(180deg, #ffffff, #f8fbff);
        border: 1px solid #dbe7f3;
        border-radius: 18px;
        padding: 18px 16px;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
    }

    div[data-testid="metric-container"] label {
        color: #475569 !important;
        font-weight: 700;
    }

    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 800;
    }

    [data-testid="stFileUploader"] section {
        background: rgba(255,255,255,0.98) !important;
        border-radius: 16px !important;
        border: 2px dashed #bfd3ea !important;
        padding: 8px !important;
    }

    [data-testid="stFileUploader"] section p,
    [data-testid="stFileUploader"] section span,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] section div {
        color: #0f172a !important;
    }

    .stButton > button,
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
        padding: 0.72rem 1rem !important;
        box-shadow: 0 12px 22px rgba(37, 99, 235, 0.28) !important;
        transition: all 0.16s ease;
    }

    .stButton > button:hover,
    [data-testid="stFileUploader"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 16px 28px rgba(37, 99, 235, 0.32) !important;
        opacity: 0.98;
    }

    div[data-baseweb="select"] > div,
    .stTextInput > div > div,
    .stDateInput > div > div,
    .stNumberInput > div > div {
        border-radius: 12px !important;
        border-color: #cbd5e1 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: #f8fbff;
        border: 1px solid #dbe7f3;
        padding: 8px;
        border-radius: 16px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 12px;
        color: #334155;
        font-weight: 800;
        background: transparent;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #e0ecff, #eef5ff) !important;
        border: 1px solid #bcd2f5 !important;
        color: #1d4ed8 !important;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #dbe7f3;
        border-radius: 18px;
        overflow: hidden;
        box-shadow: var(--shadow);
        background: white;
    }

    .stAlert {
        border-radius: 16px !important;
        border: 1px solid #dbe7f3 !important;
    }

    hr {
        border-color: #dbe7f3;
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
        <p class="hero-subtitle">Professional fleet audit dashboard with clearer analytics, stronger validation, and improved operator experience.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="status-pill-wrap">
        <div class="status-pill pill-blue">📈 Executive analytics</div>
        <div class="status-pill pill-green">📍 Geofence validation</div>
        <div class="status-pill pill-amber">⏱ Delay monitoring</div>
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
                track_df = track_df.iloc[i + 1 :].reset_index(drop=True)
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

    # Case 1: Already separate columns
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

    # Case 2: Combined Lat/Long column
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
        "Invalid geofence file format. Use either [Name, Latitude, Longitude] "
        "or a file containing [TCP/WE, Lat/Long]."
    )


def vehicle_palette(vehicle_name):
    vehicle_name = str(vehicle_name).strip().upper()

    # DUMPER family -> blues
    if vehicle_name.startswith("DUMPER"):
        return "#2563eb"

    # TT family -> greens
    if vehicle_name.startswith("TT"):
        return "#16a34a"

    # Others -> slate
    return "#64748b"


def vehicle_group(vehicle_name):
    vehicle_name = str(vehicle_name).strip().upper()
    if vehicle_name.startswith("DUMPER"):
        return "DUMPER"
    if vehicle_name.startswith("TT"):
        return "TT"
    return "OTHER"


# =========================================================
# SESSION STATE
# =========================================================
if "geo_data" not in st.session_state:
    st.session_state.geo_data = None

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/truck.png", width=80)
    st.markdown("### Control Panel")
    st.caption("Upload source files, tracker files, and geofence locations.")

    vtcs_file = st.file_uploader("1. VTCS Daily Data", type=["xlsx", "csv"])

    tracking_files = st.file_uploader(
        "2. Tracker Portal Data",
        type=["xlsx", "csv"],
        accept_multiple_files=True,
        help="Upload separate tracker file for each vehicle. File name should match vehicle name."
    )

    st.divider()
    st.markdown("### 📍 Geofence Config")

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

    # =====================================================
    # KPI METRICS
    # =====================================================
    st.markdown(
        """
        <div class="section-card">
            <p class="section-title">Executive KPIs</p>
            <p class="section-subtitle">A concise overview of fleet output, delays, and GPS validation status.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    delayed_count = len(results[results["Time_Status"].str.contains("🚨", na=False)])
    gps_conflicts = (
        len(results[results["GPS_Audit"] == "❌ Moving"])
        if "GPS_Audit" in results.columns
        else 0
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Tonnage", f"{results['Tonnage'].sum():.1f} T")
    k2.metric("Trip Count", len(results))
    k3.metric("Delayed (>30m)", delayed_count)
    k4.metric("GPS Conflicts", gps_conflicts if "GPS_Audit" in results.columns else "—")

    # =====================================================
    # ANALYTICS
    # =====================================================
    st.markdown(
        """
        <div class="section-card">
            <p class="section-title">Operational Overview</p>
            <p class="section-subtitle">Clear vehicle-wise charts with category-based coloring for DUMPER and TT fleet types.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    v_stats = results.groupby("Vehicle").agg({"Tonnage": "sum", "Data ID": "count"}).reset_index()
    v_stats.columns = ["Vehicle", "Tons", "Trips"]
    v_stats["Color"] = v_stats["Vehicle"].apply(vehicle_palette)
    v_stats["Group"] = v_stats["Vehicle"].apply(vehicle_group)

    c1, c2 = st.columns(2)

    with c1:
        tons_fig = go.Figure()
        tons_fig.add_trace(
            go.Bar(
                x=v_stats["Vehicle"],
                y=v_stats["Tons"],
                marker=dict(
                    color=v_stats["Color"],
                    line=dict(color="#ffffff", width=1.5)
                ),
                text=[f"{x:.2f}" for x in v_stats["Tons"]],
                textposition="outside",
                textfont=dict(size=12, color="#0f172a"),
                hovertemplate="<b>%{x}</b><br>Tons: %{y:.2f}<extra></extra>",
            )
        )
        tons_fig.update_layout(
            title="Tonnage by Vehicle",
            title_font=dict(size=19, color="#0f172a"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#ffffff",
            margin=dict(l=20, r=20, t=60, b=20),
            height=430,
            xaxis=dict(
                title="Vehicle",
                tickfont=dict(size=11, color="#334155"),
                title_font=dict(color="#334155"),
                showgrid=False
            ),
            yaxis=dict(
                title="Tons",
                tickfont=dict(size=11, color="#334155"),
                title_font=dict(color="#334155"),
                gridcolor="#e2e8f0",
                zerolinecolor="#cbd5e1"
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
                    color=v_stats["Color"],
                    line=dict(color="#ffffff", width=1.5)
                ),
                text=[str(x) for x in v_stats["Trips"]],
                textposition="outside",
                textfont=dict(size=12, color="#0f172a"),
                hovertemplate="<b>%{x}</b><br>Trips: %{y}<extra></extra>",
            )
        )
        trips_fig.update_layout(
            title="Trips by Vehicle",
            title_font=dict(size=19, color="#0f172a"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#ffffff",
            margin=dict(l=20, r=20, t=60, b=20),
            height=430,
            xaxis=dict(
                title="Vehicle",
                tickfont=dict(size=11, color="#334155"),
                title_font=dict(color="#334155"),
                showgrid=False
            ),
            yaxis=dict(
                title="Trips",
                tickfont=dict(size=11, color="#334155"),
                title_font=dict(color="#334155"),
                gridcolor="#e2e8f0",
                zerolinecolor="#cbd5e1"
            ),
            showlegend=False
        )
        st.plotly_chart(trips_fig, use_container_width=True)

    # =====================================================
    # LEGEND
    # =====================================================
    st.markdown(
        """
        <div class="section-card">
            <p class="section-title">Chart Color Reference</p>
            <p class="section-subtitle">
                <span style="font-weight:700;color:#2563eb;">■ DUMPER vehicles</span> &nbsp;&nbsp;
                <span style="font-weight:700;color:#16a34a;">■ TT vehicles</span> &nbsp;&nbsp;
                <span style="font-weight:700;color:#64748b;">■ Other vehicles</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =====================================================
    # TABS
    # =====================================================
    t1, t2 = st.tabs(["📋 Executive Summary", "🔍 Technical Audit Log"])

    with t1:
        st.markdown(
            """
            <div class="section-card">
                <p class="section-title">Vehicle Summary</p>
                <p class="section-subtitle">Management-ready summary with output, trips, and average duration by vehicle.</p>
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
            height=420,
        )

    with t2:
        st.markdown(
            """
            <div class="section-card">
                <p class="section-title">Detailed Audit Output</p>
                <p class="section-subtitle">Full event log including matching tracker file, GPS audit, and geofence result.</p>
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
        <div class="section-card">
            <p class="section-title">Ready to begin</p>
            <p class="section-subtitle">Upload VTCS data, tracker files, and geofence locations from the sidebar to generate the dashboard.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("Upload files from the sidebar to start the fleet audit.")
