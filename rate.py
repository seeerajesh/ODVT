import os
import json
import streamlit as st
from google.oauth2 import service_account
import gspread
import pandas as pd

# ✅ DEBUG: Check if GOOGLE_CREDENTIALS is set in environment
st.write("🔍 Checking Environment Variables...")

google_creds = os.getenv("GOOGLE_CREDENTIALS")

if google_creds:
    st.write("✅ Environment variable loaded successfully!")
    creds_info = json.loads(google_creds)  # Convert string to JSON dict
    credentials = service_account.Credentials.from_service_account_info(creds_info)
else:
    st.write("❌ ERROR: GOOGLE_CREDENTIALS not found in environment!")
    st.stop()  # Stop execution if credentials are missing

# ✅ Authorize Google Sheets API
client = gspread.authorize(credentials)

# ✅ Fetch Google Sheets Data
SHEET_URL = "https://docs.google.com/spreadsheets/d/1n8LmQ9HRG32mhKfzqYK6vJ0M4R8rXNjXdLl-8TwlB0E/edit?gid=814384498#gid=814384498"
sheet = client.open_by_url(SHEET_URL).sheet1
data = sheet.get_all_records()

# ✅ Convert to DataFrame
df = pd.DataFrame(data)

# ✅ Streamlit Dashboard UI
st.title("📊 Logistics Intelligence Dashboard")

# ✅ Filters
origin = st.selectbox("Select Origin", sorted(df["Origin"].unique()))
destination = st.selectbox("Select Destination", sorted(df["Destination"].unique()))
vehicle_type = st.selectbox("Select Vehicle Type", sorted(df["Vehicle Type"].unique()))

# ✅ Apply filters
filtered_df = df[
    (df["Origin"] == origin) &
    (df["Destination"] == destination) &
    (df["Vehicle Type"] == vehicle_type)
]

# ✅ Display Table
st.subheader("🚚 Lane-wise Pricing Data")
st.dataframe(filtered_df[["Date", "Origin", "Destination", "Vehicle Type", "Price"]])

# ✅ Line Chart for Price Trends
import plotly.express as px
st.subheader("📈 Price Trend Over Time")
fig = px.line(filtered_df, x="Date", y="Price", title="Price Fluctuation Over Selected Period")
st.plotly_chart(fig)
