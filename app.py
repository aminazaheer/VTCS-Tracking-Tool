import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
import plotly.express as px
from math import radians, cos, sin, asin, sqrt

# --- PAGE CONFIG ---
st.set_page_config(page_title="VTCS Auditor Pro", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS FOR PROFESSIONAL UI ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 5px solid #0068c9;
    }
    .stTable { background-color: white; border-radius: 10px; }
    .stDataFrame { border-radius: 10px; }
    h1, h2, h3 { color: #1e3d59; font-family: 'Segoe UI', sans-serif; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #0068c9; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- HELPER: HAVERSINE FORMULA ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000 # Meters
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2)**2 + cos(phi1) * cos(phi2) * sin(dlambda / 2)**2
    return 2 * R * asin(sqrt(a))

# --- SESSION STATE FOR COORDINATES ---
if 'geo_data' not in st.session_state:
    st.session_state.geo_data = None

st.title("🚛 VTCS & GPS Tracking Auditor")
st.markdown("Automated Daily Audit & Operation Analytics")

# --- SIDEBAR ---
with st.sidebar:
    st.header("📂 Data Control")
    vtcs_file = st.file_uploader("1. Upload VTCS Data", type=['xlsx', 'csv'])
    tracking_file = st.file_uploader("2. Upload Tracking Report", type=['xlsx', 'csv'])
    
    st.divider()
    st.header("📍 Location Settings")
    with st.expander("TCP & WE Coordinates"):
        geo_upload = st.file_uploader("Upload Geo-Fence File", type=['xlsx', 'csv'])
        if geo_upload:
            st.session_state.geo_data = pd.read_excel(geo_upload) if geo_upload.name.endswith('xlsx') else pd.read_csv(geo_upload)
            st.success("Locations Loaded!")
        
        if st.session_state.geo_data is not None:
            if st.button("🗑️ Reset Locations"):
                st.session_state.geo_data = None
                st.rerun()

def process_audit(vtcs_df, track_df=None):
    # --- 1. VTCS PROCESSING ---
    for col in ['Waste Collected (Kg)', 'Before Weight', 'After Weight (Kg)']:
        if col in vtcs_df.columns:
            vtcs_df[col] = pd.to_numeric(vtcs_df[col].astype(str).str.replace(',', ''), errors='coerce')
    
    vtcs_df['Tonnage'] = vtcs_df['Waste Collected (Kg)'] / 1000
    vtcs_df['Time In'] = pd.to_datetime(vtcs_df['Time In'], errors='coerce')
    vtcs_df['Time Out'] = pd.to_datetime(vtcs_df['Time Out'], errors='coerce')
    
    vtcs_df['Duration_Mins'] = (vtcs_df['Time Out'] - vtcs_df['Time In']).dt.total_seconds() / 60
    vtcs_df['Time_Status'] = vtcs_df['Duration_Mins'].apply(lambda x: "🚨 Suspicious (>30m)" if x > 30 else "✅ Normal")

    # --- 2. TRACKING CROSS-CHECK ---
    if track_df is not None:
        # Detect header
        if 'Time' not in [str(c).strip() for c in track_df.columns]:
            for i in range(min(len(track_df), 20)):
                row_values = [str(val).strip() for val in track_df.iloc[i].values]
                if 'Time' in row_values:
                    track_df.columns = row_values
                    track_df = track_df.iloc[i+1:].reset_index(drop=True)
                    break
        
        track_df.columns = [str(c).strip() for c in track_df.columns]
        
        if 'Time' in track_df.columns and 'Status' in track_df.columns:
            track_df['Time'] = pd.to_datetime(track_df['Time'], errors='coerce')
            
            gps_audit_results = []
            zone_results = []

            for idx, row in vtcs_df.iterrows():
                target_time = row['Time In']
                if pd.isnull(target_time):
                    gps_audit_results.append("❓ Invalid Time")
                    zone_results.append("N/A")
                    continue

                mask = (track_df['Time'] >= target_time - timedelta(minutes=2)) & \
                       (track_df['Time'] <= target_time + timedelta(minutes=2))
                nearby_pings = track_df[mask]
                
                if nearby_pings.empty:
                    gps_audit_results.append("❓ No GPS Data")
                    zone_results.append("Unknown")
                else:
                    # Status Check
                    statuses = nearby_pings['Status'].astype(str).str.lower().values
                    is_valid = any(('idle' in s or 'parked' in s or 'stopped' in s) for s in statuses)
                    gps_audit_results.append("✅ Verified (Idle)" if is_valid else "❌ Conflict (Moving)")
                    
                    # Zone Geofence Check
                    zone_found = "❌ Outside Zone"
                    if st.session_state.geo_data is not None and 'Latitude' in nearby_pings.columns:
                        v_lat = nearby_pings.iloc[0]['Latitude']
                        v_lon = nearby_pings.iloc[0]['Longitude']
                        for _, loc in st.session_state.geo_data.iterrows():
                            dist = haversine(v_lat, v_lon, loc['Latitude'], loc['Longitude'])
                            if dist <= loc.get('Radius_Meters', 150):
                                zone_found = f"✅ {loc['Name']}"
                                break
                    zone_results.append(zone_found)
            
            vtcs_df['GPS_Audit'] = gps_audit_results
            vtcs_df['Zone_Check'] = zone_results

    return vtcs_df

