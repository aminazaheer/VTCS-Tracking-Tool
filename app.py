import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="VTCS & GPS Auditor", layout="wide")

st.title("🚛 VTCS & GPS Tracking Auditor")

# --- SIDEBAR ---
st.sidebar.header("Upload Data")
vtcs_file = st.sidebar.file_uploader("1. Upload VTCS Data (Excel/CSV)", type=['xlsx', 'csv'])
tracking_file = st.sidebar.file_uploader("2. Upload Tracking Report (Excel/CSV)", type=['xlsx', 'csv'])

def convert_df_to_csv(df):
    return df.to_csv(index=True if 'Vehicle' in df.index.names else False).encode('utf-8')

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
        # Auto-detect header if not at top
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
            for idx, row in vtcs_df.iterrows():
                target_time = row['Time In']
                if pd.isnull(target_time):
                    gps_audit_results.append("❓ Invalid Time")
                    continue

                mask = (track_df['Time'] >= target_time - timedelta(minutes=2)) & \
                       (track_df['Time'] <= target_time + timedelta(minutes=2))
                
                nearby_pings = track_df[mask]
                
                if nearby_pings.empty:
                    gps_audit_results.append("❓ No GPS Data")
                else:
                    statuses = nearby_pings['Status'].astype(str).str.lower().values
                    is_valid = any(('idle' in s or 'parked' in s or 'stopped' in s) for s in statuses)
                    gps_audit_results.append("✅ Verified (Idle)" if is_valid else "❌ Conflict (Moving)")
            
            vtcs_df['GPS_Audit'] = gps_audit_results
        else:
            st.sidebar.error("Could not detect 'Time' and 'Status' in Tracking file.")

    return vtcs_df

if vtcs_file:
    df_vtcs = pd.read_excel(vtcs_file) if vtcs_file.name.endswith('xlsx') else pd.read_csv(vtcs_file)
    
    df_track = None
    if tracking_file:
        df_track = pd.read_excel(tracking_file) if tracking_file.name.endswith('xlsx') else pd.read_csv(tracking_file)
    
    results = process_audit(df_vtcs, df_track)

    # --- UI DASHBOARD ---
    st.header("📋 Audit Dashboard")
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Tonnage (Day)", f"{results['Tonnage'].sum():.2f} Tons")
    m2.metric("Delayed Trips (>30m)", len(results[results['Time_Status'].str.contains("🚨")]))
    if 'GPS_Audit' in results.columns:
        m3.metric("GPS Conflicts", len(results[results['GPS_Audit'] == "❌ Conflict (Moving)"]))

    # --- VEHICLE SUMMARY SECTION ---
    st.divider()
    st.subheader("Vehicle-Wise Summary")
    summary = results.groupby('Vehicle').agg({
        'Tonnage': 'sum', 
        'Data ID': 'count'
    }).rename(columns={'Data ID': 'Total Trips', 'Tonnage': 'Total Tonnage (Tons)'})
    
    st.table(summary)
    
    # Download Vehicle Summary
    sum_csv = convert_df_to_csv(summary)
    st.download_button(
        label="📥 Download Vehicle Summary CSV",
        data=sum_csv,
        file_name="Vehicle_Summary.csv",
        mime="text/csv",
    )

    # --- DETAILED LOGS SECTION ---
    st.divider()
    st.subheader("Detailed Audit Logs")
    display_cols = ['Vehicle', 'Time In', 'Time Out', 'Duration_Mins', 'Tonnage', 'Time_Status']
    if 'GPS_Audit' in results.columns:
        display_cols.append('GPS_Audit')

    def color_rows(val):
        if '🚨' in str(val) or '❌' in str(val): return 'background-color: #ffcccc'
        if '✅' in str(val): return 'background-color: #ccffcc'
        return ''

    st.dataframe(results[display_cols].style.applymap(color_rows), use_container_width=True)

    # Download Detailed Audit
    full_csv = convert_df_to_csv(results[display_cols])
    st.download_button(
        label="📥 Download Detailed Audit Report",
        data=full_csv,
        file_name="Full_Audit_Report.csv",
        mime="text/csv",
    )

else:
    st.info("Please upload your VTCS file from the sidebar to start.")
