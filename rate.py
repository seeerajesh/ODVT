import json
import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
import plotly.express as px

# Load Google Credentials from Streamlit Secrets
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["GOOGLE_CREDENTIALS"]
)

# Authorize Google Sheets API
client = gspread.authorize(credentials)

# Google Sheet URL (Replace with your actual sheet URL)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1n8LmQ9HRG32mhKfzqYK6vJ0M4R8rXNjXdLl-8TwlB0E/edit?gid=814384498#gid=814384498"

# Fetch data from Google Sheets
@st.cache_data
def get_data():
    sheet = client.open_by_url(SHEET_URL).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Load data
df = get_data()

# Streamlit App UI
st.title("📊 Logistics Intelligence Dashboard")

# Sidebar filters
origin = st.selectbox("Select Origin", sorted(df["Origin"].unique()))
destination = st.selectbox("Select Destination", sorted(df["Destination"].unique()))
vehicle_type = st.selectbox("Select Vehicle Type", sorted(df["Vehicle Type"].unique()))
date_range = st.date_input("Select Date Range", [])

# Apply filters
filtered_df = df[
    (df["Origin"] == origin) & 
    (df["Destination"] == destination) & 
    (df["Vehicle Type"] == vehicle_type)
]

# Display Table
st.subheader("🚚 Lane-wise Pricing Data")
st.dataframe(filtered_df[["Date", "Origin", "Destination", "Vehicle Type", "Price"]])

# Line Chart for Price Trends
st.subheader("📈 Price Trend Over Time")
fig = px.line(filtered_df, x="Date", y="Price", title="Price Fluctuation Over Selected Period")
st.plotly_chart(fig)