if vtcs_file:
    df_vtcs = pd.read_excel(vtcs_file) if vtcs_file.name.endswith('xlsx') else pd.read_csv(vtcs_file)
    df_track = None
    if tracking_file:
        df_track = pd.read_excel(tracking_file) if tracking_file.name.endswith('xlsx') else pd.read_csv(tracking_file)
    
    results = process_audit(df_vtcs, df_track)

    # --- TOP KPI METRICS ---
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1: st.metric("Total Weight", f"{results['Tonnage'].sum():.2f} Tons")
    with kpi2: st.metric("Daily Trips", len(results))
    with kpi3: st.metric("Suspicious Trips", len(results[results['Time_Status'].str.contains("🚨")]))
    with kpi4: 
        if 'GPS_Audit' in results.columns:
            st.metric("GPS Conflicts", len(results[results['GPS_Audit'] == "❌ Conflict (Moving)"]))
        else:
            st.metric("GPS Status", "Waiting...")

    # --- CHARTS SECTION ---
    st.divider()
    chart_col1, chart_col2 = st.columns(2)
    
    vehicle_stats = results.groupby('Vehicle').agg({'Tonnage':'sum', 'Data ID':'count'}).reset_index()
    vehicle_stats.columns = ['Vehicle', 'Tons', 'Trips']

    with chart_col1:
        fig1 = px.bar(vehicle_stats, x='Vehicle', y='Tons', title="Tonnage per Vehicle", color='Tons', color_continuous_scale='Blues')
        st.plotly_chart(fig1, use_container_width=True)
    
    with chart_col2:
        fig2 = px.bar(vehicle_stats, x='Vehicle', y='Trips', title="Number of Trips per Vehicle", color='Trips', color_continuous_scale='Greens')
        st.plotly_chart(fig2, use_container_width=True)

    # --- DATA TABS ---
    tab1, tab2 = st.tabs(["📊 Performance Summary", "🔍 Detailed Audit Log"])

    with tab1:
        st.subheader("Vehicle-Wise Efficiency")
        summary = results.groupby('Vehicle').agg({
            'Tonnage': 'sum', 
            'Data ID': 'count',
            'Duration_Mins': 'mean'
        }).rename(columns={'Data ID': 'Total Trips', 'Tonnage': 'Total Tons', 'Duration_Mins': 'Avg Time (m)'})
        
        # Table with colored heatmap for tonnage
        st.dataframe(summary.style.background_gradient(cmap='YlGnBu', subset=['Total Tons']).format("{:.2f}"), use_container_width=True)
        
        st.download_button("📥 Download Summary CSV", data=summary.to_csv().encode('utf-8'), file_name="Vehicle_Summary.csv")

    with tab2:
        st.subheader("Row-by-Row Validation")
        display_cols = ['Vehicle', 'Time In', 'Time Out', 'Duration_Mins', 'Tonnage', 'Time_Status']
        if 'GPS_Audit' in results.columns: display_cols.append('GPS_Audit')
        if 'Zone_Check' in results.columns: display_cols.append('Zone_Check')

        def style_rows(row):
            styles = [''] * len(row)
            if "🚨" in str(row['Time_Status']) or "❌" in str(row.get('GPS_Audit', '')):
                return ['background-color: #ffe6e6'] * len(row)
            if "✅" in str(row['Time_Status']):
                return ['background-color: #e6ffed'] * len(row)
            return styles

        st.dataframe(results[display_cols].style.apply(style_rows, axis=1), use_container_width=True)
        
        st.download_button("📥 Download Full Audit Report", data=results[display_cols].to_csv(index=False).encode('utf-8'), file_name="Audit_Report.csv")

else:
    st.info("👋 Welcome! Please upload your VTCS Daily Export from the sidebar to begin the audit.")
