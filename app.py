import streamlit as st
import pandas as pd
from datetime import timedelta
import plotly.graph_objects as go
from math import radians, cos, sin, asin, sqrt
from pathlib import Path
import re
import base64
import os
import json
import shutil

# =========================================================
# STORAGE SYSTEM (AUTO SAVE / LOAD / RESET)
# =========================================================
DATA_DIR = "saved_data"
TRACKER_DIR = os.path.join(DATA_DIR, "trackers")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TRACKER_DIR, exist_ok=True)

DAILY_PATH = os.path.join(DATA_DIR, "daily_vtcs.csv")
MONTHLY_PATH = os.path.join(DATA_DIR, "monthly_vtcs.csv")
GEO_PATH = os.path.join(DATA_DIR, "geo.json")


def save_csv(df, path):
    df.to_csv(path, index=False)

def load_csv(path):
    return pd.read_csv(path)

def delete_file(path):
    if os.path.exists(path):
        os.remove(path)

def delete_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Sargodha Suthra Punjab Tracking Tool",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# BRANDING
# =========================================================
LOGO_CANDIDATES = [
    Path("logo.jpeg"),
    Path("logo.png"),
]
LOGO_PATH = next((p for p in LOGO_CANDIDATES if p.exists()), None)

def get_base64_image(path: Path | None):
    try:
        if path and path.exists():
            return base64.b64encode(path.read_bytes()).decode()
    except:
        return None
    return None

LOGO_BASE64 = get_base64_image(LOGO_PATH)

# =========================================================
# HELPERS (YOUR ORIGINAL LOGIC UNCHANGED)
# =========================================================
def haversine(lat1, lon1, lat2, lon2):
    r = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return 2 * r * asin(sqrt(a))


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


# =========================================================
# TRACKER SYSTEM (PERSISTENT)
# =========================================================
def load_saved_trackers():
    tracker_map = {}
    for file in os.listdir(TRACKER_DIR):
        try:
            path = os.path.join(TRACKER_DIR, file)
            df = load_data_file(open(path, "rb"))
            tracker_map[normalize_name(file)] = df
        except:
            pass
    return tracker_map


# =========================================================
# SESSION STATE
# =========================================================
if "geo_data" not in st.session_state:
    st.session_state.geo_data = None


# =========================================================
# LOAD SAVED DATA AUTOMATICALLY
# =========================================================
df_vtcs = load_csv(DAILY_PATH) if os.path.exists(DAILY_PATH) else None
df_month = load_csv(MONTHLY_PATH) if os.path.exists(MONTHLY_PATH) else None
tracking_files_map = load_saved_trackers()

if os.path.exists(GEO_PATH):
    try:
        with open(GEO_PATH, "r") as f:
            st.session_state.geo_data = pd.DataFrame(json.load(f))
    except:
        st.session_state.geo_data = None


# =========================================================
# SIDEBAR (UPLOAD + RESET)
# =========================================================
with st.sidebar:

    st.title("Control Panel")

    vtcs_file = st.file_uploader("Daily VTCS", type=["xlsx", "csv"])
    monthly_file = st.file_uploader("Monthly VTCS", type=["xlsx", "csv"])
    tracker_files = st.file_uploader("Tracker Files", type=["xlsx", "csv"], accept_multiple_files=True)
    geo_upload = st.file_uploader("Geofence File", type=["xlsx", "csv"])

    # ---------------- DAILY ----------------
    if vtcs_file:
        df_vtcs = load_data_file(vtcs_file)
        save_csv(df_vtcs, DAILY_PATH)
        st.success("Daily saved")

    if st.button("🗑 Remove Daily Data"):
        delete_file(DAILY_PATH)
        df_vtcs = None
        st.rerun()

    # ---------------- MONTHLY ----------------
    if monthly_file:
        df_month = load_data_file(monthly_file)
        save_csv(df_month, MONTHLY_PATH)
        st.success("Monthly saved")

    if st.button("🗑 Remove Monthly Data"):
        delete_file(MONTHLY_PATH)
        df_month = None
        st.rerun()

    # ---------------- TRACKERS ----------------
    if tracker_files:
        for f in tracker_files:
            path = os.path.join(TRACKER_DIR, f.name)
            with open(path, "wb") as out:
                out.write(f.getbuffer())
        st.success("Trackers saved")

    if st.button("🗑 Remove Trackers"):
        delete_folder(TRACKER_DIR)
        tracking_files_map = {}
        st.rerun()

    # ---------------- GEO ----------------
    if geo_upload:
        raw = load_data_file(geo_upload)
        st.session_state.geo_data = raw

        with open(GEO_PATH, "w") as f:
            json.dump(raw.to_dict(orient="records"), f)

        st.success("Geo saved")

    if st.button("🗑 Remove Geofence"):
        delete_file(GEO_PATH)
        st.session_state.geo_data = None
        st.rerun()


# =========================================================
# MAIN DISPLAY (SIMPLE SAFE VERSION)
# =========================================================
st.title("Sargodha Suthra Punjab Tracking Tool")

st.subheader("Daily Data")
if df_vtcs is not None:
    st.dataframe(df_vtcs.head())
else:
    st.info("No daily data found")

st.subheader("Monthly Data")
if df_month is not None:
    st.dataframe(df_month.head())
else:
    st.info("No monthly data found")

st.subheader("Tracker Files Loaded")
st.write(list(tracking_files_map.keys()))

st.subheader("Geofence Data")
st.write(st.session_state.geo_data)
