import streamlit as st
import json
from google.oauth2 import service_account

# ✅ Step 1: Paste Google Credentials Directly Here
GOOGLE_CREDENTIALS_JSON = """
{
    "type": "service_account",
    "project_id": "solid-scheme-450717-q8",
    "private_key_id": "f5d059394adf9d6f192c6068adf60d6564748882",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDC50uyrwLu...",
    "client_email": "rateapi@solid-scheme-450717-q8.iam.gserviceaccount.com",
    "client_id": "102105676765134849082",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/rateapi%40solid-scheme-450717-q8.iam.gserviceaccount.com"
}
"""

st.title("Google Credentials Check ✅")

try:
    # ✅ Step 2: Try Parsing the Credentials
    creds_info = json.loads(GOOGLE_CREDENTIALS_JSON)
    credentials = service_account.Credentials.from_service_account_info(creds_info)
    
    # ✅ Step 3: Display Success Message
    st.success("✅ Google Credentials Loaded Successfully!")
    
except Exception as e:
    # ❌ If Credentials Fail, Show Error
    st.error("❌ Failed to Load Google Credentials!")
    st.write(e)
