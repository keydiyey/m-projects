import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# --- CONFIG ---
LOADOUTS_FILE = "loadouts.json"
MAX_CYCLES = {"HF": 40, "TC": 200, "DH": 2000, "Bake": 2000}

CHAMBERS = [f"Chamber {i+1}" for i in range(8)]
OVENS = [f"Oven {i+1}" for i in range(4)]
TS = ["Thermal Shock 1"]
ALL_UNITS = CHAMBERS + TS + OVENS

def get_capacity(unit):
    return 20 if unit == "Chamber 1" else 14

def load_json():
    if os.path.exists(LOADOUTS_FILE):
        with open(LOADOUTS_FILE, "r") as f:
            return json.load(f)
    return {unit: [] for unit in ALL_UNITS}

def save_json(data):
    with open(LOADOUTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

if 'state' not in st.session_state:
    st.session_state.state = load_json()

st.set_page_config(page_title="Lab Tracker", layout="wide")


with st.sidebar:
    st.header("📥 Log Readout")
    with st.form("log_form", clear_on_submit=True):
        u_date = st.date_input("Date Measured", value=datetime.now())
        u_unit = st.selectbox("Unit", ALL_UNITS)
        u_id = st.text_input("Sample ID")
        u_test = st.selectbox("Test Type", list(MAX_CYCLES.keys()))
        u_val = st.number_input("Current Cycles", min_value=0)
