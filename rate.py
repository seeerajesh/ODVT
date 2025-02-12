import json
import streamlit as st
from google.oauth2 import service_account
import gspread

# Load Google Credentials from Streamlit Secrets
try:
    creds_info = json.loads(json.dumps(st.secrets["GOOGLE_CREDENTIALS"]))  # Convert TOML to JSON format
    credentials = service_account.Credentials.from_service_account_info(creds_info)
    st.write("✅ Google authentication successful!")  # Debugging message
except Exception as e:
    st.write("❌ Error with Google authentication:", e)

# Authorize Google Sheets API
client = gspread.authorize(credentials)

# Fetch Google Sheets data
SHEET_URL = "YOUR_GOOGLE_SHEET_URL"
sheet = client.open_by_url(SHEET_URL).sheet1
data = sheet.get_all_records()

# Convert to DataFrame
import pandas as pd
df = pd.DataFrame(data)

# Display Data
st.title("📊 Logistics Intelligence Dashboard")
st.write(df.head())  # Debugging: Show first rows of data
