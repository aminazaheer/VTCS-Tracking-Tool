import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
import plotly.express as px
from math import radians, cos, sin, asin, sqrt

# --- PAGE CONFIG ---
st.set_page_config(page_title="VTCS Auditor Pro", layout="wide", initial_sidebar_state="expanded")

# --- ADVANCED UI STYLING (Updated for Green Browse Buttons) ---
st.markdown("""
    <style>
    /* Main background */
    .stApp { background-color: #f4f7f9; }
    
    /* Branded Header */
    .main-header {
        background: linear-gradient(90deg, #1e3d59 0%, #0068c9 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Metric Card Styling */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-bottom: 4px solid #0068c9;
    }

    /* GREEN BROWSE FILE BUTTONS */
    /* This targets the button inside the file uploader */
    button[kind="secondary"] {
        border: 1px solid #2ecc71 !important;
        color: #2ecc71 !important;
        background-color: transparent !important;
    }

    /* This targets the actual upload button click state */
    section[data-testid="stFileUploader"] button {
        background-color: #2ecc71 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        transition: 0.3s all ease;
    }

    section[data-testid="stFileUploader"] button:hover {
        background-color: #27ae60 !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1e3d59;
    }
    section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    </style>
    """, unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown("""
    <div class="main-header">
        <h1 style='margin:0; font-size: 2.5rem; color: white;'>🚛 VTCS AUDITOR</h1>
        <p style='margin:0; opacity: 0.8; color: white;'>Precision Fleet Audit & Geofencing Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

# ... [REST OF YOUR CODE CONTINUES AS NORMAL FROM HERE] ...

# --- HELPER: HAVERSINE ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000 
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2)**2 + cos(phi1) * cos(phi2) * sin(dlambda / 2)**2
    return 2 * R * asin(sqrt(a))

if 'geo_data' not in st.session_state:
    st.session_state.geo_data = None

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/truck.png", width=80)
    st.header("Control Panel")
    vtcs_file = st.file_uploader("1. VTCS Daily Data", type=['xlsx', 'csv'])
    tracking_file = st.file_uploader("2. Tracker Portal Data", type=['xlsx', 'csv'])
    
    st.divider()
    st.subheader("📍 Geofence Config")
    with st.expander("TCP & WE Settings"):
        geo_upload = st.file_uploader("Upload Coordinate File", type=['xlsx', 'csv'])
        if geo_upload:
            st.session_state.geo_data = pd.read_excel(geo_upload) if geo_upload.name.endswith('xlsx') else pd.read_csv(geo_upload)
            st.success("Coordinates Linked!")
        
        if st.session_state.geo_data is not None:
            st.info(f"Active Zones: {len(st.session_state.geo_data)}")
            if st.button("🗑️ Reset Zones"):
                st.session_state.geo_data = None
                st.rerun()

def process_audit(vtcs_df, track_df=None):
    # --- VTCS LOGIC ---
    for col in ['Waste Collected (Kg)', 'Before Weight', 'After Weight (Kg)']:
        if col in vtcs_df.columns:
            vtcs_df[col] = pd.to_numeric(vtcs_df[col].astype(str).str.replace(',', ''), errors='coerce')
    
    vtcs_df['Tonnage'] = vtcs_df['Waste Collected (Kg)'].fillna(0) / 1000
    vtcs_df['Time In'] = pd.to_datetime(vtcs_df['Time In'], errors='coerce')
    vtcs_df['Time Out'] = pd.to_datetime(vtcs_df['Time Out'], errors='coerce')
    vtcs_df['Duration_Mins'] = (vtcs_df['Time Out'] - vtcs_df['Time In']).dt.total_seconds() / 60
    vtcs_df['Time_Status'] = vtcs_df['Duration_Mins'].apply(lambda x: "🚨 Suspicious (>30m)" if x > 30 else "✅ Normal")

    # --- TRACKING LOGIC ---
    if track_df is not None:
        if 'Time' not in [str(c).strip() for c in track_df.columns]:
            for i in range(min(len(track_df), 20)):
                row_values = [str(val).strip() for val in track_df.iloc[i].values]
                if 'Time' in row_values:
                    track_df.columns = row_values
                    track_df = track_df.iloc[i+1:].reset_index(drop=True)
                    break
        track_df.columns = [str(c).strip() for c in track_df.columns]
        
        if 'Time' in track_df.columns:
            track_df['Time'] = pd.to_datetime(track_df['Time'], errors='coerce')
            gps_audit, zone_check = [], []

            for _, row in vtcs_df.iterrows():
                t_time = row['Time In']
                if pd.isnull(t_time):
                    gps_audit.append("❓ Invalid"); zone_check.append("N/A")
                    continue

                mask = (track_df['Time'] >= t_time - timedelta(minutes=2)) & \
                       (track_df['Time'] <= t_time + timedelta(minutes=2))
                pings = track_df[mask]
                
                if pings.empty:
                    gps_audit.append("❓ No Data"); zone_check.append("Unknown")
                else:
                    stts = pings['Status'].astype(str).str.lower().values
                    valid_idle = any(x in s for s in stts for x in ['idle', 'parked', 'stopped'])
                    gps_audit.append("✅ Verified" if valid_idle else "❌ Moving")
                    
                    z_found = "❌ Outside Zone"
                    if st.session_state.geo_data is not None and 'Latitude' in pings.columns:
                        v_lat, v_lon = pings.iloc[0]['Latitude'], pings.iloc[0]['Longitude']
                        for _, loc in st.session_state.geo_data.iterrows():
                            if haversine(v_lat, v_lon, loc['Latitude'], loc['Longitude']) <= loc.get('Radius_Meters', 150):
                                z_found = f"✅ {loc['Name']}"
                                break
                    zone_check.append(z_found)
            
            vtcs_df['GPS_Audit'], vtcs_df['Zone_Check'] = gps_audit, zone_check
    return vtcs_df

if vtcs_file:
    df_vtcs = pd.read_excel(vtcs_file) if vtcs_file.name.endswith('xlsx') else pd.read_csv(vtcs_file)
    df_track = None
    if tracking_file:
        df_track = pd.read_excel(tracking_file) if tracking_file.name.endswith('xlsx') else pd.read_csv(tracking_file)
    
    results = process_audit(df_vtcs, df_track)

    # --- KPI METRICS ---
    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Total Tonnage", f"{results['Tonnage'].sum():.1f} T")
    kpi_cols[1].metric("Trip Count", len(results))
    kpi_cols[2].metric("Delayed (>30m)", len(results[results['Time_Status'].str.contains("🚨")]))
    if 'GPS_Audit' in results.columns:
        kpi_cols[3].metric("GPS Conflicts", len(results[results['GPS_Audit'] == "❌ Moving"]))

    # --- ANALYTICS ---
    st.write("### 📊 Operational Overview")
    c1, c2 = st.columns(2)
    v_stats = results.groupby('Vehicle').agg({'Tonnage':'sum', 'Data ID':'count'}).reset_index()
    v_stats.columns = ['Vehicle', 'Tons', 'Trips']

    with c1:
        st.plotly_chart(px.bar(v_stats, x='Vehicle', y='Tons', title="Tonnage by Fleet", template="plotly_white", color_discrete_sequence=['#1e3d59']), use_container_width=True)
    with c2:
        st.plotly_chart(px.bar(v_stats, x='Vehicle', y='Trips', title="Trips by Fleet", template="plotly_white", color_discrete_sequence=['#2ecc71']), use_container_width=True)

    # --- DATA TABS ---
    t1, t2 = st.tabs(["📋 Executive Summary", "🔍 Technical Audit Log"])
    
    with t1:
        summ = results.groupby('Vehicle').agg({'Tonnage': 'sum', 'Data ID': 'count', 'Duration_Mins': 'mean'}).rename(columns={'Data ID': 'Trips', 'Tonnage': 'Total Tons', 'Duration_Mins': 'Avg Mins'})
        st.dataframe(summ.style.background_gradient(cmap='Blues', subset=['Total Tons']).format("{:.2f}"), use_container_width=True)
        st.download_button("📥 Export Summary", summ.to_csv().encode('utf-8'), "Summary.csv")

    with t2:
        cols = ['Vehicle', 'Time In', 'Time Out', 'Duration_Mins', 'Tonnage', 'Time_Status']
        for c in ['GPS_Audit', 'Zone_Check']:
            if c in results.columns: cols.append(c)
        
        def highlight(row):
            if "🚨" in str(row['Time_Status']) or "❌" in str(row.get('GPS_Audit', '')):
                return ['background-color: #fff0f0'] * len(row)
            return [''] * len(row)

        st.dataframe(results[cols].style.apply(highlight, axis=1), use_container_width=True)
        st.download_button("📥 Export Audit Report", results[cols].to_csv(index=False).encode('utf-8'), "Full_Audit.csv")

else:
    st.info("💡 **Getting Started:** Upload your VTCS export in the sidebar to populate the dashboard.")
