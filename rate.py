import os
import json
import streamlit as st

# ✅ Step 1: Check if GOOGLE_CREDENTIALS is being passed
st.write("🔍 Checking Environment Variables...")

google_creds = os.getenv("GOOGLE_CREDENTIALS")

if google_creds:
    st.write("✅ Environment variable detected!")
    
    # ✅ Try parsing JSON
    try:
        creds_info = json.loads(google_creds)
        st.write("✅ Credentials successfully loaded as JSON!")
        st.json(creds_info)  # Display JSON (remove after debugging)
    except Exception as e:
        st.write("❌ ERROR: Failed to parse credentials as JSON!")
        st.write(str(e))
else:
    st.write("❌ ERROR: GOOGLE_CREDENTIALS not found!")
