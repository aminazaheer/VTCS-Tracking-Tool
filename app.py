import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="VTCS Auditor Pro", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS FOR BETTER UI ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .status-card { padding: 20px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #e6e9ef; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚛 VTCS & GPS Tracking Auditor")
st.markdown("Automated Weight, Time, and GPS Validation for Sargodha Operations")

# --- SIDEBAR ---
st.sidebar.header("📂 Data Upload")
vtcs_file = st.sidebar.file_uploader("Upload VTCS Portal Data", type=['xlsx', 'csv'])
tracking_file = st.sidebar.file_uploader("Upload Tracking Report", type=['xlsx', 'csv'])
st.sidebar.info("Tracking Format: Time, Engine, Speed, Status, ODO, Lat, Long, Location")

def process_audit(vtcs_df, track_df=None):
    # 1. VTCS Cleaning
    for col in ['Waste Collected (Kg)', 'Before Weight', 'After Weight (Kg)']:
        if col in vtcs_df.columns:
            vtcs_df[col] = pd.to_numeric(vtcs_df[col].astype(str).str.replace(',', ''), errors='coerce')
    
    vtcs_df['Tonnage'] = vtcs_df['Waste Collected (Kg)'] / 1000
    vtcs_df['Time In'] = pd.to_datetime(vtcs_df['Time In'], errors='coerce')
    vtcs_df['Time Out'] = pd.to_datetime(vtcs_df['Time Out'], errors='coerce')
    
    # Time Logic: > 30m is Suspicious
    vtcs_df['Duration_Mins'] = (vtcs_df['Time Out'] - vtcs_df['Time In']).dt.total_seconds() / 60
    vtcs_df['Time_Status'] = vtcs_df['Duration_Mins'].apply(lambda x: "🚨 Suspicious (>30m)" if x > 30 else "✅ Normal")

    # 2. Advanced GPS Cross-Check with 2-Minute Grace Period
    if track_df is not None:
        # Standardize Tracking Columns based on your new format
        track_df.columns = ['Time', 'Engine', 'Speed', 'Status', 'ODO', 'Lat', 'Long', 'Location']
        track_df['Time'] = pd.to_datetime(track_df['Time'], errors='coerce')
        
        gps_results = []
        
        for idx, row in vtcs_df.iterrows():
            v_id = row['Vehicle']
            t_in = row['Time In']
            
            if pd.isnull(t_in):
                gps_results.append("❓ Invalid Time")
                continue

            # Filter tracking for same vehicle
            v_track = track_df[track_df['Location'].str.contains(str(v_id), na=False) | (track_df.index >= 0)] 
            # Note: For best results, ensure 'Vehicle' column exists in GPS too. 
            # Here we search for the closest time ping overall.
            
            # Find pings within +/- 2 minutes of VTCS Time In
            mask = (track_df['Time'] >= t_in - timedelta(minutes=2)) & \
                   (track_df['Time'] <= t_in + timedelta(minutes=2))
            
            nearby_pings = track_df[mask]
            
            if nearby_pings.empty:
                gps_results.append("❓ No GPS Data")
            else:
                # If any ping in that 4-minute window shows "Idle", we accept it
                statuses = nearby_pings['Status'].astype(str).str.lower().values
                if any('idle' in s for s in statuses):
                    gps_results.append("✅ Verified (Idle)")
                else:
                    gps_results.append("❌ Conflict (Moving)")
        
        vtcs_df['GPS_Audit'] = gps_results

    return vtcs_df

if vtcs_file:
    df_vtcs = pd.read_excel(vtcs_file) if vtcs_file.name.endswith('xlsx') else pd.read_csv(vtcs_file)
    df_track = None
    if tracking_file:
        df_track = pd.read_excel(tracking_file) if tracking_file.name.endswith('xlsx') else pd.read_csv(tracking_file)
    
    results = process_audit(df_vtcs, df_track)

    # --- TOP METRICS ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Trips", len(results))
    with m2:
        st.metric("Total Weight", f"{results['Tonnage'].sum():.2f} Tons")
    with m3:
        delayed = len(results[results['Time_Status'].str.contains("🚨")])
        st.metric("Delayed Trips", delayed, delta_color="inverse")
    with m4:
        if 'GPS_Audit' in results.columns:
            conflicts = len(results[results['GPS_Audit'] == "❌ Conflict (Moving)"])
            st.metric("GPS Conflicts", conflicts)

    # --- MAIN VIEW ---
    tab1, tab2 = st.tabs(["📊 Detailed Audit Log", "🚛 Vehicle Summary"])

    with tab1:
        st.subheader("Real-time Validation Table")
        
        # UI Styling function
        def style_output(row):
            styles = [''] * len(row)
            if "🚨" in str(row['Time_Status']): styles[results.columns.get_loc('Time_Status')] = 'background-color: #ffe6e6'
            if "GPS_Audit" in row and "❌" in str(row['GPS_Audit']): styles[results.columns.get_loc('GPS_Audit')] = 'background-color: #ffe6e6'
            if "GPS_Audit" in row and "✅" in str(row['GPS_Audit']): styles[results.columns.get_loc('GPS_Audit')] = 'background-color: #e6ffed'
            return styles

        st.dataframe(results.style.apply(style_output, axis=1), use_container_width=True)

    with tab2:
        st.subheader("Tonnage per Vehicle")
        v_sum = results.groupby('Vehicle').agg({'Tonnage': 'sum', 'Duration_Mins': 'mean', 'Data ID': 'count'})
        v_sum.columns = ['Total Tons', 'Avg Duration (Min)', 'Trip Count']
        st.bar_chart(v_sum['Total Tons'])
        st.table(v_sum.style.format("{:.2f}"))

else:
    st.info("👋 Welcome! Please upload your VTCS Excel file in the sidebar to begin the audit.")
