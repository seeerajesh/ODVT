import json
import streamlit as st
from google.oauth2 import service_account
import gspread

# ✅ Step 1: Manually Enter Your Google Credentials (Paste Your JSON Key Below)
GOOGLE_CREDENTIALS_JSON = """
{
    "type": "service_account",
    "project_id": "solid-scheme-450717-q8",
    "private_key_id": "f5d059394adf9d6f192c6068adf60d6564748882",
    "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDC50uyrwLu+8wQ\\npnjb/ZZzL2/YtdRySyJxA0RKl1orC4CxMLaqQG6//tz1GrO+vOrqvXZfuf/AWbP/...",
    "client_email": "rateapi@solid-scheme-450717-q8.iam.gserviceaccount.com",
    "client_id": "102105676765134849082",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/rateapi%40solid-scheme-450717-q8.iam.gserviceaccount.com"
}
"""

# ✅ Step 2: Authenticate with Google Sheets API
creds_info = json.loads(GOOGLE_CREDENTIALS_JSON)
credentials = service_account.Credentials.from_service_account_info(creds_info)
client = gspread.authorize(credentials)

# ✅ Step 3: Access Google Sheets
SHEET_URL = "https://docs.google.com/spreadsheets/d/1n8LmQ9HRG32mhKfzqYK6vJ0M4R8rXNjXdLl-8TwlB0E/edit?gid=814384498#gid=814384498"  # ❗ Replace with actual Google Sheets URL
sheet = client.open_by_url(SHEET_URL).sheet1

# ✅ Step 4: Fetch Data
data = sheet.get_all_records()

# ✅ Step 5: Print One Field (First Value in First Row)
st.write("🔍 First Field in Google Sheet:", data[0] if data else "No Data Found")
