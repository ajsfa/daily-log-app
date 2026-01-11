import streamlit as st
import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURATION ---
# 1. Name of your Google Sheet File
SHEET_NAME = "DailyLogApp"  # <--- CHECK THIS: Must match your Google Sheet Name exactly!

# 2. Define the Scope (What the bot is allowed to do)
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# 3. Connect to Google Sheets
def get_google_sheet():
    # Looks for credentials.json in the same folder
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    # Opens the sheet. Make sure the bot has access!
    sheet = client.open(SHEET_NAME).sheet1 
    return sheet

# --- APP LAYOUT ---
st.title("Daily Log")
st.write("Track the metrics, master the day.")

with st.form("daily_log_form"):
    
    # --- DATE & IDENTITY ---
    name = st.text_input("Name")
    log_date = st.date_input("Date", datetime.date.today(), format="MM/DD/YYYY")
    
    st.divider()
    st.write("### 📊 The Numbers")
    
    col1, col2 = st.columns(2)
    with col1:
        steps = st.number_input("Total Steps", min_value=0, step=100)
        calories_consumed = st.number_input("Calories Consumed", min_value=0, step=10)
        water = st.number_input("Water (oz)", min_value=0, step=8)
        
    with col2:
        kcal_burned = st.number_input("Kcal Burned (Active)", min_value=0, step=10)
        sleep = st.number_input("Sleep Hours", min_value=0.0, step=0.5)
        energy = st.slider("Energy Level", 1, 10, 5)

    st.divider()
    st.write("### 🏋️ Physical Check-in")
    
    workout = st.radio("Did you workout?", ["Yes", "No"], horizontal=True)
    
    muscle_list = [
        "Neck", "Traps", "Shoulders", "Chest", "Biceps", "Triceps", "Forearms",
        "Upper Back", "Lower Back", "Lats", 
        "Abs/Core", "Obliques",
        "Glutes", "Quads", "Hamstrings", "Calves", "Feet/Ankles", "None"
    ]
    sore_area = st.multiselect("Sore Areas (Select all that apply)", muscle_list)

    st.divider()
    st.write("### 🧠 Mental Lab")
    
    feelings = st.text_area("Feelings?", height=100)
    daily_win = st.text_input("Win for today?")
    tomorrow_goal = st.text_input("Tomorrow's Goal")
    vent = st.text_area("Let it out...", height=150)

    # --- SUBMIT ACTION ---
    submitted = st.form_submit_button("Submit Log")

    if submitted:
        if not name:
            st.error("⚠️ Please enter your name before submitting.")
        else:
            # 1. Format Data
            formatted_date = log_date.strftime("%m-%d-%Y")
            sore_string = ", ".join(sore_area) # Converts list to string
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 2. Prepare the Row (Must match Sheet Headers order)
            row_data = [
                timestamp,        # Col A
                formatted_date,   # Col B
                name,             # Col C
                steps,            # Col D
                calories_consumed,# Col E
                water,            # Col F
                kcal_burned,      # Col G
                sleep,            # Col H
                energy,           # Col I
                workout,          # Col J
                sore_string,      # Col K
                feelings,         # Col L
                daily_win,        # Col M
                tomorrow_goal,    # Col N
                vent              # Col O
            ]
            
            # 3. Send to Google
            try:
                st.info("Sending to Cloud...")
                sheet = get_google_sheet()
                sheet.append_row(row_data)
                st.success("✅ Log successfully saved to Google Sheets!")
                st.balloons() # Added a little celebration effect
            except Exception as e:
                st.error(f"❌ Error saving to Google Sheets: {e}")