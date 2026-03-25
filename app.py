import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="VTCS & AskTech Auditor", layout="wide")

st.title("🚛 VTCS & AskTech Tracker Auditor")
st.markdown("Reconciling Portal entries with AskTech (Pvt) Ltd. Tracking Reports")

# --- SIDEBAR ---
st.sidebar.header("📂 Data Upload")
vtcs_file = st.sidebar.file_uploader("1. Upload VTCS Portal Data", type=['xlsx', 'csv'])
tracking_file = st.sidebar.file_uploader("2. Upload AskTech Tracking Report", type=['xlsx', 'csv'])

def process_audit(vtcs_df, track_df=None):
    # --- 1. VTCS PROCESSING (Kept identical to your working version) ---
    for col in ['Waste Collected (Kg)', 'Before Weight', 'After Weight (Kg)']:
        if col in vtcs_df.columns:
            vtcs_df[col] = pd.to_numeric(vtcs_df[col].astype(str).str.replace(',', ''), errors='coerce')
    
    vtcs_df['Tonnage'] = vtcs_df['Waste Collected (Kg)'] / 1000
    vtcs_df['Time In'] = pd.to_datetime(vtcs_df['Time In'], errors='coerce')
    vtcs_df['Time Out'] = pd.to_datetime(vtcs_df['Time Out'], errors='coerce')
    
    # 30-minute Logic: Above 30 is Suspicious
    vtcs_df['Duration_Mins'] = (vtcs_df['Time Out'] - vtcs_df['Time In']).dt.total_seconds() / 60
    vtcs_df['Time_Status'] = vtcs_df['Duration_Mins'].apply(lambda x: "🚨 Suspicious (>30m)" if x > 30 else "✅ Normal")

    # --- 2. UPDATED TRACKING CROSS-CHECK (For AskTech Format) ---
    if track_df is not None:
        # Standardize Tracking Columns based on your image
        track_df.columns = [str(c).strip() for c in track_df.columns]
        
        # Ensure we have the 'Time' and 'Status' columns from your tracker
        if 'Time' in track_df.columns and 'Status' in track_df.columns:
            track_df['Time'] = pd.to_datetime(track_df['Time'], errors='coerce')
            
            gps_audit_results = []
            
            for idx, row in vtcs_df.iterrows():
                target_time = row['Time In']
                
                if pd.isnull(target_time):
                    gps_audit_results.append("❓ Invalid VTCS Time")
                    continue

                # 2-Minute Grace Period Logic (+/- 2 mins)
                mask = (track_df['Time'] >= target_time - timedelta(minutes=2)) & \
                       (track_df['Time'] <= target_time + timedelta(minutes=2))
                
                nearby_pings = track_df[mask]
                
                if nearby_pings.empty:
                    gps_audit_results.append("❓ No GPS Data Found")
                else:
                    # In your image: 'Parked' and 'Idle' are both stationary
                    statuses = nearby_pings['Status'].astype(str).str.lower().values
                    is_valid = any(('idle' in s or 'parked' in s) for s in statuses)
                    
                    if is_valid:
                        gps_audit_results.append("✅ Verified (Idle/Parked)")
                    else:
                        gps_audit_results.append("❌ Conflict (Moving)")
            
            vtcs_df['GPS_Audit'] = gps_audit_results
        else:
            st.error("Tracking report columns must include 'Time' and 'Status'.")

    return vtcs_df

if vtcs_file:
    # VTCS Loading
    df_vtcs = pd.read_excel(vtcs_file) if vtcs_file.name.endswith('xlsx') else pd.read_csv(vtcs_file)
    
    # Tracking Loading
    df_track = None
    if tracking_file:
        # AskTech reports have a header at the top. 
        # We start reading from where the actual data table begins.
        df_track = pd.read_excel(tracking_file, skiprows=18) 

    results = process_audit(df_vtcs, df_track)

    # --- UI DISPLAY ---
    st.header("📊 Daily Audit Summary")
    
    # Tonnage Summary
    total_tons = results['Tonnage'].sum()
    st.metric("Total Tonnage Today", f"{total_tons:.2f} Tons")

    # Vehicle Table
    st.subheader("Vehicle-wise Breakdown")
    v_sum = results.groupby('Vehicle').agg({'Tonnage': 'sum', 'Data ID': 'count'}).rename(columns={'Data ID': 'Trips'})
    st.table(v_sum)

    # Detailed Audit Log
    st.subheader("🔍 Detailed Audit Log")
    show_cols = ['Vehicle', 'Time In', 'Time Out', 'Duration_Mins', 'Tonnage', 'Time_Status']
    if 'GPS_Audit' in results.columns:
        show_cols.append('GPS_Audit')

    def highlight_results(val):
        if '🚨' in str(val) or '❌' in str(val): return 'background-color: #ffcccc'
        if '✅' in str(val): return 'background-color: #ccffcc'
        return ''

    st.dataframe(results[show_cols].style.applymap(highlight_results), use_container_width=True)

else:
    st.info("Please upload your VTCS file to begin.")
