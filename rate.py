import streamlit as st
import json
from google.oauth2 import service_account

# ✅ Step 1: Paste Google Credentials Directly Here
GOOGLE_CREDENTIALS_JSON = """
{

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
