import streamlit as st
import datetime
import gspread
from google.oauth2.service_account import Credentials
import os
import json
import pytz

# --- CONFIGURATION ---
SHEET_NAME = "DailyLogApp" 
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_google_sheet():
    # 1. Check if we are in the Cloud (Streamlit) and need to create the file
    if not os.path.exists("credentials.json"):
        # Look for the secret in Streamlit's "safe"
        if "gcp_service_account" in st.secrets:
            # Create the missing file temporarily from the secrets
            secrets_dict = dict(st.secrets["gcp_service_account"])
            with open("credentials.json", "w") as f:
                json.dump(secrets_dict, f)

    # 2. Connect to Google Sheets
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    
    # 3. Open the Sheet (Try Name first, failover to ID if needed)
    try:
        sheet = client.open(SHEET_NAME).sheet1
    except:
        st.error("Could not find sheet by name. Check your spelling!")
        return None
        
    return sheet

# --- APP INTERFACE ---
st.title("Daily Log")
st.write("Track the metrics, master the day.")

with st.form("daily_log_form"):
    name = st.text_input("Name")
    log_date = st.date_input("Date", datetime.date.today())
    
    st.write("### 📊 The Numbers")
    col1, col2 = st.columns(2)
    with col1:
        steps = st.number_input("Total Steps", step=100)
        calories_consumed = st.number_input("Calories Consumed", step=10)
        water = st.number_input("Water (oz)", step=8)
    with col2:
        kcal_burned = st.number_input("Kcal Burned (Active)", step=10)
        sleep = st.number_input("Sleep Hours", step=0.5)
        energy = st.slider("Energy Level", 1, 10, 5)

    st.write("### 🏋️ Physical Check-in")
    workout = st.radio("Did you workout?", ["Yes", "No"], horizontal=True)
    muscle_list = ["Neck", "Shoulders", "Chest", "Biceps", "Triceps", "Back", "Core", "Legs", "None"]
    sore_area = st.multiselect("Sore Areas", muscle_list)

    st.write("### 🧠 Mental Lab")
    feelings = st.text_area("Feelings?")
    daily_win = st.text_input("Win for today?")
    tomorrow_goal = st.text_input("Tomorrow's Goal")
    vent = st.text_area("Vent")

    submitted = st.form_submit_button("Submit Log")

    if submitted:
        if not name:
            st.error("⚠️ Name is required.")
        else:
            # --- TIMEZONE FIX ---
            est = pytz.timezone('US/Eastern') 
            now_est = datetime.datetime.now(est)
            timestamp = now_est.strftime("%Y-%m-%d %H:%M:%S")
            
            # Format Date
            formatted_date = log_date.strftime("%m-%d-%Y")

            row = [
                timestamp,
                formatted_date,
                name, steps, calories_consumed, water, kcal_burned, sleep, energy, 
                workout, ", ".join(sore_area), feelings, daily_win, tomorrow_goal, vent
            ]
            try:
                sheet = get_google_sheet()
                if sheet:
                    sheet.append_row(row)
                    st.success("✅ Log saved to Cloud!")
                    st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")
